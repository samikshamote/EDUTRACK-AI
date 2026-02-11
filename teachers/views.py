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

from attendance.models import Timetable
from django.contrib import messages
from attendance.forms import TimetableForm

from .forms import SubjectForm


@login_required
def teacher_dashboard(request):
    if not hasattr(request.user, 'teacher'):
        return redirect('student_dashboard')

    teacher = request.user.teacher

    # Subjects taught by this teacher
    subjects = Subject.objects.filter(teacher=teacher)

    subject_labels = []
    subject_percentages = []

    for subject in subjects:
        total = Attendance.objects.filter(
            subject=subject,
            subject__teacher=teacher
        ).count()

        present = Attendance.objects.filter(
            subject=subject,
            subject__teacher=teacher,
            status=True
        ).count()

        percentage = int((present / total) * 100) if total > 0 else 0

        subject_labels.append(subject.name)
        subject_percentages.append(percentage)

    total_students = Attendance.objects.filter(
        subject__teacher=teacher
    ).values('student').distinct().count()

    present_count = Attendance.objects.filter(
        subject__teacher=teacher,
        status=True
    ).count()

    absent_count = Attendance.objects.filter(
        subject__teacher=teacher,
        status=False
    ).count()

    context = {
        'subjects': subjects,
        'subject_labels': subject_labels,
        'subject_percentages': subject_percentages,
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

@login_required
def manage_timetable(request):
    if not hasattr(request.user, 'teacher'):
        return redirect('student_dashboard')

    teacher = request.user.teacher

    if request.method == "POST":
        form = TimetableForm(request.POST)
        if form.is_valid():
            timetable = form.save(commit=False)
            timetable.teacher = teacher
            timetable.save()
            return redirect('manage_timetable')
    else:
        form = TimetableForm()

    timetables = Timetable.objects.filter(teacher=teacher)

    return render(request, 'teachers/manage_timetable.html', {
        'form': form,
        'timetables': timetables
    })

@login_required
def timetable_view(request):
    if not hasattr(request.user, 'teacher'):
        return redirect('student_dashboard')

    teacher = request.user.teacher

    subjects = Subject.objects.filter(teacher=teacher)

    return render(request, "teachers/timetable.html", {
        "subjects": subjects
    })


# ===============================
# MANAGE SUBJECTS
# ===============================

@login_required
def manage_subjects(request):
    teacher = request.user.teacher
    subjects = Subject.objects.filter(teacher=teacher)

    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            subject = form.save(commit=False)
            subject.teacher = teacher   # 🔥 attach teacher
            subject.save()
            return redirect('manage_subjects')
    else:
        form = SubjectForm()

    return render(request, 'teachers/manage_subjects.html', {
        'form': form,
        'subjects': subjects
    })



@login_required
def add_subject(request):
    if not hasattr(request.user, 'teacher'):
        return redirect('student_dashboard')

    if request.method == "POST":
        form = SubjectForm(request.POST)
        if form.is_valid():
            subject = form.save(commit=False)
            subject.teacher = request.user.teacher
            subject.save()

    return redirect('manage_subjects')


@login_required
def delete_subject(request, subject_id):
    if not hasattr(request.user, 'teacher'):
        return redirect('student_dashboard')

    subject = Subject.objects.get(
        id=subject_id,
        teacher=request.user.teacher
    )
    subject.delete()

    return redirect('manage_subjects')
