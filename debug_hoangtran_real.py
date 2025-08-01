#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.db import get_conn

def debug_complete_flow():
    """Debug the complete flow for hoangtran"""
    
    user = 'hoangtran'
    conn = get_conn()
    
    try:
        with conn.cursor() as cursor:
            print("=== COMPLETE DEBUG FOR HOANGTRAN ===")
            
            # 1. Check if user exists in all tables
            print("\n1. USER EXISTENCE CHECK:")
            
            tables_to_check = ['tk', 'giaovien', 'thoigianmoepa']
            for table in tables_to_check:
                cursor.execute(f"SELECT * FROM {table} WHERE ten_tk = %s", (user,))
                result = cursor.fetchone()
                if result:
                    print(f"FOUND in {table}: {dict(result)}")
                else:
                    print(f"NOT found in {table}")
            
            # 2. Check session data that would be set during login
            print("\n2. LOGIN SESSION DATA:")
            cursor.execute("SELECT ten_tk, mat_khau, nhom FROM tk WHERE ten_tk = %s", (user,))
            tk_data = cursor.fetchone()
            if tk_data:
                print(f"Session would be:")
                print(f"  session['user'] = '{tk_data['ten_tk']}'")
                print(f"  session['role'] = '{tk_data['nhom']}'")
            
            # 3. Test the exact logic from sup-epa-score route
            print("\n3. SUP-EPA-SCORE ROUTE LOGIC TEST:")
            
            if not tk_data:
                print("❌ FAIL: User not found in tk table")
                return
                
            role = tk_data['nhom']
            print(f"User: {user}, Role: {role}")
            
            # Step 1: Check EPA permissions
            cursor.execute("""
                SELECT make_epa_tgv, make_epa_all FROM thoigianmoepa WHERE ten_tk = %s
            """, (user,))
            epa_record = cursor.fetchone()
            
            print(f"EPA record: {dict(epa_record) if epa_record else 'None'}")
            
            # Step 2: Permission check
            can_supervise = False
            reason = "Unknown"
            
            if epa_record:
                if epa_record['make_epa_all'] == 'yes':
                    can_supervise = True
                    reason = "make_epa_all = yes"
                elif role == 'supervisor' and epa_record['make_epa_tgv'] == 'yes':
                    can_supervise = True
                    reason = "role=supervisor AND make_epa_tgv=yes"
                else:
                    reason = f"role={role}, make_epa_tgv={epa_record['make_epa_tgv']}, make_epa_all={epa_record['make_epa_all']}"
            else:
                reason = "No EPA record found"
            
            if role == 'admin':
                can_supervise = True
                reason = "role = admin"
            
            print(f"Can supervise: {can_supervise}")
            print(f"Reason: {reason}")
            
            if not can_supervise:
                print("ROUTE WOULD RETURN 403: Ban khong co quyen xem trang nay")
                return
            
            # Step 3: Get chuc_vu and determine target
            cursor.execute("SELECT chuc_vu FROM giaovien WHERE ten_tk=%s", (user,))
            gv_row = cursor.fetchone()
            if not gv_row:
                print("ROUTE WOULD RETURN 404: Khong tim thay thong tin giao vien")
                return
                
            chuc_vu = gv_row['chuc_vu']
            print(f"chuc_vu: {chuc_vu}")
            
            # Step 4: Determine target_chuc_vu
            if chuc_vu.startswith("TGV"):
                suffix = chuc_vu[3:]
                target_chuc_vu = f"GV{suffix}"
                logic = "TGV -> GV same team"
            elif chuc_vu.startswith("GV"):
                suffix = chuc_vu[2:]
                target_chuc_vu = f"GV{suffix}"
                logic = "GV -> GV same team"
            else:
                print(f"ROUTE WOULD RETURN 403: Khong xac dinh duoc to cho chuc vu '{chuc_vu}'")
                return
                
            print(f"Target chuc_vu: {target_chuc_vu} ({logic})")
            
            # Step 5: Test query
            from datetime import datetime
            now = datetime.now()
            current_month = now.month
            current_year = now.year
            
            cursor.execute("""
                SELECT g.ten_tk, g.ho_va_ten, g.chuc_vu,
                       t.user_total_score,
                       t.sup_total_score AS sup_score,
                       CASE WHEN t.id IS NOT NULL THEN 'Đã đánh giá' ELSE 'Chưa đánh giá' END AS trang_thai
                FROM giaovien g
                LEFT JOIN tongdiem_epa t
                  ON g.ten_tk = t.ten_tk
                 AND t.year = %s
                 AND t.month = %s
                WHERE g.chuc_vu = %s
            """, (current_year, current_month, target_chuc_vu))
            
            members = cursor.fetchall()
            print(f"Found {len(members)} team members to supervise:")
            for member in members:
                print(f"  - {member['ten_tk']} ({member['chuc_vu']}) - {member['trang_thai']}")
            
            print(f"\nROUTE SHOULD WORK: User can access /sup-epa-score and see {len(members)} members")
            
            # 4. Check for potential issues
            print("\n4. POTENTIAL ISSUES CHECK:")
            
            # Check if route exists
            print("Route should be: /sup-epa-score")
            
            # Check if template exists
            template_path = "D:\\quanlynhansu\\templates\\sup_epa_score.html"
            if os.path.exists(template_path):
                print(f"Template exists: {template_path}")
            else:
                print(f"Template missing: {template_path}")
            
            # Check navigation link
            index_path = "D:\\quanlynhansu\\templates\\index.html"
            if os.path.exists(index_path):
                with open(index_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if '/data_epa' in content:
                        print("Navigation link found: /data_epa")
                    else:
                        print("Navigation link missing in index.html")
                        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    debug_complete_flow()