
import pymysql
from config import DB_CONFIG

def get_conn():
    #print("Đang kết nối database...")

    # Kết nối không chỉ định DB để tạo nếu chưa có
    conn = pymysql.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"]
    )

    with conn.cursor() as cursor:
        cursor.execute("CREATE DATABASE IF NOT EXISTS quanlytruonghoc_app")
        #print("Đã kiểm tra hoặc tạo DB 'quanlytruonghoc_app'")

    conn.close()

    # Kết nối lại với DB vừa tạo
    return pymysql.connect(**DB_CONFIG)

