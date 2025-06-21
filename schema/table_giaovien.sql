SELECT * FROM quanlytruonghoc_app.giaovien;
USE quanlytruonghoc_app;
-- MÃ GV;HỌ VÀ TÊN;TÊN TK;CHỨC VỤ;NGÀY SINH;QUÊ QUÁN;CCCD;Ngày cấp;MST;CMND;SỔ BH;SỐ ĐT;SỐ TK;Email;Nhóm máu;Địa chỉ
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
