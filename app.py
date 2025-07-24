from flask import Flask, render_template, request, redirect, session, jsonify, send_from_directory
from utils.db import get_conn
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from apis.users_api import users_bp
from apis.importdata_api import import_bp
from apis.giaovien_epa import giaovien_epa_bp
from apis.thoigianmoepa_api import thoigianmoepa_bp
from apis.bangdanhgiaepa_api import bangdanhgiaepa_bp
from config import DB_CONFIG
import sqlite3  # Giả sử dùng SQLite, thay bằng DB khác nếu cần
import mysql.connector
import pymysql
import threading
import webbrowser
import os
import json
import re
import pandas as pd

app = Flask(__name__, static_folder='Static', static_url_path='/static')
app.secret_key = "supersecretkey"
app.register_blueprint(thoigianmoepa_bp)
app.register_blueprint(users_bp)
app.register_blueprint(import_bp)
app.register_blueprint(giaovien_epa_bp)
app.register_blueprint(bangdanhgiaepa_bp)

def log_action(user_ten_tk, action, target_table=None, target_staff_id=None):
    conn = get_conn()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO logs (user_ten_tk, action, target_table, target_staff_id)
                VALUES (%s, %s, %s, %s)
            """, (user_ten_tk, action, target_table, target_staff_id))
        conn.commit()
    except Exception as e:
        print("❌ Failed to log action:", e)
    finally:
        conn.close()

def parse_date(d):
    try:
        return datetime.strptime(d, "%d/%m/%Y").date()
    except:
        return None

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

@app.route("/login", methods=["GET", "POST"])
def login():
    conn = get_conn()

    # ✅ Tạo admin mặc định nếu chưa có tài khoản admin nào
    with conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) AS count FROM tk WHERE nhom = 'admin'")
        result = cursor.fetchone()
        if result["count"] == 0:
            cursor.execute("""
                INSERT INTO tk (ten_tk, nhom, mat_khau, ngay_tao, nguoi_tao, ngay_hh)
                VALUES (%s, %s, %s, %s, %s, NULL)
            """, (
                "admin",
                "admin",
                generate_password_hash("admin123"),
                datetime.today().date(),
                "system"
            ))
            conn.commit()
            print("✅ Đã tạo tài khoản admin mặc định: admin / admin123")

    # ✅ Xử lý đăng nhập
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM tk WHERE ten_tk = %s", (username,))
            user = cursor.fetchone()

        if user and check_password_hash(user["mat_khau"], password):
            session["user"] = user["ten_tk"]
            session["role"] = user["nhom"]
            session["password_expiry"] = (
                user["ngay_hh"].strftime("%Y-%m-%d") if user["ngay_hh"] else "Unexpired"
            )

            print(f"✅ Logged in as: {session['user']} (role: {session['role']})")

            conn.close()
            return redirect("/dashboard")

        else:
            conn.close()
            return render_template("login.html", error="Invalid username or password")

    conn.close()
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")
    return render_template("index.html", user=session["user"], role=session["role"])

@app.route("/employees")
def employees():
    if "user" not in session:
        return redirect("/")

    # Check if user is "admin" or role is "Administrator"
    if session["user"] in ("admin", "kimnhung") or session["role"] in ("Administrator"):
        return render_template(
            "nhanvien__index.html",
            user=session["user"],
            role=session["role"],
            password_expiry=session.get("password_expiry")
        )
    else:
        return render_template(
            "nhansu_info.html",
            user=session["user"],
            role=session["role"],
            password_expiry=session.get("password_expiry")
        )

# Thêm dữ liệu mới cho giáo viên và học sinh
@app.route("/add", methods=["POST"])
def add_employee():
    data = request.get_json()
    dept = data.get("Dept", "GV").upper()

    if dept == "GV":
        staff_id = data.get("Ma Gv")
        full_name = data.get("Ho Va Ten")
        ten_tk = (data.get("Ten Tk") or "").strip().lower()

        if not staff_id or not full_name:
            return jsonify({"status": "error", "message": "Missing Staff ID or Full Name"}), 400

        conn = get_conn()
        with conn.cursor() as cursor:
            # ✅ Kiểm tra và tạo tài khoản trong bảng `tk` nếu chưa tồn tại
            if ten_tk:
                cursor.execute("SELECT 1 FROM tk WHERE ten_tk = %s", (ten_tk,))
                if not cursor.fetchone():
                    cursor.execute("INSERT INTO tk (ten_tk, nhom) VALUES (%s, %s)", (ten_tk, "user"))
                    log_action(user_ten_tk=session.get("user", "user"),
                               target_table="tk",
                               target_staff_id=ten_tk,
                               action=f"Created login account for teacher")

            # ✅ Kiểm tra trùng mã giáo viên
            cursor.execute("SELECT 1 FROM giaovien WHERE ma_gv = %s", (staff_id,))
            if cursor.fetchone():
                return jsonify({"status": "error", "message": f"Staff ID '{staff_id}' already exists"}), 400

            # ✅ Thêm giáo viên
            cursor.execute("""
                INSERT INTO giaovien (
                    ma_gv, ho_va_ten, ten_tk, chuc_vu, ngay_sinh, que_quan, cccd,
                    ngay_cap, mst, cmnd, so_bh, sdt, tk_nh, email, nhom_mau, dia_chi
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                staff_id,
                full_name,
                ten_tk,
                data.get("Chuc Vu"),
                parse_date(data.get("Ngay Sinh")),
                data.get("Que Quan"),
                data.get("Cccd"),
                parse_date(data.get("Ngay Cap")),
                data.get("Mst"),
                data.get("Cmnd"),
                data.get("So Bh"),
                data.get("Sdt"),
                data.get("Tk Nh"),
                data.get("Email"),
                data.get("Nhom Mau"),
                data.get("Dia Chi")
            ))

            log_action(user_ten_tk=session.get("user", "user"),
                       target_table="giaovien",
                       target_staff_id=staff_id,
                       action=f"Added GV staff {full_name}")

        conn.commit()
        conn.close()
        return jsonify({"status": "ok"})

    elif dept == "HS":
        student_id = data.get("Ma Hs")
        full_name = data.get("Ho Va Ten")
        if not student_id or not full_name:
            return jsonify({"status": "error", "message": "Missing Student ID or Full Name"}), 400
        conn = get_conn()
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1 FROM hocsinh WHERE ma_hs = %s", (student_id,))
            if cursor.fetchone():
                return jsonify({"status": "error", "message": f"Student ID '{student_id}' already exists"}), 400
            cursor.execute("""
                INSERT INTO hocsinh (
                    ma_hs, ho_va_ten, ngay_sinh, gioi_tinh, dan_toc,
                    ma_dinh_danh, ho_ten_bo, nghe_nghiep_bo, ho_ten_me,
                    nghe_nghiep_me, ho_khau, cccd_bo_me, sdt
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                student_id,
                full_name,
                parse_date(data.get("Ngay Sinh")),
                data.get("Gioi Tinh"),
                data.get("Dan Toc"),
                data.get("Ma Dinh Danh"),
                data.get("Ho Ten Bo"),
                data.get("Nghe Nghiep Bo"),
                data.get("Ho Ten Me"),
                data.get("Nghe Nghiep Me"),
                data.get("Ho Khau"),
                data.get("Cccd Bo Me"),
                data.get("Sdt")
            ))

            log_action(user_ten_tk=session.get("user", "system"),
                       target_table="hocsinh",
                       target_staff_id=student_id,
                       action=f"Added student {full_name}")
        conn.commit()
        conn.close()
        return jsonify({"status": "ok"})
    return jsonify({"status": "error", "message": "Unsupported department"}), 400

@app.route("/delete", methods=["POST"])
def delete_employee():
    data = request.get_json()
    staff_id = data.get("staff_id")
    dept = data.get("dept", "GV").upper()
    table = "giaovien" if dept == "GV" else "hocsinh" if dept == "HS" else None
    key = "ma_gv" if dept == "GV" else "ma_hs"
    if not staff_id or not table:
        return jsonify({"status": "error", "reason": "Invalid request"})
    conn = get_conn()
    try:
        with conn.cursor() as cursor:
            if dept == "GV":
                # ❗ Chỉ xóa liên kết ở lop_gv
                cursor.execute("DELETE FROM lop_gv WHERE ma_gv = %s", (staff_id,))
            
            # Xóa chính ở bảng giáo viên/học sinh
            cursor.execute(f"DELETE FROM {table} WHERE {key} = %s", (staff_id,))
            if cursor.rowcount > 0:
                log_action(user_ten_tk=session.get("user", "system"),
                           target_table=table,
                           target_staff_id=staff_id,
                           action=f"Deleted record {staff_id}")
                conn.commit()
                return jsonify({"status": "ok"})
            else:
                return jsonify({"status": "error", "reason": "ID not found"})
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "reason": str(e)})
    finally:
        conn.close()

@app.route("/update", methods=["POST"])
def update_employee():
    data = request.get_json()
    dept = data.get("Dept", "GV").upper()
    staff_id = data.get("id")
    update_data = data.get("data")

    if not staff_id or not update_data:
        return jsonify({"status": "error", "reason": "Thiếu ID hoặc dữ liệu"})

    table = "giaovien" if dept == "GV" else "hocsinh" if dept == "HS" else None
    key_col = "ma_gv" if dept == "GV" else "ma_hs"

    if not table:
        return jsonify({"status": "error", "reason": "Phòng ban không hợp lệ"})

    field_map = {
        "GV": {
            "Ma Gv": "ma_gv",
            "Ho Va Ten": "ho_va_ten",
            "Ten Tk": "ten_tk",
            "Chuc Vu": "chuc_vu",
            "Ngay Sinh": "ngay_sinh",
            "Que Quan": "que_quan",
            "Cccd": "cccd",
            "Ngay Cap": "ngay_cap",
            "Mst": "mst",
            "Cmnd": "cmnd",
            "So Bh": "so_bh",
            "Sdt": "sdt",
            "Tk Nh": "tk_nh",
            "Email": "email",
            "Nhom Mau": "nhom_mau",
            "Dia Chi": "dia_chi"
        },
        "HS": {
            "Ma Hs": "ma_hs",
            "Ho Va Ten": "ho_va_ten",
            "Ngay Sinh": "ngay_sinh",
            "Gioi Tinh": "gioi_tinh",
            "Dan Toc": "dan_toc",
            "Ma Dinh Danh": "ma_dinh_danh",
            "Ho Ten Bo": "ho_ten_bo",
            "Nghe Nghiep Bo": "nghe_nghiep_bo",
            "Ho Ten Me": "ho_ten_me",
            "Nghe Nghiep Me": "nghe_nghiep_me",
            "Ho Khau": "ho_khau",
            "Cccd Bo Me": "cccd_bo_me",
            "Sdt": "sdt"
        }
    }

    date_fields = {
        "GV": ["ngay_sinh"],
        "HS": ["ngay_sinh"]
    }

    set_clause = []
    values = []
    for key, value in update_data.items():
        if key in field_map[dept]:
            field = field_map[dept][key]
            if field in date_fields.get(dept, []):
                value = parse_date(value)
            set_clause.append(f"{field} = %s")
            values.append(value)

    if not set_clause:
        return jsonify({"status": "error", "reason": "Không có trường hợp lệ để cập nhật"})

    set_clause_str = ", ".join(set_clause)
    sql = f"UPDATE {table} SET {set_clause_str} WHERE {key_col} = %s"
    values.append(staff_id)

    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute(sql, tuple(values))
        if cursor.rowcount > 0:
            log_action(
                user_ten_tk=session.get("user", "system"),
                target_table=table,
                target_staff_id=staff_id,
                action=f"Cập nhật các trường: {', '.join(update_data.keys())}"
            )
            conn.commit()
            return jsonify({"status": "ok"})
        else:
            return jsonify({"status": "error", "reason": "Không tìm thấy ID"})

@app.route("/users")
def users():
    if "user" not in session or session.get("role") != "admin":
        return redirect("/")
    return render_template("users.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/api/table-schema")
def get_table_schema():
    conn = get_conn()
    result = {}
    try:
        with conn.cursor() as cursor:
            for table in ["giaovien", "hocsinh"]:
                cursor.execute(f"DESCRIBE {table}")
                cols = [row["Field"] for row in cursor.fetchall()]
                result["GV" if table == "giaovien" else "HS"] = cols
    finally:
        conn.close()
    return jsonify(result)


# Example API to get employees
@app.route("/api/employees")
def api_employees():
    dept = request.args.get("dept")
    if dept == "GV":
        table = "giaovien"
        query = f"SELECT * FROM {table}"
    elif dept == "HS":
        query = """
            SELECT 
                h.ma_hs,
                h.ho_va_ten,
                h.ngay_sinh,
                h.gioi_tinh,
                h.dan_toc,
                h.ma_dinh_danh,
                h.ho_ten_bo,
                h.nghe_nghiep_bo,
                h.ho_ten_me,
                h.nghe_nghiep_me,
                h.ho_khau,
                h.cccd_bo_me,
                h.sdt,
                pl.ma_lop,
                lg.ma_gv
            FROM hocsinh h
            LEFT JOIN phan_lop pl ON h.ma_hs = pl.ma_hs
            LEFT JOIN lop_gv lg ON pl.ma_lop = lg.ma_lop AND lg.vai_tro = 'GVCN'
        """
    else:
        return jsonify({"error": "Invalid department"}), 400

    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
    conn.close()
    return jsonify({"rows": rows})

# Update schema info
@app.route("/update-database", methods=["POST"])
def update_database():
    conn = get_conn()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = [row[f"Tables_in_{conn.db.decode()}"] for row in cursor.fetchall()]

            results = []
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                row_count = cursor.fetchone()["count"]

                cursor.execute(f"DESCRIBE {table}")
                columns = cursor.fetchall()
                col_names = [col["Field"] for col in columns]

                results.append({
                    "table_name": table,
                    "column_names": ", ".join(col_names),
                    "column_count": len(col_names),
                    "row_count": row_count
                })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})
    finally:
        conn.close()
    return jsonify({"success": True, "tables": results})

@app.route("/logs")
def view_logs():
    if session.get("role") != "admin":
        return redirect("/")

    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT logs.*, logs.user_ten_tk AS ten_tk
            FROM logs
            ORDER BY logs.created_at DESC
        """)
        rows = cursor.fetchall()
    conn.close()
    return render_template("logs.html", logs=rows)

