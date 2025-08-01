#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.db import get_conn

def check_user_permissions():
    conn = get_conn()
    try:
        with conn.cursor() as cursor:
            # Check giaovien table
            cursor.execute("SELECT ten_tk, ho_va_ten, chuc_vu FROM giaovien WHERE ten_tk='hoangtran'")
            giaovien = cursor.fetchone()
            print("=== BANG GIAOVIEN ===")
            if giaovien:
                print(f"ten_tk: {giaovien['ten_tk']}")
                print(f"ho_va_ten: [HIDDEN]")
                print(f"chuc_vu: {giaovien['chuc_vu']}")
            else:
                print("Khong tim thay trong bang giaovien")
            
            # Check tk table  
            cursor.execute("SELECT ten_tk, nhom FROM tk WHERE ten_tk='hoangtran'")
            tk = cursor.fetchone()
            print("\n=== BANG TK ===")
            if tk:
                print(f"ten_tk: {tk['ten_tk']}")
                print(f"nhom (role): {tk['nhom']}")
            else:
                print("Khong tim thay trong bang tk")
                
            # Check thoigianmoepa table
            cursor.execute("SELECT * FROM thoigianmoepa WHERE ten_tk='hoangtran'")
            epa_time = cursor.fetchone()
            print("\n=== BANG THOIGIANMOEPA ===")
            if epa_time:
                print(f"ten_tk: {epa_time['ten_tk']}")
                print(f"start_day: {epa_time['start_day']}")
                print(f"close_day: {epa_time['close_day']}")
                print(f"make_epa_gv: {epa_time['make_epa_gv']}")
                print(f"make_epa_tgv: {epa_time['make_epa_tgv']}")  
                print(f"make_epa_all: {epa_time['make_epa_all']}")
            else:
                print("Khong tim thay trong bang thoigianmoepa")
                
            print("\n=== PHAN TICH ===")
            if giaovien and not giaovien['chuc_vu'].startswith('TGV'):
                print(f"VAN DE: chuc_vu = '{giaovien['chuc_vu']}' khong bat dau bang 'TGV'")
                print("   Route /sup-epa-score yeu cau chuc_vu phai bat dau bang 'TGV'")
                print("   Nhung he thong phan quyen EPA dua tren bang thoigianmoepa")
                
    finally:
        conn.close()

if __name__ == "__main__":
    check_user_permissions()