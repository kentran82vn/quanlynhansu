from flask import Flask, jsonify, render_template, request, redirect, session
from apis.employees_api import employees_bp
from apis.users_api import users_bp
from apis.exportdata_api import export_bp
from apis.importdata_api import import_bp
from apis.edit_questions import edit_questions_bp
from utils.db import get_conn
from datetime import datetime
from apis.user_epa_score import user_epa_score_bp
from werkzeug.security import check_password_hash
from apis.db_structure import update_data_tables_structure
import calendar
import traceback
import webbrowser
import threading
import os
import json

app = Flask(__name__)
app.secret_key = "supersecretkey"

app.register_blueprint(employees_bp)
app.register_blueprint(users_bp)
app.register_blueprint(export_bp)
app.register_blueprint(import_bp)
app.register_blueprint(user_epa_score_bp)
app.register_blueprint(edit_questions_bp)

def log_action(user_id, action, target_staff_id=None, target_table=None):
    try:
        conn = get_conn()
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO logs (user_id, target_staff_id, target_table, action, created_at)
                VALUES (%s, %s, %s, %s, NOW())
            """, (user_id, target_staff_id, target_table, action))
            conn.commit()
    except Exception as e:
        print(f"⚠️ Log action failed: {e}")
    finally:
        if conn:
            conn.close()

@app.route("/")
def home():
    if not session.get("username"):
        return redirect("/login")
    return render_template("index.html", user=session["username"], role=session["role"], password_expiry=session.get("password_expiry"))

@app.route("/users")
def users_page():
    if session.get("role") != "admin":
        return redirect("/")
    return render_template("users.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) AS total FROM users_account")
        count = cursor.fetchone()["total"]
        print("🧾 Số lượng user hiện tại:", count)

        if count == 0:
            from werkzeug.security import generate_password_hash
            hashed_pw = generate_password_hash("abc000")
            print("🛠️ Tạo tài khoản admin mặc định...")
            print("→ Username: admin")
            print("→ Mật khẩu (raw): abc000")
            print("→ Mật khẩu (hash):", hashed_pw)

            cursor.execute("""
                INSERT INTO users_account (username, password, role, created_by, created_date, password_expiry)
                VALUES (%s, %s, %s, %s, NOW(), DATE_ADD(NOW(), INTERVAL 90 DAY))
            """, (
                "admin",
                hashed_pw,
                "admin",
                "system"
            ))
            conn.commit()
            print("✅ Tạo thành công tài khoản admin mặc định.")
    conn.close()

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        print("🔐 Login attempt:", username)

        conn = get_conn()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users_account WHERE username = %s", (username,))
            user = cursor.fetchone()
        conn.close()

        if user:
            print("🔎 Tìm thấy user:", user["username"])
            print("→ Mật khẩu nhập vào:", password)
            print("→ Mật khẩu lưu DB:", user["password"])

            if check_password_hash(user["password"], password):
                session["user_id"] = user["id"]
                session["username"] = user["username"]
                session["role"] = user["role"]
                session["password_expiry"] = str(user["password_expiry"]) if user["password_expiry"] else ""
                print("✅ Đăng nhập thành công:", username)
                return redirect("/")
            else:
                print("❌ Sai mật khẩu")
                error = "Invalid credentials. Please try again."
        else:
            print("❌ Không tìm thấy user:", username)

    return render_template("login.html", error=error)

## Update data base for tables structure #########
@app.route("/update-database", methods=["POST"])
def update_database():
    if session.get("role") != "admin":
        return jsonify({"success": False, "message": "Bạn không có quyền."}), 403

    conn = get_conn()
    try:
        update_data_tables_structure(conn)

        cursor = conn.cursor()
        cursor.execute("SELECT * FROM data_tables_structure")
        rows = cursor.fetchall()

        tables = []
        for row in rows:
            tables.append({
                "table_name": row[0],
                "column_names": row[1],
                "column_count": row[2],
                "row_count": row[3],
            })

        return jsonify({"success": True, "tables": tables})
    except Exception as e:
        print("❌ Error updating DB structure:", str(e))
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/employees")
def employees():
    if not session.get("username"):
        return redirect("/login")
    conn = get_conn()
    with conn.cursor() as cursor:    # ❌ KHÔNG có dictionary=True
        cursor.execute("SELECT * FROM info_gv")
        data_gv = cursor.fetchall()

        cursor.execute("SELECT * FROM info_hs")
        data_hs = cursor.fetchall()

    conn.close()
    return render_template(
        "employees_index.html",
        data_ops=data_gv,
        data_hs=data_hs,
        user=session["username"],
        role=session["role"],
        password_expiry=session.get("password_expiry")
    )

@app.route("/add", methods=["POST"])
def add_employee():
    data = request.get_json()
    staff_id = data.get("Staff ID")
    full_name = data.get("Full Name")

    if not staff_id or not full_name:
        return jsonify({"status": "error", "message": "Missing Staff ID or Full Name"}), 400

    conn = get_conn()
    with conn.cursor() as cursor:
        # Check trùng staff_id
        cursor.execute("SELECT 1 FROM info_gv WHERE staff_id = %s", (staff_id,))
        if cursor.fetchone():
            return jsonify({"status": "error", "message": f"Staff ID '{staff_id}' already exists"}), 400

        cursor.execute("""
            INSERT INTO info_gv (
                staff_id, full_name, nick_name, team, birth_date, hometown, cccd,
                cccd_issued_date, tax_code, cmnd, insurance_number, phone_number,
                bank_account, email, blood_type, address
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            staff_id,
            full_name,
            data.get("Nick Name"),
            data.get("Team"),
            data.get("Birth Date"),
            data.get("Hometown"),
            data.get("Cccd"),
            data.get("Cccd Issued Date"),
            data.get("Tax Code"),
            data.get("Cmnd"),
            data.get("Insurance Number"),
            data.get("Phone Number"),
            data.get("Bank Account"),
            data.get("Email"),
            data.get("Blood Type"),
            data.get("Address")
        ))

        log_action(staff_id, "add", f"Added GV staff {full_name}")

    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})

