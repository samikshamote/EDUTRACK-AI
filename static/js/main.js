// ===== Attendance Overview Chart =====
const attendanceCtx = document.getElementById('attendanceChart');

if (attendanceCtx) {
    new Chart(attendanceCtx, {
        type: 'doughnut',
        data: {
            labels: ['Present', 'Absent'],
            datasets: [{
                data: [PRESENT_COUNT, ABSENT_COUNT],
                backgroundColor: ['#198754', '#dc3545']
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// ===== Subject-wise Attendance Chart =====
const subjectCtx = document.getElementById('subjectChart');

if (subjectCtx) {
    new Chart(subjectCtx, {
        type: 'bar',
        data: {
            labels: SUBJECT_LABELS,
            datasets: [{
                label: 'Attendance %',
                data: SUBJECT_PERCENTAGES,
                backgroundColor: '#0d6efd'
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
}
