from django.contrib import admin
from django.contrib.auth.models import User
from django.http import HttpResponse
from import_export import resources, fields, widgets
from import_export.admin import ImportExportModelAdmin

# 你的模型
from .models import (
    Department, Teacher, CoursePrototype, Grade, Class, ClassInstance,
    Student, UserProfile, CourseInstance, CourseSchedule, S_Grade,
    Semester, PunishmentRecord, RewardRecord
)

# ============ 1. 定义 Resource 类（批量导入导出） ============

class GradeResource(resources.ModelResource):
    department = fields.Field(
        column_name='department',
        attribute='department',
        widget=widgets.ForeignKeyWidget(Department, 'name')
    )
    
    class Meta:
        model = Grade
        import_id_fields = ('id',)
        fields = ('id', 'name', 'department')

class DepartmentResource(resources.ModelResource):
    class Meta:
        model = Department
        import_id_fields = ('id',)
        fields = ('id', 'name',)

class TeacherResource(resources.ModelResource):
    departments = fields.Field(
        column_name='departments',
        attribute='departments',
        widget=widgets.ManyToManyWidget(Department, field='name')
    )
    
    class Meta:
        model = Teacher
        import_id_fields = ('id',)
        fields = ('id', 'user', 'departments',)

class StudentResource(resources.ModelResource):
    grade = fields.Field(
        column_name='grade',
        attribute='grade',
        widget=widgets.ForeignKeyWidget(Grade, 'name')
    )
    department = fields.Field(
        column_name='department',
        attribute='department',
        widget=widgets.ForeignKeyWidget(Department, 'name')
    )
    student_class = fields.Field(
        column_name='student_class',
        attribute='student_class',
        widget=widgets.ForeignKeyWidget(Class, 'name')
    )
    user = fields.Field(
        column_name='user',
        attribute='user',
        widget=widgets.ForeignKeyWidget(User, 'username')
    )
    
    class Meta:
        model = Student
        import_id_fields = ('id',)
        fields = (
            'id', 'user', 'age', 'gender', 'id_number',
            'department', 'student_class', 'grade'
        )

class CoursePrototypeResource(resources.ModelResource):
    department = fields.Field(
        column_name='department',
        attribute='department',
        widget=widgets.ForeignKeyWidget(Department, 'name')
    )
    
    class Meta:
        model = CoursePrototype
        import_id_fields = ('id',)
        fields = ('id', 'name', 'description', 'department', 'credits')

class CourseInstanceResource(resources.ModelResource):
    course_prototype = fields.Field(
        column_name='course_prototype',
        attribute='course_prototype',
        widget=widgets.ForeignKeyWidget(CoursePrototype, 'name')
    )
    semester = fields.Field(
        column_name='semester',
        attribute='semester',
        widget=widgets.ForeignKeyWidget(Semester, 'name')
    )
    department = fields.Field(
        column_name='department',
        attribute='department',
        widget=widgets.ForeignKeyWidget(Department, 'name')
    )
    teacher = fields.Field(
        column_name='teacher',
        attribute='teacher',
        widget=widgets.ForeignKeyWidget(Teacher, 'user__username')
    )
    
    class Meta:
        model = CourseInstance
        import_id_fields = ('id',)
        fields = (
            'id', 'course_prototype', 'semester', 'location',
            'capacity', 'selection_deadline', 'department',
            'daily_weight', 'final_weight', 'is_grades_published',
            'teacher', 'is_finalized'
        )

class CourseScheduleResource(resources.ModelResource):
    course_instance = fields.Field(
        column_name='course_instance',
        attribute='course_instance',
        widget=widgets.ForeignKeyWidget(CourseInstance, 'id')
    )
    day = fields.Field(
        column_name='day',
        attribute='day',
        widget=widgets.CharWidget()
    )
    period = fields.Field(
        column_name='period',
        attribute='period',
        widget=widgets.IntegerWidget()
    )
    
    class Meta:
        model = CourseSchedule
        import_id_fields = ('id',)
        fields = (
            'id', 'course_instance', 'day', 'period',
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
    student = fields.Field(
        column_name='student',
        attribute='student',
        widget=widgets.ForeignKeyWidget(Student, 'id_number')
    )
    
    class Meta:
        model = PunishmentRecord
        import_id_fields = ('id',)
        fields = ('id', 'student', 'date', 'type', 'description')

class RewardRecordResource(resources.ModelResource):
    student = fields.Field(
        column_name='student',
        attribute='student',
        widget=widgets.ForeignKeyWidget(Student, 'id_number')
    )
    
    class Meta:
        model = RewardRecord
        import_id_fields = ('id',)
        fields = ('id', 'student', 'date', 'type', 'description')

class S_GradeResource(resources.ModelResource):
    student = fields.Field(
        column_name='student',
        attribute='student',
        widget=widgets.ForeignKeyWidget(Student, 'id_number')
    )
    course_instance = fields.Field(
        column_name='course_instance',
        attribute='course_instance',
        widget=widgets.ForeignKeyWidget(CourseInstance, 'id')
    )
    
    class Meta:
        model = S_Grade
        import_id_fields = ('id',)
        fields = (
            'id', 'student', 'course_instance',
            'daily_score', 'final_score', 'total_score'
        )

# ============ 2. 定义自定义 Admin Actions（可选） ============

def export_selected_students_as_pdf(modeladmin, request, queryset):
    from reportlab.pdfgen import canvas
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="students_export.pdf"'

    p = canvas.Canvas(response)
    p.setFont("Helvetica", 16)
    p.drawString(100, 800, "选中学生信息报表")

    y = 760
    p.setFont("Helvetica", 12)
    for student in queryset:
        line = f"学生: {student.user.get_full_name()}, 年龄: {student.age}, 班级: {student.student_class.name}, ID: {student.id_number}"
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
class DepartmentAdmin(ImportExportModelAdmin):
    resource_class = DepartmentResource
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Teacher)
class TeacherAdmin(ImportExportModelAdmin):
    resource_class = TeacherResource
    list_display = ('id', 'get_username', 'get_departments')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    # 如果 departments 多对多，可用
    # filter_horizontal = ('departments',)

    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Username'

    def get_departments(self, obj):
        return ", ".join([dept.name for dept in obj.departments.all()])
    get_departments.short_description = 'Departments'

