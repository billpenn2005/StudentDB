from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
# auth_api/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    )
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='student',  # 默认角色
    )
    # 你可以根据需要添加自定义字段
    pass
