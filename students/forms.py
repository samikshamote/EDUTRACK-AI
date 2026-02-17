from django import forms
from django.contrib.auth.models import User
from .models import Student


# 🔹 Existing Profile Form
class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['photo', 'phone', 'department']


# 🔥 NEW Registration Form
class StudentRegistrationForm(forms.ModelForm):
    username = forms.CharField()
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Student
        fields = [
            'roll_number',
            'course',
            'phone',
            'department',
            'batch'
        ]
