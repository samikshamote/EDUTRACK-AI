from django.contrib import admin
from .models import Attendance, Subject

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'date', 'time', 'status')
    list_filter = ('subject', 'date', 'status')
    search_fields = ('student__user__username',)

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'teacher')
