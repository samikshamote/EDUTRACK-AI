from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from attendance.models import Attendance
from students.models import Student

@login_required
def dashboard(request):
    student = Student.objects.get(user=request.user)

    total = Attendance.objects.filter(student=student).count()
    present = Attendance.objects.filter(student=student, status=True).count()

    percentage = int((present / total) * 100) if total > 0 else 0

    context = {
        'total': total,
        'present': present,
        'percentage': percentage,
    }

    return render(request, 'students/dashboard.html', context)
