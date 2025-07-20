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
            print("🔍 Đang lấy danh sách ten_tk từ giaovien...")
            cursor.execute("SELECT ten_tk FROM giaovien WHERE ten_tk IS NOT NULL")
            gv_nicknames = [row["ten_tk"].strip().lower() for row in cursor.fetchall()]
            print(f"✅ Tìm được {len(gv_nicknames)} tài khoản từ giáo viên")

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

                print(f"➕ Tạo user: {username}")
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
            print(f"🎯 Sync xong. Tạo: {created}, Bỏ qua: {skipped}")

        return jsonify({"status": "ok", "created": created, "skipped": skipped})

    except Exception as e:
        conn.rollback()
        print("❌ Lỗi khi sync:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500

    finally:
        conn.close()

@users_bp.route("/add", methods=["POST"])
def add_user():
    data = request.get_json()
    username = data.get("username", "").strip().lower()
    password = data.get("password", "").strip()
    role = data.get("role", "user").strip().lower()
    password_expiry = data.get("password_expiry", "")

    if not username or not password:
        return jsonify({"message": "Missing username or password."}), 400

    if not re.match(r"^[a-zA-Z0-9_.-]{3,30}$", username):
        return jsonify({"message": "Invalid username format"}), 400

    if len(password) < 6:
        return jsonify({"message": "Password too short."}), 400

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

    if session.get("role") != "admin":
        return jsonify({"status": "error", "message": "Only admin can delete users."}), 403

    conn = get_conn()
    with conn.cursor() as cursor:
        # Lấy ma_gv từ bảng giaovien
        cursor.execute("""
            SELECT ma_gv FROM giaovien WHERE ten_tk = %s
        """, (username,))
        result = cursor.fetchone()
        ma_gv = result["ma_gv"] if result else None

        # Nếu tồn tại ma_gv, xử lý các bảng liên quan
        if ma_gv:
            # xoá liên quan tới ma_gv ở các bảng có ma_gv
            cursor.execute("DELETE FROM lop_gv WHERE ma_gv = %s", (ma_gv,))
            # … nếu có thêm bảng khác dùng ma_gv, xử lý tiếp ở đây

            # cập nhật ma_gv trong giaovien
            new_ma_gv = f"XX{ma_gv[2:]}" if len(ma_gv) >= 2 else f"XX{ma_gv}"
            cursor.execute("""
                UPDATE giaovien SET ma_gv = %s WHERE ma_gv = %s
            """, (new_ma_gv, ma_gv))

        # xoá dữ liệu liên quan tới ten_tk
        cursor.execute("DELETE FROM bangdanhgia WHERE ten_tk = %s", (username,))
        cursor.execute("DELETE FROM tongdiem_epa WHERE ten_tk = %s", (username,))
        cursor.execute("DELETE FROM logs WHERE user_ten_tk = %s", (username,))
        cursor.execute("DELETE FROM thoigianmoepa WHERE ten_tk = %s", (username,))
        # xóa user
        cursor.execute("DELETE FROM tk WHERE ten_tk = %s", (username,))
        if cursor.rowcount == 0:
            return jsonify({"status": "error", "message": f"User '{username}' not found"}), 404

        # log lại thao tác
        cursor.execute("INSERT INTO logs (target_table, action) VALUES (%s, %s)", (
            "tk",
            f"Deleted user '{username}' by {session.get('user', 'system')} (and updated ma_gv if exists)"
        ))

        conn.commit()
    conn.close()
    return jsonify({"status": "ok", "message": f"User '{username}' deleted and ma_gv updated (if applicable)."})

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
