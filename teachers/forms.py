from django import forms
from .models import Teacher

class TeacherProfileForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['photo', 'phone', 'qualification']
