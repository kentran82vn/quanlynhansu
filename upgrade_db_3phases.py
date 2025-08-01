#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.db import get_conn

def upgrade_database_3phases():
    """Upgrade database to support 3-phase EPA workflow"""
    
    conn = get_conn()
    try:
        with conn.cursor() as cursor:
            print("=== UPGRADING DATABASE FOR 3-PHASE EPA SYSTEM ===")
            
            # 1. Check if columns already exist
            cursor.execute("DESCRIBE thoigianmoepa")
            columns = cursor.fetchall()
            existing_cols = [col['Field'] for col in columns]
            
            new_columns = ['phase1_start', 'phase1_end', 'phase2_start', 'phase2_end', 'phase3_start', 'phase3_end']
            missing_cols = [col for col in new_columns if col not in existing_cols]
            
            if missing_cols:
                print(f"Adding {len(missing_cols)} new columns...")
                
                # 2. Add new columns
                for col in missing_cols:
                    phase_num = col.split('_')[0][-1]  # Extract phase number
                    stage = col.split('_')[1]  # start or end
                    comment = f"Day {stage} giai doan {phase_num}"
                    
                    cursor.execute(f"""
                        ALTER TABLE thoigianmoepa 
                        ADD COLUMN {col} INT DEFAULT NULL COMMENT '{comment}'
                    """)
                    print(f"  Added column: {col}")
                
                conn.commit()
                print("New columns added successfully!")
            else:
                print("All columns already exist, skipping column creation.")
            
            # 3. Migrate existing data
            cursor.execute("SELECT COUNT(*) as count FROM thoigianmoepa WHERE phase1_start IS NULL")
            unmigrated = cursor.fetchone()['count']
            
            if unmigrated > 0:
                print(f"Migrating {unmigrated} records to new format...")
                
                cursor.execute("""
                    UPDATE thoigianmoepa SET
                        phase1_start = 20,
                        phase1_end = 25,
                        phase2_start = 26,
                        phase2_end = 27,
                        phase3_start = 28,
                        phase3_end = 30
                    WHERE phase1_start IS NULL
                """)
                
                conn.commit()
                print("Data migration completed!")
            else:
                print("Data already migrated, skipping migration.")
            
            # 4. Verify results
            cursor.execute("""
                SELECT 
                    ten_tk,
                    CONCAT(phase1_start, '-', phase1_end) as phase1_time,
                    CONCAT(phase2_start, '-', phase2_end) as phase2_time,
                    CONCAT(phase3_start, '-', phase3_end) as phase3_time,
                    make_epa_gv, make_epa_tgv, make_epa_all
                FROM thoigianmoepa 
                LIMIT 5
            """)
            
            results = cursor.fetchall()
            print("\n=== VERIFICATION - Sample records ===")
            for result in results:
                print(f"{result['ten_tk']}: P1={result['phase1_time']}, P2={result['phase2_time']}, P3={result['phase3_time']}")
                print(f"  Permissions: GV={result['make_epa_gv']}, TGV={result['make_epa_tgv']}, ALL={result['make_epa_all']}")
            
            # 5. Show statistics
            cursor.execute("SELECT COUNT(*) as total FROM thoigianmoepa")
            total = cursor.fetchone()['total']
            print(f"\nTotal records: {total}")
            print("Database upgrade completed successfully!")
            
    except Exception as e:
        print(f"ERROR during upgrade: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    upgrade_database_3phases()