@admin.register(Grade)
class GradeAdmin(ImportExportModelAdmin):
    resource_class = GradeResource
    list_display = ('id', 'name', 'department')
    search_fields = ('name', 'department__name')
    list_filter = ('department',)

@admin.register(Student)
class StudentAdmin(ImportExportModelAdmin):
    resource_class = StudentResource
    list_display = ('id', 'get_username', 'department', 'student_class', 'get_grade', 'age', 'gender', 'id_number')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'id_number', 'grade__name')
    list_filter = ('department', 'student_class', 'grade__name', 'gender')
    actions = [export_selected_students_as_pdf]

    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Username'

    def get_grade(self, obj):
        return obj.grade.name if obj.grade else '未分配'
    get_grade.short_description = 'Grade'

@admin.register(CoursePrototype)
class CoursePrototypeAdmin(ImportExportModelAdmin):
    resource_class = CoursePrototypeResource
    list_display = ('id', 'name', 'department', 'credits')
    search_fields = ('name', 'department__name')
    list_filter = ('department',)

@admin.register(CourseInstance)
class CourseInstanceAdmin(ImportExportModelAdmin):
    resource_class = CourseInstanceResource
    list_display = ('id', 'get_course_name', 'get_semester_name', 'location', 'capacity',
                    'get_teacher_username', 'is_finalized')
    search_fields = ('course_prototype__name', 'semester__name', 'location',
                     'teacher__user__username', 'teacher__user__first_name', 'teacher__user__last_name')
    list_filter = ('semester__name', 'is_finalized', 'teacher__user__username')

    def get_course_name(self, obj):
        return obj.course_prototype.name
    get_course_name.short_description = 'Course Name'

    def get_semester_name(self, obj):
        return obj.semester.name
    get_semester_name.short_description = 'Semester Name'

    def get_teacher_username(self, obj):
        return obj.teacher.user.username if obj.teacher else '未分配'
    get_teacher_username.short_description = 'Teacher Username'

@admin.register(CourseSchedule)
class CourseScheduleAdmin(ImportExportModelAdmin):
    resource_class = CourseScheduleResource
    list_display = ('id', 'get_course_instance_id', 'get_day_display', 'get_period_display')
    search_fields = ('course_instance__id', 'day', 'period')
    list_filter = ('day', 'period', 'course_instance__id')

    def get_course_instance_id(self, obj):
        return obj.course_instance.id
    get_course_instance_id.short_description = 'Course Instance ID'

    def get_day_display(self, obj):
        return obj.get_day_display()
    get_day_display.short_description = 'Day'

    def get_period_display(self, obj):
        return obj.get_period_display()
    get_period_display.short_description = 'Period'

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
    list_display = ('id', 'get_student_username', 'type', 'date', 'description')
    search_fields = ('student__user__username', 'student__user__first_name',
                     'student__user__last_name', 'type')
    list_filter = ('type', 'date')

    def get_student_username(self, obj):
        return obj.student.user.username
    get_student_username.short_description = 'Student Username'

@admin.register(RewardRecord)
class RewardRecordAdmin(ImportExportModelAdmin):
    resource_class = RewardRecordResource
    list_display = ('id', 'get_student_username', 'type', 'date', 'description')
    search_fields = ('student__user__username', 'student__user__first_name',
                     'student__user__last_name', 'type')
    list_filter = ('type', 'date')

    def get_student_username(self, obj):
        return obj.student.user.username
    get_student_username.short_description = 'Student Username'

@admin.register(S_Grade)
class S_GradeAdmin(ImportExportModelAdmin):
    resource_class = S_GradeResource
    list_display = ('id', 'get_student_username', 'get_course_instance', 'daily_score', 'final_score', 'total_score')
    search_fields = ('student__user__username', 'student__user__first_name', 'student__user__last_name',
                     'course_instance__course_prototype__name')
    list_filter = ('course_instance__course_prototype__name',)

    def get_student_username(self, obj):
        return obj.student.username
    get_student_username.short_description = 'Student Username'

    def get_course_instance(self, obj):
        return obj.course_instance.id
    get_course_instance.short_description = 'Course Instance ID'

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
        return ", ".join([student.user.username for student in obj.selected_students.all()])
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
    #readonly_fields = ('user', 'department', 'student_class', 'grade', 'age', 'gender', 'id_number')
    readonly_fields = ('user',)
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
        if hasattr(obj, 'teacher'):
            return "Teacher"
        elif hasattr(obj, 'student'):
            return "Student"
        else:
            return "Other"
    get_user_type.short_description = 'User Type'

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

