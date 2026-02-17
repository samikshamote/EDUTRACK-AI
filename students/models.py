from django.db import models
from django.contrib.auth.models import User


class Student(models.Model):

    BATCH_CHOICES = [
        ('B-I', 'Batch I'),
        ('B-II', 'Batch II'),
        ('B-III', 'Batch III'),
    ]


    user = models.OneToOneField(User, on_delete=models.CASCADE)

    roll_number = models.CharField(max_length=20)
    course = models.CharField(max_length=50)

    photo = models.ImageField(upload_to='profiles/students/', blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True)
    department = models.CharField(max_length=100, blank=True)

    batch = models.CharField(
        max_length=10,
        choices=BATCH_CHOICES,
        default='B-I'
    )

    # 🔥 NEW FIELDS FOR APPROVAL SYSTEM
    is_approved = models.BooleanField(default=False)
    registered_on = models.DateTimeField(auto_now_add=True)

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
    is_rejected = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.user.username} ({'Approved' if self.is_approved else 'Pending'})"
