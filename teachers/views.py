from django.shortcuts import render
import subprocess
import sys
import os
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from students.models import Student
from attendance.models import Attendance, Subject
from django.utils import timezone
from django.shortcuts import redirect
from django.contrib import messages



@login_required
def teacher_dashboard(request):
    teacher = request.user.teacher
    subjects = Subject.objects.filter(teacher=teacher)

    return render(request, 'teachers/dashboard.html', {
        'subjects': subjects
    })

@login_required
def start_attendance(request):
    # Project root directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Define script path FIRST
    script_path = os.path.join(
        base_dir,
        "face_recognition_engine",
        "recognize.py"
    )

    # Clear previous session data
    open("face_recognition_engine/recognized_today.txt", "w").close()

    # Start camera process
    subprocess.Popen([sys.executable, script_path])

    return redirect('teacher_dashboard')



@login_required
def save_attendance(request, subject_id):
    subject_id = request.GET.get("subject_id")
    if not subject_id:
        return HttpResponse("Subject not selected")

    subject = Subject.objects.get(id=subject_id)

    file_path = "face_recognition_engine/recognized_today.txt"

    if not os.path.exists(file_path):
        return HttpResponse("No attendance data found.")

    with open(file_path, "r") as f:
        present_names = f.read().splitlines()

    today = timezone.now().date()

    # Get all students
    all_students = Student.objects.all()

    for student in all_students:
        status = student.user.username in present_names

        Attendance.objects.get_or_create(
            student=student,
            subject=subject,
            date=today,
            defaults={"status": status}
        )

    # Clear file after saving
    open(file_path, "w").close()

    return HttpResponse("Attendance (Present + Absent) saved successfully.")
