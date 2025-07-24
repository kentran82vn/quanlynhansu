from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from utils.db import get_conn
from datetime import datetime

# ✅ Blueprint tên 'thoigianmoepa' để khớp với url_for trong HTML
thoigianmoepa_bp = Blueprint('thoigianmoepa', __name__)

def is_allowed():
    """Kiểm tra quyền truy cập"""
    user = session.get('user', '').lower()
    role = session.get('role', '')
    return user in {'admin', 'kimnhung', 'ngocquy'} or role == 'admin'

# ✅ Route chính - khớp với menu sidebar
@thoigianmoepa_bp.route('/thoigianmoepa')
def index():
    """Trang chính quản lý thời gian mở EPA"""
    if not session.get('user'):
        return redirect('/')
    
    if not is_allowed():
        return render_template('403.html'), 403

    conn = get_conn()
    try:
        with conn.cursor() as cursor:
            # Lấy danh sách tài khoản từ bảng tk
            cursor.execute("SELECT ten_tk FROM tk WHERE ten_tk IS NOT NULL AND ten_tk != '' ORDER BY ten_tk")
            tk_rows = cursor.fetchall()
            tk_list = [row['ten_tk'] for row in tk_rows]
            
            # Lấy records hiện có từ bảng thoigianmoepa
            cursor.execute("SELECT * FROM thoigianmoepa ORDER BY ten_tk")
            records_rows = cursor.fetchall()
            
            # Chuyển thành dict để dễ truy cập
            records = {}
            for record in records_rows:
                records[record['ten_tk']] = record
                
    except Exception as e:
        print(f"❌ Lỗi database trong index(): {e}")
        tk_list = []
        records = {}
    finally:
        conn.close()
    
    return render_template('thoigianmoepa.html', tk_list=tk_list, records=records)

# ✅ Route sync_records - khớp với url_for('thoigianmoepa.sync_records') trong HTML
@thoigianmoepa_bp.route('/sync_records', methods=['POST'])
def sync_records():
    """Đồng bộ tài khoản từ bảng tk"""
    if not session.get('user'):
        return redirect('/')
    
    if not is_allowed():
        return render_template('403.html'), 403

    conn = get_conn()
    try:
        with conn.cursor() as cursor:
            # Lấy danh sách tài khoản từ bảng tk
            cursor.execute("SELECT ten_tk, nhom FROM tk WHERE ten_tk IS NOT NULL AND ten_tk != ''")
            tk_rows = cursor.fetchall()
            
            # Lấy tài khoản đã có trong thoigianmoepa
            cursor.execute("SELECT ten_tk FROM thoigianmoepa")
            existing_rows = cursor.fetchall()
            existing_tk = {row['ten_tk'] for row in existing_rows}
            
            # Lấy tài khoản có trong bảng giaovien
            cursor.execute("SELECT ten_tk FROM giaovien WHERE ten_tk IS NOT NULL AND ten_tk != ''")
            giaovien_rows = cursor.fetchall()
            giaovien_tk = {row['ten_tk'] for row in giaovien_rows}
            
            count = 0
            for tk_row in tk_rows:
                ten_tk = tk_row['ten_tk']
                nhom = tk_row.get('nhom', 'user')
                
                # Chỉ thêm nếu: chưa có trong thoigianmoepa VÀ có trong giaovien
                if ten_tk not in existing_tk and ten_tk in giaovien_tk:
                    # Cài đặt quyền mặc định dựa theo nhóm
                    make_epa_gv = 'yes'
                    make_epa_tgv = 'yes' if nhom == 'supervisor' else 'no'
                    make_epa_all = 'yes' if nhom == 'admin' else 'no'
                    
                    cursor.execute("""
                        INSERT INTO thoigianmoepa (ten_tk, start_day, close_day, remark, make_epa_gv, make_epa_tgv, make_epa_all)
                        VALUES (%s, 20, 25, '', %s, %s, %s)
                    """, (ten_tk, make_epa_gv, make_epa_tgv, make_epa_all))
                    count += 1
                    
            conn.commit()
            flash(f"✅ Đã đồng bộ {count} tài khoản mới", "success")
            
    except Exception as e:
        print(f"❌ Lỗi đồng bộ: {e}")
        flash(f"❌ Lỗi đồng bộ: {str(e)}", "danger")
        conn.rollback()
    finally:
        conn.close()
    
    # ✅ Redirect về index() của cùng blueprint
    return redirect(url_for('thoigianmoepa.index'))

# ✅ Route save_record - khớp với url_for('thoigianmoepa.save_record') trong HTML  
@thoigianmoepa_bp.route('/save_record', methods=['POST'])
def save_record():
    """Lưu cài đặt thời gian EPA cho một tài khoản"""
    if not session.get('user'):
        return redirect('/')
    
    if not is_allowed():
        return render_template('403.html'), 403

    # Lấy dữ liệu từ form
    ten_tk = request.form.get('ten_tk')
    record_id = request.form.get('id')  # Có thể None nếu là record mới
    start_day = request.form.get('start_day', type=int)
    close_day = request.form.get('close_day', type=int)
    remark = request.form.get('remark', '').strip()
    make_epa_gv = request.form.get('make_epa_gv', 'no')
    make_epa_tgv = request.form.get('make_epa_tgv', 'no') 
    make_epa_all = request.form.get('make_epa_all', 'no')
    
    # Validation
    if not ten_tk:
        flash("❌ Thiếu tên tài khoản", "danger")
        return redirect(url_for('thoigianmoepa.index'))
    
    if not start_day or not close_day:
        flash("❌ Vui lòng nhập ngày bắt đầu và kết thúc", "danger")
        return redirect(url_for('thoigianmoepa.index'))
    
    if start_day >= close_day:
        flash("❌ Ngày bắt đầu phải nhỏ hơn ngày kết thúc", "danger")
        return redirect(url_for('thoigianmoepa.index'))
    
    if not (1 <= start_day <= 31) or not (1 <= close_day <= 31):
        flash("❌ Ngày phải trong khoảng 1-31", "danger")
        return redirect(url_for('thoigianmoepa.index'))

    conn = get_conn()
    try:
        with conn.cursor() as cursor:
            # Kiểm tra tài khoản có tồn tại trong bảng tk không (thay vì giaovien)
            cursor.execute("SELECT 1 FROM tk WHERE ten_tk = %s", (ten_tk,))
            if not cursor.fetchone():
                flash(f"❌ Tài khoản {ten_tk} không tồn tại", "danger")
                return redirect(url_for('thoigianmoepa.index'))
            
            if record_id:
                # Cập nhật record hiện có
                cursor.execute("""
                    UPDATE thoigianmoepa 
                    SET start_day = %s, close_day = %s, remark = %s,
                        make_epa_gv = %s, make_epa_tgv = %s, make_epa_all = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s AND ten_tk = %s
                """, (start_day, close_day, remark, make_epa_gv, make_epa_tgv, make_epa_all, record_id, ten_tk))
            else:
                # Thêm mới hoặc cập nhật nếu đã tồn tại
                cursor.execute("""
                    INSERT INTO thoigianmoepa (ten_tk, start_day, close_day, remark, make_epa_gv, make_epa_tgv, make_epa_all)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        start_day = VALUES(start_day),
                        close_day = VALUES(close_day),
                        remark = VALUES(remark),
                        make_epa_gv = VALUES(make_epa_gv),
                        make_epa_tgv = VALUES(make_epa_tgv),
                        make_epa_all = VALUES(make_epa_all),
                        updated_at = CURRENT_TIMESTAMP
                """, (ten_tk, start_day, close_day, remark, make_epa_gv, make_epa_tgv, make_epa_all))
            
            conn.commit()
            flash(f"✅ Đã lưu cài đặt cho tài khoản {ten_tk}", "success")
            
    except Exception as e:
        print(f"❌ Lỗi lưu dữ liệu: {e}")
        flash(f"❌ Lỗi lưu dữ liệu: {str(e)}", "danger")
        conn.rollback()
    finally:
        conn.close()
    
    # ✅ Redirect về index() của cùng blueprint
    return redirect(url_for('thoigianmoepa.index'))

