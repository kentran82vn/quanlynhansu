from flask import Blueprint, request, jsonify, session
from utils.db import get_conn
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from flask import current_app
import re

users_bp = Blueprint('users_api', __name__, url_prefix="/api/users")

@users_bp.route("", methods=["GET"])
def get_users():
    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT ten_tk AS username, nhom AS role, ngay_tao AS created_date,
                   nguoi_tao AS created_by, ngay_hh AS password_expiry
            FROM tk
        """)
        result = cursor.fetchall()
    conn.close()
    return jsonify(result)

@users_bp.route("/sync", methods=["POST"])
def sync_users_from_employees():
    conn = get_conn()
    created, skipped = 0, 0
    try:
        with conn.cursor() as cursor:
            # print("🔍 Đang lấy danh sách ten_tk từ giaovien...")
            cursor.execute("SELECT ten_tk FROM giaovien WHERE ten_tk IS NOT NULL")
            gv_nicknames = [row["ten_tk"].strip().lower() for row in cursor.fetchall()]
            # print(f"✅ Tìm được {len(gv_nicknames)} tài khoản từ giáo viên")

            for username in gv_nicknames:
                if not username:
                    continue
                cursor.execute("SELECT 1 FROM tk WHERE ten_tk = %s", (username,))
                if cursor.fetchone():
                    skipped += 1
                    continue

                created_date = datetime.today().date()
                password_expiry = created_date + timedelta(days=90)
                password = generate_password_hash("abc000")

                # print(f"➕ Tạo user: {username}")
                cursor.execute("""
                    INSERT INTO tk (ten_tk, nhom, mat_khau, ngay_tao, nguoi_tao, ngay_hh)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (username, 'user', password, created_date, "system", password_expiry))
                created += 1

            if created > 0:
                cursor.execute("""
                    INSERT INTO logs (target_table, action) VALUES (%s, %s)
                """, ("tk", f"Synchronized {created} user(s) from giaovien"))

            conn.commit()
            # print(f"🎯 Sync xong. Tạo: {created}, Bỏ qua: {skipped}")

        return jsonify({"status": "ok", "created": created, "skipped": skipped})

    except Exception as e:
        conn.rollback()
        # Improved logging with more details
        current_app.logger.error(f"Error in sync_users_from_employees: {str(e)}")
        current_app.logger.error(f"User: {session.get('user', 'unknown')}")
        # Return generic error message for security
        return jsonify({"status": "error", "message": "Đã xảy ra lỗi khi đồng bộ tài khoản"}), 500

    finally:
        conn.close()