@app.route("/stats")
def view_stats():
    if session.get("role") != "admin":
        return redirect("/")

    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) AS total FROM giaovien")
        total = cursor.fetchone()["total"]

        # 👉 Giả định bạn thống kê theo chức vụ
        cursor.execute("""
            SELECT chuc_vu AS team, COUNT(*) AS count FROM giaovien
            WHERE chuc_vu IS NOT NULL AND chuc_vu != ''
            GROUP BY chuc_vu
        """)
        team_stats = cursor.fetchall()
    conn.close()

    return render_template("stats.html", total=total, team_stats=team_stats)

# Route /api/epa-years (đã có sẵn và hoạt động)
@app.route('/api/epa-years', methods=['GET'])
def get_epa_years():
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT year FROM tongdiem_epa ORDER BY year")
        years = [row['year'] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        app.logger.info(f'[DEBUG] Danh sách năm: {years}')
        return jsonify({"years": years}), 200
    except Exception as e:
        app.logger.error(f'[DEBUG] Lỗi trong get_epa_years: {str(e)}')
        return jsonify({"message": str(e)}), 500

# Route mới: /api/epa-data
@app.route('/api/epa-data', methods=['GET'])
def get_epa_data():
    try:
        # Lấy thông tin từ session
        ten_tk = session.get('user')
        role = session.get('role')
        if not ten_tk or not role:
            return jsonify({"message": "Không có người dùng trong session"}), 401

        # Lấy tham số year từ query string
        year = request.args.get('year')
        if not year:
            return jsonify({"message": "Thiếu tham số năm"}), 400

        # Kết nối tới database
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Kiểm tra chuc_vu của user
        is_supervisor_ht = False
        is_supervisor_tgv1 = False
        is_supervisor_tgv2 = False
        if role == 'supervisor':
            cursor.execute(
                "SELECT chuc_vu FROM giaovien WHERE ten_tk = %s",
                (ten_tk,)
            )
            user_details = cursor.fetchone()
            if user_details:
                chuc_vu = user_details['chuc_vu']
                if chuc_vu == 'HT':
                    is_supervisor_ht = True
                elif chuc_vu == 'TGV1':
                    is_supervisor_tgv1 = True
                elif chuc_vu == 'TGV2':
                    is_supervisor_tgv2 = True

        # Xây dựng truy vấn SQL
        query = """
            SELECT t.id, t.ten_tk, g.ho_va_ten, t.year, t.month, 
                   t.user_total_score, t.sup_total_score, t.pri_total_score, t.pri_comment
            FROM tongdiem_epa t
            LEFT JOIN giaovien g ON t.ten_tk = g.ten_tk
            WHERE t.year = %s
        """
        params = [year]

        # Điều kiện lọc dữ liệu
        if role == 'user':
            # Chỉ hiển thị dữ liệu của chính user
            query += " AND t.ten_tk = %s"
            params.append(ten_tk)
        elif role == 'supervisor':
            if is_supervisor_ht:
                # Supervisor với chuc_vu = 'HT' thấy tất cả dữ liệu
                pass
            elif is_supervisor_tgv1:
                # Supervisor với chuc_vu = 'TGV1' thấy dữ liệu của chính họ và user có chuc_vu = 'GV1'
                query += " AND (t.ten_tk = %s OR g.chuc_vu = 'GV1')"
                params.append(ten_tk)
            elif is_supervisor_tgv2:
                # Supervisor với chuc_vu = 'TGV2' thấy dữ liệu của chính họ và user có chuc_vu = 'GV2'
                query += " AND (t.ten_tk = %s OR g.chuc_vu = 'GV2')"
                params.append(ten_tk)
            else:
                # Supervisor không có chuc_vu phù hợp, không hiển thị gì
                return jsonify([]), 200
        elif role != 'admin':
            # Nếu không phải admin, không hiển thị gì
            return jsonify([]), 200

        query += " ORDER BY t.month, t.ten_tk"

        # Thực thi truy vấn
        cursor.execute(query, params)
        data = cursor.fetchall()
        cursor.close()
        conn.close()

        app.logger.info(f'[DEBUG] Dữ liệu EPA cho năm {year}: {data}')
        return jsonify(data), 200
    except Exception as e:
        app.logger.error(f'[DEBUG] Lỗi trong get_epa_data: {str(e)}')
        return jsonify({"message": str(e)}), 500

@app.route("/data_epa")
def show_data_epa():
    return render_template("data_epa.html")

# Full dữ liệu bảng đánh giá của tất cả giáo viên.
@app.route("/api/epa-full")
def api_epa_full():
    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT e.id, e.ten_tk, g.ho_va_ten, g.chuc_vu,
                   e.year, e.month,
                   e.user_total_score, e.sup_total_score,
                   e.pri_total_score, e.pri_comment,
                   CASE
                       WHEN e.pri_total_score IS NULL THEN NULL
                       WHEN e.pri_total_score <= 249 THEN 'CHƯA HOÀN THÀNH'
                       WHEN e.pri_total_score <= 270 THEN 'HOÀN THÀNH'
                       WHEN e.pri_total_score <= 280 THEN 'HOÀN THÀNH TỐT'
                       WHEN e.pri_total_score <= 300 THEN 'HOÀN THÀNH XUẤT SẮC'
                       ELSE 'Không xác định'
                   END AS xeploai
            FROM tongdiem_epa e
            LEFT JOIN giaovien g ON e.ten_tk = g.ten_tk
            ORDER BY e.year DESC, e.month DESC
        """)
        result = cursor.fetchall()
    return jsonify(result)

# Cập nhật dữ liệu điểm và comment từ Hiệu Trưởng
@app.route("/api/update-epa-kimnhung", methods=["POST"])
def update_epa_kimnhung():
    # ✅ Chỉ cho phép nếu user là hiệu trưởng "kimnhung"
    if session.get("user") != "kimnhung":
        return jsonify({"error": "Bạn không có quyền chỉnh sửa"}), 403
    data = request.get_json()
    epa_id = data.get("id")
    pri_score = data.get("pri_total_score")
    pri_comment = data.get("pri_comment", "")
    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute("""
            UPDATE tongdiem_epa
            SET pri_total_score = %s,
                pri_comment = %s
            WHERE id = %s
        """, (pri_score, pri_comment, epa_id))
        conn.commit()
    return jsonify({"message": "Cập nhật thành công!"})

# Phần cập nhật thông tin giáo viên (GV) đang hiển thị
@app.route("/api/update_gv", methods=["POST"])
def update_gv():
    data = request.get_json()
    ten_tk = data.get("ten_tk", "").strip()
    if not ten_tk:
        return jsonify({"error": "Thiếu ten_tk"}), 400
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE giaovien
        SET ma_gv=%s, ho_va_ten=%s, chuc_vu=%s, ngay_sinh=%s, que_quan=%s,
            cccd=%s, ngay_cap=%s, mst=%s, cmnd=%s, so_bh=%s, sdt=%s,
            tk_nh=%s, email=%s, nhom_mau=%s, dia_chi=%s
        WHERE ten_tk=%s
    """, (
        data.get("ma_gv"), data.get("ho_va_ten"), data.get("chuc_vu"),
        data.get("ngay_sinh"), data.get("que_quan"), data.get("cccd"),
        data.get("ngay_cap"), data.get("mst"), data.get("cmnd"),
        data.get("so_bh"), data.get("sdt"), data.get("tk_nh"),
        data.get("email"), data.get("nhom_mau"), data.get("dia_chi"),
        ten_tk
    ))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"status": "success"}), 200

