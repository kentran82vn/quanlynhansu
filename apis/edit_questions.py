from flask import Blueprint, render_template, request, jsonify, session, redirect
from utils.db import get_conn

# Blueprint cho module này
edit_questions_bp = Blueprint('edit_questions', __name__)

# Load tất cả câu hỏi từ database
def load_questions():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id, question, translate FROM epa_questions")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    questions = []
    for row in rows:
        questions.append({
            'id': row['id'],               # lấy theo tên
            'question': row['question'],   # lấy theo tên
            'translate': row['translate']  # lấy theo tên
        })

    return questions

# API render giao diện chỉnh sửa câu hỏi
@edit_questions_bp.route('/admin/questions', methods=['GET'])
def edit_questions_page():
    if session.get('role') != 'admin':
        return redirect('/')

    questions = load_questions()
    return render_template('edit_questions.html', questions=questions)

# API lưu thay đổi câu hỏi
@edit_questions_bp.route('/admin/questions', methods=['POST'])
def save_questions():
    if session.get('role') != 'admin':
        return jsonify({"success": False, "message": "Permission denied"}), 403

    data = request.get_json()
    try:
        conn = get_conn()
        cursor = conn.cursor()

        # Xóa hết bảng cũ rồi insert lại
        cursor.execute("DELETE FROM epa_questions")
        for q in data:
            cursor.execute(
                "INSERT INTO epa_questions (question, translate) VALUES (%s, %s)",
                (q['question'], q['translate'])
            )

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"success": True, "message": "Questions updated successfully."})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
