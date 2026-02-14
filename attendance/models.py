from django.db import models
from teachers.models import Teacher
from students.models import Student


# ==========================
# SUBJECT MODEL
# ==========================
class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    semester = models.IntegerField(default=1)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.code})- {self.teacher.user.username}"


# ==========================
# TIMETABLE MODEL
# ==========================
class Timetable(models.Model):
    DAYS = [
        ('Mon', 'Monday'),
        ('Tue', 'Tuesday'),
        ('Wed', 'Wednesday'),
        ('Thu', 'Thursday'),
        ('Fri', 'Friday'),
        ('Sat', 'Saturday'),
    ]

    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    day = models.CharField(max_length=3, choices=DAYS)
    period_number = models.PositiveIntegerField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        unique_together = ('teacher', 'day', 'period_number')
        ordering = ['day', 'period_number']

    def __str__(self):
        return f"{self.subject.name} - {self.day} (P{self.period_number})"


# ==========================
# ATTENDANCE MODEL
# ==========================
class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    timetable = models.ForeignKey(
        Timetable,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.student.user.username} - {self.subject.name} - {self.date}"
