# api/admin.py

from django.contrib import admin
from .models import (
    Department, CoursePrototype, Student,
    ClassInstance, CourseInstance,Class,Grade,CourseSchedule
)

admin.site.register(Department)
admin.site.register(Student)
admin.site.register(ClassInstance)
admin.site.register(CoursePrototype)
admin.site.register(Class)
admin.site.register(Grade)
admin.site.register(CourseSchedule)
# 如果有相关的内联模型，可以定义内联类
class CourseScheduleInline(admin.TabularInline):
    model = CourseSchedule
    extra = 1  # 可根据需要调整

class CourseInstanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'course_prototype', 'department')  # 列出需要显示的字段
    search_fields = ('course_prototype__name', 'department__name')  # 可搜索的字段
    filter_horizontal = ('selected_students', 'eligible_classes')  # 为ManyToMany字段添加水平过滤器
    inlines = [CourseScheduleInline]  # 如果需要内联编辑相关的CourseSchedule

    # 可选：自定义表单布局
    fieldsets = (
        (None, {
            'fields': ('course_prototype', 'department', 'eligible_classes', 'selected_students')
        }),
        ('Schedules', {
            'classes': ('collapse',),
            'fields': (),
        }),
    )

admin.site.register(CourseInstance, CourseInstanceAdmin)
# Compare this snippet from backend/api/urls.py:
