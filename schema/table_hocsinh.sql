SELECT * FROM quanlytruonghoc_app.hocsinh;
USE quanlytruonghoc_app;
-- MÃ GV;MÃ HS;HỌ VÀ TÊN;NGÀY SINH;GIỚI TÍNH;DT;MÃ ĐỊNH DANH;HỌ VÀ TÊN BỐ;NGHỀ NGHIỆP BỐ;HỌ VÀ TÊN MẸ;NGHỀ NGHIỆP MẸ;HỘ KHẨU;SỐ CCCD CỦA BỐ/MẸ;ĐT
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