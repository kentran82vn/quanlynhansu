
CREATE DATABASE IF NOT EXISTS quanlytruonghoc_app;
USE quanlytruonghoc_app;
ALTER TABLE logs MODIFY target_table VARCHAR(100);

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
    dia_chi VARCHAR(255)
);

-- Bảng học sinh
CREATE TABLE hocsinh (
    ma_hs VARCHAR(255) PRIMARY KEY,
    ma_gv VARCHAR(255),
    ho_va_ten VARCHAR(255),
    ngay_sinh DATE,
    gioi_tinh VARCHAR(255),
    dan_toc VARCHAR(255),
    ma_dinh_danh VARCHAR(255),
    ho_ten_bo VARCHAR(255),
    nghe_nghiep_bo VARCHAR(255),
    ho_ten_me VARCHAR(255),
    nghe_nghiep_me VARCHAR(255),
    ho_khau VARCHAR(255),
    cccd_bo_me VARCHAR(255),
    sdt VARCHAR(255),
    FOREIGN KEY (ma_gv) REFERENCES giaovien(ma_gv)
);

-- Bảng danh sách lớp
CREATE TABLE ds_lop (
    ma_lop VARCHAR(255) PRIMARY KEY,
    ten_lop VARCHAR(255)
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
    vai_tro VARCHAR(255),
    PRIMARY KEY (ma_lop, ma_gv),
    FOREIGN KEY (ma_lop) REFERENCES ds_lop(ma_lop),
    FOREIGN KEY (ma_gv) REFERENCES giaovien(ma_gv)
);

-- Bảng tài khoản
CREATE TABLE tk (
    ten_tk VARCHAR(255) PRIMARY KEY,
    nhom VARCHAR(255),
    mat_khau VARCHAR(255),
    ngay_tao DATE,
    nguoi_tao VARCHAR(255),
    ngay_hh DATE
);

-- Bảng câu hỏi EPA
CREATE TABLE cauhoi_epa (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question TEXT NOT NULL,
    translate TEXT
);

-- Bảng đánh giá
CREATE TABLE bangdanhgia (
    thang_nam VARCHAR(255),
    ten_tk VARCHAR(255),
    ho_va_ten VARCHAR(255),
    chuc_vu VARCHAR(255),
    ngay_sinh DATE,
    danh_sach_10_cau_hoi_EPA VARCHAR(255),
    tong_diem VARCHAR(255),
    FOREIGN KEY (ten_tk) REFERENCES tk(ten_tk)
);

-- Bảng điểm EPA của giáo viên
CREATE TABLE giaovien_scores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ten_tk VARCHAR(100) NOT NULL,
    year INT NOT NULL,
    month INT NOT NULL,
    question TEXT NOT NULL,
    translate TEXT,
    answer TEXT,
    score INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ten_tk) REFERENCES giaovien(ten_tk)
);

-- Bảng log
CREATE TABLE logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_ten_tk VARCHAR(255),
    target_staff_id VARCHAR(100),
    target_table VARCHAR(100),
    action TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_log_user FOREIGN KEY (user_ten_tk) REFERENCES tk(ten_tk) ON DELETE SET NULL
);

-- Bảng thống kê
CREATE TABLE stats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stat_date DATE NOT NULL,
    team VARCHAR(255) NOT NULL,
    count INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
