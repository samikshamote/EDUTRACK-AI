from django.urls import path
from . import views

urlpatterns = [

    # Dashboard
    path('dashboard/', views.teacher_dashboard, name='teacher_dashboard'),

    # Attendance
    path('start-attendance/', views.start_attendance, name='start_attendance'),
    path('take-attendance/', views.take_attendance_now, name='take_attendance_now'),
    path('save-attendance/', views.save_attendance, name='save_attendance'),

    # View / Export Attendance
    path('view-attendance/', views.view_attendance, name='view_attendance'),
    path('export-attendance/', views.export_attendance_csv, name='export_attendance_csv'),

    # Subjects
    path('manage-subjects/', views.manage_subjects, name='manage_subjects'),
    path('add-subject/', views.add_subject, name='add_subject'),
    path('delete-subject/<int:subject_id>/', views.delete_subject, name='delete_subject'),

    # Timetable
    path('timetable/', views.timetable_view, name='timetable_view'),
    path('manage-timetable/', views.manage_timetable, name='manage_timetable'),
    path('edit-timetable/<int:pk>/', views.edit_timetable_entry, name='edit_timetable_entry'),
    path('delete-timetable/<int:pk>/', views.delete_timetable_entry, name='delete_timetable_entry'),
    path('delete-all-timetable/', views.delete_all_timetable, name='delete_all_timetable'),

    # Profile
    path('profile/', views.teacher_profile, name='teacher_profile'),
    path('edit-profile/', views.edit_teacher_profile, name='edit_teacher_profile'),

    # Student Approval
    path('approve-students/', views.approve_students, name='approve_students'),
    path('approve/<int:student_id>/', views.approve_student, name='approve_student'),
    path('reject/<int:student_id>/', views.reject_student, name='reject_student'),

    # QR
    path('generate-qr/', views.generate_registration_qr, name='generate_registration_qr'),

    path('registration-qr/', views.generate_registration_qr, name='registration_qr'),

    path('enter-marks/<int:student_id>/', views.enter_marks, name='enter_marks'),

    path('internal-marks/', views.internal_marks, name='internal_marks'),   

]
