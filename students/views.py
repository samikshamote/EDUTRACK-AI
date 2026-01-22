from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from attendance.models import Attendance


@login_required
def dashboard(request):
    # ❌ BLOCK TEACHERS FROM STUDENT DASHBOARD
    if not hasattr(request.user, 'student'):
        return redirect('teacher_dashboard')

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

@login_required
def student_profile(request):
    if not hasattr(request.user, 'student'):
        return redirect('teacher_dashboard')

    student = request.user.student

    if request.method == 'POST':
        student.phone = request.POST.get('phone')
        student.department = request.POST.get('department')

        if request.FILES.get('photo'):
            student.photo = request.FILES['photo']

        student.save()
        return redirect('student_profile')

    return render(request, 'students/profile.html', {
        'student': student
    })


