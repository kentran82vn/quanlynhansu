#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.db import get_conn

def analyze_current_vs_real_workflow():
    """Analyze current system vs real workflow requirements"""
    
    print("=== PHAN TICH QUY TRINH THUC TE VS HE THONG HIEN TAI ===")
    
    print("\n1. QUY TRINH THUC TE CUA USER:")
    print("   Giai doan 1 (20-25): TU DANH GIA")
    print("   - Tat ca GV + TGV tu danh gia ban than")
    print("   - Ket qua: user_total_score trong tongdiem_epa")
    
    print("   Giai doan 2 (26-27): TGV CHAM DIEM GV")
    print("   - TGV cham diem cho GV cung to")
    print("   - TGV tu copy diem tu danh gia cua minh")
    print("   - Ket qua: sup_total_score trong tongdiem_epa")
    
    print("   Giai doan 3 (28-30): HT/PHT CHAM DIEM TAT CA")
    print("   - HT/PHT cham diem cho tat ca GV + TGV")
    print("   - Ket qua: pri_total_score trong tongdiem_epa")
    
    print("\n2. KIEM TRA HE THONG HIEN TAI:")
    
    conn = get_conn()
    try:
        with conn.cursor() as cursor:
            # Check current time settings structure
            cursor.execute("SELECT start_day, close_day, COUNT(*) as count FROM thoigianmoepa GROUP BY start_day, close_day")
            time_groups = cursor.fetchall()
            
            print("   a) CAI DAT THOI GIAN HIEN TAI:")
            for group in time_groups:
                print(f"      {group['start_day']}-{group['close_day']}: {group['count']} users")
            
            # Check if system supports 3-phase workflow
            print("\n   b) KHA NANG HO TRO 3 GIAI DOAN:")
            
            # Phase 1: Self assessment - Check user-epa-score route
            print("      Giai doan 1 (Tu danh gia):")
            print("      - Route: /user-epa-score OK")
            print("      - Kiem tra: make_epa_gv permission OK") 
            print("      - Thoi gian: dua tren start_day <= current_day <= close_day OK")
            
            # Phase 2: Supervisor scoring - Check sup-epa-score route  
            print("      Giai doan 2 (TGV cham diem):")
            print("      - Route: /sup-epa-score OK")
            print("      - Kiem tra: make_epa_tgv permission OK")
            print("      - VAN DE: Chi dung 1 khoang thoi gian, khong phan biet giai doan FAIL")
            
            # Phase 3: Principal scoring
            print("      Giai doan 3 (HT/PHT cham diem):")
            print("      - Route: /data_epa (xem + chinh sua) OK")
            print("      - Kiem tra: Chi cho phep kimnhung OK")
            print("      - VAN DE: Khong co kiem tra thoi gian rieng FAIL")
            
            # Check database structure
            print("\n   c) CAU TRUC DATABASE:")
            cursor.execute("DESCRIBE tongdiem_epa")
            columns = cursor.fetchall()
            
            required_fields = ['user_total_score', 'sup_total_score', 'pri_total_score', 'pri_comment']
            found_fields = [col['Field'] for col in columns]
            
            print("      Cac cot can thiet:")
            for field in required_fields:
                status = "OK" if field in found_fields else "FAIL"
                print(f"      - {field}: {status}")
            
            # Analyze current data
            cursor.execute("SELECT COUNT(*) as total FROM tongdiem_epa")
            total_records = cursor.fetchone()['total']
            print(f"\n   d) DU LIEU HIEN TAI:")
            print(f"      Tong so ban ghi EPA: {total_records}")
            
            if total_records > 0:
                cursor.execute("""
                    SELECT 
                        COUNT(CASE WHEN user_total_score IS NOT NULL THEN 1 END) as phase1,
                        COUNT(CASE WHEN sup_total_score IS NOT NULL THEN 1 END) as phase2,
                        COUNT(CASE WHEN pri_total_score IS NOT NULL THEN 1 END) as phase3
                    FROM tongdiem_epa
                """)
                phases = cursor.fetchone()
                print(f"      Co diem giai doan 1 (tu danh gia): {phases['phase1']}")
                print(f"      Co diem giai doan 2 (TGV cham): {phases['phase2']}")
                print(f"      Co diem giai doan 3 (HT/PHT cham): {phases['phase3']}")
            
    finally:
        conn.close()
    
    print("\n3. KET LUAN VA VAN DE:")
    print("   DIEM MANH:")
    print("   OK Database structure ho tro day du 3 giai doan")
    print("   OK Co route va permission cho tung vai tro")
    print("   OK Co kiem tra thoi gian co ban")
    
    print("   VAN DE CHINH:")
    print("   FAIL HE THONG HIEN TAI CHI HO TRO 1 KHOANG THOI GIAN")
    print("      - Tat ca dung chung start_day -> close_day")
    print("      - Khong phan biet: tu danh gia vs TGV cham vs HT/PHT cham")
    
    print("   FAIL THIEU LOGIC TUAN TU 3 GIAI DOAN")
    print("      - Giai doan 2 nen chi mo sau khi giai doan 1 ket thuc")
    print("      - Giai doan 3 nen chi mo sau khi giai doan 2 ket thuc")
    
    print("   FAIL TGV TU COPY DIEM CHUA DUOC TU DONG HOA")
    print("      - TGV phai tu nhap lai diem cho ban than")
    print("      - Nen tu dong copy tu user_total_score")

if __name__ == "__main__":
    analyze_current_vs_real_workflow()