# Phần cập nhật thông tin học sinh (HS) đang hiển thị
@app.route("/api/update_hs", methods=["POST"])
def update_hs():
    data = request.get_json()
    ma_hs = data.get("ma_hs", "").strip()
    if not ma_hs:
        return jsonify({"error": "Thiếu mã học sinh"}), 400
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE hocsinh
        SET ho_va_ten=%s, ngay_sinh=%s, gioi_tinh=%s, dan_toc=%s,
            ma_dinh_danh=%s, ho_ten_bo=%s, nghe_nghiep_bo=%s, ho_ten_me=%s,
            nghe_nghiep_me=%s, ho_khau=%s, cccd_bo_me=%s, sdt=%s
        WHERE ma_hs=%s
    """, (
        data.get("ho_va_ten"), data.get("ngay_sinh"),
        data.get("gioi_tinh"), data.get("dan_toc"), data.get("ma_dinh_danh"),
        data.get("ho_ten_bo"), data.get("nghe_nghiep_bo"), data.get("ho_ten_me"),
        data.get("nghe_nghiep_me"), data.get("ho_khau"), data.get("cccd_bo_me"),
        data.get("sdt"), ma_hs
    ))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"status": "success"}), 200

@app.route("/epa_preview")
def epa_preview():
    return render_template("epa_preview.html")

# Remove bảng dữ liệu trong sql -----> (Nguy hiểm ) <-----
@app.route("/remove-dept-data", methods=["POST"])
def remove_dept_data():
    data = request.get_json()
    dept = data.get("dept")

    # Xác định bảng cần xóa
    if dept == "GV":
        table = "giaovien"
    elif dept == "HS":
        table = "hocsinh"
    else:
        return jsonify({"message": "Invalid department."}), 400

    conn = get_conn()
    try:
        with conn.cursor() as cursor:
            # 🚨 Tắt kiểm tra ràng buộc khóa ngoại
            cursor.execute("SET FOREIGN_KEY_CHECKS=0")

            # 🚮 Thực hiện xóa dữ liệu
            cursor.execute(f"DELETE FROM {table}")

            # 🔒 Bật lại kiểm tra ràng buộc
            cursor.execute("SET FOREIGN_KEY_CHECKS=1")

        conn.commit()
        return jsonify({"message": f"All data from {dept} removed successfully."})
    except Exception as e:
        conn.rollback()
        return jsonify({"message": f"Error: {str(e)}"}), 500
    finally:
        conn.close()


# Phần xử lý câu hỏi EPA
@app.route("/admin/questions")
def admin_questions():
    return render_template("cauhoi_epa.html")

@app.route('/api/cauhoi_epa', methods=['GET'])
def get_questions():
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM cauhoi_epa ORDER BY id")
        data = cur.fetchall()
    conn.close()
    return jsonify(data)

@app.route('/api/cauhoi_epa', methods=['POST'])
def add_or_update_question():
    data = request.get_json()
    id = data.get('id')
    question = data.get('question', '').strip()
    translate = data.get('translate', '').strip()
    if not question:
        return jsonify({"error": "Câu hỏi không được để trống!"}), 400
    conn = get_conn()
    with conn.cursor() as cur:
        if id:
            cur.execute(
                "UPDATE cauhoi_epa SET question = %s, translate = %s WHERE id = %s",
                (question, translate, id)
            )
        else:
            cur.execute(
                "INSERT INTO cauhoi_epa (question, translate) VALUES (%s, %s)",
                (question, translate)
            )
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route('/api/cauhoi_epa/<int:id>', methods=['DELETE'])
def delete_question(id):
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM cauhoi_epa WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

# Tổng hợp điểm đánh giá EPA.
@app.route("/epa_summary")
def view_epa_summary():
    return render_template("epa_summary.html")

@app.route("/api/epa_summary", methods=["GET"])
def api_epa_summary():
    ten_tk = request.args.get("ten_tk")
    year = request.args.get("year", type=int)
    if not ten_tk or not year:
        return jsonify({"error": "Missing parameters"}), 400
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT month, user_total_score, sup_total_score, pri_total_score
            FROM tongdiem_epa
            WHERE ten_tk = %s AND year = %s
            ORDER BY month
        """, (ten_tk, year))
        rows = cur.fetchall()
    conn.close()
    return jsonify(rows)

