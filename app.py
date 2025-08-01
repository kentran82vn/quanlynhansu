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
@app.route("/")
def index():
    """Route gốc - điểm vào chính của ứng dụng"""
    if "user" not in session:
        # Neu chua dang nhap, chuyen den trang login
        return redirect("/login")
    else:
        # Neu da dang nhap, chuyen den dashboard
        return redirect("/dashboard")
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
        print("Failed to log action:", e)
    finally:
        conn.close()

def parse_date(d):
    try:
        return datetime.strptime(d, "%d/%m/%Y").date()
    except:
        return None

def get_epa_classification(pri_score, sup_score):
    """
    Tính xếp loại EPA dựa trên điểm số với logic ưu tiên:
    1. Ưu tiên điểm HT/PHT (pri_score) nếu có
    2. Fallback về điểm TGV (sup_score) nếu chưa có điểm HT/PHT
    3. Thang điểm: 95-100: Xuất Sắc, 90-94: Tốt, 80-89: Hoàn Thành, ≤79: Chưa Hoàn Thành
    """
    # Ưu tiên điểm HT/PHT trước
    final_score = pri_score if pri_score is not None else sup_score
    
    if final_score is None:
        return None
    elif final_score <= 79:
        return 'Chưa Hoàn Thành'
    elif 80 <= final_score <= 89:
        return 'Hoàn Thành Nhiệm Vụ'
    elif 90 <= final_score <= 94:
        return 'Hoàn Thành Tốt Nhiệm Vụ'
    elif 95 <= final_score <= 100:
        return 'Hoàn Thành Xuất Sắc Nhiệm Vụ'
    else:
        return 'Không xác định'

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

@app.route("/login", methods=["GET", "POST"])
def login():
    conn = get_conn()

    # Tao admin mac dinh neu chua co tai khoan admin nao
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
            # print("Da tao tai khoan admin mac dinh: admin / admin123")

    # Xu ly dang nhap
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

            # print(f"Logged in as: {session['user']} (role: {session['role']})")

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

# Them du lieu moi cho giao vien va hoc sinh
@app.route("/add", methods=["POST"])
def add_employee():
    # Enhanced input validation
    if not request.is_json:
        return jsonify({"status": "error", "message": "Content-Type phải là application/json"}), 400
        
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "Dữ liệu JSON không hợp lệ"}), 400
        
    dept = data.get("Dept", "GV").upper()
    
    # Department validation
    if dept not in ["GV", "HS"]:
        return jsonify({"status": "error", "message": "Department phải là GV hoặc HS"}), 400

    if dept == "GV":
        staff_id = str(data.get("Ma Gv", "")).strip()
        full_name = str(data.get("Ho Va Ten", "")).strip()
        ten_tk = (data.get("Ten Tk") or "").strip().lower()

        # Enhanced validation
        if not staff_id or not full_name:
            return jsonify({"status": "error", "message": "Missing Staff ID or Full Name"}), 400
            
        if len(staff_id) > 50:  # Reasonable limit
            return jsonify({"status": "error", "message": "Mã giáo viên quá dài"}), 400
            
        if len(full_name) > 255:  # Database limit
            return jsonify({"status": "error", "message": "Họ tên quá dài"}), 400

        conn = get_conn()
        try:
            with conn.cursor() as cursor:
                # Kiem tra va tao tai khoan trong bang tk neu chua ton tai
                if ten_tk:
                    cursor.execute("SELECT 1 FROM tk WHERE ten_tk = %s", (ten_tk,))
                    if not cursor.fetchone():
                        cursor.execute("INSERT INTO tk (ten_tk, nhom) VALUES (%s, %s)", (ten_tk, "user"))
                        log_action(user_ten_tk=session.get("user", "user"),
                                   target_table="tk",
                                   target_staff_id=ten_tk,
                                   action=f"Created login account for teacher")

                # Kiem tra trung ma giao vien
                cursor.execute("SELECT 1 FROM giaovien WHERE ma_gv = %s", (staff_id,))
                if cursor.fetchone():
                    return jsonify({"status": "error", "message": f"Staff ID '{staff_id}' already exists"}), 400

                # Them giao vien
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
            return jsonify({"status": "ok"})
        except Exception as e:
            conn.rollback()
            app.logger.error(f"Error in add_employee (GV): {str(e)}")
            return jsonify({"status": "error", "message": "Đã xảy ra lỗi khi thêm giáo viên"}), 500
        finally:
            conn.close()

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
                #  Chi xoa lien ket o lop_gv
                cursor.execute("DELETE FROM lop_gv WHERE ma_gv = %s", (staff_id,))
            
            # Xoa chinh o bang giao vien/hoc sinh
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
    try:
        with conn.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
        return jsonify({"rows": rows})
    except Exception as e:
        app.logger.error(f"Error in api_employees: {str(e)}")
        return jsonify({"error": "Đã xảy ra lỗi khi lấy dữ liệu nhân viên"}), 500
    finally:
        conn.close()

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

        #  Gia dinh ban thong ke theo chuc vu
        cursor.execute("""
            SELECT chuc_vu AS team, COUNT(*) AS count FROM giaovien
            WHERE chuc_vu IS NOT NULL AND chuc_vu != ''
            GROUP BY chuc_vu
        """)
        team_stats = cursor.fetchall()
    conn.close()

    return render_template("stats.html", total=total, team_stats=team_stats)

