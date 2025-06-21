import mysql.connector

QUESTIONS = [
    {
        "question": "How do you evaluate your work performance this month?",
        "translate": "Bạn cảm thấy hiệu quả công việc trong tháng qua như thế nào?"
    },
    {
        "question": "Did you complete all assigned tasks?",
        "translate": "Bạn có hoàn thành đủ công việc được giao không?"
    },
    {
        "question": "Did you encounter any difficulties during your work?",
        "translate": "Bạn có gặp khó khăn gì trong quá trình làm việc không?"
    },
    {
        "question": "Did you proactively learn new knowledge?",
        "translate": "Bạn đã chủ động học hỏi thêm kiến thức mới chưa?"
    },
    {
        "question": "Did you make any improvements or changes in your work methods?",
        "translate": "Bạn có cải tiến hay thay đổi gì trong cách làm việc không?"
    },
    {
        "question": "How was your collaboration and support with colleagues?",
        "translate": "Mức độ hợp tác và hỗ trợ đồng nghiệp của bạn ra sao?"
    },
    {
        "question": "Did you share experiences with your colleagues?",
        "translate": "Bạn có chia sẻ kinh nghiệm cho đồng nghiệp không?"
    },
    {
        "question": "How was your work attitude this month?",
        "translate": "Thái độ làm việc của bạn trong tháng qua như thế nào?"
    },
    {
        "question": "Did you contribute any ideas or initiatives to the team?",
        "translate": "Bạn có đóng góp ý tưởng/sáng kiến nào cho team không?"
    },
    {
        "question": "Was your relationship with colleagues good?",
        "translate": "Mối quan hệ với đồng nghiệp có tốt không?"
    },
    {
        "question": "Did you achieve your KPIs or work goals?",
        "translate": "Bạn đã hoàn thành KPI hay mục tiêu công việc chưa?"
    },
    {
        "question": "Did you participate in team activities?",
        "translate": "Bạn có tham gia các hoạt động chung của team không?"
    },
    {
        "question": "Did you proactively take on tasks beyond your main responsibilities?",
        "translate": "Bạn có chủ động nhận việc ngoài phạm vi công việc chính không?"
    },
    {
        "question": "Did you overcome any personal weaknesses this month?",
        "translate": "Bạn đã khắc phục được điểm yếu gì của bản thân trong tháng này?"
    },
    {
        "question": "Are you satisfied with your work results?",
        "translate": "Bạn có hài lòng với kết quả làm việc của mình không?"
    },
    {
        "question": "Do you have any suggestions to improve the work environment?",
        "translate": "Bạn có đề xuất gì để cải thiện môi trường làm việc không?"
    },
    {
        "question": "What are your aspirations for the next month?",
        "translate": "Bạn có mong muốn gì trong tháng tới?"
    },
    {
        "question": "Did you learn anything new from your colleagues?",
        "translate": "Bạn có học hỏi được điều gì mới từ đồng nghiệp không?"
    },
    {
        "question": "Do you have any additional comments about your work or the organization?",
        "translate": "Bạn có chia sẻ gì thêm về công việc hoặc tổ chức không?"
    },
    {
        "question": "How do you assess your personal progress this month?",
        "translate": "Bạn đánh giá mức độ tiến bộ của bản thân trong tháng qua thế nào?"
    }
]

conn = mysql.connector.connect(
    host='localhost',
    user='root',  # hoặc user khác nếu không dùng root
    password='steven2906',
    database='employee_app'
)
cursor = conn.cursor()

# Xóa cũ để tránh trùng lặp
cursor.execute("DELETE FROM epa_questions")

# Insert mới
for q in QUESTIONS:
    cursor.execute("INSERT INTO epa_questions (question, translate) VALUES (%s, %s)", (q["question"], q["translate"]))

conn.commit()
cursor.close()
conn.close()
print("✅ Đã import 20 câu hỏi mặc định vào bảng epa_questions.")
