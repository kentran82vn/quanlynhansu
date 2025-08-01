from flask import Blueprint, request, jsonify, make_response
import pandas as pd
from utils.db import get_conn

import_bp = Blueprint("import_bp", __name__)

def clean(val):
    """Clean and validate data values"""
    if pd.isna(val) or val is None:
        return None
    # Convert to string and strip whitespace
    str_val = str(val).strip()
    # Return None for empty strings
    return str_val if str_val != '' and str_val.lower() != 'nan' else None

def clean_numeric_string(val):
    """Clean numeric values that should be stored as strings (to preserve leading zeros)"""
    if pd.isna(val) or val is None:
        return None
    
    # Convert to string, remove decimal points for integers
    str_val = str(val).strip()
    
    # Remove .0 from the end if it's a float representation of an integer
    if str_val.endswith('.0'):
        str_val = str_val[:-2]
    
    # Return None for empty strings
    return str_val if str_val != '' and str_val.lower() != 'nan' else None

def format_vietnamese_id(val, id_type):
    """Format Vietnamese ID numbers with proper leading zeros"""
    if pd.isna(val) or val is None:
        return None
    
    # Clean the value first
    str_val = clean_numeric_string(val)
    if not str_val or not str_val.isdigit():
        return str_val
    
    current_len = len(str_val)
    
    if id_type == "cccd":
        # CCCD: should be 12 digits
        if current_len < 12:
            return str_val.zfill(12)
    elif id_type == "cmnd":
        # CMND: can be 9 or 12 digits, pad to 12 if less than 9
        if current_len < 9:
            return str_val.zfill(9)
        elif 9 <= current_len < 12:
            return str_val  # Keep as is
        elif current_len < 12:
            return str_val.zfill(12)  
    elif id_type == "phone":
        # Phone: should be 10 digits for mobile
        if current_len == 9:  # Missing leading 0
            return "0" + str_val
        elif current_len < 10:
            return str_val.zfill(10)
    elif id_type == "ma_dinh_danh":
        # Mã định danh: should be 12 digits  
        if current_len < 12:
            return str_val.zfill(12)
    
    return str_val

def parse_date_to_mysql(val):
    """Convert date from various formats to YYYY-MM-DD format for MySQL"""
    if pd.isna(val) or val is None:
        return None
    
    str_val = str(val).strip()
    if str_val == '' or str_val.lower() == 'nan':
        return None
    
    try:
        # If already in datetime format (e.g., '2019-11-06 00:00:00')
        if ' 00:00:00' in str_val:
            date_obj = pd.to_datetime(str_val, errors='coerce')
            if pd.notna(date_obj):
                return date_obj.strftime('%Y-%m-%d')
        
        # Try to parse DD/MM/YYYY format
        date_obj = pd.to_datetime(str_val, format='%d/%m/%Y', errors='coerce')
        if pd.notna(date_obj):
            return date_obj.strftime('%Y-%m-%d')
        
        # Try YYYY-MM-DD format
        date_obj = pd.to_datetime(str_val, format='%Y-%m-%d', errors='coerce')
        if pd.notna(date_obj):
            return date_obj.strftime('%Y-%m-%d')
        
        # Try other common formats with day first
        date_obj = pd.to_datetime(str_val, dayfirst=True, errors='coerce')
        if pd.notna(date_obj):
            return date_obj.strftime('%Y-%m-%d')
            
    except:
        pass
    
    return None

