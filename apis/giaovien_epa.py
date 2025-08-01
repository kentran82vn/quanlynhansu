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
    
    # Get days in current month for validation
    days_in_current_month = monthrange(year, month)[1]
    
    conn = get_conn()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        cursor.execute(
            """
            SELECT phase1_start, phase1_end, phase2_start, phase2_end, phase3_start, phase3_end,
                   make_epa_gv, make_epa_tgv, start_day, close_day
            FROM thoigianmoepa
            WHERE ten_tk = %s
            """,
            (ten_tk,)
        )
        record = cursor.fetchone()
        if not record:
            return {
                'is_open': False,
                'start_day': 0,
                'close_day': 0,
                'year': year,
                'month': month,
                'current_phase': None,
                'message': 'Khong tim thay cai dat thoi gian'
            }
        
        # Determine user type and appropriate phase
        is_tgv = record.get('make_epa_tgv') == 'yes'
        
        # Adjust phase end dates if they exceed days in current month
        phase1_start = record['phase1_start'] or 20
        phase1_end = min(record['phase1_end'] or 25, days_in_current_month)
        phase2_start = record['phase2_start'] or 26  
        phase2_end = min(record['phase2_end'] or 27, days_in_current_month)
        phase3_start = record['phase3_start'] or 28
        phase3_end = min(record['phase3_end'] or 30, days_in_current_month)
        
        # For teachers (GV): only Phase 1 matters
        # For supervisors (TGV): Phase 1 (self) + Phase 2 (supervise others) 
        phase1_open = phase1_start <= day <= phase1_end
        phase2_open = phase2_start <= day <= phase2_end if phase2_start and phase2_end else False
        phase3_open = phase3_start <= day <= phase3_end if phase3_start and phase3_end else False
        
        # Determine if user can assess themselves
        if is_tgv:
            # TGV can self-assess in Phase 1 or Phase 2
            is_open = phase1_open or phase2_open
            if phase1_open:
                current_phase = 'Phase 1 (Tu danh gia)'
                start_day = phase1_start
                close_day = phase1_end
            elif phase2_open:
                current_phase = 'Phase 2 (Tu danh gia TGV)'
                start_day = phase2_start
                close_day = phase2_end
            else:
                current_phase = 'Phase 3 (Chi HT/PHT danh gia)'
                start_day = phase3_start
                close_day = phase3_end
        else:
            # Regular teachers: only Phase 1
            is_open = phase1_open
            if phase1_open:
                current_phase = 'Phase 1 (Tu danh gia)'
            elif phase2_open:
                current_phase = 'Phase 2 (TGV danh gia)'
            elif phase3_open:
                current_phase = 'Phase 3 (HT/PHT danh gia)'
            else:
                current_phase = 'Ngoai thoi gian danh gia'
            
            start_day = phase1_start
            close_day = phase1_end
        
        return {
            'is_open': is_open,
            'start_day': start_day,
            'close_day': close_day,
            'year': year,
            'month': month,
            'current_phase': current_phase,
            'message': f'Hien tai: {current_phase}'
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
        cursor.execute("SELECT id, question, translate, score as max_score FROM cauhoi_epa")
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
        if not user or user['nhom'] not in ['user', 'supervisor', 'admin']:
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

# AUTO-COPY điểm cho TGV: Copy điểm giai đoạn 1 (tự đánh giá) thành điểm giai đoạn 2
def auto_copy_tgv_scores(ten_tk, year, month):
    """
    Khi TGV hoàn thành giai đoạn 1 (tự đánh giá), tự động copy điểm đó làm điểm giai đoạn 2
    Theo quy trình thực tế: TGV không cần đánh giá bản thân 2 lần
    """
    logging.info(f'🔄 Bắt đầu auto-copy điểm cho TGV {ten_tk}')
    
    conn = get_conn()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        # Lấy tất cả điểm tự đánh giá (user_score) của TGV
        cursor.execute(
            """
            SELECT id, question, translate, user_score, user_comment
            FROM bangdanhgia 
            WHERE ten_tk = %s AND year = %s AND month = %s 
              AND user_score IS NOT NULL
            """,
            (ten_tk, year, month)
        )
        self_assessments = cursor.fetchall()
        
        if not self_assessments:
            logging.warning(f'⚠️ TGV {ten_tk} chưa có điểm tự đánh giá để copy')
            return
        
        copy_count = 0
        for assessment in self_assessments:
            # Copy user_score -> sup_score và user_comment -> sup_comment
            # CHỈ copy nếu sup_score chưa có (tránh ghi đè)
            cursor.execute(
                """
                UPDATE bangdanhgia 
                SET sup_score = %s, sup_comment = %s
                WHERE id = %s AND (sup_score IS NULL OR sup_score = 0)
                """,
                (assessment['user_score'], assessment['user_comment'], assessment['id'])
            )
            
            if cursor.rowcount > 0:  # Có record được update
                copy_count += 1
                logging.debug(f'📋 Copy câu hỏi "{assessment["question"][:30]}...": {assessment["user_score"]} điểm')
        
        conn.commit()
        logging.info(f'✅ Auto-copy hoàn thành cho TGV {ten_tk}: {copy_count}/{len(self_assessments)} câu hỏi')
        
    except Exception as e:
        logging.error(f'❌ Lỗi auto-copy cho TGV {ten_tk}: {e}')
        conn.rollback()
        raise e
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
        'month': date_info['month'],
        'current_phase': date_info.get('current_phase'),
        'message': date_info.get('message')
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
    logging.debug(f'Month value being used: {month}')
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
        # Thay vì DELETE + INSERT, sử dụng UPSERT để bảo toàn dữ liệu chưa thay đổi
        logging.debug(f'Cập nhật kết quả đánh giá cho ten_tk={ten_tk}, year={year}, month={month}')
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
            
            # Lấy thông tin câu hỏi bao gồm điểm tối đa
            cursor.execute(
                "SELECT question, translate, score as max_score FROM cauhoi_epa WHERE id = %s",
                (question_id,)
            )
            question = cursor.fetchone()
            if not question:
                logging.warning(f'ID câu hỏi không hợp lệ: {question_id}')
                continue
            
            # Validate điểm không được vượt quá điểm tối đa của câu hỏi
            max_score = question.get('max_score', 30)  # Fallback to 30 if no score defined
            if user_score > max_score:
                logging.warning(f'Điểm vượt quá giới hạn: question_id={question_id}, user_score={user_score}, max_score={max_score}')
                return jsonify({'message': f'Câu hỏi {question_id}: Điểm tối đa chỉ được {max_score}, không thể chấm {user_score} điểm'}), 400
            
            if user_score < 0:
                logging.warning(f'Điểm âm không hợp lệ: question_id={question_id}, user_score={user_score}')
                return jsonify({'message': f'Câu hỏi {question_id}: Điểm không thể âm'}), 400
            
            # Kiểm tra xem đã có record chưa, nếu có thì UPDATE, chưa có thì INSERT
            cursor.execute(
                """
                SELECT id FROM bangdanhgia 
                WHERE ten_tk = %s AND year = %s AND month = %s AND question = %s
                """,
                (ten_tk, year, month, question['question'])
            )
            existing_record = cursor.fetchone()
            
            if existing_record:
                # Cập nhật record đã có, chỉ cập nhật các field không null/empty
                update_fields = ["user_score = %s", "user_comment = %s", "created_at = NOW()"]
                update_values = [user_score, user_comment]
                
                if sup_score is not None:
                    update_fields.append("sup_score = %s")
                    update_values.append(sup_score)
                
                if sup_comment:
                    update_fields.append("sup_comment = %s") 
                    update_values.append(sup_comment)
                
                update_values.append(existing_record['id'])
                
                cursor.execute(
                    f"UPDATE bangdanhgia SET {', '.join(update_fields)} WHERE id = %s",
                    update_values
                )
                logging.debug(f'Cập nhật câu hỏi ID {question_id} cho ten_tk={ten_tk}')
            else:
                # Tạo record mới
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
                logging.debug(f'Tạo mới câu hỏi ID {question_id} cho ten_tk={ten_tk}')
        conn.commit()
        logging.debug(f'Đã lưu kết quả đánh giá cho ten_tk={ten_tk}')
        
        # 🚀 AUTO-COPY cho TGV: Nếu là supervisor và đang trong giai đoạn 1, tự động copy làm điểm giai đoạn 2
        if role == 'supervisor':
            try:
                auto_copy_tgv_scores(ten_tk, year, month)
                logging.info(f'✅ Đã auto-copy điểm giai đoạn 1 -> 2 cho TGV {ten_tk}')
            except Exception as auto_copy_error:
                logging.error(f'❌ Lỗi auto-copy cho TGV {ten_tk}: {auto_copy_error}')
        
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