#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.db import get_conn

def analyze_time_setting_rules():
    """Analyze the current time setting rules and data structure"""
    
    conn = get_conn()
    try:
        with conn.cursor() as cursor:
            print("=== PHAN TICH QUY TAC SET NGAY EPA ===")
            
            # 1. Check who has admin rights
            print("\n1. QUYEN ADMIN SET NGAY:")
            print("   Code logic: user in {'admin', 'kimnhung', 'ngocquy'} or role == 'admin'")
            
            cursor.execute("SELECT ten_tk, nhom FROM tk WHERE ten_tk IN ('admin', 'kimnhung', 'ngocquy') OR nhom = 'admin'")
            admins = cursor.fetchall()
            print("   Cac tai khoan co quyen set ngay:")
            for admin in admins:
                print(f"     - {admin['ten_tk']} (role: {admin['nhom']})")
            
            # 2. Check current time settings structure
            print("\n2. CAU TRUC DU LIEU THOI GIAN:")
            cursor.execute("SELECT COUNT(*) as total FROM thoigianmoepa")
            total = cursor.fetchone()['total']
            print(f"   Tong so ban ghi trong thoigianmoepa: {total}")
            
            # 3. Sample current settings
            cursor.execute("SELECT * FROM thoigianmoepa LIMIT 5")
            samples = cursor.fetchall()
            print("   Mau du lieu:")
            for sample in samples:
                print(f"     {sample['ten_tk']}: {sample['start_day']}-{sample['close_day']} (GV:{sample['make_epa_gv']}, TGV:{sample['make_epa_tgv']}, ALL:{sample['make_epa_all']})")
            
            # 4. Check if settings are per-user or global
            cursor.execute("SELECT start_day, close_day, COUNT(*) as count FROM thoigianmoepa GROUP BY start_day, close_day")
            time_groups = cursor.fetchall()
            print("\n3. PHAN TICH THOI GIAN HIEN TAI:")
            if len(time_groups) == 1:
                print("   TAT CA USER DUNG CHUNG THOI GIAN:")
                for group in time_groups:
                    print(f"     Ngay {group['start_day']}-{group['close_day']}: {group['count']} users")
            else:
                print("   CAC USER CO THOI GIAN KHAC NHAU:")
                for group in time_groups:
                    print(f"     Ngay {group['start_day']}-{group['close_day']}: {group['count']} users")
            
            # 5. Check permission distribution
            print("\n4. PHAN BO QUYEN EPA:")
            cursor.execute("""
                SELECT 
                    SUM(CASE WHEN make_epa_gv = 'yes' THEN 1 ELSE 0 END) as gv_count,
                    SUM(CASE WHEN make_epa_tgv = 'yes' THEN 1 ELSE 0 END) as tgv_count,
                    SUM(CASE WHEN make_epa_all = 'yes' THEN 1 ELSE 0 END) as all_count,
                    COUNT(*) as total
                FROM thoigianmoepa
            """)
            perm_stats = cursor.fetchone()
            print(f"   Co quyen lam GV (make_epa_gv=yes): {perm_stats['gv_count']}/{perm_stats['total']}")
            print(f"   Co quyen lam TGV (make_epa_tgv=yes): {perm_stats['tgv_count']}/{perm_stats['total']}")
            print(f"   Co quyen lam ALL (make_epa_all=yes): {perm_stats['all_count']}/{perm_stats['total']}")
            
            # 6. Analyze the rules
            print("\n5. QUY TAC HIEN TAI:")
            print("   a) QUYEN SET NGAY:")
            print("      - Chi 3 tai khoan: admin, kimnhung, ngocquy")
            print("      - Hoac bat ky ai co role='admin'")
            print("      - Co the set ngay cho tung user rieng biet")
            print("      - Co the set quyen (make_epa_gv, make_epa_tgv, make_epa_all) cho tung user")
            
            print("   b) CAU TRUC DU LIEU:")
            print("      - Moi user co 1 dong rieng trong bang thoigianmoepa")
            print("      - start_day, close_day: ngay bat dau va ket thuc trong thang")
            print("      - make_epa_gv: quyen tu danh gia (user role)")
            print("      - make_epa_tgv: quyen cham diem to vien (supervisor role)")
            print("      - make_epa_all: quyen toan quyen (override tat ca)")
            
            print("   c) TINH LINH HOAT:")
            if len(time_groups) == 1:
                print("      - Hien tai: TAT CA dung chung thoi gian")
                print("      - Co the thay doi thanh: tung user co thoi gian rieng")
            else:
                print("      - Hien tai: tung user co the co thoi gian khac nhau")
                print("      - Linh hoat toi da!")
                
            print("   d) KET LUAN:")
            print("      - KHONG co han che theo to")
            print("      - Admin co the set bat ky ai, bat ky thoi gian nao") 
            print("      - Co the tao nhieu kich ban: tung to khac thoi gian, hoac chung thoi gian")
            
    finally:
        conn.close()

if __name__ == "__main__":
    analyze_time_setting_rules()