from django.shortcuts import render, redirect
import subprocess
import sys
import os
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from students.models import Student
from django.shortcuts import render, redirect, get_object_or_404
import csv

from students.models import Student
from attendance.models import Attendance, Subject

from .forms import TeacherProfileForm

from attendance.models import Timetable
from django.contrib import messages
from attendance.forms import TimetableForm

from .forms import SubjectForm
from teachers.models import Teacher

from django.db.models import F
from django.shortcuts import get_object_or_404, redirect

from attendance.models import Attendance
from attendance.models import Subject
from django.shortcuts import render


import qrcode
from django.http import HttpResponse
from io import BytesIO



@login_required
def teacher_dashboard(request):
    if not hasattr(request.user, 'teacher'):
        return redirect('student_dashboard')

    teacher = request.user.teacher

    # 🔥 Get all attendance linked through timetable
    attendance_qs = Attendance.objects.filter(
        timetable__teacher=teacher
    )

    # ✅ Correct Counts
    total_students = attendance_qs.values('student').distinct().count()
    present_count = attendance_qs.filter(status=True).count()
    absent_count = attendance_qs.filter(status=False).count()

    # 🔥 Subject-wise percentage
    subjects = Subject.objects.filter(teacher=teacher)

    subject_labels = []
    subject_percentages = []

    for subject in subjects:
        subject_attendance = attendance_qs.filter(subject=subject)

        total = subject_attendance.count()
        present = subject_attendance.filter(status=True).count()

        percentage = int((present / total) * 100) if total > 0 else 0

        subject_labels.append(subject.name)
        subject_percentages.append(percentage)

    context = {
        'total_students': total_students,
        'present_count': present_count,
        'absent_count': absent_count,
        'subjects': subjects,
        'subject_labels': subject_labels,
        'subject_percentages': subject_percentages,
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
    teacher = request.user.teacher

    subjects = Subject.objects.filter(teacher=teacher)

    # 🔥 IMPORTANT FIX
    records = Attendance.objects.filter(
        timetable__teacher=teacher
    ).select_related("student", "subject", "timetable").order_by("-id")

    # Filtering
    subject_id = request.GET.get("subject")
    date = request.GET.get("date")

    if subject_id:
        records = records.filter(subject_id=subject_id)

    if date:
        records = records.filter(date=date)

    return render(request, "teachers/view_attendance.html", {
        "records": records,
        "subjects": subjects
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
    user = request.user  # 🔥 get Django User

    if request.method == 'POST':
        form = TeacherProfileForm(request.POST, request.FILES, instance=teacher)

        if form.is_valid():
            form.save()

            # 🔥 Save email to Django User model
            user.email = request.POST.get("email")
            user.save()

            messages.success(request, "Profile updated successfully!")
            return redirect('teacher_profile')
    else:
        form = TeacherProfileForm(instance=teacher)

    return render(request, 'teachers/edit_profile.html', {
        'form': form,
        'user': user  # 🔥 pass user to template
    })

@login_required
def manage_timetable(request):
    teacher = request.user.teacher

    if request.method == "POST":
        form = TimetableForm(request.POST, teacher=teacher)
        if form.is_valid():
            timetable = form.save(commit=False)
            timetable.teacher = teacher
            timetable.save()
            return redirect('manage_timetable')
    else:
        form = TimetableForm(teacher=teacher)

    timetables = Timetable.objects.filter(
        teacher=teacher
    ).order_by("day", "start_time")

    return render(request, "teachers/manage_timetable.html", {
        "form": form,
        "timetable": timetables
    })



@login_required
def timetable_view(request):

    timetable = Timetable.objects.select_related("subject").order_by("start_time")

    timetable_slots = (
        Timetable.objects
        .order_by("start_time")
        .values("start_time", "end_time")
        .distinct()
    )

    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

    return render(request, "teachers/timetable.html", {
        "timetable": timetable,
        "timetable_slots": timetable_slots,
        "days": days,
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

    if request.method == "POST":
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('add_subject')
    else:
        form = SubjectForm()

    return render(request, 'teachers/add_subject.html', {
        'form': form
    })


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

@login_required
def delete_timetable_entry(request, pk):
    entry = get_object_or_404(Timetable, pk=pk)
    entry.delete()
    messages.success(request, "Timetable entry deleted successfully.")
    return redirect("manage_timetable")

@login_required
def delete_all_timetable(request):
    if request.method == "POST":
        Timetable.objects.all().delete()
        messages.success(request, "All timetable entries deleted successfully.")
    return redirect("manage_timetable")

@login_required
def edit_timetable_entry(request, pk):
    entry = get_object_or_404(Timetable, pk=pk)

    if request.method == "POST":
        form = TimetableForm(request.POST, instance=entry, teacher=request.user.teacher)

        if form.is_valid():
            form.save()
            return redirect("manage_timetable")
    else:
        form = TimetableForm(instance=entry, teacher=request.user.teacher)

    return render(request, "teachers/edit_timetable.html", {
        "form": form
    })

@login_required
def take_attendance_now(request):
    teacher = request.user.teacher

    now = timezone.localtime()
    today_day = now.strftime("%a")
    current_time = now.time()
    today_date = now.date()   # 🔥 ADD THIS

    timetable_entry = Timetable.objects.filter(
        teacher=teacher,
        day=today_day,
        start_time__lte=current_time,
        end_time__gte=current_time
    ).select_related("subject").first()

    if not timetable_entry:
        return HttpResponse("❌ No class scheduled right now.")

    subject = timetable_entry.subject
    batch = timetable_entry.batch

    # Run recognition and WAIT
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    script_path = os.path.join(base_dir, "face_recognition_engine", "recognize.py")

    subprocess.run([sys.executable, script_path])

    file_path = os.path.join(base_dir, "face_recognition_engine", "recognized_today.txt")

    if not os.path.exists(file_path):
        return HttpResponse("❌ No attendance data found.")

    with open(file_path, "r") as f:
        names = f.read().splitlines()

    # 🔥 Batch logic
    if batch:
        students = Student.objects.filter(batch=batch)
    else:
        students = Student.objects.all()

    print("Recognized Names:", names)
    print("Total Students in Batch:", students.count())

    for student in students:
        status = student.user.username in names

        # ✅ FIXED: include date to avoid conflicts
        Attendance.objects.update_or_create(
            student=student,
            timetable=timetable_entry,
            date=today_date,   # 🔥 VERY IMPORTANT
            defaults={
                "subject": subject,
                "status": status
            }
        )

    # Clear file after saving
    open(file_path, "w").close()

    return HttpResponse("✅ Attendance completed and saved successfully.")




@login_required
def approve_students(request):
    pending_students = Student.objects.filter(is_approved=False, is_rejected=False)

    return render(request, 'teachers/approve_students.html', {
        'pending_students': pending_students
    })

@login_required
def approve_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    student.is_approved = True
    student.user.is_active = True

    student.user.save()
    student.save()

    return redirect('approve_students')


@login_required
def reject_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    student.is_rejected = True
    student.user.is_active = False

    student.user.save()
    student.save()

    return redirect('approve_students')


@login_required
def generate_registration_qr(request):
    registration_url = request.build_absolute_uri('/students/register/')

    qr = qrcode.make(registration_url)

    buffer = BytesIO()
    qr.save(buffer, format='PNG')

    return HttpResponse(buffer.getvalue(), content_type="image/png")

