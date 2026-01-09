from django.shortcuts import render
import subprocess
import sys
import os
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from students.models import Student
from attendance.models import Attendance, Subject
from django.utils import timezone

@login_required
def teacher_dashboard(request):
    return render(request, 'teachers/dashboard.html')


@login_required
def start_attendance(request):
    # Get project root directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Path to recognize.py
    script_path = os.path.join(
        base_dir,
        "face_recognition_engine",
        "recognize.py"
    )

    # Run face recognition script
    subprocess.Popen([sys.executable, script_path])

    return HttpResponse("Camera started. Attendance is being marked.")


@login_required
def save_attendance(request, subject_id):
    subject = Subject.objects.get(id=subject_id)

    file_path = "face_recognition_engine/recognized_today.txt"

    if not os.path.exists(file_path):
        return HttpResponse("No attendance data found.")

    with open(file_path, "r") as f:
        names = f.read().splitlines()

    for name in names:
        try:
            student = Student.objects.get(user__username=name)

            Attendance.objects.get_or_create(
                student=student,
                subject=subject,
                date=timezone.now().date(),
                defaults={"status": True}
            )
        except Student.DoesNotExist:
            continue

    # Clear file after saving
    open(file_path, "w").close()

    return HttpResponse("Attendance saved successfully.")