@app.route("/api/list_ten_tk")
def list_ten_tk():
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("SELECT ten_tk FROM tk ORDER BY ten_tk")
        rows = cur.fetchall()
    conn.close()
    return jsonify([row["ten_tk"] for row in rows])

@app.route("/api/epa_monthly_all", methods=["GET"])
def api_epa_monthly_all():
    year = request.args.get("year", type=int)
    if not year:
        return jsonify({"error": "Missing year"}), 400
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT month, ten_tk, COALESCE(pri_total_score, 0) AS total_score
            FROM tongdiem_epa
            WHERE year = %s
            ORDER BY month, total_score DESC
        """, (year,))
        rows = cur.fetchall()
    conn.close()
    from collections import defaultdict
    result = defaultdict(list)
    for row in rows:
        result[row["month"]].append({
            "ten_tk": row["ten_tk"],
            "score": row["total_score"]
        })
    return jsonify(result)

#Đọc dữ liệu bảng để lấy danh sách mã
@app.route("/api/danh-sach-ma")
def api_danh_sach_ma():
    conn = get_conn()
    result = {"maGVList": [], "maLopList": []}
    try:
        with conn.cursor() as cursor:
            # Lấy danh sách mã giáo viên
            cursor.execute("SELECT ma_gv FROM giaovien")
            result["maGVList"] = [row["ma_gv"] for row in cursor.fetchall()]
            # Lấy danh sách mã lớp
            cursor.execute("SELECT ma_lop FROM ds_lop")
            result["maLopList"] = [row["ma_lop"] for row in cursor.fetchall()]
    finally:
        conn.close()
    return jsonify(result)

# 📄 ROUTE RENDER TEMPLATE
@app.route("/classes")
def classes_page():
    return render_template("classes.html")

@app.route("/assign-classes")
def assign_classes_page():
    return render_template("assign_classes.html")

@app.route("/assign-teachers")
def assign_teachers_page():
    return render_template("assign_teachers.html")

# API: Lấy danh sách lớp
@app.route("/api/classes", methods=["GET"])
def get_classes():
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM ds_lop")
        result = cur.fetchall()
    conn.close()
    return jsonify(result)

@app.route("/api/delete-class", methods=["POST"])
def delete_class():
    data = request.get_json()
    ma_lop = data.get("ma_lop")
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            # Xoá giáo viên gán với lớp đó
            cur.execute("DELETE FROM lop_gv WHERE ma_lop = %s", (ma_lop,))
            # Xoá học sinh phân lớp (nếu có)
            cur.execute("DELETE FROM phan_lop WHERE ma_lop = %s", (ma_lop,))
            # Xoá lớp
            cur.execute("DELETE FROM ds_lop WHERE ma_lop = %s", (ma_lop,))
            conn.commit()
        return jsonify({"message": f"Đã xoá lớp {ma_lop} và dữ liệu liên quan"})
    finally:
        conn.close()

# API: Thêm lớp mới
@app.route("/api/classes", methods=["POST"])
def add_class():
    data = request.json
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("INSERT INTO ds_lop (ma_lop, ten_lop) VALUES (%s, %s)", (data["ma_lop"], data["ten_lop"]))
        conn.commit()
    conn.close()
    return jsonify({"message": "Lớp đã thêm"})

# Cập nhật nút sửa tên lớp
@app.route("/api/update-class", methods=["POST"])
def update_class():
    data = request.get_json()
    ma_lop = data.get("ma_lop")
    ten_lop = data.get("ten_lop")
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE ds_lop SET ten_lop = %s WHERE ma_lop = %s", (ten_lop, ma_lop))
            conn.commit()
        return jsonify({"message": "success"})
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

# Chức năng tự nhận diện số lớn nhất có trong mã HS
@app.route("/api/last-ma-hs-prefix", methods=["GET"])
def get_last_ma_hs():
    prefix = request.args.get("prefix", "HS").upper()
    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute("SELECT ma_hs FROM hocsinh WHERE ma_hs LIKE %s", (f"{prefix}%",))
        ma_list = [row["ma_hs"] for row in cursor.fetchall()]
    conn.close()
    # Tìm số lớn nhất
    max_num = 0
    for m in ma_list:
        match = re.match(rf"{prefix}(\d+)", m)
        if match:
            num = int(match.group(1))
            if num > max_num:
                max_num = num
    return jsonify({"prefix": prefix, "next_num": max_num + 1})

# Hiển thị gợi ý mã ma_hs tiếp theo trong input động
@app.route("/api/next-ma-hs", methods=["GET"])
def get_next_ma_hs():
    prefix = request.args.get("prefix", "HS").upper()
    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute("SELECT ma_hs FROM hocsinh WHERE ma_hs LIKE %s", (f"{prefix}%",))
        ma_list = [row["ma_hs"] for row in cursor.fetchall()]
    conn.close()
    max_num = 0
    for m in ma_list:
        match = re.match(rf"{prefix}(\d{{5}})", m)
        if match:
            num = int(match.group(1))
            if num > max_num:
                max_num = num
    next_code = f"{prefix}{str(max_num + 1).zfill(5)}"
    return jsonify({"next_ma_hs": next_code})

# Hiển thị gợi ý mã ma_gv tiếp theo trong input động
@app.route("/api/next-ma-gv", methods=["GET"])
def get_next_ma_gv():
    prefix = request.args.get("prefix", "GV").upper()
    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute("SELECT ma_gv FROM giaovien WHERE ma_gv LIKE %s", (f"{prefix}%",))
        ma_list = [row["ma_gv"] for row in cursor.fetchall()]
    conn.close()
    import re
    max_num = 0
    for m in ma_list:
        match = re.match(rf"{prefix}(\d{{5}})", m)
        if match:
            num = int(match.group(1))
            if num > max_num:
                max_num = num
    next_code = f"{prefix}{str(max_num + 1).zfill(5)}"
    return jsonify({"next_ma_gv": next_code})

# API lấy danh sách học sinh kèm tên lớp
@app.route("/api/students")
def get_students():
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT hs.ma_hs, hs.ho_va_ten, hs.ngay_sinh, hs.gioi_tinh,
                   hs.dan_toc, hs.ma_dinh_danh, hs.ho_ten_bo, hs.nghe_nghiep_bo,
                   hs.ho_ten_me, hs.nghe_nghiep_me, hs.ho_khau, hs.cccd_bo_me, hs.sdt,
                   pl.ma_lop, dl.ten_lop
            FROM hocsinh hs
            LEFT JOIN phan_lop pl ON hs.ma_hs = pl.ma_hs
            LEFT JOIN ds_lop dl ON pl.ma_lop = dl.ma_lop
        """)
        result = cur.fetchall()
    conn.close()
    return jsonify(result)

