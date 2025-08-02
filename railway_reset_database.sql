-- Script để reset và tạo lại database đầy đủ cho Railway
-- CẢNH BÁO: Script này sẽ XÓA TẤT CẢ DỮ LIỆU hiện tại

-- Tắt các ràng buộc khóa ngoại để có thể drop table
SET FOREIGN_KEY_CHECKS = 0;

-- Drop tất cả các bảng nếu tồn tại
DROP TABLE IF EXISTS `bangdanhgia`;
DROP TABLE IF EXISTS `cauhoi_epa`;
DROP TABLE IF EXISTS `giaovien`;
DROP TABLE IF EXISTS `giaovien_score`;
DROP TABLE IF EXISTS `hocsinh`;
DROP TABLE IF EXISTS `ds_lop`;
DROP TABLE IF EXISTS `phan_lop`;
DROP TABLE IF EXISTS `lop_gv`;
DROP TABLE IF EXISTS `thoigianmoepa`;
DROP TABLE IF EXISTS `tongdiem_epa`;
DROP TABLE IF EXISTS `tk`;
DROP TABLE IF EXISTS `logs`;

-- Bật lại ràng buộc khóa ngoại
SET FOREIGN_KEY_CHECKS = 1;

-- Tạo lại bảng tk (phải tạo trước vì các bảng khác reference đến nó)
CREATE TABLE `tk` (
  `ten_tk` varchar(255) NOT NULL,
  `nhom` ENUM('admin', 'user', 'supervisor') NOT NULL DEFAULT 'user',
  `mat_khau` varchar(255) NOT NULL,
  `ngay_tao` date DEFAULT (curdate()),
  `nguoi_tao` varchar(255) DEFAULT NULL,
  `ngay_hh` date DEFAULT NULL,
  `pass` varchar(255) DEFAULT NULL,
  `ho_va_ten` varchar(255) DEFAULT NULL,
  `chuc_vu` varchar(255) DEFAULT NULL,
  `ngay_sinh` date DEFAULT NULL,
  `gioi_tinh` varchar(10) DEFAULT NULL,
  `sdt` varchar(15) DEFAULT NULL,
  `dia_chi` text,
  `cccd` varchar(20) DEFAULT NULL,
  `ngay_vao_lam` date DEFAULT NULL,
  `luong_co_ban` decimal(15,2) DEFAULT NULL,
  `phu_cap` decimal(15,2) DEFAULT NULL,
  `tong_luong` decimal(15,2) DEFAULT NULL,
  `status` varchar(50) DEFAULT 'active',
  `role` varchar(50) DEFAULT 'user',
  PRIMARY KEY (`ten_tk`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Tạo bảng cauhoi_epa (bao gồm cột score)
CREATE TABLE `cauhoi_epa` (
  `id` int NOT NULL AUTO_INCREMENT,
  `question` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `translate` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
  `score` int DEFAULT 20,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Tạo bảng bangdanhgia
CREATE TABLE `bangdanhgia` (
  `id` int NOT NULL AUTO_INCREMENT,
  `ten_tk` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `ho_va_ten` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `chuc_vu` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `ngay_sinh` date DEFAULT NULL,
  `year` int NOT NULL,
  `month` int NOT NULL,
  `question` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `translate` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
  `user_comment` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
  `user_score` int DEFAULT NULL,
  `sup_comment` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
  `sup_score` int DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ten_tk` (`ten_tk`),
  CONSTRAINT `bangdanhgia_ibfk_1` FOREIGN KEY (`ten_tk`) REFERENCES `tk` (`ten_tk`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Tạo bảng giaovien
CREATE TABLE `giaovien` (
  `ma_gv` varchar(255) NOT NULL,
  `ho_va_ten` varchar(255) DEFAULT NULL,
  `ten_tk` varchar(255) DEFAULT NULL,
  `chuc_vu` varchar(255) DEFAULT NULL,
  `ngay_sinh` date DEFAULT NULL,
  `que_quan` varchar(255) DEFAULT NULL,
  `cccd` varchar(255) DEFAULT NULL,
  `ngay_cap` date DEFAULT NULL,
  `mst` varchar(255) DEFAULT NULL,
  `cmnd` varchar(255) DEFAULT NULL,
  `so_bh` varchar(255) DEFAULT NULL,
  `sdt` varchar(255) DEFAULT NULL,
  `tk_nh` varchar(255) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `nhom_mau` varchar(255) DEFAULT NULL,
  `dia_chi` varchar(255) DEFAULT NULL,
  `gioi_tinh` varchar(10) DEFAULT NULL,
  `ngay_vao_lam` date DEFAULT NULL,
  `luong_co_ban` decimal(15,2) DEFAULT NULL,
  `phu_cap` decimal(15,2) DEFAULT NULL,
  `tong_luong` decimal(15,2) DEFAULT NULL,
  `status` varchar(50) DEFAULT 'active',
  PRIMARY KEY (`ma_gv`),
  UNIQUE KEY `ten_tk` (`ten_tk`),
  CONSTRAINT `giaovien_ibfk_1` FOREIGN KEY (`ten_tk`) REFERENCES `tk` (`ten_tk`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Tạo bảng ds_lop
CREATE TABLE `ds_lop` (
  `ma_lop` varchar(50) NOT NULL,
  `ten_lop` varchar(255) NOT NULL,
  `khoi` varchar(50) DEFAULT NULL,
  `nam_hoc` varchar(20) DEFAULT NULL,
  `si_so` int DEFAULT 0,
  `ghi_chu` text,
  PRIMARY KEY (`ma_lop`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Tạo bảng hocsinh
CREATE TABLE `hocsinh` (
  `ma_hs` varchar(255) NOT NULL,
  `ho_va_ten` varchar(255) NOT NULL,
  `ngay_sinh` date DEFAULT NULL,
  `gioi_tinh` ENUM('Nam', 'Nữ') DEFAULT NULL,
  `dan_toc` varchar(255) DEFAULT NULL,
  `ma_dinh_danh` varchar(255) DEFAULT NULL,
  `ho_ten_bo` varchar(255) DEFAULT NULL,
  `nghe_nghiep_bo` varchar(255) DEFAULT NULL,
  `ho_ten_me` varchar(255) DEFAULT NULL,
  `nghe_nghiep_me` varchar(255) DEFAULT NULL,
  `ho_khau` varchar(255) DEFAULT NULL,
  `cccd_bo_me` varchar(255) DEFAULT NULL,
  `sdt` varchar(255) DEFAULT NULL,
  `dia_chi` varchar(255) DEFAULT NULL,
  `ma_lop` varchar(255) DEFAULT NULL,
  `nam_hoc` varchar(20) DEFAULT NULL,
  `trang_thai` varchar(50) DEFAULT 'active',
  PRIMARY KEY (`ma_hs`),
  KEY `ma_lop` (`ma_lop`),
  CONSTRAINT `hocsinh_ibfk_1` FOREIGN KEY (`ma_lop`) REFERENCES `ds_lop` (`ma_lop`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Tạo bảng phan_lop
CREATE TABLE `phan_lop` (
  `ma_hs` varchar(255) NOT NULL,
  `ma_lop` varchar(255) NOT NULL,
  `nam_hoc` varchar(20) DEFAULT NULL,
  `ngay_phan` date DEFAULT (curdate()),
  PRIMARY KEY (`ma_hs`),
  KEY `ma_lop` (`ma_lop`),
  CONSTRAINT `phan_lop_ibfk_1` FOREIGN KEY (`ma_hs`) REFERENCES `hocsinh` (`ma_hs`),
  CONSTRAINT `phan_lop_ibfk_2` FOREIGN KEY (`ma_lop`) REFERENCES `ds_lop` (`ma_lop`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Tạo bảng lop_gv  
CREATE TABLE `lop_gv` (
  `ma_lop` varchar(255) NOT NULL,
  `ma_gv` varchar(255) NOT NULL,
  `vai_tro` ENUM('GVCN', 'Bộ môn', 'Bảo mẫu') DEFAULT 'Bộ môn',
  `nam_hoc` varchar(20) DEFAULT NULL,
  `ngay_phan_cong` date DEFAULT (curdate()),
  PRIMARY KEY (`ma_lop`, `ma_gv`),
  KEY `ma_gv` (`ma_gv`),
  CONSTRAINT `lop_gv_ibfk_1` FOREIGN KEY (`ma_lop`) REFERENCES `ds_lop` (`ma_lop`),
  CONSTRAINT `lop_gv_ibfk_2` FOREIGN KEY (`ma_gv`) REFERENCES `giaovien` (`ma_gv`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Tạo bảng thoigianmoepa
CREATE TABLE `thoigianmoepa` (
  `id` int NOT NULL AUTO_INCREMENT,
  `ten_tk` varchar(255) DEFAULT NULL,
  `start_day` int NOT NULL,
  `close_day` int NOT NULL,
  `month` int NOT NULL,
  `year` int NOT NULL,
  `remark` text DEFAULT NULL,
  `make_epa_gv` ENUM('yes', 'no') DEFAULT 'no',
  `make_epa_tgv` ENUM('yes', 'no') DEFAULT 'no',
  `make_epa_all` ENUM('yes', 'no') DEFAULT 'no',
  `phase1_start` int DEFAULT NULL,
  `phase1_end` int DEFAULT NULL,
  `phase2_start` int DEFAULT NULL,
  `phase2_end` int DEFAULT NULL,
  `phase3_start` int DEFAULT NULL,
  `phase3_end` int DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Tạo bảng tongdiem_epa
CREATE TABLE `tongdiem_epa` (
  `id` int NOT NULL AUTO_INCREMENT,
  `ten_tk` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `ho_va_ten` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `chuc_vu` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `year` int NOT NULL,
  `month` int NOT NULL,
  `user_total_score` int DEFAULT 0,
  `sup_total_score` int DEFAULT 0,
  `pri_total_score` int DEFAULT NULL,
  `pri_comment` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
  `pri_updated_by` varchar(100) DEFAULT NULL,
  `pri_updated_at` datetime DEFAULT NULL,
  `xeploai` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ten_tk` (`ten_tk`),
  CONSTRAINT `tongdiem_epa_ibfk_1` FOREIGN KEY (`ten_tk`) REFERENCES `tk` (`ten_tk`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Tạo bảng giaovien_score
CREATE TABLE `giaovien_score` (
  `id` int NOT NULL AUTO_INCREMENT,
  `ten_tk` varchar(100) NOT NULL,
  `ho_va_ten` varchar(255) DEFAULT NULL,
  `chuc_vu` varchar(255) DEFAULT NULL,
  `year` int NOT NULL,
  `month` int NOT NULL,
  `question` text NOT NULL,
  `translate` text DEFAULT NULL,
  `answer` text DEFAULT NULL,
  `score` int DEFAULT NULL,
  `thang_nam` varchar(10) DEFAULT NULL,
  `diem_td` decimal(5,2) DEFAULT NULL,
  `diem_cm` decimal(5,2) DEFAULT NULL,
  `diem_ht` decimal(5,2) DEFAULT NULL,
  `diem_at` decimal(5,2) DEFAULT NULL,
  `diem_bt` decimal(5,2) DEFAULT NULL,
  `diem_cs` decimal(5,2) DEFAULT NULL,
  `diem_sk` decimal(5,2) DEFAULT NULL,
  `diem_pt` decimal(5,2) DEFAULT NULL,
  `diem_px` decimal(5,2) DEFAULT NULL,
  `diem_ut` decimal(5,2) DEFAULT NULL,
  `tong_diem` decimal(5,2) DEFAULT NULL,
  `xep_loai` varchar(50) DEFAULT NULL,
  `ghi_chu` text,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ten_tk` (`ten_tk`),
  CONSTRAINT `giaovien_score_ibfk_1` FOREIGN KEY (`ten_tk`) REFERENCES `tk` (`ten_tk`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Tạo bảng logs
CREATE TABLE `logs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_ten_tk` varchar(255) DEFAULT NULL,
  `target_staff_id` varchar(100) DEFAULT NULL,
  `target_table` varchar(100) DEFAULT NULL,
  `action` text NOT NULL,
  `user` varchar(100) DEFAULT NULL,
  `timestamp` datetime DEFAULT CURRENT_TIMESTAMP,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `details` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Tạo bảng stats
CREATE TABLE `stats` (
  `id` int NOT NULL AUTO_INCREMENT,
  `stat_date` date NOT NULL,
  `team` varchar(255) NOT NULL,
  `count` int NOT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Insert dữ liệu mẫu cho cauhoi_epa
INSERT INTO cauhoi_epa (question, translate, score) VALUES
("Do you strictly comply with working hours this month? (Late arrivals, unpermitted absences, non-participation in collective activities…)",
"Bạn có chấp hành nghiêm túc giờ giấc làm việc trong tháng này không? (Đi trễ, nghỉ không phép, không tham gia sinh hoạt chung…)", 20),

("Do you fully and correctly implement professional activities: etiquette, weekly activities, morning exercise, learning activities, corner activities, and outdoor activities?",
"Bạn có thực hiện đầy đủ và đúng quy trình các hoạt động chuyên môn: lễ giáo, sinh hoạt đầu tuần, thể dục sáng, hoạt động học, hoạt động góc, hoạt động ngoài trời không?", 20),

("Do you prepare teaching aids, music, and tools sufficiently and follow proper teaching methods in professional activities? (Be proactive, memorize demonstration movements, model activities for children…)",
"Trong các hoạt động chuyên môn, bạn có chuẩn bị giáo cụ, nhạc, dụng cụ đầy đủ và thực hiện đúng phương pháp sư phạm không? (Chú ý cả sự chủ động, thuộc vận động mẫu, thao tác mẫu cho trẻ…)", 20),

("Do you ensure children's safety during all learning and outdoor play activities? (No accidents, unsafe play, or lack of safety tools…)",
"Bạn có đảm bảo an toàn cho trẻ trong suốt các hoạt động học tập và vui chơi ngoài trời không? (Không để xảy ra tai nạn, trẻ chơi sai cách, thiếu dụng cụ an toàn…)", 20),

("For boarding care: Do you maintain hygiene during mealtime, distribute food in the correct portions, and support children to eat enough according to the menu?",
"Công tác bán trú: Bạn có đảm bảo vệ sinh giờ ăn, chia thức ăn đúng khẩu phần, hỗ trợ trẻ ăn đủ định lượng và đủ món theo thực đơn không?", 20),

("Do you ensure personal hygiene, sleep, clothing, toilet routines, and clean handling of personal items for children?",
"Bạn có đảm bảo công tác chăm sóc trẻ: vệ sinh cá nhân, giấc ngủ, trang phục, hỗ trợ trẻ đi vệ sinh đúng quy trình và xử lý đồ dùng cá nhân sạch sẽ không?", 20),

("Did any child experience weight loss, no weight gain, or health issues this month due to your fault?",
"Trong tháng, có tình trạng trẻ bị sụt cân, không lên cân, hoặc sức khỏe trẻ bị ảnh hưởng do lỗi của bạn không?", 10),

("Do you complete all assigned extra duties such as updating the app, submitting assignments on time, and fully participating in festivals and meetings?",
"Bạn có thực hiện đầy đủ các công việc được phân công thêm: cập nhật app, nộp bài tập chuyên môn đúng hạn, tham gia đầy đủ lễ hội và họp không?", 20),

("Do you collaborate well with parents and colleagues in caring for, educating children, and preserving facilities? (Put toys away, keep areas clean, work with parents to solve children's issues…)",
"Bạn có phối hợp tốt với phụ huynh và đồng nghiệp trong công tác chăm sóc, giáo dục trẻ và bảo quản cơ sở vật chất không? (Cất đồ chơi đúng chỗ, giữ vệ sinh khu vực phụ trách, phối hợp phụ huynh giải quyết các vấn đề của trẻ…)", 20),

("Have you been negatively reported by parents, caught on camera, or caused incidents that harmed the school's reputation this month?",
"Trong tháng, bạn có bị phụ huynh/phản ánh tiêu cực, bị trích xuất camera, hoặc để xảy ra sự cố ảnh hưởng uy tín nhà trường không?", 10);

-- Insert admin mặc định
INSERT INTO tk (ten_tk, nhom, mat_khau, ngay_tao, nguoi_tao) VALUES 
('admin', 'admin', 'scrypt:32768:8:1$HhkGxlkkMqAfpk0k$16c91ae47fcd5d6c4f4a4f7c5a7c6e7b8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0', curdate(), 'system');

-- Commit tất cả thay đổi
COMMIT;