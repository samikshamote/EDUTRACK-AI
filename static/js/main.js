document.addEventListener("DOMContentLoaded", function () {

    // ===== ATTENDANCE PIE CHART =====
    const attendanceCanvas = document.getElementById("attendanceChart");

    if (attendanceCanvas) {
        const attendanceCtx = attendanceCanvas.getContext("2d");

        new Chart(attendanceCtx, {
            type: "pie",
            data: {
                labels: ["Present", "Absent"],
                datasets: [{
                    data: [PRESENT_COUNT, ABSENT_COUNT],
                    backgroundColor: ["#4CAF50", "#F44336"]
                }]
            },
            options: {
                responsive: true
            }
        });
    }

    // ===== SUBJECT-WISE BAR CHART =====
    const subjectCanvas = document.getElementById("subjectChart");

    if (subjectCanvas) {
        const subjectCtx = subjectCanvas.getContext("2d");

        new Chart(subjectCtx, {
            type: "bar",
            data: {
                labels: SUBJECT_LABELS,
                datasets: [{
                    label: "Attendance %",
                    data: SUBJECT_PERCENTAGES,
                    backgroundColor: "#2196F3"
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

});

.timetable-container {
    overflow-x: auto;
    margin-top: 20px;
}

.timetable-table {
    width: 100%;
    border-collapse: collapse;
    background: white;
    border-radius: 10px;
    overflow: hidden;
}

.timetable-table th {
    background: #1e293b;
    color: white;
    padding: 12px;
    text-align: center;
}

.timetable-table td {
    border: 1px solid #e2e8f0;
    padding: 15px;
    text-align: center;
    vertical-align: middle;
}

.time-col {
    font-weight: 600;
    background: #f1f5f9;
}

.subject-box {
    background: #e0f2fe;
    padding: 8px;
    border-radius: 6px;
}
