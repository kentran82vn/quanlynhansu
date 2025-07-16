import pymysql
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "steven2906",  # đúng mật khẩu MySQL
    "db": "quanlytruonghoc_app",  # ← sửa 'database' → 'db'
    "cursorclass": pymysql.cursors.DictCursor
}
