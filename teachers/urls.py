from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('start-attendance/', views.start_attendance, name='start_attendance'),
    path('save-attendance/', views.save_attendance, name='save_attendance'),
    path('view-attendance/', views.view_attendance, name='view_attendance'),

]
