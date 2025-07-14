SELECT * FROM quanlytruonghoc_app.cauhoi_epa;
USE quanlytruonghoc_app;
CREATE TABLE cauhoi_epa (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question TEXT NOT NULL,
    translate TEXT
);
SET SQL_SAFE_UPDATES = 0;
DELETE FROM cauhoi_epa;
ALTER TABLE cauhoi_epa AUTO_INCREMENT = 1;
SET SQL_SAFE_UPDATES = 1; -- Bật lại nếu cần
INSERT INTO cauhoi_epa (question, translate) VALUES
("Do you strictly comply with working hours this month? (Late arrivals, unpermitted absences, non-participation in collective activities…)",
"Bạn có chấp hành nghiêm túc giờ giấc làm việc trong tháng này không? (Đi trễ, nghỉ không phép, không tham gia sinh hoạt chung…)"),

("Do you fully and correctly implement professional activities: etiquette, weekly activities, morning exercise, learning activities, corner activities, and outdoor activities?",
"Bạn có thực hiện đầy đủ và đúng quy trình các hoạt động chuyên môn: lễ giáo, sinh hoạt đầu tuần, thể dục sáng, hoạt động học, hoạt động góc, hoạt động ngoài trời không?"),

("Do you prepare teaching aids, music, and tools sufficiently and follow proper teaching methods in professional activities? (Be proactive, memorize demonstration movements, model activities for children…)",
"Trong các hoạt động chuyên môn, bạn có chuẩn bị giáo cụ, nhạc, dụng cụ đầy đủ và thực hiện đúng phương pháp sư phạm không? (Chú ý cả sự chủ động, thuộc vận động mẫu, thao tác mẫu cho trẻ…)"),

("Do you ensure children’s safety during all learning and outdoor play activities? (No accidents, unsafe play, or lack of safety tools…)",
"Bạn có đảm bảo an toàn cho trẻ trong suốt các hoạt động học tập và vui chơi ngoài trời không? (Không để xảy ra tai nạn, trẻ chơi sai cách, thiếu dụng cụ an toàn…)"),

("For boarding care: Do you maintain hygiene during mealtime, distribute food in the correct portions, and support children to eat enough according to the menu?",
"Công tác bán trú: Bạn có đảm bảo vệ sinh giờ ăn, chia thức ăn đúng khẩu phần, hỗ trợ trẻ ăn đủ định lượng và đủ món theo thực đơn không?"),

("Do you ensure personal hygiene, sleep, clothing, toilet routines, and clean handling of personal items for children?",
"Bạn có đảm bảo công tác chăm sóc trẻ: vệ sinh cá nhân, giấc ngủ, trang phục, hỗ trợ trẻ đi vệ sinh đúng quy trình và xử lý đồ dùng cá nhân sạch sẽ không?"),

("Did any child experience weight loss, no weight gain, or health issues this month due to your fault?",
"Trong tháng, có tình trạng trẻ bị sụt cân, không lên cân, hoặc sức khỏe trẻ bị ảnh hưởng do lỗi của bạn không?"),

("Do you complete all assigned extra duties such as updating the app, submitting assignments on time, and fully participating in festivals and meetings?",
"Bạn có thực hiện đầy đủ các công việc được phân công thêm: cập nhật app, nộp bài tập chuyên môn đúng hạn, tham gia đầy đủ lễ hội và họp không?"),

("Do you collaborate well with parents and colleagues in caring for, educating children, and preserving facilities? (Put toys away, keep areas clean, work with parents to solve children’s issues…)",
"Bạn có phối hợp tốt với phụ huynh và đồng nghiệp trong công tác chăm sóc, giáo dục trẻ và bảo quản cơ sở vật chất không? (Cất đồ chơi đúng chỗ, giữ vệ sinh khu vực phụ trách, phối hợp phụ huynh giải quyết các vấn đề của trẻ…)"),

("Have you been negatively reported by parents, caught on camera, or caused incidents that harmed the school's reputation this month?",
"Trong tháng, bạn có bị phụ huynh/phản ánh tiêu cực, bị trích xuất camera, hoặc để xảy ra sự cố ảnh hưởng uy tín nhà trường không?");
