#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.db import get_conn
import pymysql
from datetime import datetime

def debug_phase_logic():
    ten_tk = 'ksira'
    now = datetime.now()
    day = now.day
    
    print(f"Current day: {day}")
    
    conn = get_conn()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    cursor.execute(
        """
        SELECT phase1_start, phase1_end, phase2_start, phase2_end, phase3_start, phase3_end,
               make_epa_gv, make_epa_tgv, start_day, close_day
        FROM thoigianmoepa
        WHERE ten_tk = %s
        """,
        (ten_tk,)
    )
    record = cursor.fetchone()
    
    print(f"Database record: {record}")
    
    if record:
        is_tgv = record.get('make_epa_tgv') == 'yes'
        print(f"Is TGV: {is_tgv}")
        
        phase1_open = record['phase1_start'] <= day <= record['phase1_end']
        phase2_open = record['phase2_start'] <= day <= record['phase2_end'] if record['phase2_start'] and record['phase2_end'] else False
        phase3_open = record['phase3_start'] <= day <= record['phase3_end'] if record['phase3_start'] and record['phase3_end'] else False
        
        print(f"Phase 1 open: {phase1_open} ({record['phase1_start']}-{record['phase1_end']})")
        print(f"Phase 2 open: {phase2_open} ({record['phase2_start']}-{record['phase2_end']})")
        print(f"Phase 3 open: {phase3_open} ({record['phase3_start']}-{record['phase3_end']})")
        
        # Debug logic flow
        if is_tgv:
            print("Following TGV logic...")
            is_open = phase1_open or phase2_open
            if phase1_open:
                current_phase = 'Phase 1 (Tu danh gia)'
                print(f"TGV: Phase 1 active")
            elif phase2_open:
                current_phase = 'Phase 2 (Tu danh gia TGV)'
                print(f"TGV: Phase 2 active")
            else:
                current_phase = 'Phase 3 (Chi HT/PHT danh gia)'
                print(f"TGV: Phase 3 active")
        else:
            print("Following regular teacher logic...")
            is_open = phase1_open
            if phase1_open:
                current_phase = 'Phase 1 (Tu danh gia)'
                print(f"Teacher: Phase 1 active")
            elif phase2_open:
                current_phase = 'Phase 2 (TGV danh gia)'
                print(f"Teacher: Phase 2 active")
            elif phase3_open:
                current_phase = 'Phase 3 (HT/PHT danh gia)'
                print(f"Teacher: Phase 3 active")
            else:
                current_phase = 'Ngoai thoi gian danh gia'
                print(f"Teacher: Outside assessment time")
        
        print(f"Final current_phase: {current_phase}")
        print(f"Final is_open: {is_open}")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    debug_phase_logic()