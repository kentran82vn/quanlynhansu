const API_BASE_URL = '/api';
document.addEventListener('DOMContentLoaded', async () => {
    console.log('Sự kiện DOMContentLoaded được kích hoạt');
    if (document.getElementById('non-admin-epa-section')) {
        console.log('Tìm thấy non-admin-epa-section, đang gọi loadYears()');
        await loadYears();
        document.getElementById('year_epa').addEventListener('change', loadEPATable);
    } else {
        console.warn('Không tìm thấy non-admin-epa-section');
    }
});

async function loadYears() {
    try {
        console.log('Đang gửi yêu cầu tới:', `${API_BASE_URL}/epa-years`);
        const response = await fetch(`${API_BASE_URL}/epa-years`);
        console.log('Mã trạng thái:', response.status);
        const data = await response.json();
        console.log('Dữ liệu trả về:', data);
        if (!response.ok) throw new Error(data.message || 'Lỗi khi tải danh sách năm');
        
        const yearSelect = document.getElementById('year_epa');
        yearSelect.innerHTML = '<option value="">-- Chọn Năm --</option>';
        if (!data.years || data.years.length === 0) {
            console.warn('Không có năm nào được trả về từ /epa-years');
            return;
        }
        data.years.forEach(year => {
            yearSelect.innerHTML += `<option value="${year}">${year}</option>`;
        });
    } catch (error) {
        console.error('Lỗi tải danh sách năm:', error);
        document.getElementById('epa-table-body').innerHTML = '<tr><td colspan="7">Lỗi khi tải danh sách năm: ' + error.message + '</td></tr>';
    }
}

async function loadEPATable() {
    const year = document.getElementById('year_epa').value;
    if (!year) {
        document.getElementById('epa-table-body').innerHTML = '<tr><td colspan="7">Vui lòng chọn năm.</td></tr>';
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/epa-data?year=${year}`);
        const data = await response.json();
        if (!response.ok) throw new Error(data.message || 'Lỗi khi tải dữ liệu EPA');

        const tableBody = document.getElementById('epa-table-body');
        if (data.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="7">Không tìm thấy dữ liệu cho năm này.</td></tr>';
            return;
        }

        tableBody.innerHTML = data.map(row => `
            <tr>
                <td>${row.year}</td>
                <td>${row.month}</td>
                <td>${row.user_total_score || 'N/A'}</td>
                <td>${row.sup_total_score || 'N/A'}</td>
                <td>${row.pri_total_score || 'N/A'}</td>
                <td>${row.pri_comment || 'Không có'}</td>
                <td><button onclick="viewAssessment(${row.id})">Xem</button></td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Lỗi tải dữ liệu EPA:', error);
        tableBody.innerHTML = '<tr><td colspan="7">Lỗi khi tải dữ liệu EPA.</td></tr>';
    }
}

function viewAssessment(id) {
    sessionStorage.setItem('epa_id', id);
    window.location.href = 'giaovien_epa.html';
}

async function loadLastAssessment() {
    try {
        const response = await fetch(`${API_BASE_URL}/last-assessment`);
        const data = await response.json();
        debugLog('Kết quả đánh giá trước:', data);
        if (!response.ok) throw new Error(data.message || 'Lỗi khi tải đánh giá');
        const assessmentDiv = document.getElementById('last-assessment');
        const totalScoreTableBody = document.getElementById('total-score-table-body');

        if (data.assessments && data.assessments.length === 0) {
            assessmentDiv.innerHTML = '<p>Không tìm thấy kết quả đánh giá trước đây.</p>';
        } else {
            assessmentDiv.innerHTML = (data.assessments || data).map(a => `
                <div class="assessment-entry">
                    <p class="highlight">Năm: ${a.year}, Tháng: ${a.month}</p>
                    <p><strong>Câu hỏi:</strong> ${a.translate}</p>
                    <p><strong>Điểm tự chấm:</strong> ${a.user_score || 'N/A'}</p>
                    <p><strong>Điểm từ Supervisor:</strong> ${a.sup_score || 'Chưa chấm'}</p>
                    <p><strong>Ý kiến tự đánh giá:</strong> ${a.user_comment || 'Không có ý kiến'}</p>
                    <p><strong>Ý kiến từ Supervisor:</strong> ${a.sup_comment || 'Không có ý kiến'}</p>
                </div>
            `).join('<hr>');
        }

        if (data.total_score) {
            totalScoreTableBody.innerHTML = `
                <tr>
                    <td>${data.total_score.year}</td>
                    <td>${data.total_score.month}</td>
                    <td>${data.total_score.user_total_score || 0}</td>
                    <td>${data.total_score.sup_total_score || 0}</td>
                    <td>${data.total_score.pri_total_score || 'Chưa có'}</td>
                    <td>${data.total_score.pri_comment || 'Chưa có'}</td>
                </tr>
            `;
        } else {
            totalScoreTableBody.innerHTML = '<tr><td colspan="6">Không tìm thấy tổng điểm.</td></tr>';
        }
    } catch (error) {
        debugLog('Lỗi tải đánh giá trước:', error);
        document.getElementById('last-assessment').innerHTML = '<p class="error">Hãy hoàn thành bảng đánh giá tháng.</p>';
        document.getElementById('total-score-table-body').innerHTML = '<tr><td colspan="6">Lỗi khi tải tổng điểm.</td></tr>';
    }
}

function debugLog(...args) {
    console.log('[DEBUG]', ...args);
}