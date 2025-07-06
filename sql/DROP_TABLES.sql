USE quanlytruonghoc_app;

-- ⚠️ Tắt kiểm tra khóa ngoại tạm thời để tránh lỗi khi drop
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS logs;
DROP TABLE IF EXISTS stats;
DROP TABLE IF EXISTS tongdiem_epa;
DROP TABLE IF EXISTS bangdanhgia;
DROP TABLE IF EXISTS thoigianmoepa;
DROP TABLE IF EXISTS cauhoi_epa;
DROP TABLE IF EXISTS lop_gv;
DROP TABLE IF EXISTS phan_lop;
DROP TABLE IF EXISTS hocsinh;
DROP TABLE IF EXISTS ds_lop;
DROP TABLE IF EXISTS giaovien;
DROP TABLE IF EXISTS tk;

SET FOREIGN_KEY_CHECKS = 1;
