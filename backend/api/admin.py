# api/admin.py

from django.contrib import admin
from .models import (
    Department, CoursePrototype, Student,
    ClassInstance, CourseInstance,Class,Grade
)

admin.site.register(Department)
admin.site.register(Student)
admin.site.register(ClassInstance)
admin.site.register(CoursePrototype)
admin.site.register(CourseInstance)
admin.site.register(Class)
admin.site.register(Grade)
# Compare this snippet from backend/api/urls.py:
