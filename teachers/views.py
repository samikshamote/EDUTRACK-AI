from django.shortcuts import render, redirect
import subprocess
import sys
import os
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import csv

from students.models import Student
from attendance.models import Attendance, Subject

from .forms import TeacherProfileForm

@login_required
def teacher_dashboard(request):
    # ❌ Block students
    if not hasattr(request.user, 'teacher'):
        return redirect('student_dashboard')

    teacher = request.user.teacher
    today = timezone.now().date()

    # 📘 Subjects taught by this teacher
    subjects = Subject.objects.filter(teacher=teacher)

    subject_stats = []

    for subject in subjects:
        total = Attendance.objects.filter(subject=subject).count()
        present = Attendance.objects.filter(subject=subject, status=True).count()
        absent = Attendance.objects.filter(subject=subject, status=False).count()

        percentage = int((present / total) * 100) if total > 0 else 0

        subject_stats.append({
            'name': subject.name,
            'total': total,
            'present': present,
            'absent': absent,
            'percentage': percentage,
        })

    # 👨‍🎓 TOTAL STUDENTS (unique)
    total_students = Attendance.objects.filter(
        subject__teacher=teacher
    ).values('student').distinct().count()

    # ✅ PRESENT / ❌ ABSENT (overall)
    present_count = Attendance.objects.filter(
        subject__teacher=teacher,
        status=True
    ).count()

    absent_count = Attendance.objects.filter(
        subject__teacher=teacher,
        status=False
    ).count()

    context = {
        'today': today,
        'subject_stats': subject_stats,
        'total_students': total_students,
        'present_count': present_count,
        'absent_count': absent_count,
    }

    return render(request, 'teachers/dashboard.html', context)
@login_required
def start_attendance(request):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    script_path = os.path.join(
        base_dir,
        "face_recognition_engine",
        "recognize.py"
    )

    subprocess.Popen([sys.executable, script_path])
    return HttpResponse("📷 Camera started. Attendance is being marked.")


@login_required
def save_attendance(request):
    subject_id = request.GET.get("subject_id")

    if not subject_id:
        return HttpResponse("❌ Subject not selected")

    try:
        subject = Subject.objects.get(
            id=subject_id,
            teacher=request.user.teacher
        )
    except Subject.DoesNotExist:
        return HttpResponse("❌ Invalid subject")

    file_path = "face_recognition_engine/recognized_today.txt"

    if not os.path.exists(file_path):
        return HttpResponse("❌ No attendance data found")

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

    open(file_path, "w").close()
    return HttpResponse("✅ Attendance saved successfully")


@login_required
def view_attendance(request):
    subject_id = request.GET.get('subject')
    date = request.GET.get('date')
    status = request.GET.get('status')  # 👈 NEW

    records = Attendance.objects.filter(
        subject__teacher=request.user.teacher
    )

    if subject_id:
        records = records.filter(subject_id=subject_id)

    if date:
        records = records.filter(date=date)

    if status == 'present':
        records = records.filter(status=True)
    elif status == 'absent':
        records = records.filter(status=False)

    subjects = Subject.objects.filter(teacher=request.user.teacher)

    return render(request, 'teachers/view_attendance.html', {
        'records': records,
        'subjects': subjects,
        'selected_status': status,
    })



@login_required
def export_attendance_csv(request):
    subject_id = request.GET.get('subject')
    date = request.GET.get('date')

    records = Attendance.objects.filter(
        subject__teacher=request.user.teacher
    )

    if subject_id:
        records = records.filter(subject_id=subject_id)

    if date:
        records = records.filter(date=date)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="attendance.csv"'

    writer = csv.writer(response)
    writer.writerow(['Student', 'Subject', 'Date', 'Status'])

    for record in records:
        writer.writerow([
            record.student.user.username,
            record.subject.name,
            record.date,
            'Present' if record.status else 'Absent'
        ])

    return response

@login_required
def teacher_profile(request):
    if not hasattr(request.user, 'teacher'):
        return redirect('student_dashboard')

    teacher = request.user.teacher

    if request.method == 'POST':
        form = TeacherProfileForm(request.POST, request.FILES, instance=teacher)
        if form.is_valid():
            form.save()
            return redirect('teacher_profile')
    else:
        form = TeacherProfileForm(instance=teacher)

    return render(request, 'teachers/profile.html', {
        'teacher': teacher,
        'form': form
    })

@login_required
def edit_teacher_profile(request):
    teacher = request.user.teacher

    if request.method == 'POST':
        form = TeacherProfileForm(request.POST, request.FILES, instance=teacher)
        if form.is_valid():
            form.save()
            return redirect('teacher_profile')
    else:
        form = TeacherProfileForm(instance=teacher)

    # 👇 THIS IS WHERE THAT LINE GOES
    return render(request, 'teachers/edit_profile.html', {'form': form})
