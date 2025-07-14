from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session, flash
from sqlalchemy import create_engine, text
from config import DB_CONFIG

thoigianmoepa_bp = Blueprint('thoigianmoepa', __name__, url_prefix='/thoigianmoepa')

DB_URL = f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}/{DB_CONFIG['db']}"
engine = create_engine(DB_URL)

ALLOWED_USERS = {'admin', 'kimnhung', 'ngocquy'}

def is_allowed():
    return session.get('user', '').lower() in ALLOWED_USERS

@thoigianmoepa_bp.route('/')
def index():
    if not is_allowed():
        return render_template('403.html'), 403

    with engine.connect() as conn:
        tk_list = [row[0] for row in conn.execute(text("SELECT ten_tk FROM tk")).fetchall()]
        rs = conn.execute(text("SELECT * FROM thoigianmoepa")).fetchall()
        records = {r.ten_tk: r for r in rs}

    return render_template(
        'thoigianmoepa.html',
        tk_list=tk_list,
        records=records,
        css_url=url_for('static', filename='styles.css')
    )

@thoigianmoepa_bp.route('/api/list')
def list_records():
    if not is_allowed():
        return jsonify({'error': 'unauthorized'}), 403

    with engine.connect() as conn:
        rs = conn.execute(text("SELECT * FROM thoigianmoepa")).mappings().all()
        return jsonify(list(rs))

@thoigianmoepa_bp.route('/api/save', methods=['POST'])
def save_record():
    if not is_allowed():
        return jsonify({'error': 'unauthorized'}), 403

    data = request.form
    record_id = data.get('id')
    start_day = data.get('start_day')
    close_day = data.get('close_day')
    remark = data.get('remark')
    ten_tk = data.get('ten_tk', session.get('user'))
    make_epa_gv = data.get('make_epa_gv', 'yes')
    make_epa_tgv = data.get('make_epa_tgv', 'no')
    make_epa_all = data.get('make_epa_all', 'no')

    with engine.connect() as conn:
        if record_id:
            conn.execute(text("""
                UPDATE thoigianmoepa SET start_day=:start_day, close_day=:close_day, remark=:remark,
                    make_epa_gv=:make_epa_gv, make_epa_tgv=:make_epa_tgv, make_epa_all=:make_epa_all
                WHERE id=:id
            """), {
                'start_day': start_day,
                'close_day': close_day,
                'remark': remark,
                'id': record_id,
                'make_epa_gv': make_epa_gv,
                'make_epa_tgv': make_epa_tgv,
                'make_epa_all': make_epa_all
            })
            flash(f"Cập nhật thành công cho {ten_tk}", "success")
        else:
            conn.execute(text("""
                INSERT INTO thoigianmoepa (ten_tk, start_day, close_day, remark, make_epa_gv, make_epa_tgv, make_epa_all)
                VALUES (:ten_tk, :start_day, :close_day, :remark, :make_epa_gv, :make_epa_tgv, :make_epa_all)
            """), {
                'ten_tk': ten_tk,
                'start_day': start_day,
                'close_day': close_day,
                'remark': remark,
                'make_epa_gv': make_epa_gv,
                'make_epa_tgv': make_epa_tgv,
                'make_epa_all': make_epa_all
            })
            flash(f"Tạo mới bản ghi cho {ten_tk}", "success")

        conn.commit()
    return redirect(url_for('thoigianmoepa.index'))

@thoigianmoepa_bp.route('/sync', methods=['POST'])
def sync_records():
    if not is_allowed():
        return jsonify({'error': 'unauthorized'}), 403

    with engine.connect() as conn:
        tk_list = [row[0] for row in conn.execute(text("SELECT ten_tk FROM tk")).fetchall()]
        existing_tk = {row[0] for row in conn.execute(text("SELECT ten_tk FROM thoigianmoepa")).fetchall()}

        missing_tk = [tk for tk in tk_list if tk not in existing_tk]

        for ten_tk in missing_tk:
            conn.execute(text("""
                INSERT INTO thoigianmoepa (ten_tk, start_day, close_day, remark, make_epa_gv, make_epa_tgv, make_epa_all)
                VALUES (:ten_tk, 1, 2, '', 'no', 'no', 'no')
            """), {'ten_tk': ten_tk})

        conn.commit()

    flash(f"Đồng bộ thành công {len(missing_tk)} tài khoản", "success")
    return redirect(url_for('thoigianmoepa.index'))
