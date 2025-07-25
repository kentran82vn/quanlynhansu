-- MySQL dump 10.13  Distrib 8.0.43, for Win64 (x86_64)
--
-- Host: localhost    Database: quanlytruonghoc_app
-- ------------------------------------------------------
-- Server version	8.0.43

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `bangdanhgia`
--

DROP TABLE IF EXISTS `bangdanhgia`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
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
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bangdanhgia`
--

LOCK TABLES `bangdanhgia` WRITE;
/*!40000 ALTER TABLE `bangdanhgia` DISABLE KEYS */;
/*!40000 ALTER TABLE `bangdanhgia` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cauhoi_epa`
--

DROP TABLE IF EXISTS `cauhoi_epa`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cauhoi_epa` (
  `id` int NOT NULL AUTO_INCREMENT,
  `question` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `translate` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cauhoi_epa`
--

LOCK TABLES `cauhoi_epa` WRITE;
/*!40000 ALTER TABLE `cauhoi_epa` DISABLE KEYS */;
INSERT INTO `cauhoi_epa` VALUES (4,'Bạn có chấp hành nghiêm túc giờ giấc làm việc trong tháng này không?\n(Đi trễ, nghỉ không phép, không tham gia sinh hoạt chung…)',''),(5,'Bạn có thực hiện đầy đủ và đúng quy trình các hoạt động chuyên môn: lễ giáo, sinh hoạt đầu tuần, thể dục sáng, hoạt động học, hoạt động góc, hoạt động ngoài trời không ?',''),(6,'Trong các hoạt động chuyên môn, bạn có chuẩn bị giáo cụ, nhạc, dụng cụ đầy đủ và thực hiện đúng phương pháp sư phạm không?\n(Chú ý cả sự chủ động, thuộc vận động mẫu, thao tác mẫu cho trẻ…)',''),(7,'Bạn có đảm bảo an toàn cho trẻ trong suốt các hoạt động học tập và vui chơi ngoài trời không ?\n(Không để xảy ra tai nạn, trẻ chơi sai cách, thiếu dụng cụ an toàn…)',''),(8,'Công tác bán trú: Bạn có đảm bảo vệ sinh giờ ăn, chia thức ăn đúng khẩu phần, hỗ trợ trẻ ăn đủ định lượng và đủ món theo thực đơn không ?',''),(9,'Bạn có đảm bảo công tác chăm sóc trẻ: vệ sinh cá nhân, giấc ngủ, trang phục, hỗ trợ trẻ đi vệ sinh đúng quy trình và xử lý đồ dùng cá nhân sạch sẽ không ?',''),(10,'Trong tháng, có tình trạng trẻ bị sụt cân, không lên cân, hoặc sức khỏe trẻ bị ảnh hưởng do lỗi của bạn không ?',''),(11,'Bạn có thực hiện đầy đủ các công việc được phân công thêm: cập nhật app, nộp bài tập chuyên môn đúng hạn, tham gia đầy đủ lễ hội và họp không ?',''),(12,'Bạn có phối hợp tốt với phụ huynh và đồng nghiệp trong công tác chăm sóc, giáo dục trẻ và bảo quản cơ sở vật chất không ?\n(Cất đồ chơi đúng chỗ, giữ vệ sinh khu vực phụ trách, phối hợp phụ huynh giải quyết các vấn đề của trẻ…)',''),(13,'Trong tháng, bạn có bị phụ huynh/phản ánh tiêu cực, bị trích xuất camera, hoặc để xảy ra sự cố ảnh hưởng uy tín nhà trường không ?','');
/*!40000 ALTER TABLE `cauhoi_epa` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ds_lop`
--

DROP TABLE IF EXISTS `ds_lop`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ds_lop` (
  `ma_lop` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `ten_lop` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  PRIMARY KEY (`ma_lop`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ds_lop`
--

LOCK TABLES `ds_lop` WRITE;
/*!40000 ALTER TABLE `ds_lop` DISABLE KEYS */;
INSERT INTO `ds_lop` VALUES ('Bee','Bee'),('Bird 1','Bird 1'),('Bird 2','Bird 2'),('Cat','Cat'),('Pig','Pig'),('Tiger 1','Tiger 1'),('Tiger 2','Tiger 2');
/*!40000 ALTER TABLE `ds_lop` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `giaovien`
--

DROP TABLE IF EXISTS `giaovien`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `giaovien` (
  `ma_gv` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `ho_va_ten` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `ten_tk` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `chuc_vu` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `ngay_sinh` date DEFAULT NULL,
  `que_quan` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `cccd` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `ngay_cap` date DEFAULT NULL,
  `mst` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `cmnd` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `so_bh` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `sdt` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `tk_nh` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `email` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `nhom_mau` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `dia_chi` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  PRIMARY KEY (`ma_gv`),
  UNIQUE KEY `ten_tk` (`ten_tk`),
  CONSTRAINT `giaovien_ibfk_1` FOREIGN KEY (`ten_tk`) REFERENCES `tk` (`ten_tk`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `giaovien`
--

LOCK TABLES `giaovien` WRITE;
/*!40000 ALTER TABLE `giaovien` DISABLE KEYS */;
INSERT INTO `giaovien` VALUES ('GV00001','Nguyễn Văn K','k.tk','giáo viên','2001-11-08','none','123456789012','2011-12-08','00983401','281297130','18271371','033331231','1273912712','','A','none');
/*!40000 ALTER TABLE `giaovien` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `hocsinh`
--

DROP TABLE IF EXISTS `hocsinh`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `hocsinh` (
  `ma_hs` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `ma_gv` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `ma_lop` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `ho_va_ten` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `ngay_sinh` date DEFAULT NULL,
  `dan_toc` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `ma_dinh_danh` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `ho_ten_bo` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `nghe_nghiep_bo` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `ho_ten_me` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `nghe_nghiep_me` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `ho_khau` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `cccd_bo_me` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `sdt` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `gioi_tinh` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`ma_hs`),
  KEY `ma_lop` (`ma_lop`),
  KEY `idx_hocsinh_ma_gv` (`ma_gv`),
  CONSTRAINT `hocsinh_ibfk_1` FOREIGN KEY (`ma_lop`) REFERENCES `ds_lop` (`ma_lop`),
  CONSTRAINT `hocsinh_ibfk_2` FOREIGN KEY (`ma_gv`) REFERENCES `giaovien` (`ma_gv`),
  CONSTRAINT `chk_gioi_tinh` CHECK ((`gioi_tinh` in (_utf8mb4'Nam',_utf8mb4'Nữ')))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `hocsinh`
--

LOCK TABLES `hocsinh` WRITE;
/*!40000 ALTER TABLE `hocsinh` DISABLE KEYS */;
INSERT INTO `hocsinh` VALUES ('HS0001',NULL,NULL,'Trần Bùi Bảo Hân','2019-11-06','Kinh','1319027148','Trần Văn Quân','Tài xế','Bùi T Thanh Tâm','Buôn bán','Phú Xuyên-HN','1080046867','943108127','Nữ'),('HS0002',NULL,NULL,'Nguyễn Ngọc Hân','2019-12-25','Kinh','68319004493','Nguyễn Minh Tường','Kinh doanh','Nguyễn Thanh Hiền','Bác sĩ','Tân Trung-Tân Hà','68195003930','369085268','Nữ'),('HS0003',NULL,NULL,'Ngô Huỳnh Phúc Hưng ','2019-07-22','Kinh','68219010383','Ngô Thanh Xuân','Tự do','Huỳnh Thị Thắm','Giáo viên','Văn Tâm','49191006461','327345845','Nam'),('HS0004',NULL,NULL,'Dương Đăng Khôi','2019-01-29','Kinh','68219003176','Dương Trung Thạnh','Kinh doanh','Trịnh Thị Hà','Kế toán','Quảng Đức','11900453558','972282708','Nam'),('HS0005',NULL,NULL,'Tô Nhật Minh','2019-03-26','Kinh','68219003997','Tô Thành Tánh','Nông','Nguyễn Thị Kim Ly','Nông','Tân Thành-TV','60091015331','383050052','Nam'),('HS0006',NULL,NULL,'Mai Ngọc Nhiên','2019-12-18','Kinh','68319001500','Mai Văn Hiền','Cơ khí','Trần Thị Hằng','Nông','CoYa','36190017299','984292094','Nữ'),('HS0007',NULL,NULL,'Hoàng Trần An Nhiên','2019-11-08','Kinh','68319003177','Hoàng Xuân Tiên','Nông','Trần Thị Hoa','Nội trợ','Quảng Đức','40199021238','792281703','Nữ'),('HS0008',NULL,NULL,'Nguyễn Đình Gia Phúc','2019-05-16','Kinh','1219027433','Nguyễn Đình Nhân','CT Cấp nước ','Trần T Th. Huyền','CT Cấp nước ','Sê Nhắc','19179013442','02633.506.924','Nam'),('HS0009',NULL,NULL,'Đỗ Phương Thảo','2019-02-21','Kinh','68319013032','Đỗ Danh Hưởng','Tự do','Nguyễn Thị Huế','CNV','Quảng Đức','68184002360','917179787','Nữ'),('HS0010',NULL,NULL,'Vũ Ngọc Thanh Trúc','2019-11-09','Kinh','68319000536','Vũ Mạnh Trinh','Kinh doanh','Đinh Thị Phương Anh','Giáo viên','Quảng Đức','1184045829','965974333','Nữ'),('HS0011',NULL,NULL,'Trần Ngọc Thảo Vy','2019-06-23','Kinh','68319002166','Trần Ngọc Thảo','Nhân viên','Nguyễn Thị Thảo','Nhân viên','Đarơmăng','52191014281','986955026','Nữ'),('HS0012',NULL,NULL,'Phạm Ngọc Huy','2020-12-20','Kinh','68220004411','Phạm Ngọc Tuân','Công an','Phạm Thị Mỹ Ngân','Công an','Quảng Đức','68102004934','868207992','Nam'),('HS0013',NULL,NULL,'Bùi Gia Hân','2020-08-13','Kinh','đang cập nhật','Bùi Mạnh Hiệp','Lái xe','Vy Thị Thảo Phương','Giáo viên','Tân Lợi - TV','68194000913','397084438','Nữ'),('HS0014',NULL,NULL,'Võ Kiệt Luân','2020-07-06','Kinh','68220006200','Võ Nguyên Văn','NVVP','Phùng T Như Ngọc','Tự do','Quảng Đức','68195009095','972237797','Nam'),('HS0015',NULL,NULL,'Trần Ngọc Bảo Trân','2020-01-19','Kinh','68320005857','Trần Sỹ Biển','CNV','Trần Thị Hương','Giáo viên','Văn Tâm','40180023812','914248600','Nữ');
/*!40000 ALTER TABLE `hocsinh` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `hocsinh_backup`
--

DROP TABLE IF EXISTS `hocsinh_backup`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `hocsinh_backup` (
  `ma_hs` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `ma_gv` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `ma_lop` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `ho_va_ten` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `ngay_sinh` date DEFAULT NULL,
  `dan_toc` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `ma_dinh_danh` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `ho_ten_bo` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `nghe_nghiep_bo` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `ho_ten_me` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `nghe_nghiep_me` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `ho_khau` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `cccd_bo_me` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `sdt` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `gioi_tinh` enum('Nam','N?') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`ma_hs`),
  KEY `ma_lop` (`ma_lop`),
  KEY `idx_hocsinh_ma_gv` (`ma_gv`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `hocsinh_backup`
--

LOCK TABLES `hocsinh_backup` WRITE;
/*!40000 ALTER TABLE `hocsinh_backup` DISABLE KEYS */;
/*!40000 ALTER TABLE `hocsinh_backup` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `logs`
--

DROP TABLE IF EXISTS `logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `logs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_ten_tk` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `target_staff_id` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `target_table` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `action` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_ten_tk` (`user_ten_tk`),
  CONSTRAINT `logs_ibfk_1` FOREIGN KEY (`user_ten_tk`) REFERENCES `tk` (`ten_tk`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=55 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `logs`
--

LOCK TABLES `logs` WRITE;
/*!40000 ALTER TABLE `logs` DISABLE KEYS */;
INSERT INTO `logs` VALUES (1,'admin','HS001','hocsinh','Added student None','2025-06-28 07:03:38'),(2,'admin','TEST001','hocsinh','Deleted record TEST001','2025-06-28 07:28:37'),(3,'admin','TEST007','hocsinh','Deleted record TEST007','2025-06-28 07:28:40'),(4,'admin','HS001','hocsinh','Deleted record HS001','2025-06-28 07:29:00'),(5,NULL,NULL,'tk','Updated role for \'kimnhung\' to \'admin\'','2025-06-28 08:53:54'),(6,NULL,NULL,'tk','Updated role for \'hoangtran\' to \'supervisor\'','2025-06-28 08:54:06'),(7,'admin','ngocnguyen','tk','Changed password','2025-06-28 08:54:50'),(8,'admin','hoangtran','tk','Changed password','2025-06-28 08:55:07'),(9,NULL,NULL,'tk','Added new user \'nguyenthao\' with role \'user\'','2025-06-29 13:09:15'),(10,'admin','anhtho','tk','Changed password','2025-06-29 13:11:06'),(12,NULL,NULL,'tk','Deleted user \'huongphuong\' by admin','2025-06-29 13:24:02'),(13,NULL,NULL,'tk','Updated role for \'ngocquy\' to \'admin\'','2025-06-30 02:39:45'),(14,'admin','ngocquy','tk','Changed password','2025-06-30 02:39:58'),(15,'admin','hoangtran','tk','Changed password','2025-07-14 00:59:45'),(16,'admin','admin','tk','Changed password','2025-07-14 01:03:34'),(17,'admin','kimnhung','tk','Reset password','2025-07-14 01:07:20'),(18,'kimnhung','kdien','tk','Reset password','2025-07-14 01:13:36'),(20,'admin','kimoanh','tk','Reset password','2025-07-14 01:34:20'),(21,NULL,NULL,'tk','Updated role for \'hoangtran\' to \'user\'','2025-07-14 16:27:50'),(22,NULL,NULL,'tk','Deleted user \'nguyenthao\' by kimnhung','2025-07-14 16:38:11'),(23,NULL,NULL,'tk','Deleted user \'hoangtran\' by kimnhung','2025-07-14 16:38:19'),(24,'kimnhung','admin','tk','Reset password','2025-07-14 16:38:49'),(25,NULL,NULL,'tk','Deleted user \'ngocnguyen\' by admin','2025-07-14 16:46:59'),(26,NULL,NULL,'tk','Deleted user \'thuuyen\' by kimnhung','2025-07-16 10:00:57'),(27,NULL,NULL,'tk','Added new user \'nguyenthao1991\' with role \'user\'','2025-07-21 12:58:10'),(28,NULL,NULL,'tk','Added new user \'ccac\' with role \'user\'','2025-07-24 11:36:53'),(29,NULL,NULL,'tk','Deleted user \'ccac\' and related data by kimnhung','2025-07-24 11:52:13'),(30,'kimnhung','GV00001','giaovien','Added GV staff Nguyen A','2025-07-24 12:02:33'),(31,'kimnhung','HS00001','hocsinh','Added student Tien Tran','2025-07-24 12:04:38'),(32,NULL,NULL,'tk','Added new user \'nhahah\' with role \'user\'','2025-07-24 12:05:15'),(33,NULL,NULL,'tk','Deleted user \'nhahah\' and related data by kimnhung','2025-07-24 12:05:34'),(34,NULL,NULL,'tk','Deleted user \'anhtho\' and related data by kimnhung','2025-07-24 12:57:27'),(35,NULL,NULL,'tk','Deleted user \'kimoanh\' and related data by kimnhung','2025-07-24 12:57:32'),(36,NULL,NULL,'tk','Deleted user \'hannguyen\' and related data by kimnhung','2025-07-24 12:57:58'),(37,NULL,NULL,'tk','Deleted user \'ngocphuong\' and related data by kimnhung','2025-07-24 12:58:04'),(38,NULL,NULL,'tk','Deleted user \'thanhhuyen\' and related data by kimnhung','2025-07-24 12:58:09'),(39,NULL,NULL,'tk','Deleted user \'ksira\' and related data by kimnhung','2025-07-24 12:58:15'),(40,NULL,NULL,'tk','Deleted user \'kdien\' and related data by admin','2025-07-24 17:36:46'),(41,NULL,NULL,'tk','Deleted user \'hangnguyen\' and related data by admin','2025-07-24 17:50:37'),(42,NULL,NULL,'tk','Deleted user \'ngocba\' and related data by admin','2025-07-24 17:50:42'),(43,NULL,NULL,'tk','Deleted user \'thamtran\' and related data by admin','2025-07-24 17:50:48'),(44,NULL,NULL,'tk','Deleted user \'thanhtuyen\' and related data by admin','2025-07-24 17:51:20'),(45,NULL,NULL,'tk','Deleted user \'tronghung\' and related data by admin','2025-07-24 17:51:24'),(46,NULL,NULL,'tk','Deleted user \'nguyenthao1991\' and related data by admin','2025-07-24 17:51:34'),(47,NULL,NULL,'tk','Added new user \'nguyenthao\' with role \'user\'','2025-07-24 17:54:08'),(48,'kimnhung','nan','hocsinh','Deleted record nan','2025-07-24 18:28:28'),(49,'kimnhung','nan','hocsinh','Deleted record nan','2025-07-24 18:28:41'),(50,NULL,NULL,'tk','Deleted user \'nguyenthao\' and related data by kimnhung','2025-07-24 18:30:51'),(51,'kimnhung','ngocquy','tk','Reset password','2025-07-24 18:34:44'),(52,NULL,NULL,'tk','Added new user \'thao\' with role \'user\'','2025-07-25 03:26:53'),(53,'kimnhung','k.tk','tk','Created login account for teacher','2025-07-25 18:08:34'),(54,'kimnhung','GV00001','giaovien','Added GV staff Nguyễn Văn K','2025-07-25 18:08:34');
/*!40000 ALTER TABLE `logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `lop_gv`
--

DROP TABLE IF EXISTS `lop_gv`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `lop_gv` (
  `ma_lop` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `ma_gv` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `vai_tro` enum('GVCN','B??? m??n','B???o m???u') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (`ma_lop`,`ma_gv`),
  KEY `idx_lop_gv_ma_gv` (`ma_gv`),
  CONSTRAINT `lop_gv_ibfk_1` FOREIGN KEY (`ma_lop`) REFERENCES `ds_lop` (`ma_lop`),
  CONSTRAINT `lop_gv_ibfk_2` FOREIGN KEY (`ma_gv`) REFERENCES `giaovien` (`ma_gv`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lop_gv`
--

LOCK TABLES `lop_gv` WRITE;
/*!40000 ALTER TABLE `lop_gv` DISABLE KEYS */;
/*!40000 ALTER TABLE `lop_gv` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `phan_lop`
--

DROP TABLE IF EXISTS `phan_lop`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `phan_lop` (
  `ma_hs` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `ma_lop` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  PRIMARY KEY (`ma_hs`),
  KEY `idx_phan_lop_ma_lop` (`ma_lop`),
  CONSTRAINT `phan_lop_ibfk_1` FOREIGN KEY (`ma_hs`) REFERENCES `hocsinh` (`ma_hs`),
  CONSTRAINT `phan_lop_ibfk_2` FOREIGN KEY (`ma_lop`) REFERENCES `ds_lop` (`ma_lop`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `phan_lop`
--

LOCK TABLES `phan_lop` WRITE;
/*!40000 ALTER TABLE `phan_lop` DISABLE KEYS */;
/*!40000 ALTER TABLE `phan_lop` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `stats`
--

DROP TABLE IF EXISTS `stats`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `stats` (
  `id` int NOT NULL AUTO_INCREMENT,
  `stat_date` date NOT NULL,
  `team` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `count` int NOT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `stats`
--

LOCK TABLES `stats` WRITE;
/*!40000 ALTER TABLE `stats` DISABLE KEYS */;
/*!40000 ALTER TABLE `stats` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `thoigianmoepa`
--

DROP TABLE IF EXISTS `thoigianmoepa`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `thoigianmoepa` (
  `id` int NOT NULL AUTO_INCREMENT,
  `ten_tk` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `start_day` int NOT NULL,
  `close_day` int NOT NULL,
  `remark` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
  `make_epa_gv` enum('yes','no') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT 'no',
  `make_epa_tgv` enum('yes','no') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT 'no',
  `make_epa_all` enum('yes','no') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT 'no',
  PRIMARY KEY (`id`),
  KEY `ten_tk` (`ten_tk`),
  CONSTRAINT `thoigianmoepa_ibfk_1` FOREIGN KEY (`ten_tk`) REFERENCES `giaovien` (`ten_tk`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `thoigianmoepa`
--

LOCK TABLES `thoigianmoepa` WRITE;
/*!40000 ALTER TABLE `thoigianmoepa` DISABLE KEYS */;
/*!40000 ALTER TABLE `thoigianmoepa` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tk`
--

DROP TABLE IF EXISTS `tk`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tk` (
  `ten_tk` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `nhom` enum('admin','user','supervisor') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `mat_khau` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `ngay_tao` date DEFAULT NULL,
  `nguoi_tao` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `ngay_hh` date DEFAULT NULL,
  PRIMARY KEY (`ten_tk`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tk`
--

LOCK TABLES `tk` WRITE;
/*!40000 ALTER TABLE `tk` DISABLE KEYS */;
INSERT INTO `tk` VALUES ('admin','admin','scrypt:32768:8:1$Nc6vkzB7Dr64Ga4r$39fb51ccbe4e28275835e7b4c8a7410d0c32210651d7d15b7895591d0e544696cefa1bdd2db3e3284bdb108290410f24607e8bfec8ae65223a595e19b5d5b489','2025-06-28','system',NULL),('k.tk','user',NULL,NULL,NULL,NULL),('kimnhung','admin','scrypt:32768:8:1$85lyZTwYscM9BRUZ$0aa62d223d201aef1529c8b914f504cb2a71af54339f55c30af95bd8f1bf6f4c5d3df6e67961a26322cb70df58dd5724f1a78af98d0ad67f74ac0cefab175015','2025-06-28',NULL,NULL),('ngocquy','admin','scrypt:32768:8:1$y6Coq8rk4XjhlqT8$29cf664ee77830987005c1f98fce3a3c0701d6f8e6f9c3274025855c7ddbf7dd638ce08bc7d68a9b8edf3e2ea198c247104613482b37c6311bfa6df7837e0124','2025-06-28',NULL,NULL),('thao','user','scrypt:32768:8:1$blUKkZO8nul3oPSi$aeff2e395dbe5a4bdb53eed2b3286b8d8e38147431870936cb09cae017bd62f34b87b9cbd246a4711ee3260d9f991bc030edee8a9c62344756d6c4e1ba799ecb','2025-07-25','kimnhung','2025-10-23');
/*!40000 ALTER TABLE `tk` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tongdiem_epa`
--

DROP TABLE IF EXISTS `tongdiem_epa`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tongdiem_epa` (
  `id` int NOT NULL AUTO_INCREMENT,
  `ten_tk` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `year` int NOT NULL,
  `month` int NOT NULL,
  `user_total_score` int DEFAULT '0',
  `sup_total_score` int DEFAULT '0',
  `pri_total_score` int DEFAULT NULL,
  `pri_comment` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_user_month` (`ten_tk`,`year`,`month`),
  CONSTRAINT `tongdiem_epa_ibfk_1` FOREIGN KEY (`ten_tk`) REFERENCES `tk` (`ten_tk`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tongdiem_epa`
--

LOCK TABLES `tongdiem_epa` WRITE;
/*!40000 ALTER TABLE `tongdiem_epa` DISABLE KEYS */;
/*!40000 ALTER TABLE `tongdiem_epa` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'quanlytruonghoc_app'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-07-25 18:18:12
