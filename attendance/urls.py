from django.urls import path
from . import views

urlpatterns = [
    path('manage/', views.manage_timetable, name='manage_timetable'),
    path('view/', views.timetable_view, name='timetable_view'),
    path('mark/', views.mark_attendance, name='mark_attendance'),
    path('take-attendance/', take_attendance_now, name='take_attendance_now'),
    path('my-attendance/', views.student_attendance_view, name='student_attendance'),
]