# Route /api/epa-years (da co san va hoat dong)
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

# Route moi: /api/epa-data va /api/epa-full (same functionality)
@app.route('/api/epa-data', methods=['GET'])
@app.route('/api/epa-full', methods=['GET'])
def get_epa_data():
    try:
        # Lay thong tin tu session
        ten_tk = session.get('user')
        role = session.get('role')
        if not ten_tk or not role:
            return jsonify({"message": "Không có người dùng trong session"}), 401

        # Lay tham so year va month tu query string
        year = request.args.get('year')
        month = request.args.get('month')
        
        # Neu khong co, dung gia tri hien tai
        if not year:
            from datetime import datetime
            year = datetime.now().year
        if not month:
            from datetime import datetime  
            month = datetime.now().month
            
        year = int(year)
        month = int(month)

        # Ket noi toi database
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Kiem tra chuc_vu cua user
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

        # Xay dung truy van SQL - Hiển thị TẤT CẢ giáo viên (dù có làm EPA hay chưa)
        query = """
            SELECT t.id, g.ten_tk, g.ho_va_ten, g.chuc_vu, %s as year, %s as month,
                   t.user_total_score, t.sup_total_score, t.pri_total_score, t.pri_comment,
                   CASE
                       WHEN COALESCE(t.pri_total_score, t.sup_total_score) IS NULL THEN NULL
                       WHEN COALESCE(t.pri_total_score, t.sup_total_score) <= 79 THEN 'Chưa Hoàn Thành'
                       WHEN COALESCE(t.pri_total_score, t.sup_total_score) >= 80 AND COALESCE(t.pri_total_score, t.sup_total_score) <= 89 THEN 'Hoàn Thành Nhiệm Vụ'
                       WHEN COALESCE(t.pri_total_score, t.sup_total_score) >= 90 AND COALESCE(t.pri_total_score, t.sup_total_score) <= 94 THEN 'Hoàn Thành Tốt Nhiệm Vụ'
                       WHEN COALESCE(t.pri_total_score, t.sup_total_score) >= 95 AND COALESCE(t.pri_total_score, t.sup_total_score) <= 100 THEN 'Hoàn Thành Xuất Sắc Nhiệm Vụ'
                       ELSE 'Không xác định'
                   END as xeploai
            FROM giaovien g
            LEFT JOIN tongdiem_epa t ON g.ten_tk = t.ten_tk AND t.year = %s AND t.month = %s
            WHERE 1=1
        """
        params = [year, month, year, month]

        # Dieu kien loc du lieu
        if role == 'user':
            # Chi hien thi du lieu cua chinh user  
            query += " AND g.ten_tk = %s"
            params.append(ten_tk)
        elif role == 'supervisor':
            if is_supervisor_ht:
                # HT/PHT thay tat ca giao vien (QUAN TRONG: đây là lý do kimnhung phải thấy tất cả)
                pass
            elif is_supervisor_tgv1:
                # TGV1 thay du lieu cua chinh ho va GV1
                query += " AND (g.ten_tk = %s OR g.chuc_vu = 'GV1')"
                params.append(ten_tk)
            elif is_supervisor_tgv2:
                # TGV2 thay du lieu cua chinh ho va GV2
                query += " AND (g.ten_tk = %s OR g.chuc_vu = 'GV2')"
                params.append(ten_tk)
            else:
                # Supervisor khong co chuc_vu phu hop
                return jsonify([]), 200
        elif role != 'admin':
            # Neu khong phai admin, khong hien thi gi
            return jsonify([]), 200

        query += " ORDER BY g.chuc_vu, g.ten_tk"

        # Thuc thi truy van
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

