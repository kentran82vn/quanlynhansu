let epaTitleValue = "";

document.addEventListener("DOMContentLoaded", () => {
    console.log("[INFO] Load data EPA từ file...");
    loadDataFromFile();
});

function loadDataFromFile(){
    fetch('/api/epa/user-score-load')
    .then(res => res.json())
    .then(resData => {
        if (!resData.success) {
            alert("Cannot load your EPA data.");
            return;
        }
        // Đổ nguyên content file HTML vào khung riêng
        document.getElementById('file_content').innerHTML = resData.content;
        const oldAnswers = extractAnswersFromHtml(resData.content);
        fetch('/api/epa/questions')
        .then(res => res.json())
        .then(qData => {
            if (!qData.success) return;
            renderQuestions(oldAnswers, qData.questions);
        });
    });
}


function extractAnswersFromHtml(content) {
    const result = [];
    const pattern = /<strong>Question \d+: (.*?)<\/strong><br>Answer: (.*?)<br>Score: (\d)\/5<\/p>/g;
    let match;
    while ((match = pattern.exec(content)) !== null) {
        result.push({
            question: match[1],
            answer: match[2],
            score: match[3]
        });
    }
    return result;
}

function renderQuestions(oldAnswers = []) {
    fetch('/api/epa/questions')
    .then(res => res.json())
    .then(data => {
        if (!data.success) return;
        const questions = data.questions;
        const container = document.getElementById('questionnaire');

        container.innerHTML = '';

        questions.forEach((q, idx) => {
            const oldAnswer = oldAnswers[idx]?.answer || "";
            const oldScore = oldAnswers[idx]?.score || 3;

            const block = document.createElement('div');
            block.className = 'question-block';

            block.innerHTML = `
                <div class="mb-2 question-text">Question ${idx + 1}: ${q.question}</div>
                <div class="mb-2 translation">(Câu hỏi: ${q.translate})</div>
                <div class="mb-2">
                    <textarea class="form-control" rows="2">${oldAnswer}</textarea>
                </div>
                <div>
                    <label>Score:</label>
                    <select class="form-select score-select" style="width: 100px; display: inline-block; margin-left: 10px;">
                        ${[1,2,3,4,5].map(v => `<option value="${v}" ${v == oldScore ? 'selected' : ''}>${v}</option>`).join('')}
                    </select>
                </div>
                <hr>
            `;
            container.appendChild(block);
        });
    });
}
