# admin.py
from django.contrib import admin
from .models import Student

class StudentAdmin(admin.ModelAdmin):
    # 指定在列表页面显示哪些字段
    list_display = ('name', 'student_id', 'age', 'gender', 'department', 'major', 'user')
    search_fields = ('name', 'student_id', 'department', 'major')
    list_filter = ('gender', 'department')

    # 使用 fieldsets 进行字段分组
    fieldsets = (
        ('个人信息', {'fields': ('name', 'student_id', 'age', 'gender')}),
        ('学术信息', {'fields': ('department', 'major')}),
        ('用户信息', {'fields': ('user',)}),
    )

    # 你不需要再指定 fields，因为你已经使用了 fieldsets

admin.site.register(Student, StudentAdmin)
