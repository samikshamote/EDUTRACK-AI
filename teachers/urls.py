from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('start-attendance/', views.start_attendance, name='start_attendance'),
    path('save-attendance/', views.save_attendance, name='save_attendance'),
    path('view-attendance/', views.view_attendance, name='view_attendance'),
    path('export-attendance/', views.export_attendance_csv, name='export_attendance_csv'),
    path('profile/', views.teacher_profile, name='teacher_profile'),
    path('profile/edit/', views.edit_teacher_profile, name='edit_teacher_profile'),

    path('subjects/', views.manage_subjects, name='manage_subjects'),
    path('subjects/add/', views.add_subject, name='add_subject'),
    path('subjects/delete/<int:subject_id>/', views.delete_subject, name='delete_subject'),

    path('manage-timetable/', views.manage_timetable, name='manage_timetable'),
    path('timetable/', views.timetable_view, name='timetable_view'),
    path("delete-timetable/<int:pk>/", views.delete_timetable_entry, name="delete_timetable"),
    path("edit-timetable/<int:pk>/", views.edit_timetable_entry, name="edit_timetable"),
    path("delete-all-timetable/", views.delete_all_timetable, name="delete_all_timetable"),

]


