from django.urls import path
from .views import role_redirect

urlpatterns = [
    path('', role_redirect, name='home'),        # 👈 ROOT URL FIX
    path('redirect/', role_redirect, name='role_redirect'),
]
