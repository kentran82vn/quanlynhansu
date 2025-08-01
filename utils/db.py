
import pymysql
from config import DB_CONFIG

def get_conn():
    #print("Dang ket noi database...")

    # Ket noi khong chi dinh DB de tao neu chua co
    conn = pymysql.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"]
    )

    with conn.cursor() as cursor:
        cursor.execute("CREATE DATABASE IF NOT EXISTS quanlytruonghoc_app")
        #print("Da kiem tra hoac tao DB 'quanlytruonghoc_app'")

    conn.close()

    # Ket noi lai voi DB vua tao
    return pymysql.connect(**DB_CONFIG)

