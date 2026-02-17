from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView  

urlpatterns = [
    path('admin/', admin.site.urls),

    # Authentication (login, logout, password reset)
    path('accounts/', include('django.contrib.auth.urls')),

    # Core app (landing / redirects)
    path('', include('core.urls')),

    # Student & Teacher apps
    path('students/', include('students.urls')),
    path('teachers/', include('teachers.urls')),
    path('logout/', LogoutView.as_view(), name='logout'),

]

# Serve media files (profile photos etc.) in development
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
