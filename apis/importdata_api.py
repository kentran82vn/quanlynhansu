from flask import Blueprint, request, jsonify
import pandas as pd
from utils.db import get_conn
import traceback

import_bp = Blueprint("import_bp", __name__)

def clean(val):
    return val if pd.notnull(val) else None

@import_bp.route("/import_gv", methods=["POST"])
def import_employees_gv():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    try:
        df = pd.read_excel(file)
        df.columns = df.columns.str.strip()

        # ⚠️ Đổi tên cột đúng theo cấu trúc bảng `giaovien`
        df.rename(columns={
            "MÃ GV": "ma_gv",
            "HỌ VÀ TÊN": "ho_va_ten",
            "TÊN TK": "ten_tk",
            "CHỨC VỤ": "chuc_vu",
            "NGÀY SINH": "ngay_sinh",
            "QUÊ QUÁN": "que_quan",
            "CCCD": "cccd",
            "Ngày cấp": "ngay_cap",
            "MST": "mst",
            "CMND": "cmnd",
            "SỐ SỔ BH": "so_bh",
            "SỐ ĐT": "sdt",
            "SỐ TK": "tk_nh",
            "Email": "email",
            "Nhóm máu": "nhom_mau",
            "Địa chỉ": "dia_chi"
        }, inplace=True)

        conn = get_conn()
        cursor = conn.cursor()

        # Lấy danh sách ten_tk đã có sẵn trong bảng tk
        cursor.execute("SELECT ten_tk FROM tk")
        existing_ten_tk = {row["ten_tk"] for row in cursor.fetchall()}

        for _, row in df.iterrows():
            ten_tk_val = clean(str(row.get("ten_tk")))

            # Nếu có ten_tk nhưng chưa tồn tại thì tạo mới trong bảng tk
            if ten_tk_val and ten_tk_val not in existing_ten_tk:
                cursor.execute("""
                    INSERT INTO tk (ten_tk, nhom, mat_khau, ngay_tao)
                    VALUES (%s, %s, %s, CURDATE())
                """, (ten_tk_val, 'user', 'abc123'))
                existing_ten_tk.add(ten_tk_val)

            values = {
                "ma_gv": clean(str(row.get("ma_gv"))),
                "ho_va_ten": clean(str(row.get("ho_va_ten"))),
                "ten_tk": ten_tk_val,
                "chuc_vu": clean(str(row.get("chuc_vu"))),
                "ngay_sinh": pd.to_datetime(row.get("ngay_sinh"), dayfirst=True).date() if pd.notnull(row.get("ngay_sinh")) else None,
                "que_quan": clean(str(row.get("que_quan"))),
                "cccd": clean(str(row.get("cccd"))),
                "ngay_cap": pd.to_datetime(row.get("ngay_cap"), dayfirst=True).date() if pd.notnull(row.get("ngay_cap")) else None,
                "mst": clean(str(row.get("mst"))),
                "cmnd": clean(str(row.get("cmnd"))),
                "so_bh": clean(str(row.get("so_bh"))),
                "sdt": clean(str(row.get("sdt"))),
                "tk_nh": clean(str(row.get("tk_nh"))),
                "email": clean(str(row.get("email"))),
                "nhom_mau": clean(str(row.get("nhom_mau"))),
                "dia_chi": clean(str(row.get("dia_chi")))
            }

            cursor.execute("""
                INSERT INTO giaovien (
                    ma_gv, ho_va_ten, ten_tk, chuc_vu, ngay_sinh, que_quan,
                    cccd, ngay_cap, mst, cmnd, so_bh, sdt,
                    tk_nh, email, nhom_mau, dia_chi
                ) VALUES (%(ma_gv)s, %(ho_va_ten)s, %(ten_tk)s, %(chuc_vu)s, %(ngay_sinh)s, %(que_quan)s,
                          %(cccd)s, %(ngay_cap)s, %(mst)s, %(cmnd)s, %(so_bh)s, %(sdt)s,
                          %(tk_nh)s, %(email)s, %(nhom_mau)s, %(dia_chi)s)
                ON DUPLICATE KEY UPDATE
                    ho_va_ten = VALUES(ho_va_ten),
                    ten_tk = VALUES(ten_tk),
                    chuc_vu = VALUES(chuc_vu),
                    ngay_sinh = VALUES(ngay_sinh),
                    que_quan = VALUES(que_quan),
                    cccd = VALUES(cccd),
                    ngay_cap = VALUES(ngay_cap),
                    mst = VALUES(mst),
                    cmnd = VALUES(cmnd),
                    so_bh = VALUES(so_bh),
                    sdt = VALUES(sdt),
                    tk_nh = VALUES(tk_nh),
                    email = VALUES(email),
                    nhom_mau = VALUES(nhom_mau),
                    dia_chi = VALUES(dia_chi)
            """, values)

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"status": "success"}), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@import_bp.route("/import_hs", methods=["POST"])
def import_students_hs():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    try:
        df = pd.read_excel(file)
        df.columns = df.columns.str.strip()

        # Đổi tên cột cho khớp SQL
        df.rename(columns={
            "MÃ HS": "ma_hs",
            "MÃ GV": "ma_gv",
            "HỌ VÀ TÊN": "ho_va_ten",
            "NGÀY SINH": "ngay_sinh",
            "GIỚI TÍNH": "gioi_tinh",
            "DT": "dan_toc",
            "MÃ ĐỊNH DANH": "ma_dinh_danh",
            "HỌ VÀ TÊN BỐ": "ho_ten_bo",
            "NGHỀ NGHIỆP BỐ": "nghe_nghiep_bo",
            "HỌ VÀ TÊN MẸ": "ho_ten_me",
            "NGHỀ NGHIỆP MẸ": "nghe_nghiep_me",
            "HỘ KHẨU": "ho_khau",
            "SỐ CCCD CỦA BỐ/MẸ": "cccd_bo_me",
            "ĐT": "sdt"
        }, inplace=True)

        conn = get_conn()
        cursor = conn.cursor()

        for _, row in df.iterrows():
            values = {
                "ma_hs": clean(str(row.get("ma_hs"))),
                "ma_gv": clean(str(row.get("ma_gv"))),
                "ho_va_ten": clean(str(row.get("ho_va_ten"))),
                "ngay_sinh": pd.to_datetime(row.get("ngay_sinh"), dayfirst=True).date() if pd.notnull(row.get("ngay_sinh")) else None,
                "gioi_tinh": clean(str(row.get("gioi_tinh"))),
                "dan_toc": clean(str(row.get("dan_toc"))),
                "ma_dinh_danh": clean(str(row.get("ma_dinh_danh"))),
                "ho_ten_bo": clean(str(row.get("ho_ten_bo"))),
                "nghe_nghiep_bo": clean(str(row.get("nghe_nghiep_bo"))),
                "ho_ten_me": clean(str(row.get("ho_ten_me"))),
                "nghe_nghiep_me": clean(str(row.get("nghe_nghiep_me"))),
                "ho_khau": clean(str(row.get("ho_khau"))),
                "cccd_bo_me": clean(str(row.get("cccd_bo_me"))),
                "sdt": clean(str(row.get("sdt")))
            }

            cursor.execute("""
                INSERT INTO hocsinh (
                    ma_hs, ma_gv, ho_va_ten, ngay_sinh, gioi_tinh, dan_toc,
                    ma_dinh_danh, ho_ten_bo, nghe_nghiep_bo, ho_ten_me,
                    nghe_nghiep_me, ho_khau, cccd_bo_me, sdt
                ) VALUES (
                    %(ma_hs)s, %(ma_gv)s, %(ho_va_ten)s, %(ngay_sinh)s, %(gioi_tinh)s, %(dan_toc)s,
                    %(ma_dinh_danh)s, %(ho_ten_bo)s, %(nghe_nghiep_bo)s, %(ho_ten_me)s,
                    %(nghe_nghiep_me)s, %(ho_khau)s, %(cccd_bo_me)s, %(sdt)s
                )
                ON DUPLICATE KEY UPDATE
                    ma_gv = VALUES(ma_gv),
                    ho_va_ten = VALUES(ho_va_ten),
                    ngay_sinh = VALUES(ngay_sinh),
                    gioi_tinh = VALUES(gioi_tinh),
                    dan_toc = VALUES(dan_toc),
                    ma_dinh_danh = VALUES(ma_dinh_danh),
                    ho_ten_bo = VALUES(ho_ten_bo),
                    nghe_nghiep_bo = VALUES(nghe_nghiep_bo),
                    ho_ten_me = VALUES(ho_ten_me),
                    nghe_nghiep_me = VALUES(nghe_nghiep_me),
                    ho_khau = VALUES(ho_khau),
                    cccd_bo_me = VALUES(cccd_bo_me),
                    sdt = VALUES(sdt)
            """, values)

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"status": "success"}), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@import_bp.route("/fetch_hs", methods=["GET"])
def fetch_hs():
    try:
        conn = get_conn()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM hocsinh ORDER BY id ASC")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({"rows": rows}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