@app.route("/delete", methods=["POST"])
def delete_employee():
    data = request.get_json()
    staff_id = data.get("staff_id")
    dept = data.get("dept", "GV").upper()  # Default thành "GV"

    if not staff_id:
        return jsonify({"status": "error", "reason": "Missing staff_id"})

    table = "info_gv" if dept == "GV" else None
    if not table:
        return jsonify({"status": "error", "reason": f"Unsupported dept '{dept}'"})

    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute(f"DELETE FROM {table} WHERE staff_id = %s", (staff_id,))
        if cursor.rowcount > 0:
            log_action(
                user_id=session.get("user_id"),
                action=f"Deleted employee {staff_id}",
                target_staff_id=staff_id,
                target_table=table
            )
            conn.commit()
            return jsonify({"status": "ok"})
        else:
            return jsonify({"status": "error", "reason": "Staff ID not found"})

@app.route("/update", methods=["POST"])
def update_employee():
    data = request.get_json()
    dept = data.pop("Dept", "GV").upper()
    index = data.pop("index")
    key = list(data.keys())[0]
    value = data[key]

    field_map = {
        "GV": {
            "Staff ID": "staff_id",
            "Full Name": "full_name",
            "Nick Name": "nick_name",
            "Team": "team",
            "Birth Date": "birth_date",
            "Hometown": "hometown",
            "Cccd": "cccd",
            "Cccd Issued Date": "cccd_issued_date",
            "Tax Code": "tax_code",
            "Cmnd": "cmnd",
            "Insurance Number": "insurance_number",
            "Phone Number": "phone_number",
            "Bank Account": "bank_account",
            "Email": "email",
            "Blood Type": "blood_type",
            "Address": "address"
        }
    }

    if dept not in field_map or key not in field_map[dept]:
        return jsonify({"status": "error", "reason": "Invalid dept or field"})

    field = field_map[dept][key]
    table = "info_gv"

    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute(f"SELECT staff_id FROM {table} ORDER BY staff_id LIMIT 1 OFFSET %s", (index,))
        row = cursor.fetchone()
        if row:
            staff_id = row["staff_id"]
            cursor.execute(f"UPDATE {table} SET {field} = %s WHERE staff_id = %s", (value, staff_id))
            log_action(staff_id, "update", f"Updated {field} to '{value}'")
            conn.commit()
            return jsonify({"status": "ok"})
        else:
            return jsonify({"status": "error", "reason": "Invalid index"})

