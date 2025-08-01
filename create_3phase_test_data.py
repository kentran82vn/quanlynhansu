#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.db import get_conn
from datetime import datetime

def create_3phase_test_data():
    """Tao du lieu mau test cho he thong 3 giai doan EPA"""
    
    print("=== TAO DU LIEU MAU CHO HE THONG 3 GIAI DOAN EPA ===")
    
    conn = get_conn()
    try:
        with conn.cursor() as cursor:
            
            # 1. Dam bao co admin accounts voi full permissions
            print("\n1. THIET LAP ADMIN ACCOUNTS:")
            admin_accounts = ['admin', 'kimnhung', 'ngocquy']
            
            for admin in admin_accounts:
                # Update/Insert vao thoigianmoepa voi quyen day du
                cursor.execute("""
                    INSERT INTO thoigianmoepa (ten_tk, phase1_start, phase1_end, phase2_start, phase2_end, 
                                             phase3_start, phase3_end, start_day, close_day, 
                                             make_epa_gv, make_epa_tgv, make_epa_all, remark)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        phase1_start = VALUES(phase1_start),
                        phase1_end = VALUES(phase1_end),
                        phase2_start = VALUES(phase2_start),
                        phase2_end = VALUES(phase2_end),
                        phase3_start = VALUES(phase3_start),
                        phase3_end = VALUES(phase3_end),
                        start_day = VALUES(start_day),
                        close_day = VALUES(close_day),
                        make_epa_all = VALUES(make_epa_all),
                        remark = VALUES(remark)
                """, (admin, 20, 25, 26, 27, 28, 30, 20, 25, 'yes', 'yes', 'yes', f'Admin account - Full permissions'))
                print(f"   OK {admin}: Toan quyen setup thoi gian")
            
            # 2. Tao scenario test thuc te
            print("\n2. TAO SCENARIO TEST:")
            
            # Scenario: Tháng hiện tại, 3 giai đoạn tuần tự
            now = datetime.now()
            current_day = now.day
            
            # Thiết lập 3 giai đoạn dựa trên ngày hiện tại để có thể test
            if current_day <= 20:
                # Chưa đến giai đoạn nào, set để giai đoạn 1 bắt đầu sớm
                phase1_start, phase1_end = current_day, current_day + 2
                phase2_start, phase2_end = current_day + 3, current_day + 4  
                phase3_start, phase3_end = current_day + 5, current_day + 7
                test_note = f"Test scenario - Giai đoạn 1 đang mở ({current_day}-{current_day + 2})"
            elif current_day <= 25:
                # Trong giai đoạn 1
                phase1_start, phase1_end = 20, 25
                phase2_start, phase2_end = 26, 27
                phase3_start, phase3_end = 28, 30
                test_note = "Test scenario - Giai đoạn 1 (Tự đánh giá) đang mở"
            elif current_day <= 27:
                # Trong giai đoạn 2
                phase1_start, phase1_end = 20, 25
                phase2_start, phase2_end = 26, 27
                phase3_start, phase3_end = 28, 30
                test_note = "Test scenario - Giai đoạn 2 (TGV chấm điểm) đang mở"
            else:
                # Trong giai đoạn 3 hoặc sau đó
                phase1_start, phase1_end = 20, 25
                phase2_start, phase2_end = 26, 27
                phase3_start, phase3_end = 28, 30
                test_note = "Test scenario - Giai đoạn 3 (HT/PHT chấm điểm) hoặc đã kết thúc"
            
            # Lấy danh sách users từ bảng tk
            cursor.execute("SELECT ten_tk, nhom FROM tk WHERE ten_tk NOT IN ('admin', 'kimnhung', 'ngocquy')")
            users = cursor.fetchall()
            
            print(f"   Thiết lập thời gian: P1({phase1_start}-{phase1_end}), P2({phase2_start}-{phase2_end}), P3({phase3_start}-{phase3_end})")
            print(f"   Ghi chú: {test_note}")
            print(f"   Tìm thấy {len(users)} user accounts để setup")
            
            for user in users:
                ten_tk = user['ten_tk']
                nhom = user['nhom']
                
                # Phân quyền dựa trên nhóm
                if nhom == 'supervisor':
                    make_epa_gv = 'yes'  # TGV được tự đánh giá
                    make_epa_tgv = 'yes'  # TGV được chấm điểm GV
                    make_epa_all = 'no'   # TGV không có quyền admin
                    remark = f"TGV - Team leader permissions"
                elif nhom == 'user':
                    make_epa_gv = 'yes'   # GV được tự đánh giá
                    make_epa_tgv = 'no'   # GV không được chấm điểm người khác
                    make_epa_all = 'no'   # GV không có quyền admin
                    remark = f"GV - Self assessment only"
                else:
                    make_epa_gv = 'yes'
                    make_epa_tgv = 'no'
                    make_epa_all = 'no'
                    remark = f"User - Role: {nhom}"
                
                cursor.execute("""
                    INSERT INTO thoigianmoepa (ten_tk, phase1_start, phase1_end, phase2_start, phase2_end, 
                                             phase3_start, phase3_end, start_day, close_day, 
                                             make_epa_gv, make_epa_tgv, make_epa_all, remark)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        phase1_start = VALUES(phase1_start),
                        phase1_end = VALUES(phase1_end),
                        phase2_start = VALUES(phase2_start),
                        phase2_end = VALUES(phase2_end),
                        phase3_start = VALUES(phase3_start),
                        phase3_end = VALUES(phase3_end),
                        start_day = VALUES(start_day),
                        close_day = VALUES(close_day),
                        make_epa_gv = VALUES(make_epa_gv),
                        make_epa_tgv = VALUES(make_epa_tgv),
                        make_epa_all = VALUES(make_epa_all),
                        remark = VALUES(remark)
                """, (ten_tk, phase1_start, phase1_end, phase2_start, phase2_end, phase3_start, phase3_end,
                      phase1_start, phase1_end, make_epa_gv, make_epa_tgv, make_epa_all, remark))
                
                print(f"   ✅ {ten_tk} ({nhom}): GV={make_epa_gv}, TGV={make_epa_tgv}, ALL={make_epa_all}")
            
            conn.commit()
            
            # 3. Hiển thị kết quả
            print("\n3. XÁC NHẬN CÀI ĐẶT:")
            cursor.execute("""
                SELECT 
                    ten_tk,
                    CONCAT(phase1_start, '-', phase1_end) as phase1_time,
                    CONCAT(phase2_start, '-', phase2_end) as phase2_time,
                    CONCAT(phase3_start, '-', phase3_end) as phase3_time,
                    make_epa_gv, make_epa_tgv, make_epa_all,
                    remark
                FROM thoigianmoepa 
                ORDER BY 
                    CASE 
                        WHEN ten_tk IN ('admin', 'kimnhung', 'ngocquy') THEN 1 
                        ELSE 2 
                    END,
                    ten_tk
                LIMIT 10
            """)
            
            results = cursor.fetchall()
            print("   Sample cài đặt (10 records đầu):")
            for result in results:
                print(f"   {result['ten_tk']}: P1={result['phase1_time']}, P2={result['phase2_time']}, P3={result['phase3_time']}")
                print(f"      Quyền: GV={result['make_epa_gv']}, TGV={result['make_epa_tgv']}, ALL={result['make_epa_all']}")
                print(f"      Ghi chú: {result['remark']}")
                print()
            
            # 4. Thống kê tổng quan
            cursor.execute("SELECT COUNT(*) as total FROM thoigianmoepa")
            total = cursor.fetchone()['total']
            
            cursor.execute("SELECT COUNT(*) as admin_count FROM thoigianmoepa WHERE make_epa_all = 'yes'")
            admin_count = cursor.fetchone()['admin_count']
            
            cursor.execute("SELECT COUNT(*) as tgv_count FROM thoigianmoepa WHERE make_epa_tgv = 'yes'")
            tgv_count = cursor.fetchone()['tgv_count']
            
            cursor.execute("SELECT COUNT(*) as gv_count FROM thoigianmoepa WHERE make_epa_gv = 'yes'")
            gv_count = cursor.fetchone()['gv_count']
            
            print("4. THỐNG KÊ TỔNG QUAN:")
            print(f"   📊 Tổng số accounts: {total}")
            print(f"   👑 Admin (full rights): {admin_count}")
            print(f"   👥 TGV (team leaders): {tgv_count}")  
            print(f"   👤 GV (self assessment): {gv_count}")
            
            print(f"\n✅ TẠO DỮ LIỆU MẪU HOÀN THÀNH!")
            print(f"📅 Ngày hiện tại: {current_day}")
            print(f"📝 {test_note}")
            print("\n🚀 HỆ THỐNG 3 GIAI ĐOẠN ĐÃ SẴN SÀNG TEST!")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    create_3phase_test_data()