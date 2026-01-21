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