# API cập nhật mã lớp cho học sinh
@app.route("/api/update-student-class", methods=["POST"])
def update_student_class():
    data = request.get_json()
    ma_hs = data.get("ma_hs")
    new_ma_lop = data.get("ma_lop")
    conn = get_conn()
    with conn.cursor() as cur:
        # ✅ Chỉ cập nhật bảng phan_lop
        cur.execute("SELECT 1 FROM phan_lop WHERE ma_hs = %s", (ma_hs,))
        if cur.fetchone():
            cur.execute("""
                UPDATE phan_lop
                SET ma_lop = %s
                WHERE ma_hs = %s
            """, (new_ma_lop, ma_hs))
        else:
            cur.execute("""
                INSERT INTO phan_lop (ma_hs, ma_lop)
                VALUES (%s, %s)
            """, (ma_hs, new_ma_lop))
        conn.commit()
    return jsonify({"message": "Cập nhật thành công"})

# API: Phân lớp học sinh
@app.route("/api/assign-class", methods=["POST"])
def assign_class():
    data = request.json
    ma_hs = data.get("ma_hs")
    ma_lop = data.get("ma_lop")
    if not ma_hs or not ma_lop:
        return jsonify({"error": "Thiếu mã học sinh hoặc mã lớp"}), 400
    conn = get_conn()
    with conn.cursor() as cur:
        # Kiểm tra học sinh đã được phân lớp chưa
        cur.execute("SELECT * FROM phan_lop WHERE ma_hs = %s", (ma_hs,))
        existing = cur.fetchone()
        if existing:
            # Cập nhật phân lớp
            cur.execute("UPDATE phan_lop SET ma_lop = %s WHERE ma_hs = %s", (ma_lop, ma_hs))
        else:
            # Thêm mới phân lớp
            cur.execute("INSERT INTO phan_lop (ma_hs, ma_lop) VALUES (%s, %s)", (ma_hs, ma_lop))
        conn.commit()
    conn.close()
    return jsonify({"message": "Đã gán học sinh vào lớp thành công"})

