from flask import Flask, render_template, request, jsonify
import pymysql
from utils.db import get_conn
import threading
import webbrowser

app = Flask(__name__)

def update_data_tables_structure():
    conn = get_conn()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS data_tables_structure (
            id INT AUTO_INCREMENT PRIMARY KEY,
            table_name VARCHAR(255),
            columns TEXT,
            column_count INT,
            row_count INT
        )
    ''')
    cursor.execute("DELETE FROM data_tables_structure")

    cursor.execute("SHOW TABLES")
    tables = [row[f'Tables_in_{conn.db.decode()}'] for row in cursor.fetchall() if row[f'Tables_in_{conn.db.decode()}'] != 'data_tables_structure']

    for table_name in tables:
        cursor.execute(f"SHOW COLUMNS FROM {table_name}")
        cols = cursor.fetchall()
        column_names = ', '.join([col['Field'] for col in cols])
        col_count = len(cols)
        cursor.execute(f"SELECT COUNT(*) AS cnt FROM {table_name}")
        row_count = cursor.fetchone()['cnt']

        cursor.execute('''
            INSERT INTO data_tables_structure (table_name, columns, column_count, row_count)
            VALUES (%s, %s, %s, %s)
        ''', (table_name, column_names, col_count, row_count))

    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_table', methods=['POST'])
def create_table():
    data = request.json
    table_name = data['table_name']
    columns = data['columns']

    col_defs = []
    for col in columns:
        col_type = {
            'text': 'VARCHAR(255)',
            'integer': 'INT',
            'real': 'FLOAT',
            'date': 'DATE'
        }.get(col['type'], 'VARCHAR(255)')
        col_defs.append(f"`{col['name']}` {col_type}")

    sql = f"CREATE TABLE IF NOT EXISTS `{table_name}` (id INT AUTO_INCREMENT PRIMARY KEY, {', '.join(col_defs)})"
    
    conn = get_conn()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute(sql)
    conn.commit()
    conn.close()

    update_data_tables_structure()
    return jsonify({"status": "success"})

@app.route('/check_database', methods=['GET'])
def check_database():
    conn = get_conn()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    cursor.execute("SELECT table_name, column_count, row_count FROM data_tables_structure")
    data = cursor.fetchall()

    # Map về đúng key frontend đang cần
    response = [
        {
            "table": row["table_name"],
            "columns": row["column_count"],
            "rows": row["row_count"]
        }
        for row in data
    ]

    conn.close()
    print(">>> data_tables_structure:", data)
    return jsonify(response)

def open_browser():
    webbrowser.open("http://localhost:5000")

if __name__ == "__main__":
    threading.Timer(1.0, open_browser).start()
    app.run(debug=True, use_reloader=False)