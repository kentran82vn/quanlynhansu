import os, pymysql

DB_CONFIG = {
    "host":     os.environ.get("MYSQL_HOST",    "mysql.railway.internal"),
    "port":     int(os.environ.get("MYSQL_PORT", 3306)),
    "user":     os.environ.get("MYSQL_USER",    "root"),
    "password": os.environ.get("MYSQL_PASSWORD","steven2906"),
    "db":       os.environ.get("MYSQL_DATABASE","quanlytruonghoc_app"),
    "cursorclass": pymysql.cursors.DictCursor
}
