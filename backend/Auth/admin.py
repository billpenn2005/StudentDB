from django.contrib import admin
from .models import AuthUser,Role

# Register your models here.

admin.site.register(AuthUser)
admin.site.register(Role)