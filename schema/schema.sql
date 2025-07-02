CREATE DATABASE IF NOT EXISTS quanlytruonghoc_app;
USE quanlytruonghoc_app;

-- Bảng tài khoản
CREATE TABLE tk (
    ten_tk VARCHAR(255) PRIMARY KEY,
    nhom ENUM('admin', 'user', 'supervisor') NOT NULL,
    mat_khau VARCHAR(255),
    ngay_tao DATE,
    nguoi_tao VARCHAR(255),
    ngay_hh DATE
);

-- Bảng giáo viên
CREATE TABLE giaovien (
    ma_gv VARCHAR(255) PRIMARY KEY,
    ho_va_ten VARCHAR(255),
    ten_tk VARCHAR(255) UNIQUE,
    chuc_vu VARCHAR(255),
    ngay_sinh DATE,
    que_quan VARCHAR(255),
    cccd VARCHAR(255),
    ngay_cap DATE,
    mst VARCHAR(255),
    cmnd VARCHAR(255),
    so_bh VARCHAR(255),
    sdt VARCHAR(255),
    tk_nh VARCHAR(255),
    email VARCHAR(255),
    nhom_mau VARCHAR(255),
    dia_chi VARCHAR(255) ,
    FOREIGN KEY (ten_tk) REFERENCES tk(ten_tk) ON DELETE SET NULL
);

-- Bảng danh sách lớp
CREATE TABLE ds_lop (
    ma_lop VARCHAR(255) PRIMARY KEY,
    ten_lop VARCHAR(255)
);

-- Bảng học sinh
CREATE TABLE hocsinh (
    ma_hs VARCHAR(255) PRIMARY KEY,
    ma_gv VARCHAR(255), -- chọn ma_gv có sẵn từ bảng quanlytruonghoc_app.giavien
    ma_lop VARCHAR(255),
    ho_va_ten VARCHAR(255),
    ngay_sinh DATE,
    gioi_tinh ENUM('Nam', 'Nữ'),
    dan_toc VARCHAR(255),
    ma_dinh_danh VARCHAR(255),
    ho_ten_bo VARCHAR(255),
    nghe_nghiep_bo VARCHAR(255),
    ho_ten_me VARCHAR(255),
    nghe_nghiep_me VARCHAR(255),
    ho_khau VARCHAR(255),
    cccd_bo_me VARCHAR(255),
    sdt VARCHAR(255),
    FOREIGN KEY (ma_lop) REFERENCES ds_lop(ma_lop),
    FOREIGN KEY (ma_gv) REFERENCES giaovien(ma_gv)
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

-- Bảng câu hỏi EPA
CREATE TABLE cauhoi_epa (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question TEXT NOT NULL,
    translate TEXT
);

CREATE TABLE thoigianmoepa (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ten_tk VARCHAR(255),  -- Liên kết đến giaovien(ten_tk)
    start_day INT NOT NULL,
    close_day INT NOT NULL,
    remark TEXT,
    make_epa_gv ENUM('yes', 'no') DEFAULT 'no',
    make_epa_tgv ENUM('yes', 'no') DEFAULT 'no',
    make_epa_all ENUM('yes', 'no') DEFAULT 'no',
    FOREIGN KEY (ten_tk) REFERENCES giaovien(ten_tk) ON DELETE SET NULL
);

-- Bảng đánh giá tổng hợp
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
    user_comment TEXT NULL, -- ý kiến cá nhân user tự đánh giá dạng TEXT
    user_score INT, -- điểm dành cho câu hỏi user tự đánh giá dạng INT
    sup_comment TEXT NULL, -- ý kiến đánh giá của supervisor dành cho câu hỏi tương ứng mà user đã trả lời
    sup_score INT NULL, -- điểm đánh giá mà supervisor đưa ra dành cho câu hỏi tương ứng mà user đã trả lời
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ten_tk) REFERENCES tk(ten_tk)
);

-- Bảng tổng điểm EPA
CREATE TABLE tongdiem_epa (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ten_tk VARCHAR(100) NOT NULL,
    year INT NOT NULL,
    month INT NOT NULL,
    user_total_score INT DEFAULT 0, -- tổng điểm các câu hỏi user tự đánh giá ở cột user_score của  bảng 'giaovien_epa'
    sup_total_score INT DEFAULT 0, -- tổng điểm các câu hỏi supervisor đánh giá ở cở cột sup_score bảng 'giaovien_epa'
    pri_total_score INT NULL,
    pri_comment TEXT NULL,
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

-- INDEXS
CREATE INDEX idx_hocsinh_ma_gv ON hocsinh(ma_gv);
CREATE INDEX idx_phan_lop_ma_lop ON phan_lop(ma_lop);
CREATE INDEX idx_lop_gv_ma_gv ON lop_gv(ma_gv);
CREATE INDEX idx_bangdanhgia_ten_tk ON bangdanhgia(ten_tk);
CREATE INDEX idx_bangdanhgia_ten_tk_year_month ON bangdanhgia(ten_tk, year, month);
CREATE INDEX idx_tongdiem_epa_year_month ON tongdiem_epa(year, month);
CREATE INDEX idx_logs_target_staff_id ON logs(target_staff_id);
