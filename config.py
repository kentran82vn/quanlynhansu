
import os, pymysql

def _e(keys, default=None):
    for k in keys:
        v = os.environ.get(k)
        if v: return v
    return default
DB_CONFIG = {
        "host":      _e(["MYSQL_HOST", "MYSQLHOST"], "shuttle.proxy.rlwy.net"),
        "port":      int(_e(["MYSQL_PORT", "MYSQLPORT"], 36286)),
        "user":      _e(["MYSQL_USER", "MYSQLUSER"], "root"),
        "password":  _e(["MYSQL_PASSWORD", "MYSQLPASSWORD", "MYSQL_ROOT_PASSWORD"], "kZwsdDWOrUWwXDamELJNjAAoUnzCtROz"),
        "db":        _e(["MYSQL_DATABASE"], "railway"),
        "cursorclass": pymysql.cursors.DictCursor
        }