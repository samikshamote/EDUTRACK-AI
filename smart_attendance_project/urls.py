from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.shortcuts import render   # ✅ Import render
from core.views import redirect_user


# ✅ Define home view
def home(request):
    return render(request, 'index.html')


urlpatterns = [

    # ✅ Landing Page
    path('', home, name='home'),

    # Admin
    path('admin/', admin.site.urls),

    # Login / Logout
    path('login/', auth_views.LoginView.as_view(
        template_name='registration/login.html'
    ), name='login'),

    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Auth URLs
    path('accounts/', include('django.contrib.auth.urls')),

    # Student & Teacher apps
    path('students/', include('students.urls')),
    path('teachers/', include('teachers.urls')),

    # PredictaMind
    path('predict/', include('predictamind.urls')),

     path('', include('core.urls')),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )