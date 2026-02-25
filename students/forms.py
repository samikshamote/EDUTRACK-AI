from django import forms
from django.contrib.auth.models import User
from .models import Student


# =========================================
# 🔹 Student Profile Update Form
# =========================================
class StudentProfileForm(forms.ModelForm):

    class Meta:
        model = Student
        fields = ['photo', 'phone', 'department', 'year']

    YEAR_CHOICES = [
        ('FY', 'First Year'),
        ('SY', 'Second Year'),
        ('TY', 'Third Year'),
    ]

    year = forms.ChoiceField(
        choices=YEAR_CHOICES,
        required=True
    )


# =========================================
# 🔥 Student Registration Form
# =========================================
class StudentRegistrationForm(forms.ModelForm):

    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    YEAR_CHOICES = [
        ('FY', 'First Year'),
        ('SY', 'Second Year'),
        ('TY', 'Third Year'),
    ]

    year = forms.ChoiceField(
        choices=YEAR_CHOICES,
        required=True
    )

    class Meta:
        model = Student
        fields = [
            'roll_number',
            'course',
            'phone',
            'department',
            'batch',
            'year'
        ]