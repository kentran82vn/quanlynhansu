-- =====================================================
-- UPGRADE DATABASE CHO HE THONG 3 GIAI DOAN EPA
-- =====================================================

USE quanlytruonghoc_app;

-- 1. Backup bang cu (phong truong hop can rollback)
CREATE TABLE thoigianmoepa_backup AS SELECT * FROM thoigianmoepa;

-- 2. Them cac cot moi cho 3 giai doan
ALTER TABLE thoigianmoepa 
ADD COLUMN phase1_start INT DEFAULT NULL COMMENT 'Ngay bat dau giai doan 1 (Tu danh gia)',
ADD COLUMN phase1_end INT DEFAULT NULL COMMENT 'Ngay ket thuc giai doan 1 (Tu danh gia)',
ADD COLUMN phase2_start INT DEFAULT NULL COMMENT 'Ngay bat dau giai doan 2 (TGV cham diem)',
ADD COLUMN phase2_end INT DEFAULT NULL COMMENT 'Ngay ket thuc giai doan 2 (TGV cham diem)', 
ADD COLUMN phase3_start INT DEFAULT NULL COMMENT 'Ngay bat dau giai doan 3 (HT/PHT cham diem)',
ADD COLUMN phase3_end INT DEFAULT NULL COMMENT 'Ngay ket thuc giai doan 3 (HT/PHT cham diem)';

-- 3. Migrate du lieu cu sang format moi
-- Gia su start_day va close_day cu la cho giai doan 1
UPDATE thoigianmoepa SET
    phase1_start = start_day,
    phase1_end = close_day,
    phase2_start = close_day + 1,
    phase2_end = close_day + 2,
    phase3_start = close_day + 3,
    phase3_end = close_day + 5
WHERE start_day IS NOT NULL AND close_day IS NOT NULL;

-- 4. Them constraint dam bao logic thoi gian
ALTER TABLE thoigianmoepa 
ADD CONSTRAINT chk_phase_order 
CHECK (
    (phase1_start IS NULL OR phase1_end IS NULL OR phase1_start <= phase1_end) AND
    (phase2_start IS NULL OR phase2_end IS NULL OR phase2_start <= phase2_end) AND  
    (phase3_start IS NULL OR phase3_end IS NULL OR phase3_start <= phase3_end) AND
    (phase1_end IS NULL OR phase2_start IS NULL OR phase1_end < phase2_start) AND
    (phase2_end IS NULL OR phase3_start IS NULL OR phase2_end < phase3_start)
);

-- 5. Cap nhat du lieu mau theo quy trinh thuc te
-- Tat ca user se co chung thoi gian theo quy trinh mac dinh
UPDATE thoigianmoepa SET
    phase1_start = 20,  -- Tu danh gia: 20-25
    phase1_end = 25,
    phase2_start = 26,  -- TGV cham diem: 26-27  
    phase2_end = 27,
    phase3_start = 28,  -- HT/PHT cham diem: 28-30
    phase3_end = 30;

-- 6. Xac nhan ket qua
SELECT 'Migration completed successfully' as status;
SELECT COUNT(*) as total_records FROM thoigianmoepa;
SELECT 
    ten_tk,
    CONCAT(phase1_start, '-', phase1_end) as phase1,
    CONCAT(phase2_start, '-', phase2_end) as phase2, 
    CONCAT(phase3_start, '-', phase3_end) as phase3,
    make_epa_gv, make_epa_tgv, make_epa_all
FROM thoigianmoepa 
LIMIT 5;