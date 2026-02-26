from django.urls import path
from . import views
from predictamind.views import predict_view

urlpatterns = [
    path('', views.dashboard, name='student_home'),
    path('dashboard/', views.dashboard, name='student_dashboard'),
    path('profile/', views.student_profile, name='student_profile'),
    path('profile/edit/', views.edit_student_profile, name='edit_student_profile'),
    path('register/', views.student_register, name='student_register'),
    path('predict/', predict_view, name='student_predict'),
    path('results/', views.student_results, name='student_results'),
    path('predict-result/', views.predict_result, name='predict_result'),
    path('timetable/', views.student_timetable, name='student_timetable'),
    path('attendance/', views.student_attendance, name='student_attendance'),
    path('download-result-pdf/', views.download_result_pdf, name='download_result_pdf'),

]
    