# API: Lấy danh sách giáo viên
@app.route("/api/teachers", methods=["GET"])
def get_teachers():
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("SELECT ma_gv, ho_va_ten FROM giaovien")
        result = cur.fetchall()
    conn.close()
    return jsonify(result)

# API: Gán giáo viên cho lớp
@app.route("/api/assigned-teachers", methods=["GET"])
def get_assigned_teachers():
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT gv.ma_gv, gv.ho_va_ten, gv.chuc_vu,
                   l.ten_lop, lg.ma_lop, lg.vai_tro
            FROM lop_gv lg
            JOIN giaovien gv ON gv.ma_gv = lg.ma_gv
            JOIN ds_lop l ON l.ma_lop = lg.ma_lop
        """)
        rows = cur.fetchall()
    conn.close()
    return jsonify(rows)

#API: Cập nhật vai trò hoặc lớp học
@app.route("/api/update-assignment", methods=["POST"])
def update_assignment():
    data = request.get_json()
    ma_gv = data.get("ma_gv")
    field = data.get("field")
    value = data.get("value")
    if field not in ("ma_lop", "vai_tro"):
        return jsonify({"error": "Invalid field"}), 400
    conn = get_conn()
    with conn.cursor() as cur:
        if field == "ma_lop":
            # Khi đổi lớp, cần biết lớp cũ để cập nhật đúng dòng
            cur.execute("SELECT ma_lop FROM lop_gv WHERE ma_gv = %s", (ma_gv,))
            old = cur.fetchone()
            if not old:
                return jsonify({"error": "Không tìm thấy phân công"}), 404
            cur.execute("""
                UPDATE lop_gv
                SET ma_lop = %s
                WHERE ma_gv = %s AND ma_lop = %s
            """, (value, ma_gv, old["ma_lop"]))
        elif field == "vai_tro":
            cur.execute("""
                UPDATE lop_gv
                SET vai_tro = %s
                WHERE ma_gv = %s
            """, (value, ma_gv))
        conn.commit()
    conn.close()
    return jsonify({"message": "Đã cập nhật"})

#API: Xóa phân công giáo viên khỏi lớp
@app.route("/api/delete-assignment", methods=["POST"])
def delete_assignment():
    data = request.get_json()
    ma_gv = data.get("ma_gv")
    ma_lop = data.get("ma_lop")
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("""
            DELETE FROM lop_gv
            WHERE ma_gv = %s AND ma_lop = %s
        """, (ma_gv, ma_lop))
        conn.commit()
    conn.close()
    return jsonify({"message": "Đã xóa phân công"})

@app.route("/export-data")
def view_export_data():
    return render_template("export_data.html")

# THời gian mở EPA
def open_browser():
    webbrowser.open("http://localhost:5000")

#Hàm đổi mật khẩu user đang logging
@app.route('/change-password', methods=['POST'])
def change_password():
    data = request.get_json()
    user = session.get('user')
    if not user:
        return jsonify({"status": "fail", "message": "Chưa đăng nhập"})

    old_password = data.get('old_password')
    new_password = data.get('new_password')

    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT mat_khau FROM tk WHERE ten_tk=%s", (user,))
            row = cursor.fetchone()
            if not row or not check_password_hash(row['mat_khau'], old_password):
                return jsonify({"status": "fail", "message": "Mật khẩu cũ không đúng!"})

            new_hash = generate_password_hash(new_password)
            cursor.execute("UPDATE tk SET mat_khau=%s WHERE ten_tk=%s", (new_hash, user))
            conn.commit()
            return jsonify({"status": "success"})
    finally:
        conn.close()

#Bảng đánh giá dành cho tổ trưởng 
@app.route('/sup-epa-score')
def sup_epa_score():
    from datetime import datetime
    import pymysql

    user = session.get('user')
    if not user:
        return redirect('/login')

    now = datetime.now()
    current_month = now.month
    current_year = now.year

    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            # 📌 Lấy chức vụ của user
            cursor.execute("""
                SELECT chuc_vu FROM giaovien WHERE ten_tk=%s
            """, (user,))
            row = cursor.fetchone()
            if not row:
                return "Không tìm thấy người dùng", 404

            chuc_vu = row['chuc_vu']
            if not chuc_vu.startswith("TGV"):
                return "Bạn không có quyền xem trang này", 403

            suffix = chuc_vu[3:]  # ví dụ: '2' từ 'TGV2'
            target_chuc_vu = f"GV{suffix}"

            # 📌 Lấy danh sách tổ viên và trạng thái đánh giá từ tongdiem_epa
            cursor.execute("""
                SELECT g.ten_tk, g.ho_va_ten, g.chuc_vu,
                       t.user_total_score,
                       t.sup_total_score AS sup_score,
                       CASE WHEN t.id IS NOT NULL THEN 'Đã đánh giá' ELSE 'Chưa đánh giá' END AS trang_thai
                FROM giaovien g
                LEFT JOIN tongdiem_epa t
                  ON g.ten_tk = t.ten_tk
                 AND t.year = %s
                 AND t.month = %s
                WHERE g.chuc_vu = %s
            """, (current_year, current_month, target_chuc_vu))

            members = cursor.fetchall()

        return render_template(
            "sup_epa_score.html",
            members=members,
            target_chuc_vu=target_chuc_vu,
            current_month=current_month,
            current_year=current_year
        )

    finally:
        conn.close()

@app.route('/sup-epa-detail')
def sup_epa_detail():
    ten_tk = request.args.get('ten_tk')
    thang = request.args.get('thang')
    nam = request.args.get('nam')

    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, question, user_comment, user_score, sup_comment, sup_score
                FROM bangdanhgia
                WHERE ten_tk=%s AND year=%s AND month=%s
                ORDER BY created_at
            """, (ten_tk, nam, thang))
            rows = cursor.fetchall()

            return render_template("sup_epa_detail.html", rows=rows, ten_tk=ten_tk, thang=thang, nam=nam)
    finally:
        conn.close()

