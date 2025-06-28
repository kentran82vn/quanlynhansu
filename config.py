import os, pymysql

DB_CONFIG = {
    "host":     os.environ.get("MYSQL_HOST",    "localhost"),
    "port":     int(os.environ.get("MYSQL_PORT", 33060)),
    "user":     os.environ.get("MYSQL_USER",    "root"),
    "password": os.environ.get("MYSQL_PASSWORD","steven2906"),
    "db":       os.environ.get("MYSQL_DATABASE","quanlytruonghoc_app"),
    "cursorclass": pymysql.cursors.DictCursor
}
