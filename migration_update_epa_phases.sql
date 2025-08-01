-- ==========================================
-- MIGRATION: Cập nhật bảng thoigianmoepa với các field phase mới
-- Date: 2025-07-30
-- Purpose: Thêm support cho 3 giai đoạn EPA và fix logic tháng
-- ==========================================

USE quanlytruonghoc_app;

-- Kiểm tra và thêm các cột phase mới vào bảng thoigianmoepa
ALTER TABLE thoigianmoepa 
ADD COLUMN IF NOT EXISTS phase1_start INT DEFAULT 20,
ADD COLUMN IF NOT EXISTS phase1_end INT DEFAULT 25,
ADD COLUMN IF NOT EXISTS phase2_start INT DEFAULT 26,
ADD COLUMN IF NOT EXISTS phase2_end INT DEFAULT 27,
ADD COLUMN IF NOT EXISTS phase3_start INT DEFAULT 28,
ADD COLUMN IF NOT EXISTS phase3_end INT DEFAULT 30;

-- Thêm các cột tracking cho principal scoring
ALTER TABLE tongdiem_epa 
ADD COLUMN IF NOT EXISTS pri_updated_by VARCHAR(100),
ADD COLUMN IF NOT EXISTS pri_updated_at DATETIME;

-- Cập nhật dữ liệu hiện có với default values
UPDATE thoigianmoepa SET 
    phase1_start = 20,
    phase1_end = 25,
    phase2_start = 26,
    phase2_end = 27,
    phase3_start = 28,
    phase3_end = 30
WHERE phase1_start IS NULL OR phase1_start = 0;

-- Thêm score column vào cauhoi_epa nếu chưa có
ALTER TABLE cauhoi_epa 
ADD COLUMN IF NOT EXISTS score INT DEFAULT 20;

-- Cập nhật score mặc định cho các câu hỏi hiện có
UPDATE cauhoi_epa SET score = 20 WHERE score IS NULL OR score = 0;

-- Tạo index để tối ưu performance
CREATE INDEX IF NOT EXISTS idx_thoigianmoepa_phases ON thoigianmoepa(phase1_start, phase1_end, phase2_start, phase2_end, phase3_start, phase3_end);
CREATE INDEX IF NOT EXISTS idx_tongdiem_epa_pri_updated ON tongdiem_epa(pri_updated_by, pri_updated_at);

-- Xóa dữ liệu test cũ (nếu có)
DELETE FROM bangdanhgia WHERE ten_tk LIKE 'test%' OR ten_tk LIKE 'demo%';
DELETE FROM tongdiem_epa WHERE ten_tk LIKE 'test%' OR ten_tk LIKE 'demo%';

COMMIT;

-- Show updated structure
DESCRIBE thoigianmoepa;
DESCRIBE tongdiem_epa;
DESCRIBE cauhoi_epa;

SELECT COUNT(*) as total_users FROM thoigianmoepa;
SELECT COUNT(*) as total_questions FROM cauhoi_epa;

-- Migration completed successfully
SELECT 'Migration completed successfully! 🎉' as status;