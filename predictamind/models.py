from django.db import models
from students.models import Student
from attendance.models import Subject


class PredictionReport(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    attendance_percentage = models.FloatField()
    internal_marks = models.FloatField()
    assignment_marks = models.FloatField()
    result = models.CharField(max_length=10)
    advice = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.user.username} - {self.result}"

class InternalMark(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    internal_marks = models.FloatField()
    assignment_marks = models.FloatField()

    def total(self):
        return self.internal_marks + self.assignment_marks

    def __str__(self):
        return f"{self.student} - {self.subject}"