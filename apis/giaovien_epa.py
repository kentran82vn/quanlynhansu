from datetime import datetime
from flask import Blueprint, request, jsonify, session, redirect, render_template
import pymysql
import logging
from calendar import monthrange
from utils.db import get_conn

# Cấu hình logging với UTF-8
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('server.log', encoding='utf-8'),  # Thêm encoding='utf-8'
        logging.StreamHandler()
    ]
)

giaovien_epa_bp = Blueprint('giaovien_epa', __name__)

# Hàm lấy thông tin ngày và thời gian đánh giá từ bảng thoigianmoepa sql
def check_epa_period_for_user(ten_tk):
    now = datetime.now()
    day = now.day
    year = now.year
    month = now.month
    conn = get_conn()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        cursor.execute(
            """
            SELECT start_day, close_day
            FROM thoigianmoepa
            WHERE ten_tk = %s
            """,
            (ten_tk,)
        )
        record = cursor.fetchone()
        if record:
            start_day = record['start_day'] or 0
            close_day = record['close_day'] or 0
            is_open = start_day <= day <= close_day
        else:
            start_day = 0
            close_day = 0
            is_open = False
        return {
            'is_open': is_open,
            'start_day': start_day,
            'close_day': close_day,
            'year': year,
            'month': month
        }
    finally:
        cursor.close()
        conn.close()

# Tải câu hỏi EPA từ cauhoi_epa
def load_questions():
    logging.info('Đang tải câu hỏi EPA')
    conn = get_conn()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        cursor.execute("SELECT id, question, translate FROM cauhoi_epa")
        rows = cursor.fetchall()
        logging.debug(f'Câu hỏi đã tải: {rows}')
        return rows
    except Exception as e:
        logging.error(f'Lỗi khi tải câu hỏi: {e}')
        return []
    finally:
        cursor.close()
        conn.close()

def is_valid_user(ten_tk):
    logging.info(f'Đang kiểm tra vai trò cho ten_tk={ten_tk}')
    conn = get_conn()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        cursor.execute("SELECT nhom FROM tk WHERE ten_tk = %s", (ten_tk,))
        user = cursor.fetchone()
        if not user or user['nhom'] not in ['user', 'supervisor']:
            logging.warning(f'Vai trò không hợp lệ: ten_tk={ten_tk}, role={user.get("nhom") if user else None}')
            return False
        logging.debug(f'Người dùng hợp lệ: ten_tk={ten_tk}, role={user["nhom"]}')
        return True
    except Exception as e:
        logging.error(f'Lỗi khi kiểm tra vai trò: {e}')
        return False
    finally:
        cursor.close()
        conn.close()

# Cập nhật bảng tongdiem_epa
def update_tongdiem_epa(ten_tk, year, month):
    logging.info(f'Đang cập nhật tongdiem_epa cho ten_tk={ten_tk}, year={year}, month={month}')
    conn = get_conn()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        cursor.execute(
            """
            SELECT COALESCE(SUM(user_score), 0) as user_total_score, COALESCE(SUM(sup_score), 0) as sup_total_score
            FROM bangdanhgia
            WHERE ten_tk = %s AND year = %s AND month = %s
            """,
            (ten_tk, year, month)
        )
        totals = cursor.fetchone()
        user_total_score = totals['user_total_score']
        sup_total_score = totals['sup_total_score']

        cursor.execute(
            """
            SELECT id FROM tongdiem_epa
            WHERE ten_tk = %s AND year = %s AND month = %s
            """,
            (ten_tk, year, month)
        )
        existing = cursor.fetchone()

        if existing:
            cursor.execute(
                """
                UPDATE tongdiem_epa
                SET user_total_score = %s, sup_total_score = %s
                WHERE ten_tk = %s AND year = %s AND month = %s
                """,
                (user_total_score, sup_total_score, ten_tk, year, month)
            )
        else:
            cursor.execute(
                """
                INSERT INTO tongdiem_epa (ten_tk, year, month, user_total_score, sup_total_score)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (ten_tk, year, month, user_total_score, sup_total_score)
            )
        conn.commit()
        logging.debug(f'Đã cập nhật tongdiem_epa: user_total_score={user_total_score}, sup_total_score={sup_total_score}')
    except Exception as e:
        logging.error(f'Lỗi khi cập nhật tongdiem_epa: {e}')
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

# Hiển thị giao diện tự đánh giá
@giaovien_epa_bp.route('/user-epa-score')
def user_epa_score():
    role = session.get('role')
    user = session.get('user')
    logging.info(f'Đang truy cập user_epa_score cho user={user}, role={role}')
    if role == 'admin':
        logging.warning(f'Truy cập bị từ chối cho admin user={user}')
        return redirect('/')
    if not user:
        logging.error('Không có người dùng trong session')
        return redirect('/login')
    return render_template('giaovien_epa.html', user=user, role=role)

# API 1: Kiểm tra thời gian đánh giá
@giaovien_epa_bp.route('/api/assessment-period', methods=['GET'])
def assessment_period():
    logging.info('Đang kiểm tra thời gian đánh giá')
    ten_tk = session.get('user')
    if not ten_tk:
        return jsonify({'isOpen': False, 'message': 'Không có người dùng'}), 401
    date_info = check_epa_period_for_user(ten_tk)
    response = {
        'isOpen': date_info['is_open'],
        'start_day': date_info['start_day'],
        'close_day': date_info['close_day'],
        'year': date_info['year'],
        'month': date_info['month']
    }
    logging.debug(f'Kết quả kiểm tra thời gian: {response}')
    return jsonify(response)

# API 2: Lấy danh sách câu hỏi EPA
@giaovien_epa_bp.route('/api/epa-questions', methods=['GET'])
def epa_questions():
    logging.info('Đang lấy danh sách câu hỏi EPA')
    questions = load_questions()
    if not questions:
        logging.error('Không lấy được câu hỏi')
        return jsonify({'message': 'Không thể lấy câu hỏi'}), 500
    return jsonify({'questions': questions})

# API 3: Lấy kết quả đánh giá trước đó
@giaovien_epa_bp.route('/api/last-assessment', methods=['GET'])
def last_assessment():
    ten_tk = request.args.get("ten_tk") or session.get("user")
    logging.info(f'Đang lấy kết quả đánh giá trước cho ten_tk={ten_tk}')
    if not ten_tk:
        logging.error('Không có người dùng trong session')
        return jsonify({'message': 'Không được phép'}), 401
    if not is_valid_user(ten_tk):
        logging.warning(f'Truy cập không được phép: ten_tk={ten_tk}')
        return jsonify({'message': 'Không được phép'}), 403

    # Lấy year và month từ query parameters (truyền từ frontend)
    year = request.args.get('year')
    month = request.args.get('month')
    print('Giá trị tháng đang sử dụng', month)
    if not year or not month:
        now = datetime.now()
        year = now.year
        month = now.month

    conn = get_conn()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        # Lấy danh sách câu hỏi đánh giá từ bangdanhgia
        cursor.execute(
            """
            SELECT id, question, translate, user_score, sup_score, year, month, user_comment, sup_comment
            FROM bangdanhgia
            WHERE ten_tk = %s AND year = %s AND month = %s
            """,
            (ten_tk, year, month)
        )
        assessments = cursor.fetchall()

        # Lấy tổng điểm từ tongdiem_epa
        cursor.execute(
            """
            SELECT year, month, user_total_score, sup_total_score, pri_total_score, pri_comment
            FROM tongdiem_epa
            WHERE ten_tk = %s AND year = %s AND month = %s
            """,
            (ten_tk, year, month)
        )
        total_score = cursor.fetchone()

        logging.debug(f'Đã lấy kết quả đánh giá: {assessments}')
        logging.debug(f'Tổng điểm: {total_score}')

        return jsonify({
            'assessments': assessments,
            'total_score': total_score if total_score else {
                'year': int(year),
                'month': int(month),
                'user_total_score': 0,
                'sup_total_score': 0,
                'pri_total_score': None,
                'pri_comment': None
            }
        })
    except Exception as e:
        logging.error(f'Lỗi khi lấy kết quả đánh giá: {e}')
        return jsonify({'message': 'Không thể lấy kết quả đánh giá'}), 500
    finally:
        cursor.close()
        conn.close()

# API 5: Mở bảng đánh giá cũ
@giaovien_epa_bp.route("/epa-preview")
def epa_preview():
    year = request.args.get("year")
    month = request.args.get("month")
    ten_tk = request.args.get("ten_tk")
    return render_template("epa_preview.html", year=year, month=month, ten_tk=ten_tk)

@giaovien_epa_bp.route("/api/epa-available-years")
def get_epa_years():
    conn = get_conn()
    cursor = conn.cursor(pymysql.cursors.DictCursor)  # ✅ PHẢI là DictCursor
    cursor.execute("SELECT DISTINCT year FROM tongdiem_epa ORDER BY year DESC")
    rows = cursor.fetchall()
    years = [row["year"] for row in rows]  # ✅ lấy theo key 'year'
    cursor.close()
    conn.close()
    return jsonify({"years": years})

@giaovien_epa_bp.route("/api/epa-available-months")
def get_epa_months():
    year = request.args.get("year")
    if not year:
        return jsonify({"months": []})
    conn = get_conn()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT DISTINCT month FROM tongdiem_epa WHERE year = %s ORDER BY month", (year,))
    months = [row["month"] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return jsonify({"months": months})

# API 4: Gửi kết quả đánh giá
@giaovien_epa_bp.route('/api/submit-assessment', methods=['POST'])
def submit_assessment():
    ten_tk = session.get('user')
    role = session.get('role')
    logging.info(f'Đang gửi kết quả đánh giá cho ten_tk={ten_tk}, role={role}')
    if not ten_tk:
        logging.error('Không có người dùng trong session')
        return jsonify({'message': 'Không được phép'}), 401
    if not is_valid_user(ten_tk):
        logging.warning(f'Truy cập không được phép: ten_tk={ten_tk}')
        return jsonify({'message': 'Không được phép'}), 403
    data = request.get_json()
    scores = data.get('scores', [])
    year = data.get('year')
    month = data.get('month')
    if not scores:
        logging.warning('Không có điểm số nào được cung cấp')
        return jsonify({'message': 'Không có điểm số nào được cung cấp'}), 400
    # Kiểm tra thời gian hiện tại
    current_date = datetime.now()
    current_year = current_date.year
    current_month = current_date.month
    if year != current_year or month != current_month:
        logging.warning(f'Kỳ đánh giá không khớp với thời gian hiện tại: Current year={current_year}, month={current_month}, Request year={year}, month={month}')
        return jsonify({'message': 'Chỉ có thể gửi đánh giá cho tháng hiện tại'}), 400
    date_info = check_epa_period_for_user(ten_tk)
    if date_info['year'] != year or date_info['month'] != month:
        logging.warning(f'Kỳ đánh giá không khớp: DB year={date_info["year"]}, month={date_info["month"]}, Request year={year}, month={month}')
        return jsonify({'message': 'Kỳ đánh giá không khớp'}), 400
    if not date_info['is_open']:
        logging.warning(f'Thời gian đánh giá đã đóng: hôm nay không nằm trong khoảng {date_info["start_day"]} - {date_info["close_day"]}')
        return jsonify({'message': 'Thời gian đánh giá đã đóng'}), 403
    conn = get_conn()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        cursor.execute(
            "SELECT ho_va_ten, chuc_vu, ngay_sinh FROM giaovien WHERE ten_tk = %s",
            (ten_tk,)
        )
        user_details = cursor.fetchone()
        if not user_details:
            logging.warning(f'Không tìm thấy hồ sơ giáo viên cho ten_tk={ten_tk}')
            return jsonify({'message': 'Hồ sơ người dùng không tìm thấy'}), 404
        ho_va_ten = user_details['ho_va_ten']
        chuc_vu = user_details['chuc_vu']
        ngay_sinh = user_details['ngay_sinh']
        cursor.execute(
            """
            DELETE FROM bangdanhgia
            WHERE ten_tk = %s AND year = %s AND month = %s
            """,
            (ten_tk, year, month)
        )
        logging.debug(f'Đã xóa kết quả đánh giá cũ cho ten_tk={ten_tk}, year={year}, month={month}')
        for score_entry in scores:
            question_id = score_entry.get('questionId')
            user_score = score_entry.get('score')
            user_comment = score_entry.get('user_comment', '')
            # For supervisor, set sup_score = user_score and sup_comment = user_comment
            if role == 'supervisor':
                sup_score = user_score
                sup_comment = user_comment
            else:
                # For other roles (e.g., user), use provided sup_score and sup_comment
                sup_score = score_entry.get('sup_score') if role in ['admin'] else None
                sup_comment = score_entry.get('sup_comment', '') if role in ['admin'] else ''
            if not question_id or user_score is None:
                logging.warning(f'Mục điểm không hợp lệ: {score_entry}')
                continue
            cursor.execute(
                "SELECT question, translate FROM cauhoi_epa WHERE id = %s",
                (question_id,)
            )
            question = cursor.fetchone()
            if not question:
                logging.warning(f'ID câu hỏi không hợp lệ: {question_id}')
                continue
            cursor.execute(
                """
                INSERT INTO bangdanhgia (
                    ten_tk, ho_va_ten, chuc_vu, ngay_sinh, year, month,
                    question, translate, user_score, sup_score, user_comment, sup_comment, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                """,
                (
                    ten_tk, ho_va_ten, chuc_vu, ngay_sinh,
                    year, month,
                    question['question'], question['translate'],
                    user_score, sup_score, user_comment, sup_comment
                )
            )
        conn.commit()
        logging.debug(f'Đã lưu kết quả đánh giá cho ten_tk={ten_tk}')
        update_tongdiem_epa(ten_tk, year, month)
        cursor.execute(
            """
            INSERT INTO logs (user_ten_tk, target_staff_id, target_table, action, created_at)
            VALUES (%s, %s, %s, %s, NOW())
            """,
            (ten_tk, ten_tk, 'bangdanhgia', 'Gửi kết quả tự đánh giá EPA')
        )
        conn.commit()
        logging.info(f'Đã ghi log hành động cho ten_tk={ten_tk}')
        return jsonify({'message': f'Đã lưu {len(scores)} câu trả lời cho {ten_tk}'})
    except Exception as e:
        conn.rollback()
        logging.error(f'Lỗi khi gửi kết quả đánh giá: {e}')
        return jsonify({'message': 'Không thể gửi kết quả đánh giá'}), 500
    finally:
        cursor.close()
        conn.close()