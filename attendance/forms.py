from django import forms
from .models import Timetable, Subject

class TimetableForm(forms.ModelForm):
    class Meta:
        model = Timetable
        fields = ['subject', 'day', 'period_number', 'start_time', 'end_time']

    def __init__(self, *args, **kwargs):
        teacher = kwargs.pop('teacher', None)
        super().__init__(*args, **kwargs)

        if teacher:
            self.fields['subject'].queryset = Subject.objects.filter(teacher=teacher)