# Full du lieu bang danh gia cua tat ca giao vien.
@app.route("/api/epa-full")
def api_epa_full():
    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT e.id, e.ten_tk, g.ho_va_ten, g.chuc_vu,
                   e.year, e.month,
                   e.user_total_score, e.sup_total_score,
                   e.pri_total_score, e.pri_comment,
                   -- Logic mới: Ưu tiên điểm HT/PHT, fallback về điểm TGV
                   COALESCE(e.pri_total_score, e.sup_total_score) AS final_score,
                   CASE
                       WHEN COALESCE(e.pri_total_score, e.sup_total_score) IS NULL THEN NULL
                       WHEN COALESCE(e.pri_total_score, e.sup_total_score) <= 79 THEN 'Chưa Hoàn Thành'
                       WHEN COALESCE(e.pri_total_score, e.sup_total_score) >= 80 AND COALESCE(e.pri_total_score, e.sup_total_score) <= 89 THEN 'Hoàn Thành Nhiệm Vụ'
                       WHEN COALESCE(e.pri_total_score, e.sup_total_score) >= 90 AND COALESCE(e.pri_total_score, e.sup_total_score) <= 94 THEN 'Hoàn Thành Tốt Nhiệm Vụ'
                       WHEN COALESCE(e.pri_total_score, e.sup_total_score) >= 95 AND COALESCE(e.pri_total_score, e.sup_total_score) <= 100 THEN 'Hoàn Thành Xuất Sắc Nhiệm Vụ'
                       ELSE 'Không xác định'
                   END AS xeploai,
                   -- Thêm thông tin về nguồn điểm
                   CASE 
                       WHEN e.pri_total_score IS NOT NULL THEN 'HT/PHT'
                       WHEN e.sup_total_score IS NOT NULL THEN 'TGV'
                       ELSE NULL
                   END AS score_source
            FROM tongdiem_epa e
            LEFT JOIN giaovien g ON e.ten_tk = g.ten_tk
            ORDER BY e.year DESC, e.month DESC
        """)
        result = cursor.fetchall()
    return jsonify(result)

# Cap nhat du lieu diem va comment tu Hieu Truong / Pho Hieu Truong
@app.route("/api/update-epa-principal", methods=["POST"])
def update_epa_principal():
    # Cho phep HT (kimnhung) va PHT (ngocquy) cham diem bat ky thang nao
    current_user = session.get("user")
    if current_user not in ["kimnhung", "ngocquy"]:
        return jsonify({"error": "Chỉ Hiệu trưởng và Phó hiệu trưởng mới có quyền chấm điểm"}), 403
    data = request.get_json()
    epa_id = data.get("id")
    pri_score = data.get("pri_total_score")
    pri_comment = data.get("pri_comment", "")
    
    if not epa_id or pri_score is None:
        return jsonify({"error": "Thiếu thông tin cần thiết"}), 400
    
    conn = get_conn()
    try:
        with conn.cursor() as cursor:
            # Lấy thông tin record trước khi update
            cursor.execute("SELECT ten_tk, year, month FROM tongdiem_epa WHERE id = %s", (epa_id,))
            record_info = cursor.fetchone()
            
            if not record_info:
                return jsonify({"error": "Không tìm thấy bản ghi EPA"}), 404
            
            # Cập nhật điểm và nhận xét HT/PHT
            cursor.execute("""
                UPDATE tongdiem_epa
                SET pri_total_score = %s,
                    pri_comment = %s,
                    pri_updated_by = %s,
                    pri_updated_at = NOW()
                WHERE id = %s
            """, (pri_score, pri_comment, current_user, epa_id))
            
            # Ghi log
            cursor.execute("""
                INSERT INTO logs (user_ten_tk, target_staff_id, target_table, action, created_at)
                VALUES (%s, %s, 'tongdiem_epa', %s, NOW())
            """, (current_user, record_info['ten_tk'], 
                  f"Chấm điểm EPA {record_info['month']}/{record_info['year']}: {pri_score} điểm"))
            
            conn.commit()
            
        return jsonify({
            "message": f"✅ Đã cập nhật điểm {pri_score} cho {record_info['ten_tk']} (tháng {record_info['month']}/{record_info['year']})",
            "updated_by": current_user,
            "score": pri_score
        })
        
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"Lỗi cập nhật: {str(e)}"}), 500
    finally:
        conn.close()

# Phan cap nhat thong tin giao vien (GV) dang hien thi
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

# Phan cap nhat thong tin hoc sinh (HS) dang hien thi
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

# Remove bang du lieu trong sql -----> (Nguy hiem ) <-----
@app.route("/remove-dept-data", methods=["POST"])
def remove_dept_data():
    data = request.get_json()
    dept = data.get("dept")

    # Xac dinh bang can xoa
    if dept == "GV":
        table = "giaovien"
    elif dept == "HS":
        table = "hocsinh"
    else:
        return jsonify({"message": "Invalid department."}), 400

    conn = get_conn()
    try:
        with conn.cursor() as cursor:
            #  Tat kiem tra rang buoc khoa ngoai
            cursor.execute("SET FOREIGN_KEY_CHECKS=0")

            #  Thuc hien xoa du lieu
            cursor.execute(f"DELETE FROM {table}")

            #  Bat lai kiem tra rang buoc
            cursor.execute("SET FOREIGN_KEY_CHECKS=1")

        conn.commit()
        return jsonify({"message": f"All data from {dept} removed successfully."})
    except Exception as e:
        conn.rollback()
        return jsonify({"message": f"Error: {str(e)}"}), 500
    finally:
        conn.close()


# Phan xu ly cau hoi EPA
@app.route("/admin/questions")
def admin_questions():
    if "user" not in session:
        return redirect("/")
    
    # Chi cho phep admin hoac kimnhung truy cap
    user = session.get("user")
    role = session.get("role")
    if not (role == "admin" or user == "kimnhung"):
        return render_template("403.html"), 403
        
    return render_template("cauhoi_epa.html", user=user, role=role)

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
    if "user" not in session:
        return jsonify({"error": "Chưa đăng nhập"}), 401
    
    # Chi cho phep admin hoac kimnhung chinh sua diem
    user = session.get("user")
    role = session.get("role")
    can_edit_score = (role == "admin" or user == "kimnhung")
    
    data = request.get_json()
    id = data.get('id')
    question = data.get('question', '').strip()
    translate = data.get('translate', '').strip()
    score = data.get('score', 20)  # Mặc định 20 điểm
    
    if not question:
        return jsonify({"error": "Câu hỏi không được để trống!"}), 400
    
    # Validate score chi khi user co quyen chinh sua
    if can_edit_score and score not in [5, 10, 20]:
        return jsonify({"error": "Điểm phải là 5, 10 hoặc 20!"}), 400
        
    conn = get_conn()
    with conn.cursor() as cur:
        if id:
            # Chi cap nhat diem neu user co quyen
            if can_edit_score:
                cur.execute(
                    "UPDATE cauhoi_epa SET question = %s, translate = %s, score = %s WHERE id = %s",
                    (question, translate, score, id)
                )
            else:
                cur.execute(
                    "UPDATE cauhoi_epa SET question = %s, translate = %s WHERE id = %s",
                    (question, translate, id)
                )
        else:
            # Khi tao moi, chi set diem neu user co quyen
            if can_edit_score:
                cur.execute(
                    "INSERT INTO cauhoi_epa (question, translate, score) VALUES (%s, %s, %s)",
                    (question, translate, score)
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

# Tong hop diem danh gia EPA.
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

#Doc du lieu bang de lay danh sach ma
@app.route("/api/danh-sach-ma")
def api_danh_sach_ma():
    conn = get_conn()
    result = {"maGVList": [], "maLopList": []}
    try:
        with conn.cursor() as cursor:
            # Lay danh sach ma giao vien
            cursor.execute("SELECT ma_gv FROM giaovien")
            result["maGVList"] = [row["ma_gv"] for row in cursor.fetchall()]
            # Lay danh sach ma lop
            cursor.execute("SELECT ma_lop FROM ds_lop")
            result["maLopList"] = [row["ma_lop"] for row in cursor.fetchall()]
    finally:
        conn.close()
    return jsonify(result)

#  ROUTE RENDER TEMPLATE
@app.route("/classes")
def classes_page():
    return render_template("classes.html")

@app.route("/assign-classes")
def assign_classes_page():
    return render_template("assign_classes.html")

@app.route("/assign-teachers")
def assign_teachers_page():
    return render_template("assign_teachers.html")

# API: Lay danh sach lop
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
            # Xoa giao vien gan voi lop do
            cur.execute("DELETE FROM lop_gv WHERE ma_lop = %s", (ma_lop,))
            # Xoa hoc sinh phan lop (neu co)
            cur.execute("DELETE FROM phan_lop WHERE ma_lop = %s", (ma_lop,))
            # Xoa lop
            cur.execute("DELETE FROM ds_lop WHERE ma_lop = %s", (ma_lop,))
            conn.commit()
        return jsonify({"message": f"Đã xoá lớp {ma_lop} và dữ liệu liên quan"})
    finally:
        conn.close()

# API: Them lop moi
@app.route("/api/classes", methods=["POST"])
def add_class():
    data = request.json
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("INSERT INTO ds_lop (ma_lop, ten_lop) VALUES (%s, %s)", (data["ma_lop"], data["ten_lop"]))
        conn.commit()
    conn.close()
    return jsonify({"message": "Lớp đã thêm"})

# Cap nhat nut sua ten lop
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

# Chuc nang tu nhan dien so lon nhat co trong ma HS
@app.route("/api/last-ma-hs-prefix", methods=["GET"])
def get_last_ma_hs():
    prefix = request.args.get("prefix", "HS").upper()
    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute("SELECT ma_hs FROM hocsinh WHERE ma_hs LIKE %s", (f"{prefix}%",))
        ma_list = [row["ma_hs"] for row in cursor.fetchall()]
    conn.close()
    # Tim so lon nhat
    max_num = 0
    for m in ma_list:
        match = re.match(rf"{prefix}(\d+)", m)
        if match:
            num = int(match.group(1))
            if num > max_num:
                max_num = num
    return jsonify({"prefix": prefix, "next_num": max_num + 1})

# Hien thi goi y ma ma_hs tiep theo trong input dong
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

# Hien thi goi y ma ma_gv tiep theo trong input dong
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

# API lay danh sach hoc sinh kem ten lop
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

# API cap nhat ma lop cho hoc sinh
@app.route("/api/update-student-class", methods=["POST"])
def update_student_class():
    data = request.get_json()
    ma_hs = data.get("ma_hs")
    new_ma_lop = data.get("ma_lop")
    conn = get_conn()
    with conn.cursor() as cur:
        #  Chi cap nhat bang phan_lop
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
@app.route("/api/assign-teacher", methods=["POST"])
def assign_teacher():
    data    = request.get_json(force=True)
    ma_gv   = data.get("ma_gv")
    ma_lop  = data.get("ma_lop")
    vai_tro = data.get("vai_tro")

    # 1. Validate input
    if not all([ma_gv, ma_lop, vai_tro]):
        return jsonify({"error": "Thiếu dữ liệu"}), 400

    # 2. Mo ket noi va cursor tuple
    conn = get_conn()
    cur  = conn.cursor()
    try:
        # 3. Giang vien co ton tai?
        cur.execute(
            "SELECT 1 FROM giaovien WHERE ma_gv = %s LIMIT 1",
            (ma_gv,)
        )
        if cur.fetchone() is None:
            return jsonify({"error": "Giáo viên không tồn tại"}), 404

        # 4. Lop co ton tai?
        cur.execute(
            "SELECT 1 FROM ds_lop WHERE ma_lop = %s LIMIT 1",
            (ma_lop,)
        )
        if cur.fetchone() is None:
            return jsonify({"error": "Lớp không tồn tại"}), 404

        # 5. Da phan cong chua?
        cur.execute(
            "SELECT 1 FROM lop_gv WHERE ma_lop = %s AND ma_gv = %s LIMIT 1",
            (ma_lop, ma_gv)
        )
        if cur.fetchone() is not None:
            return jsonify({"error": "Đã phân công rồi"}), 409

        # 6. Them phan cong moi
        cur.execute(
            "INSERT INTO lop_gv (ma_lop, ma_gv, vai_tro) VALUES (%s, %s, %s)",
            (ma_lop, ma_gv, vai_tro)
        )
        conn.commit()

        # 7. (Tuy chon) Ghi log
        user = session.get("user_ten_tk")
        if user:
            action = f"Assigned teacher {ma_gv} to class {ma_lop} as {vai_tro}"
            cur.execute(
                "INSERT INTO logs (user_ten_tk, target_staff_id, target_table, action) "
                "VALUES (%s, %s, 'lop_gv', %s)",
                (user, ma_gv, action)
            )
            conn.commit()

        # 8. Thanh cong
        return jsonify({"message": "Gán giáo viên thành công"}), 201

    except Exception as e:
        # Tra loi chi tiet de debug neu can
        return jsonify({"error": str(e)}), 500

    finally:
        # luon dong tai nguyen
        cur.close()
        conn.close()

# API: Phan lop hoc sinh
@app.route("/api/assign-class", methods=["POST"])
def assign_class():
    data = request.json
    ma_hs = data.get("ma_hs")
    ma_lop = data.get("ma_lop")
    if not ma_hs or not ma_lop:
        return jsonify({"error": "Thiếu mã học sinh hoặc mã lớp"}), 400
    conn = get_conn()
    with conn.cursor() as cur:
        # Kiem tra hoc sinh da duoc phan lop chua
        cur.execute("SELECT * FROM phan_lop WHERE ma_hs = %s", (ma_hs,))
        existing = cur.fetchone()
        if existing:
            # Cap nhat phan lop
            cur.execute("UPDATE phan_lop SET ma_lop = %s WHERE ma_hs = %s", (ma_lop, ma_hs))
        else:
            # Them moi phan lop
            cur.execute("INSERT INTO phan_lop (ma_hs, ma_lop) VALUES (%s, %s)", (ma_hs, ma_lop))
        conn.commit()
    conn.close()
    return jsonify({"message": "Đã gán học sinh vào lớp thành công"})

# API: Lay danh sach giao vien
@app.route("/api/teachers", methods=["GET"])
def get_teachers():
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("SELECT ma_gv, ho_va_ten FROM giaovien")
        result = cur.fetchall()
    conn.close()
    return jsonify(result)

# API: Gan giao vien cho lop
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

#API: Cap nhat vai tro hoac lop hoc
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
            # Khi doi lop, can biet lop cu de cap nhat dung dong
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

#API: Xoa phan cong giao vien khoi lop
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

# THoi gian mo EPA  
def open_browser():
    # Su dung protocol-relative URL hoac de browser tu detect
    import socket
    try:
        # Kiem tra xem co dang chay tren HTTPS khong
        webbrowser.open("http://localhost:5000")
    except Exception as e:
        print(f" Could not open browser: {e}")

#Ham doi mat khau user dang logging
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

#Bang danh gia danh cho to truong 
@app.route('/sup-epa-score')
def sup_epa_score():
    from datetime import datetime
    import pymysql

    user = session.get('user')
    role = session.get('role', '')
    
    # DEBUG: Log session info
    print(f"[DEBUG] sup-epa-score accessed by user='{user}', role='{role}'")
    
    if not user:
        print(f"[DEBUG] No user in session, redirecting to login")
        return redirect('/login')

    now = datetime.now()
    current_month = now.month
    current_year = now.year

    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            # Kiểm tra quyền supervisor EPA thay vì chuc_vu
            cursor.execute("""
                SELECT make_epa_tgv, make_epa_all FROM thoigianmoepa WHERE ten_tk = %s
            """, (user,))
            epa_record = cursor.fetchone()
            
            print(f"[DEBUG] EPA record for {user}: {epa_record}")
            
            # Kiểm tra quyền supervisor EPA
            can_supervise = False
            if epa_record:
                if epa_record['make_epa_all'] == 'yes':
                    can_supervise = True
                    print(f"[DEBUG] Access granted: make_epa_all = yes")
                elif role == 'supervisor' and epa_record['make_epa_tgv'] == 'yes':
                    can_supervise = True
                    print(f"[DEBUG] Access granted: role=supervisor AND make_epa_tgv=yes")
                else:
                    print(f"[DEBUG] Access check failed: role={role}, make_epa_tgv={epa_record['make_epa_tgv']}")
            else:
                print(f"[DEBUG] No EPA record found for user {user}")
            
            # Admin luôn được phép
            if role == 'admin':
                can_supervise = True
                print(f"[DEBUG] Access granted: role = admin")
                
            if not can_supervise:
                print(f"[DEBUG] RETURNING 403: can_supervise = {can_supervise}")
                return "Bạn không có quyền xem trang này", 403
                
            print(f"[DEBUG] Permission check passed for {user}")

            # Lấy chuc_vu để xác định nhóm cần đánh giá  
            cursor.execute("""
                SELECT chuc_vu FROM giaovien WHERE ten_tk=%s
            """, (user,))
            row = cursor.fetchone()
            if not row:
                return "Không tìm thấy thông tin giáo viên", 404

            chuc_vu = row['chuc_vu']
            
            # Xác định target_chuc_vu dựa trên chuc_vu hiện tại
            if chuc_vu.startswith("TGV"):
                # TGV -> quản lý GV cùng tổ (cùng số)
                suffix = chuc_vu[3:]  # ví dụ: '2' từ 'TGV2'
                target_chuc_vu = f"GV{suffix}"
            elif chuc_vu.startswith("GV"):
                # GV -> có thể được phép chấm điểm cho GV cùng tổ
                suffix = chuc_vu[2:]  # ví dụ: '1' từ 'GV1'
                target_chuc_vu = f"GV{suffix}"
            else:
                # Chức vụ khác -> không xác định được tổ, từ chối
                return f"Không xác định được tổ cho chức vụ '{chuc_vu}'", 403

            #  Lay danh sach thanh vien cung to va trang thai danh gia tu tongdiem_epa
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

            #  Cap nhat tung cau hoi trong bangdanhgia
            for key, value in updates.items():
                if key.startswith('sup_comment_') or key.startswith('sup_score_'):
                    col, id_ = key.rsplit('_', 1)
                    cursor.execute(
                        f"UPDATE bangdanhgia SET {col}=%s WHERE id=%s",
                        (value, id_)
                    )

            #  Tong hop lai sup_score tu bangdanhgia
            cursor.execute("""
                SELECT ten_tk, year, month, SUM(sup_score) AS total_sup
                FROM bangdanhgia
                WHERE year=%s AND month=%s
                GROUP BY ten_tk, year, month
            """, (current_year, current_month))

            rows = cursor.fetchall()

            #  Cap nhat hoac chen moi vao tongdiem_epa
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
