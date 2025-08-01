#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.db import get_conn

def upgrade_principal_tracking():
    """Add columns to track principal scoring"""
    
    print("=== UPGRADE PRINCIPAL TRACKING COLUMNS ===")
    
    conn = get_conn()
    try:
        with conn.cursor() as cursor:
            
            # 1. Check if columns already exist
            cursor.execute("DESCRIBE tongdiem_epa")
            columns = cursor.fetchall()
            existing_cols = [col['Field'] for col in columns]
            
            new_columns = ['pri_updated_by', 'pri_updated_at']
            missing_cols = [col for col in new_columns if col not in existing_cols]
            
            if missing_cols:
                print(f"Adding {len(missing_cols)} new columns...")
                
                # 2. Add tracking columns
                if 'pri_updated_by' in missing_cols:
                    cursor.execute("""
                        ALTER TABLE tongdiem_epa 
                        ADD COLUMN pri_updated_by VARCHAR(50) DEFAULT NULL COMMENT 'Nguoi cap nhat diem HT/PHT'
                    """)
                    print("  Added column: pri_updated_by")
                
                if 'pri_updated_at' in missing_cols:
                    cursor.execute("""
                        ALTER TABLE tongdiem_epa 
                        ADD COLUMN pri_updated_at TIMESTAMP NULL DEFAULT NULL COMMENT 'Thoi gian cap nhat diem HT/PHT'
                    """)
                    print("  Added column: pri_updated_at")
                
                conn.commit()
                print("New columns added successfully!")
            else:
                print("All columns already exist, skipping column creation.")
            
            # 3. Update existing records that have pri_total_score but no tracking info
            cursor.execute("""
                UPDATE tongdiem_epa 
                SET pri_updated_by = 'kimnhung', pri_updated_at = NOW()
                WHERE pri_total_score IS NOT NULL 
                  AND pri_updated_by IS NULL
            """)
            
            updated_rows = cursor.rowcount
            if updated_rows > 0:
                conn.commit()
                print(f"Updated {updated_rows} existing records with default tracking info")
            
            # 4. Verify results
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(pri_total_score) as with_pri_score,
                    COUNT(pri_updated_by) as with_tracking
                FROM tongdiem_epa
            """)
            
            stats = cursor.fetchone()
            print(f"\nStatistics:")
            print(f"  Total records: {stats['total']}")
            print(f"  With pri_total_score: {stats['with_pri_score']}")
            print(f"  With tracking info: {stats['with_tracking']}")
            
            print(f"\nSUCCESS: Principal tracking upgrade completed!")
            
    except Exception as e:
        print(f"ERROR: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    upgrade_principal_tracking()