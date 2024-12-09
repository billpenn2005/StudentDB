# api/admin.py

from django.contrib import admin
from .models import (
    Department, Specialty, Student,
    RewardPunishment, Course, Enrollment,
    Exam, RetakeExam
)

admin.site.register(Department)
admin.site.register(Specialty)
admin.site.register(Student)
admin.site.register(RewardPunishment)
admin.site.register(Course)
admin.site.register(Enrollment)
admin.site.register(Exam)
admin.site.register(RetakeExam)
