# student_api/models.py
from django.conf import settings
from django.db import models

class Student(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default="null")
    student_id = models.CharField(max_length=20, unique=True, default="null")  # 学号字段，确保唯一
    age = models.IntegerField()
    gender = models.CharField(max_length=10, default="null")
    department = models.CharField(max_length=100, default="null")
    major = models.CharField(max_length=100, default="null")
    # 其他字段...

    def __str__(self):
        return f"{self.name} ({self.student_id})"