from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Department)
admin.site.register(Building)
admin.site.register(ClassRoom)
admin.site.register(Student)
admin.site.register(Teacher)