from django import forms
from .models import Timetable

class TimetableForm(forms.ModelForm):

    class Meta:
        model = Timetable
        fields = [
            'subject',
            'day',
            'period_number',
            'start_time',
            'end_time',
            'batch'   # ✅ ADD THIS
        ]

    def __init__(self, *args, **kwargs):
        teacher = kwargs.pop('teacher', None)
        super().__init__(*args, **kwargs)

        # Show only that teacher's subjects
        if teacher:
            self.fields['subject'].queryset = teacher.subject_set.all()

        # ✅ Make batch NOT compulsory
        self.fields['batch'].required = False

        self.fields['batch'].label = "Batch (Select only for practicals)"
