# backend/api/admin.py

from django.contrib import admin
from django.contrib.auth.models import User
from .models import (
    Department, Teacher, CoursePrototype, Grade, Class, ClassInstance,
    Student, UserProfile, CourseInstance, CourseSchedule, S_Grade
)

# 注册 Department 模型
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# 注册 Teacher 模型
@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_departments')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    filter_horizontal = ('departments',)

    def get_departments(self, obj):
        return ", ".join([dept.name for dept in obj.departments.all()])
    get_departments.short_description = 'Departments'

# 注册 UserProfile 模型
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_departments')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    filter_horizontal = ('departments',)

    def get_departments(self, obj):
        return ", ".join([dept.name for dept in obj.departments.all()])
    get_departments.short_description = 'Departments'

# 注册 CoursePrototype 模型
@admin.register(CoursePrototype)
class CoursePrototypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'credits')
    search_fields = ('name', 'department__name')
    list_filter = ('department',)

# 注册 Grade 模型
@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('name', 'department')
    search_fields = ('name', 'department__name')
    list_filter = ('department',)

# 注册 Class 模型
@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'grade', 'department')
    search_fields = ('name', 'grade__name', 'department__name')
    list_filter = ('grade', 'department',)

# 注册 Student 模型
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'student_class', 'grade', 'age', 'gender', 'id_number')
    search_fields = (
        'user__username', 'user__first_name', 'user__last_name',
        'department__name', 'student_class__name', 'id_number'
    )
    list_filter = ('department', 'student_class', 'grade', 'gender')

# 注册 CourseInstance 模型
@admin.register(CourseInstance)
class CourseInstanceAdmin(admin.ModelAdmin):
    list_display = ('course_prototype', 'semester', 'location', 'capacity', 'teacher', 'is_finalized')
    search_fields = (
        'course_prototype__name', 'semester', 'location',
        'teacher__user__username', 'teacher__user__first_name', 'teacher__user__last_name'
    )
    list_filter = ('semester', 'is_finalized', 'teacher')
    autocomplete_fields = ('course_prototype', 'teacher')
    filter_horizontal = ('eligible_departments', 'eligible_grades', 'eligible_classes', 'selected_students',)

# 注册 CourseSchedule 模型
@admin.register(CourseSchedule)
class CourseScheduleAdmin(admin.ModelAdmin):
    list_display = ('day', 'period', 'course_instance')
    search_fields = ('day', 'period', 'course_instance__course_prototype__name')
    list_filter = ('day', 'period',)

# 注册 ClassInstance 模型
@admin.register(ClassInstance)
class ClassInstanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_selected_students')
    search_fields = ('id',)
    filter_horizontal = ('selected_students',)

    def get_selected_students(self, obj):
        return ", ".join([student.username for student in obj.selected_students.all()])
    get_selected_students.short_description = 'Selected Students'

# 注册 S_Grade 模型
@admin.register(S_Grade)
class S_GradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'course_instance', 'daily_score', 'final_score', 'total_score')
    search_fields = (
        'student__username', 'student__first_name', 'student__last_name',
        'course_instance__course_prototype__name'
    )
    list_filter = ('course_instance',)

# 自定义 UserAdmin 以显示关联的 Teacher 或 Student 信息
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

class TeacherInline(admin.StackedInline):
    model = Teacher
    can_delete = False
    verbose_name_plural = 'Teacher Profile'
    filter_horizontal = ('departments',)

class StudentInline(admin.StackedInline):
    model = Student
    can_delete = False
    verbose_name_plural = 'Student Profile'

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'User Profile'
    filter_horizontal = ('departments',)

class CustomUserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_user_type')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')

    inlines = [UserProfileInline, TeacherInline, StudentInline]

    def get_user_type(self, obj):
        if hasattr(obj, 'teacher_profile'):
            return "Teacher"
        elif hasattr(obj, 'student_profile'):
            return "Student"
        else:
            return "Other"
    get_user_type.short_description = 'User Type'

# 重新注册 UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
