USE quanlytruonghoc_app;

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
ALTER TABLE thoigianmoepa AUTO_INCREMENT = 1;
INSERT INTO thoigianmoepa 
(ten_tk, start_day, close_day, remark, make_epa_gv, make_epa_tgv, make_epa_all)
VALUES
('kimnhung',      1, 25, 'Mở EPA tháng 7',   'yes', 'yes', 'no'),
('ngocquy',       1, 25, NULL,               'yes', 'no',  'no'),
('ngocnguyen',    1, 25, NULL,               'yes', 'no',  'no'),
('kdien',         1, 25, NULL,               'yes', 'no',  'no'),
('hoangtran',     1, 25, NULL,               'yes', 'no',  'no'),
('huongphuong',   1, 25, NULL,               'yes', 'no',  'no'),
('kimoanh',       1, 25, NULL,               'yes', 'no',  'no'),
('thanhhuyen',    1, 25, NULL,               'yes', 'no',  'no'),
('ksira',         1, 25, NULL,               'yes', 'no',  'no'),
('thanhtuyen',    1, 25, NULL,               'yes', 'no',  'no'),
('anhtho',        1, 25, NULL,               'yes', 'no',  'no'),
('hangnguyen',    1, 25, NULL,               'yes', 'no',  'no'),
('ngocba',        1, 25, NULL,               'yes', 'no',  'no'),
('tronghung',     1, 25, NULL,               'yes', 'no',  'no'),
('thamtran',      1, 25, NULL,               'yes', 'no',  'no'),
('hannguyen',     1, 25, NULL,               'yes', 'no',  'no'),
('ngocphuong',    1, 25, NULL,               'yes', 'no',  'no');


