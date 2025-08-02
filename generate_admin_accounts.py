#!/usr/bin/env python3
from werkzeug.security import generate_password_hash
import pymysql
from datetime import date

# Tạo password hash
password_hash = generate_password_hash("abc000")
print(f"Password hash for 'abc000': {password_hash}")

# Kết nối database
conn = pymysql.connect(
    host='shuttle.proxy.rlwy.net',
    port=36286,
    user='root',
    password='kZwsdDWOrUWwXDamELJNjAAoUnzCtROz',
    database='railway',
    cursorclass=pymysql.cursors.DictCursor
)

try:
    with conn.cursor() as cursor:
        # Xóa tài khoản cũ nếu có
        cursor.execute("DELETE FROM tk WHERE ten_tk IN ('administrator', 'kimnhung')")
        
        # Tạo tài khoản mới với password hash
        admin_hash = generate_password_hash("abc000")
        kim_hash = generate_password_hash("abc000")
        
        cursor.execute("""
            INSERT INTO tk (ten_tk, nhom, mat_khau, ngay_tao, nguoi_tao, ho_va_ten) VALUES 
            (%s, %s, %s, %s, %s, %s)
        """, ('administrator', 'admin', admin_hash, date.today(), 'system', 'Administrator'))
        
        cursor.execute("""
            INSERT INTO tk (ten_tk, nhom, mat_khau, ngay_tao, nguoi_tao, ho_va_ten) VALUES 
            (%s, %s, %s, %s, %s, %s)
        """, ('kimnhung', 'admin', kim_hash, date.today(), 'system', 'Kim Nhung'))
    
    conn.commit()
    print("✅ Đã tạo thành công 2 tài khoản admin với password hash")
    
    # Kiểm tra
    with conn.cursor() as cursor:
        cursor.execute("SELECT ten_tk, nhom, ho_va_ten FROM tk WHERE nhom = 'admin'")
        admins = cursor.fetchall()
        print("\n📋 Danh sách admin:")
        for admin in admins:
            print(f"  - {admin['ten_tk']} ({admin['ho_va_ten']}) - Nhóm: {admin['nhom']}")

finally:
    conn.close()