from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from students.models import Student
from teachers.models import Teacher

@login_required
def role_redirect(request):
    user = request.user

    if Teacher.objects.filter(user=user).exists():
        return redirect('teacher_dashboard')

    if Student.objects.filter(user=user).exists():
        return redirect('student_dashboard')

    return redirect('/admin/')
