from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from attendance.models import Attendance
from .forms import StudentProfileForm


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
        form = StudentProfileForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            return redirect('student_profile')
    else:
        form = StudentProfileForm(instance=student)

    return render(request, 'students/profile.html', {
        'student': student,
        'form': form
    })

@login_required
def edit_student_profile(request):
    student = request.user.student

    if request.method == 'POST':
        form = StudentProfileForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            return redirect('student_profile')
    else:
        form = StudentProfileForm(instance=student)

    return render(request, 'students/edit_profile.html', {'form': form})

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import StudentRegistrationForm


def student_register(request):
    if request.method == "POST":
        form = StudentRegistrationForm(request.POST, request.FILES)

        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists")
                return redirect('student_register')

            # 🔥 Create user but inactive
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                is_active=False
            )

            student = form.save(commit=False)
            student.user = user
            student.is_approved = False
            student.save()

            messages.success(request, "Registration submitted. Wait for teacher approval.")
            return redirect('login')

    else:
        form = StudentRegistrationForm()

    return render(request, 'students/register.html', {'form': form})
