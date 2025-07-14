SELECT * FROM quanlytruonghoc_app.logs;
USE quanlytruonghoc_app;
CREATE TABLE logs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_ten_tk VARCHAR(255),  -- Trùng với tk.ten_tk
  target_staff_id VARCHAR(20),
  target_table ENUM('tk', 'giaovien', 'hocsinh') DEFAULT NULL,
  action TEXT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_log_user FOREIGN KEY (user_ten_tk) REFERENCES tk(ten_tk) ON DELETE SET NULL
);