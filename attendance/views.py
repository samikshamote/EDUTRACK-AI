from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def mark_attendance(request):
    return render(request, 'attendance/mark.html')

# Create your views here.
