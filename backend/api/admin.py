# api/admin.py

from django.contrib import admin
from .models import (
    Department, Specialty, Student,
    Course,ClassInstance
)

admin.site.register(Department)
admin.site.register(Specialty)
admin.site.register(Student)
admin.site.register(Course)
admin.site.register(ClassInstance)
