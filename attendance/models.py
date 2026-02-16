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
        return f"{self.name} ({self.code})"


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

    BATCH_CHOICES = [
        ('B-I', 'Batch I'),
        ('B-II', 'Batch II'),
        ('B-III', 'Batch III'),
    ]

    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    day = models.CharField(max_length=3, choices=DAYS)
    period_number = models.PositiveIntegerField()

    start_time = models.TimeField()
    end_time = models.TimeField()

    # Optional → only for practicals
    batch = models.CharField(
        max_length=10,
        choices=BATCH_CHOICES,
        blank=True,
        null=True
    )

    class Meta:
        ordering = ['day', 'start_time']

    def __str__(self):
        if self.batch:
            return f"{self.subject.name} ({self.batch}) - {self.day}"
        return f"{self.subject.name} - {self.day}"


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
    status = models.BooleanField(default=True)

    class Meta:
        unique_together = ('student', 'timetable', 'date')

    def __str__(self):
        return f"{self.student.user.username} - {self.subject.name} - {self.date}"