@app.route("/epa_score")
def epa_score_page():
    if not session.get("username"):
        return redirect("/login")

    if session.get("role") != "admin":
        print(f"[ACCESS DENIED] User {session.get('username')} tried to access EPA Score")
        return "⛔ Access denied. Admin only!", 403

    return render_template(
        "epa_score.html",
        user=session["username"],
        role=session["role"]
    )

# --- Collect existed Team namename---
@app.route("/api/epa/team-list")
def api_epa_team_list():
    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute("SELECT DISTINCT team FROM info_gv WHERE team IS NOT NULL AND team != ''")
        teams = sorted([row["team"] for row in cursor.fetchall()])
    conn.close()
    return jsonify({"success": True, "teams": sorted(teams)})

# --- API: Load EPA Scores ---
@app.route("/api/epa/load")
def api_epa_load():
    year = int(request.args.get("year"))
    month = int(request.args.get("month"))
    team_filter = request.args.get("team")

    # Tính số ngày thực tế trong tháng
    num_days = calendar.monthrange(year, month)[1]
    days = list(range(1, num_days + 1))
    default_score = round(300 / num_days, 2)  # làm tròn 2 số thập phân

    print(f"==> Received year={year}, month={month}, team_filter={team_filter}")
    print(f"==> Month has {num_days} days. Default score = {default_score}")

    conn = get_conn()
    with conn.cursor() as cursor:
        if team_filter:
            cursor.execute("""SELECT full_name, team, staff_id, '' AS position FROM info_gv WHERE team = %s""", (team_filter,))
        else:
            cursor.execute("""SELECT full_name, team, staff_id, '' AS position FROM info_gv""")
        employees = cursor.fetchall()
        print(f"==> Fetched {len(employees)} employees")

        cursor.execute("SELECT staff_id, day, score FROM epa_scores WHERE year = %s AND month = %s", (year, month))
        raw_scores = cursor.fetchall()
        print(f"==> Loaded {len(raw_scores)} EPA scores")

    conn.close()

    score_map = {}
    for s in raw_scores:
        score_map.setdefault(s["staff_id"], {})[s["day"]] = s["score"]

    records = []
    for emp in employees:
        emp_id = emp["staff_id"]
        scores = [score_map.get(emp_id, {}).get(day, default_score) for day in days]
        print(f"--> {emp['full_name']} ({emp_id}) scores: {scores}")
        records.append({
            "name": emp["full_name"],
            "position": emp.get("position", ""),
            "team": emp["team"],
            "id": emp_id,
            "scores": scores
        })

    return jsonify({"success": True, "days": days, "records": records})

@app.route("/api/epa/save", methods=["POST"])
def api_epa_save():
    if 'username' not in session or session.get("role") != "admin":
        return jsonify({"success": False, "message": "unauthorized"})

    data = request.json
    year = int(data.get("year"))
    month = int(data.get("month"))
    records = data.get("data", [])

    conn = get_conn()
    with conn.cursor() as cursor:
        for rec in records:
            emp_id = rec["id"]
            scores = rec["scores"]
            for i, score in enumerate(scores):
                day = i + 1
                cursor.execute("""
                    INSERT INTO epa_scores (staff_id, year, month, day, score)
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE score = VALUES(score)
                """, (emp_id, year, month, day, score))
        cursor.execute("INSERT INTO logs (user_id, action) VALUES (%s, %s)", (
            session.get("user_id"),  # <-- lấy user_id từ session
            f"Saved EPA scores for {year}-{month}"
        ))
        conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Scores saved to database."})

