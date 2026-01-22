from django.db import models
from django.contrib.auth.models import User

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=50)
    photo = models.ImageField(upload_to='profiles/teachers/', blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True)
    qualification = models.CharField(max_length=100, blank=True)

    def profile_completion(self):
        filled = 0
        total = 4

        if self.user.first_name: filled += 1
        if self.user.email: filled += 1
        if self.phone: filled += 1
        if self.photo: filled += 1

        return int((filled / total) * 100)

    def __str__(self):
        return self.user.username