# ============================
# API ENDPOINTS
# ============================

@thoigianmoepa_bp.route('/api/assessment-period')
def get_assessment_period():
    """API kiểm tra thời gian đánh giá EPA cho user hiện tại"""
    if not session.get('user'):
        return jsonify({"error": "Not logged in"}), 401
    
    user = session.get('user')
    role = session.get('role', '')
    now = datetime.now()
    current_day = now.day
    current_month = now.month
    current_year = now.year
    
    conn = get_conn()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT start_day, close_day, make_epa_gv, make_epa_tgv, make_epa_all
                FROM thoigianmoepa 
                WHERE ten_tk = %s
            """, (user,))
            
            record = cursor.fetchone()
            
            if not record:
                # Nếu không có cài đặt, dùng mặc định
                start_day = 20
                close_day = 25
                make_epa_gv = "yes"
                make_epa_tgv = "no"
                make_epa_all = "no"
            else:
                start_day = record['start_day']
                close_day = record['close_day']
                make_epa_gv = record['make_epa_gv']
                make_epa_tgv = record['make_epa_tgv']
                make_epa_all = record['make_epa_all']
            
            # Kiểm tra quyền đánh giá
            can_assess = False
            
            if make_epa_all == "yes":
                can_assess = True
            elif role == "user" and make_epa_gv == "yes":
                can_assess = True
            elif role == "supervisor" and make_epa_tgv == "yes":
                can_assess = True
            elif role == "admin":
                can_assess = True
                
            # Kiểm tra thời gian
            is_open = False
            if can_assess and start_day <= current_day <= close_day:
                is_open = True
                
            return jsonify({
                "year": current_year,
                "month": current_month,
                "start_day": start_day,
                "close_day": close_day,
                "current_day": current_day,
                "isOpen": is_open,
                "can_assess": can_assess,
                "make_epa_gv": make_epa_gv,
                "make_epa_tgv": make_epa_tgv,
                "make_epa_all": make_epa_all
            })
            
    except Exception as e:
        print(f"❌ Lỗi API assessment-period: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()
@thoigianmoepa_bp.route('/thoigianmoepa/')
def index_with_slash():
    """Route backup với trailing slash - redirect về route chính"""
    return redirect(url_for('thoigianmoepa.index'))

# ✅ Hoặc thêm strict_slashes=False cho route chính (thay thế route hiện tại):
@thoigianmoepa_bp.route('/thoigianmoepa', strict_slashes=False)
def index():
    """Trang chính quản lý thời gian mở EPA - chấp nhận cả có và không có trailing slash"""
    if not session.get('user'):
        return redirect('/')
    
    if not is_allowed():
        return render_template('403.html'), 403

    conn = get_conn()
    try:
        with conn.cursor() as cursor:
            # Lấy danh sách tài khoản từ bảng tk
            cursor.execute("SELECT ten_tk FROM tk WHERE ten_tk IS NOT NULL AND ten_tk != '' ORDER BY ten_tk")
            tk_rows = cursor.fetchall()
            tk_list = [row['ten_tk'] for row in tk_rows]
            
            # Lấy records hiện có từ bảng thoigianmoepa
            cursor.execute("SELECT * FROM thoigianmoepa ORDER BY ten_tk")
            records_rows = cursor.fetchall()
            
            # Chuyển thành dict để dễ truy cập
            records = {}
            for record in records_rows:
                records[record['ten_tk']] = record
                
    except Exception as e:
        print(f"❌ Lỗi database trong index(): {e}")
        tk_list = []
        records = {}
    finally:
        conn.close()
    
    return render_template('thoigianmoepa.html', tk_list=tk_list, records=records)