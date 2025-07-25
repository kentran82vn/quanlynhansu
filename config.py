import os, pymysql

def _e(keys, default=None):
    for k in keys:
        v = os.environ.get(k)
        if v: return v
    return default

DB_CONFIG = {
    # Dùng host local thay vì shuttle.proxy...
    "host":      _e(["MYSQL_HOST", "MYSQLHOST"], "127.0.0.1"),
    # Cổng MySQL mặc định
    "port":      int(_e(["MYSQL_PORT", "MYSQLPORT"], 3306)),
    # User local
    "user":      _e(["MYSQL_USER", "MYSQLUSER"], "root"),
    # Mật khẩu local
    "password":  _e(["MYSQL_PASSWORD", "MYSQLPASSWORD", "MYSQL_ROOT_PASSWORD"], "173915Snow"),
    # Tên database local
    "db":        _e(["MYSQL_DATABASE"], "quanlytruonghoc_app"),
    "cursorclass": pymysql.cursors.DictCursor
}