@import_bp.route("/import_gv", methods=["POST"])
def import_employees_gv():
    """Import giáo viên từ file Excel"""
    try:
        if 'file' not in request.files:
            response = make_response(jsonify({"error": "Không có file được upload"}), 400)
            response.headers['Content-Type'] = 'application/json'
            return response

        file = request.files['file']
        if file.filename == "":
            response = make_response(jsonify({"error": "Tên file trống"}), 400)
            response.headers['Content-Type'] = 'application/json'
            return response

        # Validate file extension
        allowed_extensions = ['.xlsx', '.xls']
        file_ext = '.' + file.filename.split('.')[-1].lower()
        if file_ext not in allowed_extensions:
            response = make_response(jsonify({"error": "Chỉ chấp nhận file Excel (.xlsx, .xls)"}), 400)
            response.headers['Content-Type'] = 'application/json'
            return response
        # Read Excel file - all data as string to preserve leading zeros, specify engine
        df = pd.read_excel(file, engine='openpyxl', dtype=str, date_format=None, parse_dates=False)
        df.columns = df.columns.str.strip()
        
        # Version indicator - will appear in logs when new code is loaded
        print("INFO: Using FIXED import GV code v2.0")

        # Doi ten cot dung theo cau truc bang giaovien
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
            "SỔ BH": "so_bh",
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
                "ma_gv": clean(row.get("ma_gv")),
                "ho_va_ten": clean(row.get("ho_va_ten")),
                "ten_tk": ten_tk_val,
                "chuc_vu": clean(row.get("chuc_vu")),
                "ngay_sinh": parse_date_to_mysql(row.get("ngay_sinh")),
                "que_quan": clean(row.get("que_quan")),
                "cccd": format_vietnamese_id(row.get("cccd"), "cccd"),
                "ngay_cap": parse_date_to_mysql(row.get("ngay_cap")),
                "mst": clean_numeric_string(row.get("mst")),
                "cmnd": format_vietnamese_id(row.get("cmnd"), "cmnd"),
                "so_bh": clean_numeric_string(row.get("so_bh")),
                "sdt": format_vietnamese_id(row.get("sdt"), "phone"),
                "tk_nh": clean(row.get("tk_nh")),
                "email": clean(row.get("email")),
                "nhom_mau": clean(row.get("nhom_mau")),
                "dia_chi": clean(row.get("dia_chi"))
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

        response = make_response(jsonify({"status": "success", "message": "Import giáo viên thành công"}), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    except Exception as e:
        # Enhanced error logging with context
        from flask import current_app, session
        current_app.logger.error(f"Error in import_employees_gv: {str(e)}")
        current_app.logger.error(f"User: {session.get('user', 'unknown')}")
        current_app.logger.error(f"File: {file.filename if 'file' in locals() else 'unknown'}")
        
        # Safe error categorization for user
        error_msg = str(e)
        if "pandas" in error_msg.lower():
            error_msg = "Lỗi đọc file Excel. Vui lòng kiểm tra định dạng file."
        elif "mysql" in error_msg.lower() or "database" in error_msg.lower():
            error_msg = "Lỗi kết nối cơ sở dữ liệu."
        elif "permission" in error_msg.lower():
            error_msg = "Không có quyền truy cập file."
        else:
            error_msg = "Đã xảy ra lỗi khi import dữ liệu."
            
        response = make_response(jsonify({"error": error_msg}), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

@import_bp.route("/import_hs", methods=["POST"])
def import_students_hs():
    """Import học sinh từ file Excel"""
    try:
        if 'file' not in request.files:
            response = make_response(jsonify({"error": "Không có file được upload"}), 400)
            response.headers['Content-Type'] = 'application/json'
            return response

        file = request.files['file']
        if file.filename == "":
            response = make_response(jsonify({"error": "Tên file trống"}), 400)
            response.headers['Content-Type'] = 'application/json'
            return response

        # Validate file extension
        allowed_extensions = ['.xlsx', '.xls']
        file_ext = '.' + file.filename.split('.')[-1].lower()
        if file_ext not in allowed_extensions:
            response = make_response(jsonify({"error": "Chỉ chấp nhận file Excel (.xlsx, .xls)"}), 400)
            response.headers['Content-Type'] = 'application/json'
            return response
        # Read Excel file - prevent auto date parsing, specify engine
        df = pd.read_excel(file, engine='openpyxl', dtype=str, date_format=None, parse_dates=False)
        df.columns = df.columns.str.strip()
        
        # Version indicator - will appear in logs when new code is loaded
        print("INFO: Using FIXED import code v2.0")

        # Đổi tên cột cho khớp SQL - FIXED: mapping sau khi strip()
        df.rename(columns={
            "MÃ HS": "ma_hs",
            "HỌ VÀ TÊN": "ho_va_ten",
            "NGÀY SINH": "ngay_sinh",      # FIXED: sau strip() không còn space
            "GIỚI TÍNH": "gioi_tinh",
            "DT": "dan_toc",
            "MÃ ĐỊNH DANH": "ma_dinh_danh",
            "HỌ VÀ TÊN BỐ": "ho_ten_bo",
            "NGHỀ NGHIỆP BỐ": "nghe_nghiep_bo",
            "HỌ VÀ TÊN MẸ": "ho_ten_me",
            "NGHỀ NGHIỆP MẸ": "nghe_nghiep_me",
            "HỘ KHẨU": "ho_khau",
            "SỐ CCCD CỦA BỐ/MẸ": "cccd_bo_me",  # FIXED: sau strip() không còn space ở đầu
            "ĐT": "sdt"
        }, inplace=True)

        conn = get_conn()
        cursor = conn.cursor()

        for _, row in df.iterrows():
            values = {
                "ma_hs": clean(row.get("ma_hs")),
                "ho_va_ten": clean(row.get("ho_va_ten")),
                "ngay_sinh": parse_date_to_mysql(row.get("ngay_sinh")),
                "gioi_tinh": clean(row.get("gioi_tinh")),
                "dan_toc": clean(row.get("dan_toc")),
                "ma_dinh_danh": format_vietnamese_id(row.get("ma_dinh_danh"), "ma_dinh_danh"),
                "ho_ten_bo": clean(row.get("ho_ten_bo")),
                "nghe_nghiep_bo": clean(row.get("nghe_nghiep_bo")),
                "ho_ten_me": clean(row.get("ho_ten_me")),
                "nghe_nghiep_me": clean(row.get("nghe_nghiep_me")),
                "ho_khau": clean(row.get("ho_khau")),
                "cccd_bo_me": format_vietnamese_id(row.get("cccd_bo_me"), "cccd"),
                "sdt": format_vietnamese_id(row.get("sdt"), "phone")
            }

            cursor.execute("""
                INSERT INTO hocsinh (
                    ma_hs, ho_va_ten, ngay_sinh, gioi_tinh, dan_toc,
                    ma_dinh_danh, ho_ten_bo, nghe_nghiep_bo, ho_ten_me,
                    nghe_nghiep_me, ho_khau, cccd_bo_me, sdt
                ) VALUES (
                    %(ma_hs)s, %(ho_va_ten)s, %(ngay_sinh)s, %(gioi_tinh)s, %(dan_toc)s,
                    %(ma_dinh_danh)s, %(ho_ten_bo)s, %(nghe_nghiep_bo)s, %(ho_ten_me)s,
                    %(nghe_nghiep_me)s, %(ho_khau)s, %(cccd_bo_me)s, %(sdt)s
                )
                ON DUPLICATE KEY UPDATE
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

        response = make_response(jsonify({"status": "success", "message": "Import học sinh thành công"}), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    except Exception as e:
        # Enhanced error logging with context
        from flask import current_app, session
        current_app.logger.error(f"Error in import_students_hs: {str(e)}")
        current_app.logger.error(f"User: {session.get('user', 'unknown')}")
        current_app.logger.error(f"File: {file.filename if 'file' in locals() else 'unknown'}")
        
        # Safe error categorization for user
        error_msg = str(e)
        if "pandas" in error_msg.lower():
            error_msg = "Lỗi đọc file Excel. Vui lòng kiểm tra định dạng file."
        elif "mysql" in error_msg.lower() or "database" in error_msg.lower():
            error_msg = "Lỗi kết nối cơ sở dữ liệu."
        elif "permission" in error_msg.lower():
            error_msg = "Không có quyền truy cập file."
        else:
            error_msg = "Đã xảy ra lỗi khi import dữ liệu."
            
        response = make_response(jsonify({"error": error_msg}), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

@import_bp.route("/fetch_hs", methods=["GET"])
def fetch_hs():
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM hocsinh ORDER BY ma_hs ASC")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({"rows": rows}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@import_bp.route("/fetch_gv", methods=["GET"])
def fetch_gv():
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM giaovien ORDER BY ma_gv ASC")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({"rows": rows}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
