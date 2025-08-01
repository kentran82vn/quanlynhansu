#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.db import get_conn

def verify_login_data():
    """Verify what would be set in session during login"""
    
    users = ['kdien', 'hoangtran']
    
    conn = get_conn()
    try:
        with conn.cursor() as cursor:
            print("=== LOGIN SESSION VERIFICATION ===")
            
            for user in users:
                print(f"\n--- User: {user} ---")
                
                # This is the exact query used in login route
                cursor.execute("SELECT ten_tk, mat_khau, nhom FROM tk WHERE ten_tk = %s", (user,))
                result = cursor.fetchone()
                
                if result:
                    print(f"Login would set:")
                    print(f"  session['user'] = '{result['ten_tk']}'")
                    print(f"  session['role'] = '{result['nhom']}'")
                    
                    # Verify EPA permissions
                    cursor.execute("SELECT make_epa_tgv, make_epa_all FROM thoigianmoepa WHERE ten_tk = %s", (user,))
                    epa = cursor.fetchone()
                    if epa:
                        print(f"  EPA permissions: tgv={epa['make_epa_tgv']}, all={epa['make_epa_all']}")
                        
                        # Check if supervisor with EPA rights
                        if result['nhom'] == 'supervisor' and epa['make_epa_tgv'] == 'yes':
                            print(f"  ✓ Should be able to access /sup-epa-score")
                        else:
                            print(f"  ✗ Cannot access /sup-epa-score")
                    else:
                        print(f"  ✗ No EPA record")
                else:
                    print(f"  ✗ User not found in tk table")
                    
    finally:
        conn.close()

if __name__ == "__main__":
    verify_login_data()