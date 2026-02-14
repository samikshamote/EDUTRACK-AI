from django import forms
from .models import Teacher
from attendance.models import Subject


class TeacherProfileForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['photo', 'phone', 'qualification']

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'code', 'semester']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter subject name'
            })
        }
