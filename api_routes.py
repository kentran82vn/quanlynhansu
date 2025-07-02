from flask import Flask, request, jsonify
import pymysql

app = Flask(__name__)

def get_conn():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="your_password",
        database="quanlytruonghoc_app",
        cursorclass=pymysql.cursors.DictCursor
    )

# API: Lấy danh sách lớp
@app.route("/api/classes", methods=["GET"])
def get_classes():
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM ds_lop")
        result = cur.fetchall()
    conn.close()
    return jsonify(result)

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

# API: Lấy danh sách học sinh
@app.route("/api/students", methods=["GET"])
def get_students():
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("SELECT ma_hs, ho_va_ten FROM hocsinh")
        result = cur.fetchall()
    conn.close()
    return jsonify(result)

# API: Phân lớp học sinh
@app.route("/api/assign-class", methods=["POST"])
def assign_class():
    data = request.json
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("REPLACE INTO phan_lop (ma_hs, ma_lop) VALUES (%s, %s)", (data["ma_hs"], data["ma_lop"]))
        conn.commit()
    conn.close()
    return jsonify({"message": "Đã phân lớp"})

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
@app.route("/api/assign-teacher", methods=["POST"])
def assign_teacher():
    data = request.json
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("""
            REPLACE INTO lop_gv (ma_lop, ma_gv, vai_tro) VALUES (%s, %s, %s)
        """, (data["ma_lop"], data["ma_gv"], data["vai_tro"]))
        conn.commit()
    conn.close()
    return jsonify({"message": "Đã gán giáo viên"})