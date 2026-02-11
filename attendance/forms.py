from django import forms
from .models import Timetable

class TimetableForm(forms.ModelForm):
    class Meta:
        model = Timetable
        fields = ['subject', 'day', 'period_number', 'start_time', 'end_time']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }
