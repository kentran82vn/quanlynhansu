from flask import Blueprint, request, jsonify, session
from sqlalchemy import create_engine, text
from config import DB_CONFIG

bangdanhgiaepa_bp = Blueprint('bangdanhgiaepa', __name__, url_prefix='/api/bangdanhgiaepa')

DB_URL = f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}/{DB_CONFIG['db']}"
engine = create_engine(DB_URL)

def get_current_user():
    return session.get('user', '').lower()

@bangdanhgiaepa_bp.route('/history')
def history():
    user = request.args.get('user') or get_current_user()
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT id, ten_tk, year, month, user_total_score, sup_total_score, pri_total_score, pri_comment, created_at 
            FROM tongdiem_epa 
            WHERE ten_tk = :user
            ORDER BY year DESC, month DESC
        """), {'user': user}).mappings().all()
    return jsonify([dict(r) for r in rows])

@bangdanhgiaepa_bp.route('/detail/<int:id>')
def detail(id):
    with engine.connect() as conn:
        info = conn.execute(text("""
            SELECT ten_tk, year, month, pri_total_score, pri_comment
            FROM tongdiem_epa 
            WHERE id = :id
        """), {'id': id}).mappings().first()

        if not info:
            return jsonify({'error': 'Không tìm thấy tongdiem_epa'}), 404

        questions = conn.execute(text("""
            SELECT question AS text, user_score AS score, user_comment AS comment, sup_comment, sup_score
            FROM bangdanhgia
            WHERE ten_tk = :ten_tk AND year = :year AND month = :month
        """), dict(info)).mappings().all()

        supervisor_comment = questions[0]['sup_comment'] if questions else ''

    return jsonify({
        'questions': [dict(q) for q in questions],
        'supervisor_comment': supervisor_comment,
        'pri_total_score': info['pri_total_score'],
        'pri_comment': info['pri_comment']
    }), 200