@app.route('/update-sup-epa', methods=['POST'])
def update_sup_epa():
    from flask import request, redirect, url_for
    import pymysql
    from datetime import datetime

    user = session.get('user')
    if not user:
        return redirect('/login')

    now = datetime.now()
    current_year = now.year
    current_month = now.month

    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            updates = request.form

            # ✅ Cập nhật từng câu hỏi trong bangdanhgia
            for key, value in updates.items():
                if key.startswith('sup_comment_') or key.startswith('sup_score_'):
                    col, id_ = key.rsplit('_', 1)
                    cursor.execute(
                        f"UPDATE bangdanhgia SET {col}=%s WHERE id=%s",
                        (value, id_)
                    )

            # ✅ Tổng hợp lại sup_score từ bangdanhgia
            cursor.execute("""
                SELECT ten_tk, year, month, SUM(sup_score) AS total_sup
                FROM bangdanhgia
                WHERE year=%s AND month=%s
                GROUP BY ten_tk, year, month
            """, (current_year, current_month))

            rows = cursor.fetchall()

            # ✅ Cập nhật hoặc chèn mới vào tongdiem_epa
            for row in rows:
                cursor.execute("""
                    INSERT INTO tongdiem_epa (ten_tk, year, month, sup_total_score)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE sup_total_score=%s
                """, (
                    row['ten_tk'], row['year'], row['month'],
                    row['total_sup'], row['total_sup']
                ))

            conn.commit()

        return redirect(url_for('sup_epa_score'))

    finally:
        conn.close()

if __name__ == "__main__":
    threading.Timer(1.0, open_browser).start()
    app.run(debug=True, use_reloader=False)
