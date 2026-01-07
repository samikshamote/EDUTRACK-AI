from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='student_home'),
    path('dashboard/', views.dashboard, name='student_dashboard'),
]
