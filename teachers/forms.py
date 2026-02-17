from django import forms
from .models import Teacher
from attendance.models import Subject
from attendance.models import Timetable

# -----------------------------
# Teacher Profile Form
# -----------------------------
# -----------------------------
# Teacher Profile Form
# -----------------------------
class TeacherProfileForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['photo', 'phone', 'qualification']


# -----------------------------
# Subject Form
# -----------------------------
class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'code', 'semester', 'teacher']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter subject name'
            }),
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter subject code'
            }),
            'semester': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter semester'
            }),
            'teacher': forms.Select(attrs={
                'class': 'form-control'
            }),
        }


class TimetableForm(forms.ModelForm):
    class Meta:
        model = Timetable
        fields = ['subject', 'day', 'period_number', 'start_time', 'end_time','batch']

    def __init__(self, *args, **kwargs):
        self.teacher = kwargs.pop('teacher', None)  # ✅ accept teacher
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

        teacher = self.initial.get('teacher')
        day = cleaned_data.get('day')
        period = cleaned_data.get('period_number')
        batch = cleaned_data.get('batch')

        if teacher and day and period:

            existing = Timetable.objects.filter(
                teacher=teacher,
                day=day,
                period_number=period
            ).exclude(pk=self.instance.pk)

            # THEORY (no batch selected)
            if not batch:
                if existing.exists():
                    raise forms.ValidationError(
                        "A lecture already exists in this period."
                    )

            # PRACTICAL (batch selected)
            else:
                if existing.filter(batch=batch).exists():
                    raise forms.ValidationError(
                        "This batch already has a practical in this period."
                    )

        return cleaned_data
