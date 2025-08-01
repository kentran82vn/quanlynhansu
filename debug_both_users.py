#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.db import get_conn

def debug_user(user_name):
    """Debug a specific user's access"""
    
    conn = get_conn()
    try:
        with conn.cursor() as cursor:
            print(f"\n=== DEBUGGING USER: {user_name.upper()} ===")
            
            # Step 1: Get role from tk table
            cursor.execute("SELECT ten_tk, nhom FROM tk WHERE ten_tk = %s", (user_name,))
            tk_data = cursor.fetchone()
            if not tk_data:
                print("FAIL: User not found in tk table")
                return
            
            role = tk_data['nhom']
            print(f"Role from tk table: {role}")
            
            # Step 2: Get EPA permissions
            cursor.execute("SELECT make_epa_tgv, make_epa_all FROM thoigianmoepa WHERE ten_tk = %s", (user_name,))
            epa_record = cursor.fetchone()
            
            if not epa_record:
                print("FAIL: No EPA record found in thoigianmoepa")
                return
                
            print(f"EPA permissions: make_epa_tgv={epa_record['make_epa_tgv']}, make_epa_all={epa_record['make_epa_all']}")
            
            # Step 3: Permission check (exact logic from route)
            can_supervise = False
            reason = ""
            
            if epa_record['make_epa_all'] == 'yes':
                can_supervise = True
                reason = "make_epa_all = yes"
            elif role == 'supervisor' and epa_record['make_epa_tgv'] == 'yes':
                can_supervise = True  
                reason = "role=supervisor AND make_epa_tgv=yes"
            elif role == 'admin':
                can_supervise = True
                reason = "role = admin"
            else:
                reason = f"DENIED: role={role}, make_epa_tgv={epa_record['make_epa_tgv']}, make_epa_all={epa_record['make_epa_all']}"
                
            print(f"Permission check: {can_supervise} - {reason}")
            
            if not can_supervise:
                print("ROUTE WOULD RETURN 403 HERE")
                return
                
            # Step 4: Get chuc_vu from giaovien
            cursor.execute("SELECT chuc_vu FROM giaovien WHERE ten_tk = %s", (user_name,))
            gv_row = cursor.fetchone()
            if not gv_row:
                print("FAIL: User not found in giaovien table")
                return
                
            chuc_vu = gv_row['chuc_vu']
            print(f"chuc_vu from giaovien: {chuc_vu}")
            
            # Step 5: Target determination logic
            if chuc_vu.startswith("TGV"):
                suffix = chuc_vu[3:]
                target_chuc_vu = f"GV{suffix}"
                logic_path = "TGV branch"
            elif chuc_vu.startswith("GV"):
                suffix = chuc_vu[2:]
                target_chuc_vu = f"GV{suffix}"
                logic_path = "GV branch"
            else:
                print(f"ROUTE WOULD RETURN 403: Khong xac dinh duoc to cho chuc vu '{chuc_vu}'")
                return
                
            print(f"Target logic: {logic_path} -> target_chuc_vu = {target_chuc_vu}")
            
            # Step 6: Check how many members they can supervise
            cursor.execute("""
                SELECT ten_tk, chuc_vu FROM giaovien 
                WHERE chuc_vu = %s
                ORDER BY ten_tk
            """, (target_chuc_vu,))
            
            members = cursor.fetchall()
            print(f"Can supervise {len(members)} members:")
            for member in members:
                print(f"  - {member['ten_tk']} ({member['chuc_vu']})")
                
            print(f"CONCLUSION: User {user_name} SHOULD be able to access /sup-epa-score")
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

def main():
    print("=== COMPARATIVE DEBUG FOR BOTH USERS ===")
    debug_user('kdien')     # Working user
    debug_user('hoangtran') # Broken user

if __name__ == "__main__":
    main()