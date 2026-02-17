from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from teachers.models import Teacher
from .forms import TimetableForm

from datetime import datetime
from .models import Timetable, Attendance
from students.models import Student
from django.contrib import messages
from django.utils import timezone


def take_attendance_now(request):

    if not hasattr(request.user, 'teacher'):
        messages.error(request, "Only teachers can take attendance.")
        return redirect('dashboard')

    today = datetime.today().strftime('%A')
    now = datetime.now().time()

    timetable_entry = Timetable.objects.filter(
        teacher=request.user.teacher,
        day=today,
        start_time__lte=now,
        end_time__gte=now
    ).first()

    if not timetable_entry:
        messages.warning(request, "No lecture scheduled right now.")
        return redirect('teacher_dashboard')

    if timetable_entry.batch:
        students = Student.objects.filter(batch=timetable_entry.batch)
    else:
        students = Student.objects.all()

    if request.method == "POST":
        for student in students:
            status = request.POST.get(f'status_{student.id}')

            Attendance.objects.create(
                student=student,
                timetable=timetable_entry,
                date=timezone.now().date(),
                status=status
            )

        messages.success(request, "Attendance saved successfully.")
        return redirect('teacher_dashboard')

    context = {
        'students': students,
        'timetable': timetable_entry
    }

    return render(request, 'attendance/take_attendance.html', context)
