CREATE DATABASE IF NOT EXISTS quanlytruonghoc_app;
USE quanlytruonghoc_app;
DESCRIBE bangdanhgia;
-- Bảng tài khoản
CREATE TABLE tk (
    ten_tk VARCHAR(255) PRIMARY KEY,
    nhom ENUM('admin', 'user', 'supervisor') NOT NULL,
    mat_khau VARCHAR(255),
    ngay_tao DATE,
    nguoi_tao VARCHAR(255),
    ngay_hh DATE
);

-- Bảng giáo viên chính
CREATE TABLE giaovien (
    ma_gv VARCHAR(255) PRIMARY KEY,
    ho_va_ten VARCHAR(255),
    ten_tk VARCHAR(255) UNIQUE,
    chuc_vu VARCHAR(255),
    ngay_sinh DATE,
    que_quan VARCHAR(255),
    cccd VARCHAR(20),
    ngay_cap DATE,
    mst VARCHAR(20),
    cmnd VARCHAR(20),
    so_bh VARCHAR(20),
    sdt VARCHAR(20),
    tk_nh VARCHAR(30),
    email VARCHAR(255),
    nhom_mau VARCHAR(255),
    dia_chi VARCHAR(255),
    FOREIGN KEY (ten_tk) REFERENCES tk(ten_tk) ON DELETE SET NULL
);

-- Bảng danh sách lớp
CREATE TABLE ds_lop (
    ma_lop VARCHAR(255) PRIMARY KEY,
    ten_lop VARCHAR(255)
);

-- Bảng học sinh (đã loại bỏ ma_gv)
CREATE TABLE hocsinh (
    ma_hs VARCHAR(255) PRIMARY KEY,
    ho_va_ten VARCHAR(255),
    ngay_sinh DATE,
    gioi_tinh ENUM('Nam', 'Nữ'),
    dan_toc VARCHAR(255),
    ma_dinh_danh VARCHAR(20),
    ho_ten_bo VARCHAR(255),
    nghe_nghiep_bo VARCHAR(255),
    ho_ten_me VARCHAR(255),
    nghe_nghiep_me VARCHAR(255),
    ho_khau VARCHAR(255),
    cccd_bo_me VARCHAR(20),
    sdt VARCHAR(20)
);

-- Bảng phân lớp học sinh
CREATE TABLE phan_lop (
    ma_hs VARCHAR(255) PRIMARY KEY,
    ma_lop VARCHAR(255),
    FOREIGN KEY (ma_hs) REFERENCES hocsinh(ma_hs),
    FOREIGN KEY (ma_lop) REFERENCES ds_lop(ma_lop)
);

-- Bảng ánh xạ lớp - giáo viên
CREATE TABLE lop_gv (
    ma_lop VARCHAR(255),
    ma_gv VARCHAR(255),
    vai_tro ENUM('GVCN', 'Bộ môn', 'Bảo mẫu') NOT NULL,
    PRIMARY KEY (ma_lop, ma_gv),
    FOREIGN KEY (ma_lop) REFERENCES ds_lop(ma_lop),
    FOREIGN KEY (ma_gv) REFERENCES giaovien(ma_gv)
);

-- Bảng câu hỏi EPA (Updated với score field)
CREATE TABLE cauhoi_epa (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question TEXT NOT NULL,
    translate TEXT,
    score INT DEFAULT 20
);

-- Bảng thời gian mở EPA (Updated với 3 giai đoạn)
CREATE TABLE thoigianmoepa (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ten_tk VARCHAR(255),
    start_day INT NOT NULL,
    close_day INT NOT NULL,
    phase1_start INT DEFAULT 20,
    phase1_end INT DEFAULT 25,
    phase2_start INT DEFAULT 26,
    phase2_end INT DEFAULT 27,
    phase3_start INT DEFAULT 28,
    phase3_end INT DEFAULT 30,
    remark TEXT,
    make_epa_gv ENUM('yes', 'no') DEFAULT 'no',
    make_epa_tgv ENUM('yes', 'no') DEFAULT 'no',
    make_epa_all ENUM('yes', 'no') DEFAULT 'no',
    FOREIGN KEY (ten_tk) REFERENCES giaovien(ten_tk) ON DELETE SET NULL
);

-- Bảng đánh giá EPA
CREATE TABLE bangdanhgia (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ten_tk VARCHAR(100) NOT NULL,
    ho_va_ten VARCHAR(255),
    chuc_vu VARCHAR(255),
    ngay_sinh DATE,
    year INT NOT NULL,
    month INT NOT NULL,
    question TEXT NOT NULL,
    translate TEXT,
    user_comment TEXT,
    user_score INT,
    sup_comment TEXT,
    sup_score INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ten_tk) REFERENCES tk(ten_tk)
);

-- Bảng tổng điểm EPA (Updated với tracking fields)
CREATE TABLE tongdiem_epa (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ten_tk VARCHAR(100) NOT NULL,
    year INT NOT NULL,
    month INT NOT NULL,
    user_total_score INT DEFAULT 0,
    sup_total_score INT DEFAULT 0,
    pri_total_score INT,
    pri_comment TEXT,
    pri_updated_by VARCHAR(100),
    pri_updated_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ten_tk) REFERENCES tk(ten_tk) ON DELETE CASCADE,
    UNIQUE KEY unique_user_month (ten_tk, year, month)
);

-- Bảng log
CREATE TABLE logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_ten_tk VARCHAR(255),
    target_staff_id VARCHAR(100),
    target_table VARCHAR(100),
    action TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_ten_tk) REFERENCES tk(ten_tk) ON DELETE SET NULL
);

-- Bảng thống kê
CREATE TABLE stats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stat_date DATE NOT NULL,
    team VARCHAR(255) NOT NULL,
    count INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
-- DESCRIBE hocsinh;

-- INDEXES (Updated with new EPA indexes)
CREATE INDEX idx_phan_lop_ma_lop ON phan_lop(ma_lop);
CREATE INDEX idx_lop_gv_ma_gv ON lop_gv(ma_gv);
CREATE INDEX idx_bangdanhgia_ten_tk ON bangdanhgia(ten_tk);
CREATE INDEX idx_bangdanhgia_ten_tk_year_month ON bangdanhgia(ten_tk, year, month);
CREATE INDEX idx_tongdiem_epa_year_month ON tongdiem_epa(year, month);
CREATE INDEX idx_tongdiem_epa_pri_updated ON tongdiem_epa(pri_updated_by, pri_updated_at);
CREATE INDEX idx_thoigianmoepa_phases ON thoigianmoepa(phase1_start, phase1_end, phase2_start, phase2_end, phase3_start, phase3_end);
CREATE INDEX idx_logs_target_staff_id ON logs(target_staff_id);
