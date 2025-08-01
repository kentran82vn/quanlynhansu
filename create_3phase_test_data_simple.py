#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.db import get_conn
from datetime import datetime

def create_3phase_test_data():
    """Create sample test data for 3-phase EPA system"""
    
    print("=== CREATE 3-PHASE EPA TEST DATA ===")
    
    conn = get_conn()
    try:
        with conn.cursor() as cursor:
            
            # 1. Setup admin accounts with full permissions
            print("\n1. SETUP ADMIN ACCOUNTS:")
            # Get admin accounts that exist in both tk and giaovien tables
            cursor.execute("""
                SELECT tk.ten_tk FROM tk 
                INNER JOIN giaovien ON tk.ten_tk = giaovien.ten_tk 
                WHERE tk.ten_tk IN ('admin', 'kimnhung', 'ngocquy')
            """)
            admin_accounts = [row['ten_tk'] for row in cursor.fetchall()]
            print(f"   Found admin accounts: {admin_accounts}")
            
            for admin in admin_accounts:
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
                print(f"   OK {admin}: Full admin permissions")
            
            # 2. Create realistic test scenario
            print("\n2. CREATE TEST SCENARIO:")
            
            now = datetime.now()
            current_day = now.day
            
            # Setup 3 phases based on current day for testing
            if current_day <= 20:
                # Before any phase, set phase 1 to start early
                phase1_start, phase1_end = current_day, current_day + 2
                phase2_start, phase2_end = current_day + 3, current_day + 4  
                phase3_start, phase3_end = current_day + 5, current_day + 7
                test_note = f"Test scenario - Phase 1 is open ({current_day}-{current_day + 2})"
            elif current_day <= 25:
                # In phase 1
                phase1_start, phase1_end = 20, 25
                phase2_start, phase2_end = 26, 27
                phase3_start, phase3_end = 28, 30
                test_note = "Test scenario - Phase 1 (Self Assessment) is open"
            elif current_day <= 27:
                # In phase 2
                phase1_start, phase1_end = 20, 25
                phase2_start, phase2_end = 26, 27
                phase3_start, phase3_end = 28, 30
                test_note = "Test scenario - Phase 2 (Team Leader Assessment) is open"
            else:
                # In phase 3 or after
                phase1_start, phase1_end = 20, 25
                phase2_start, phase2_end = 26, 27
                phase3_start, phase3_end = 28, 30
                test_note = "Test scenario - Phase 3 (Principal Assessment) or ended"
            
            # Get user list from tk table (only users who exist in giaovien table)
            cursor.execute("""
                SELECT tk.ten_tk, tk.nhom FROM tk 
                INNER JOIN giaovien ON tk.ten_tk = giaovien.ten_tk 
                WHERE tk.ten_tk NOT IN ('admin', 'kimnhung', 'ngocquy')
            """)
            users = cursor.fetchall()
            
            print(f"   Time setup: P1({phase1_start}-{phase1_end}), P2({phase2_start}-{phase2_end}), P3({phase3_start}-{phase3_end})")
            print(f"   Note: {test_note}")
            print(f"   Found {len(users)} user accounts to setup")
            
            for user in users:
                ten_tk = user['ten_tk']
                nhom = user['nhom']
                
                # Assign permissions based on role
                if nhom == 'supervisor':
                    make_epa_gv = 'yes'  # TGV can self-assess
                    make_epa_tgv = 'yes'  # TGV can assess team members
                    make_epa_all = 'no'   # TGV doesn't have admin rights
                    remark = f"TGV - Team leader permissions"
                elif nhom == 'user':
                    make_epa_gv = 'yes'   # GV can self-assess
                    make_epa_tgv = 'no'   # GV cannot assess others
                    make_epa_all = 'no'   # GV doesn't have admin rights
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
                
                print(f"   OK {ten_tk} ({nhom}): GV={make_epa_gv}, TGV={make_epa_tgv}, ALL={make_epa_all}")
            
            conn.commit()
            
            # 3. Display results
            print("\n3. VERIFY SETTINGS:")
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
            print("   Sample settings (first 10 records):")
            for result in results:
                print(f"   {result['ten_tk']}: P1={result['phase1_time']}, P2={result['phase2_time']}, P3={result['phase3_time']}")
                print(f"      Permissions: GV={result['make_epa_gv']}, TGV={result['make_epa_tgv']}, ALL={result['make_epa_all']}")
                print(f"      Note: {result['remark']}")
                print()
            
            # 4. Statistics
            cursor.execute("SELECT COUNT(*) as total FROM thoigianmoepa")
            total = cursor.fetchone()['total']
            
            cursor.execute("SELECT COUNT(*) as admin_count FROM thoigianmoepa WHERE make_epa_all = 'yes'")
            admin_count = cursor.fetchone()['admin_count']
            
            cursor.execute("SELECT COUNT(*) as tgv_count FROM thoigianmoepa WHERE make_epa_tgv = 'yes'")
            tgv_count = cursor.fetchone()['tgv_count']
            
            cursor.execute("SELECT COUNT(*) as gv_count FROM thoigianmoepa WHERE make_epa_gv = 'yes'")
            gv_count = cursor.fetchone()['gv_count']
            
            print("4. STATISTICS:")
            print(f"   Total accounts: {total}")
            print(f"   Admin (full rights): {admin_count}")
            print(f"   TGV (team leaders): {tgv_count}")  
            print(f"   GV (self assessment): {gv_count}")
            
            print(f"\nSUCCESS: Test data created!")
            print(f"Current day: {current_day}")
            print(f"Note: {test_note}")
            print("\n3-PHASE SYSTEM READY FOR TESTING!")
            
    except Exception as e:
        print(f"ERROR: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    create_3phase_test_data()