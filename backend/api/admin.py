from django.contrib import admin
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.utils import timezone
from import_export import resources
from import_export.admin import ImportExportModelAdmin

# 如果你想要导入/导出某些外键字段，需要 from import_export import fields, widgets
# from import_export import fields
# from import_export import widgets

# 你的模型
from .models import (
    Department, Teacher, CoursePrototype, Grade, Class, ClassInstance,
    Student, UserProfile, CourseInstance, CourseSchedule, S_Grade,
    Semester, PunishmentRecord, RewardRecord
)

# ============ 1. 定义 Resource 类（批量导入导出） ============

class DepartmentResource(resources.ModelResource):
    class Meta:
        model = Department
        import_id_fields = ('id',)  # 假设你想使用ID作为唯一标识
        fields = ('id', 'name',)    # 仅示例

class TeacherResource(resources.ModelResource):
    class Meta:
        model = Teacher
        # 如果你想连带 user 字段导入/导出，需要做更多定制
        import_id_fields = ('id',)
        fields = ('id', 'user',)  # 仅示例

class StudentResource(resources.ModelResource):
    class Meta:
        model = Student
        import_id_fields = ('id',)
        fields = (
            'id', 'user', 'age', 'gender', 'id_number',
            'department', 'student_class', 'grade'
        )

class CoursePrototypeResource(resources.ModelResource):
    class Meta:
        model = CoursePrototype
        import_id_fields = ('id',)
        fields = ('id', 'name', 'description', 'department', 'credits')

class CourseInstanceResource(resources.ModelResource):
    class Meta:
        model = CourseInstance
        import_id_fields = ('id',)
        fields = (
            'id', 'course_prototype', 'semester', 'location',
            'capacity', 'selection_deadline', 'department',
            'daily_weight', 'final_weight', 'is_grades_published',
            'teacher', 'is_finalized'
        )

class SemesterResource(resources.ModelResource):
    class Meta:
        model = Semester
        import_id_fields = ('id',)
        fields = (
            'id', 'name', 'start_date', 'end_date',
            'selection_start_week', 'selection_end_week', 'current_week'
        )

class PunishmentRecordResource(resources.ModelResource):
    class Meta:
        model = PunishmentRecord
        import_id_fields = ('id',)
        fields = ('id', 'student', 'date', 'type', 'description')

class RewardRecordResource(resources.ModelResource):
    class Meta:
        model = RewardRecord
        import_id_fields = ('id',)
        fields = ('id', 'student', 'date', 'type', 'description')

class S_GradeResource(resources.ModelResource):
    class Meta:
        model = S_Grade
        import_id_fields = ('id',)
        fields = (
            'id', 'student', 'course_instance',
            'daily_score', 'final_score', 'total_score'
        )


# ============ 2. 定义自定义 Admin Actions（可选） ============
# 以下示例：导出选中的 Student 信息为 PDF
# 仅作思路演示，如果你需要更复杂的报表，可结合reportlab或其他库
# 并在 StudentAdmin 或其他 admin 的 actions[] 中注册

def export_selected_students_as_pdf(modeladmin, request, queryset):
    # queryset 是选中的 Student 对象集合
    from reportlab.pdfgen import canvas
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="students_export.pdf"'

    p = canvas.Canvas(response)
    p.setFont("Helvetica", 16)
    p.drawString(100, 800, "选中学生信息报表")

    y = 760
    p.setFont("Helvetica", 12)
    for student in queryset:
        line = f"学生: {student.user.get_full_name()}, 年龄: {student.age}, 班级: {student.student_class}, ID: {student.id_number}"
        p.drawString(100, y, line)
        y -= 20
        if y < 50:
            p.showPage()
            y = 800

    p.showPage()
    p.save()
    return response

export_selected_students_as_pdf.short_description = "导出选中学生为PDF"


# ============ 3. 定义 Admin 类（继承 ImportExportModelAdmin） ============

@admin.register(Department)
class DepartmentAdmin(ImportExportModelAdmin):
    resource_class = DepartmentResource
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Teacher)
class TeacherAdmin(ImportExportModelAdmin):
    resource_class = TeacherResource
    list_display = ('id', 'user', 'get_departments')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    # 如果 departments 多对多，可用
    # filter_horizontal = ('departments',)

    def get_departments(self, obj):
        return ", ".join([dept.name for dept in obj.departments.all()])
    get_departments.short_description = 'Departments'


