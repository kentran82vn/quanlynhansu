SELECT * FROM quanlytruonghoc_app.giaovien_epa;
USE quanlytruonghoc_app;
-- Bảng điểm epa của giáo viên 
CREATE TABLE giaovien_epa (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ten_tk VARCHAR(100) NOT NULL,
    year INT NOT NULL,
    month INT NOT NULL,
    question TEXT NOT NULL,
    translate TEXT,
    answer TEXT,
    score INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);