@app.route("/logs")
def view_logs():
    if session.get("role") != "admin":
        return redirect("/")
    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT logs.*, users_account.username 
            FROM logs 
            LEFT JOIN users_account ON logs.user_id = users_account.id
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
        cursor.execute("SELECT COUNT(*) AS total FROM info_gv")
        total = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT team, COUNT(*) AS count FROM info_gv
            WHERE team IS NOT NULL AND team != ''
            GROUP BY team
        """)
        team_stats = cursor.fetchall()
    conn.close()

    return render_template("stats.html", total=total, team_stats=team_stats)

@app.route("/epa_summary")
def epa_summary():
    if session.get("role") != "admin":
        return redirect("/")

    year = datetime.now().year
    month = datetime.now().month

    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT e.staff_id, e.full_name, e.team, s.year, s.month,
                   AVG(s.score) AS avg_score
            FROM (
                SELECT staff_id, full_name, team FROM info_gv
            ) AS e
            JOIN epa_scores s ON e.staff_id = s.staff_id
            WHERE s.year = %s AND s.month = %s
            GROUP BY e.staff_id, s.year, s.month
        """, (year, month))
        scores = cursor.fetchall()
    conn.close()

    for s in scores:
        avg = s["avg_score"]
        if avg >= 240:
            s["grade"] = "A"
        elif avg >= 220:
            s["grade"] = "B"
        elif avg >= 200:
            s["grade"] = "C"
        else:
            s["grade"] = "D"

    return render_template("epa_summary.html", data=scores, year=year, month=month)

@app.route("/export-data")
def export_data_page():
    if session.get("role") != "admin":
        return redirect("/")

    export_path = os.path.join("data", "export_columns.json")
    columns_by_table = {}

    if os.path.exists(export_path):
        try:
            with open(export_path, "r", encoding="utf-8") as f:
                columns_by_table = json.load(f)
        except Exception as e:
            print(f"[WARN] Failed to load column metadata: {e}")
            columns_by_table = {}
    else:
        print("[INFO] export_columns.json not found. Please click 'Update Tables' to generate.")
        columns_by_table = {}

    return render_template("export_data.html", columns_by_table=columns_by_table)

########## Khai báo cấu trúc các bảng trong mysql #######
@app.route("/api/table-schema")
def get_table_schema():
    table_map = {
        "HS": "info_hs",
        "GV": "info_gv"
    }

    result = {}
    conn = get_conn()
    with conn.cursor() as cursor:
        for label, table in table_map.items():
            cursor.execute(f"SHOW COLUMNS FROM {table}")
            cols = [row["Field"] for row in cursor.fetchall()]
            result[label] = cols
    conn.close()
    return jsonify(result)
######## Thêm route API trả về danh sách employees_mis ###########
@app.route('/api/employees')
def api_employees():
    dept = request.args.get("dept")
    conn = get_conn()
    cursor = conn.cursor()

    if dept == "HS":
        cursor.execute("SELECT * FROM info_hs")
    elif dept == "GV":
        cursor.execute("SELECT * FROM info_gv")
    else:
        return jsonify({"error": "Phòng ban không hợp lệ"}), 400

    rows = cursor.fetchall()
    conn.close()
    return jsonify({"rows": rows})

@app.route("/remove-dept-data", methods=["POST"])
def remove_dept_data():
    if session.get("role") != "admin":
        return jsonify({"message": "Unauthorized"}), 403
    data = request.get_json()
    dept = data.get("dept", "").upper()
    table_map = {
        "HS": "info_hs",
        "GV": "info_gv"
    }
    table = table_map.get(dept)
    if not table:
        return jsonify({"message": "Invalid department"}), 400
    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute(f"DELETE FROM {table}")
    conn.commit()
    conn.close()
    return jsonify({"message": f"All data from {dept} removed."})

def open_browser():
    webbrowser.open("http://localhost:5000/login")

if __name__ == "__main__":
    threading.Timer(1.0, open_browser).start()
    app.run(debug=True, use_reloader=False)
