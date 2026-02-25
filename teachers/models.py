from django.db import models
from django.contrib.auth.models import User
from students.models import Student


class Teacher(models.Model):

    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    designation = models.CharField(max_length=100, blank=True, null=True)

    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        blank=True,
        null=True
    )

    department = models.CharField(max_length=50, blank=True, null=True)

    photo = models.ImageField(
        upload_to='profiles/teachers/',
        blank=True,
        null=True
    )

    phone = models.CharField(max_length=15, blank=True, null=True)
    qualification = models.CharField(max_length=100, blank=True, null=True)

    email = models.EmailField(blank=True, null=True)

    @property
    def profile_completion(self):
        filled = 0
        total = 4

        if self.user.first_name:
            filled += 1
        if self.user.email:
            filled += 1
        if self.phone:
            filled += 1
        if self.photo:
            filled += 1

        return int((filled / total) * 100)

    def __str__(self):
        return self.user.username


class InternalMarks(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey("attendance.Subject", on_delete=models.CASCADE)
    marks = models.PositiveIntegerField()

    class Meta:
        unique_together = ('student', 'subject')

    def save(self, *args, **kwargs):
        if self.marks > 15:
            raise ValueError("Marks cannot exceed 15")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.user.username} - {self.subject.name}"