@users_bp.route("/add", methods=["POST"])
def add_user():
    # Enhanced input validation
    if not request.is_json:
        return jsonify({"message": "Content-Type phải là application/json"}), 400
    
    data = request.get_json()
    if not data:
        return jsonify({"message": "Dữ liệu JSON không hợp lệ"}), 400
    
    username = data.get("username", "").strip().lower()
    password = data.get("password", "").strip()
    role = data.get("role", "user").strip().lower()
    password_expiry = data.get("password_expiry", "")

    # Existing validation (keep original logic)
    if not username or not password:
        return jsonify({"message": "Missing username or password."}), 400

    if not re.match(r"^[a-zA-Z0-9_.-]{3,30}$", username):
        return jsonify({"message": "Invalid username format"}), 400

    if len(password) < 6:
        return jsonify({"message": "Password too short."}), 400
    
    # Additional safe validation
    if role not in ["admin", "user", "supervisor"]:
        role = "user"  # Default to safe value instead of rejecting
        
    # Password strength check (warning only, doesn't block)
    if password.lower() in ["password", "123456", "admin", "user"]:
        current_app.logger.warning(f"Weak password detected for user: {username}")

    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM tk WHERE ten_tk = %s", (username,))
        if cursor.fetchone():
            return jsonify({"message": f"User '{username}' already exists."}), 400

        created_date = datetime.today().date()
        created_by = session.get("user", "system")  # FIXED
        staff_id = None
        password_expiry_val = None if role == "admin" else (created_date + timedelta(days=90))
        hashed_password = generate_password_hash(password)

        # Đúng
        cursor.execute("""
            INSERT INTO tk (ten_tk, nhom, mat_khau, ngay_tao, nguoi_tao, ngay_hh)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (username, role, hashed_password, created_date, created_by, password_expiry_val))

        # Log đúng
        cursor.execute("INSERT INTO logs (target_table, action) VALUES (%s, %s)", (
            "tk",
            f"Added new user '{username}' with role '{role}'"
        ))

        conn.commit()
    conn.close()

    return jsonify({"message": f"User '{username}' added successfully!", "clear_fields": True})

@users_bp.route("/change-password", methods=["POST"])
def change_password():
    data = request.get_json()
    username = data.get("ten_tk", "").strip().lower()
    new_password = data.get("new_password", "").strip()

    if not username or not new_password:
        return jsonify({"error": "Missing data."}), 400

    if len(new_password) < 6:
        return jsonify({"error": "Password too short."}), 400

    conn = get_conn()
    with conn.cursor() as cursor:
        hashed_password = generate_password_hash(new_password)
        cursor.execute("UPDATE tk SET mat_khau = %s WHERE ten_tk = %s", (hashed_password, username))

        cursor.execute("""
            INSERT INTO logs (user_ten_tk, target_table, target_staff_id, action)
            VALUES (%s, %s, %s, %s)
        """, (
            session.get("user", "system"),  # người thao tác
            "tk",                           # bảng bị tác động
            username,                       # tài khoản bị đổi
            "Changed password"
        ))

        conn.commit()
    conn.close()

    return jsonify({"message": f"Password for '{username}' changed successfully!"})
 
@users_bp.route("/delete", methods=["POST"])
def delete_user():
    data = request.get_json()
    username = data.get("ten_tk", "").strip().lower()
    if not username:
        return jsonify({"status": "error", "message": "Missing username"}), 400
    # Debug: log current session info
    current_user = session.get("user", "")
    current_role = session.get("role", "")
    print(f"[DEBUG] Current user: {current_user}, role: {current_role}")
    
    # Temporary: allow specific users for testing
    allowed_users = ["admin", "kimnhung", "ngocquy"] 
    if current_role != "admin" and current_user not in allowed_users:
        return jsonify({"status": "error", "message": f"Only admin can delete users. Current user: {current_user}, role: {current_role}"}), 403

    conn = get_conn()
    deleted_counts = {}
    remaining_counts = {}
    with conn.cursor() as cursor:
        # print(f"[INFO] 🔎 Bắt đầu kiểm tra dữ liệu liên quan đến user: {username}")
        related_tables = {
            "giaovien": "ten_tk",
            "bangdanhgia": "ten_tk",
            "tongdiem_epa": "ten_tk",
            "thoigianmoepa": "ten_tk",
            "logs": "user_ten_tk",
        }
        related = {}
        for table, col in related_tables.items():
            cursor.execute(f"SELECT COUNT(*) AS cnt FROM {table} WHERE {col} = %s", (username,))
            cnt = cursor.fetchone()["cnt"]
            related[table] = cnt
            # print(f"[INFO] 📊 {table}: {cnt}")

        cursor.execute("SELECT ma_gv FROM giaovien WHERE ten_tk = %s", (username,))
        ma_gv_row = cursor.fetchone()
        ma_gv = ma_gv_row["ma_gv"] if ma_gv_row else None
        if ma_gv:
            cursor.execute("SELECT COUNT(*) AS cnt FROM lop_gv WHERE ma_gv = %s", (ma_gv,))
            cnt = cursor.fetchone()["cnt"]
            related["lop_gv"] = cnt
            # print(f"[INFO] 📊 lop_gv: {cnt}")
        else:
            related["lop_gv"] = 0

        if str(data.get("confirm")).lower() != "true":
            # print(f"[INFO] 🚦 Đang ở bước xác nhận, chưa xoá.")
            return jsonify({"status": "pending", "message": "Data found for deletion", "related": related}), 200

        # print(f"[INFO] 🗑️ Bắt đầu xoá dữ liệu của user: {username}")

        if ma_gv:
            cursor.execute("DELETE FROM lop_gv WHERE ma_gv = %s", (ma_gv,))
            deleted_counts["lop_gv"] = cursor.rowcount
            # print(f"[INFO] ✅ Đã xoá {deleted_counts['lop_gv']} bản ghi ở lop_gv")

            new_ma_gv = f"XX{ma_gv[2:]}" if len(ma_gv) >= 2 else f"XX{ma_gv}"
            cursor.execute("UPDATE giaovien SET ma_gv = %s WHERE ma_gv = %s", (new_ma_gv, ma_gv))
            deleted_counts["giaovien_update"] = cursor.rowcount
            # print(f"[INFO] ✍️ Đã cập nhật ma_gv thành {new_ma_gv} ở giaovien")

        for table in ["bangdanhgia", "tongdiem_epa", "thoigianmoepa", "logs"]:
            col = "user_ten_tk" if table == "logs" else "ten_tk"
            cursor.execute(f"DELETE FROM {table} WHERE {col} = %s", (username,))
            deleted_counts[table] = cursor.rowcount
            # print(f"[INFO] ✅ Đã xoá {deleted_counts[table]} bản ghi ở {table}")

        cursor.execute("DELETE FROM tk WHERE ten_tk = %s", (username,))
        if cursor.rowcount == 0:
            # print(f"[ERROR] 🚫 User '{username}' không tìm thấy ở bảng tk.")
            return jsonify({"status": "error", "message": f"User '{username}' not found"}), 404
        deleted_counts["tk"] = cursor.rowcount
        # print(f"[INFO] 🗑️ Đã xoá user ở bảng tk")

        cursor.execute(
            "INSERT INTO logs (target_table, action) VALUES (%s, %s)",
            ("tk", f"Deleted user '{username}' and related data by {session.get('user', 'system')}")
        )
        # print(f"[INFO] 📝 Đã ghi log thao tác")

        conn.commit()
        # print(f"[INFO] 💾 Commit transaction thành công")

        # Kiểm tra lại dữ liệu còn không
        # print(f"[INFO] 🔍 Kiểm tra lại dữ liệu còn sót lại của user: {username}")
        for table, col in related_tables.items():
            cursor.execute(f"SELECT COUNT(*) AS cnt FROM {table} WHERE {col} = %s", (username,))
            cnt = cursor.fetchone()["cnt"]
            remaining_counts[table] = cnt
            print(f"[CHECK] {table}: còn lại {cnt}")
        if ma_gv:
            cursor.execute("SELECT COUNT(*) AS cnt FROM lop_gv WHERE ma_gv = %s", (ma_gv,))
            cnt = cursor.fetchone()["cnt"]
            remaining_counts["lop_gv"] = cnt
            print(f"[CHECK] lop_gv: còn lại {cnt}")
        else:
            remaining_counts["lop_gv"] = 0

    conn.close()

    return jsonify({
        "status": "ok",
        "message": f"User '{username}' and related data deleted.",
        "deleted_counts": deleted_counts,
        "remaining_counts": remaining_counts
    }), 200

@users_bp.route("/update", methods=["POST"])
def update_user_role():
    data = request.get_json()
    username = data.get("username", "").strip().lower() # Thay ten_tk thành username
    new_role = data.get("role", "").strip().lower()     # Thay nhom thành role

    if not username or new_role not in ["admin", "user", "supervisor"]:
        return jsonify({"message": "Invalid data"}), 400

    conn = get_conn()
    with conn.cursor() as cursor:
        if new_role == "admin":
            cursor.execute("UPDATE tk SET nhom = %s, ngay_hh = NULL WHERE ten_tk = %s",
                           (new_role, username))
        else:
            expiry = datetime.today().date() + timedelta(days=90)
            cursor.execute("UPDATE tk SET nhom = %s, ngay_hh = %s WHERE ten_tk = %s",
                           (new_role, expiry, username))

        cursor.execute("INSERT INTO logs (target_table, action) VALUES (%s, %s)", (
            "tk", f"Updated role for '{username}' to '{new_role}'"
        ))

        conn.commit()
    conn.close()
    return jsonify({"message": f"Role updated to '{new_role}' for '{username}'."})

@users_bp.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json()
    username = data.get("username", "").strip().lower()
    if not username:
        return jsonify({"error": "Missing username"}), 400
    new_pass = "mnhhd000"
    hashed_password = generate_password_hash(new_pass)
    conn = get_conn()
    with conn.cursor() as cursor:
        # ✅ Cập nhật mật khẩu
        cursor.execute("UPDATE tk SET mat_khau = %s WHERE ten_tk = %s", (hashed_password, username))
        # ✅ Ghi log
        cursor.execute("""
            INSERT INTO logs (user_ten_tk, target_table, target_staff_id, action)
            VALUES (%s, %s, %s, %s)
        """, (
            session.get("user", "system"),
            "tk",
            username,
            "Reset password"
        ))
        conn.commit()
    conn.close()
    return jsonify({"new_pass": new_pass})
