from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from teachers.models import Teacher
from .models import Timetable
from .forms import TimetableForm


# ==============================
# MANAGE TIMETABLE
# ==============================
@login_required
def manage_timetable(request):
    teacher = Teacher.objects.get(user=request.user)

    if request.method == 'POST':
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


# ==============================
# VIEW TIMETABLE
# ==============================
@login_required
def timetable_view(request):
    teacher = Teacher.objects.get(user=request.user)

    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

    timetables = Timetable.objects.filter(teacher=teacher)

    timetable_dict = {}

    for t in timetables:
        time_key = (t.start_time, t.end_time)

        if time_key not in timetable_dict:
            timetable_dict[time_key] = {}

        timetable_dict[time_key][t.day] = t

    return render(request, 'teachers/timetable.html', {
        'timetable': timetable_dict,
        'days': days
    })
