from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from attendance.models import Attendance

@login_required
def dashboard(request):
    student = request.user.student

    total = Attendance.objects.filter(student=student).count()
    present = Attendance.objects.filter(student=student, status=True).count()
    percentage = (present / total * 100) if total > 0 else 0

    context = {
        'total': total,
        'present': present,
        'percentage': round(percentage, 2)
    }

    return render(request, 'students/dashboard.html', context)
