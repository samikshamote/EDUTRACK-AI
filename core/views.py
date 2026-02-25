from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from students.models import Student
from teachers.models import Teacher
from django.shortcuts import render

@login_required
def role_redirect(request):
    user = request.user

    if Teacher.objects.filter(user=user).exists():
        return redirect('teacher_dashboard')

    if Student.objects.filter(user=user).exists():
        return redirect('student_dashboard')

    return redirect('/admin/')

def home(request):
    return render(request, 'index.html')

from django.shortcuts import redirect

def redirect_user(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(name='Teachers').exists():
            return redirect('teacher_dashboard')
        elif request.user.groups.filter(name='Students').exists():
            return redirect('student_dashboard')
    return redirect('login')