@admin.register(Student)
class StudentAdmin(ImportExportModelAdmin):
    resource_class = StudentResource
    list_display = ('id', 'user', 'department', 'student_class', 'grade', 'age', 'gender', 'id_number')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'id_number')
    list_filter = ('department', 'student_class', 'grade', 'gender')
    actions = [export_selected_students_as_pdf]  # 自定义action示例


@admin.register(CoursePrototype)
class CoursePrototypeAdmin(ImportExportModelAdmin):
    resource_class = CoursePrototypeResource
    list_display = ('id', 'name', 'department', 'credits')
    search_fields = ('name', 'department__name')
    list_filter = ('department',)


@admin.register(CourseInstance)
class CourseInstanceAdmin(ImportExportModelAdmin):
    resource_class = CourseInstanceResource
    list_display = ('id', 'course_prototype', 'semester', 'location', 'capacity',
                    'teacher', 'is_finalized')
    search_fields = ('course_prototype__name', 'semester__name', 'location',
                     'teacher__user__username', 'teacher__user__first_name', 'teacher__user__last_name')
    list_filter = ('semester', 'is_finalized', 'teacher')
    # 如果有多对多字段 eligible_departments / eligible_classes 等，也可加 filter_horizontal
    # filter_horizontal = ('eligible_departments', 'eligible_grades', 'eligible_classes', 'selected_students',)


@admin.register(Semester)
class SemesterAdmin(ImportExportModelAdmin):
    resource_class = SemesterResource
    list_display = ('id', 'name', 'start_date', 'end_date',
                    'selection_start_week', 'selection_end_week', 'current_week')
    search_fields = ('name',)
    list_filter = ('start_date', 'end_date')


@admin.register(PunishmentRecord)
class PunishmentRecordAdmin(ImportExportModelAdmin):
    resource_class = PunishmentRecordResource
    list_display = ('id', 'student', 'type', 'date', 'description')
    search_fields = ('student__user__username', 'student__user__first_name',
                     'student__user__last_name', 'type')
    list_filter = ('type', 'date')


@admin.register(RewardRecord)
class RewardRecordAdmin(ImportExportModelAdmin):
    resource_class = RewardRecordResource
    list_display = ('id', 'student', 'type', 'date', 'description')
    search_fields = ('student__user__username', 'student__user__first_name',
                     'student__user__last_name', 'type')
    list_filter = ('type', 'date')


@admin.register(S_Grade)
class S_GradeAdmin(ImportExportModelAdmin):
    resource_class = S_GradeResource
    list_display = ('id', 'student', 'course_instance', 'daily_score', 'final_score', 'total_score')
    search_fields = ('student__username', 'student__first_name', 'student__last_name',
                     'course_instance__course_prototype__name')
    list_filter = ('course_instance',)


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'grade', 'department')
    search_fields = ('name', 'grade__name', 'department__name')
    list_filter = ('grade', 'department',)


@admin.register(ClassInstance)
class ClassInstanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_selected_students')
    search_fields = ('id',)
    filter_horizontal = ('selected_students',)

    def get_selected_students(self, obj):
        return ", ".join([student.username for student in obj.selected_students.all()])
    get_selected_students.short_description = 'Selected Students'


# ============ 4. 自定义 UserAdmin 也可保留 ============

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

class ReadOnlyUserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'User Profile'
    readonly_fields = ('user',)
    max_num = 1

class ReadOnlyTeacherInline(admin.StackedInline):
    model = Teacher
    can_delete = False
    verbose_name_plural = 'Teacher Profile'
    readonly_fields = ('user',)
    filter_horizontal = ('departments',)
    max_num = 1

class ReadOnlyStudentInline(admin.StackedInline):
    model = Student
    can_delete = False
    verbose_name_plural = 'Student Profile'
    readonly_fields = ('user', 'department', 'student_class', 'grade', 'age', 'gender', 'id_number')
    max_num = 1

class CustomUserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_user_type')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')

    inlines = [ReadOnlyUserProfileInline, ReadOnlyTeacherInline, ReadOnlyStudentInline]

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        return super().get_inline_instances(request, obj)

    def get_user_type(self, obj):
        if hasattr(obj, 'teacher_profile'):
            return "Teacher"
        elif hasattr(obj, 'student_profile'):
            return "Student"
        else:
            return "Other"
    get_user_type.short_description = 'User Type'

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

