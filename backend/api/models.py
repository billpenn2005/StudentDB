from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Department(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    departments = models.ManyToManyField(Department, related_name='teachers', blank=True)
    # 其他教师相关字段

    def __str__(self):
        return self.user.get_full_name()

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    departments = models.ManyToManyField(Department, related_name='users', blank=True)

    def __str__(self):
        return self.user.username



class CoursePrototype(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='course_prototypes')
    credits = models.PositiveIntegerField(default=0)  # 学分字段

    def __str__(self):
        return self.name

class Grade(models.Model):
    name = models.CharField(max_length=20)  # 如 "2024级"
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='grades')

    def __str__(self):
        return f"{self.department.name} - {self.name}"

class Class(models.Model):
    name = models.CharField(max_length=50)  # 如 "2024级1班"
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name='classes')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='classes', null=True)

    def __str__(self):
        return self.name

class ClassInstance(models.Model):
    selected_students = models.ManyToManyField(User, related_name='class_selected_courses', blank=True)
    # 其他字段

    def __str__(self):
        return f"ClassInstance {self.id}"
class Student(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    department = models.ForeignKey(Department, related_name='students', on_delete=models.SET_NULL, null=True)
    age = models.PositiveIntegerField()
    student_class = models.ForeignKey('Class', related_name='students', on_delete=models.SET_NULL, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    id_number = models.CharField(max_length=18, unique=True)  # 身份证号码
    grade = models.ForeignKey(Grade, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')  # 改为 ForeignKey

    def __str__(self):
        return self.user.get_full_name()
class Semester(models.Model):
    name = models.CharField(max_length=50, unique=True)  # 例如 "2024春季"
    start_date = models.DateField()
    end_date = models.DateField()
    selection_start_week = models.PositiveIntegerField(default=1)
    selection_end_week = models.PositiveIntegerField(default=2)
    current_week = models.PositiveIntegerField(default=1)  # 当前周数

    def __str__(self):
        return self.name

class CourseInstance(models.Model):
    course_prototype = models.ForeignKey(CoursePrototype, on_delete=models.CASCADE, related_name='instances')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='course_instances')
    location = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField()
    selection_deadline = models.DateTimeField()
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='course_instances')
    daily_weight = models.PositiveSmallIntegerField(default=50)  # 平时分占比，默认为50%
    final_weight = models.PositiveSmallIntegerField(default=50)  # 期末分占比，默认为50%
    is_grades_published = models.BooleanField(default=False)  # 成绩是否已发布
    eligible_departments = models.ManyToManyField(Department, related_name='eligible_course_instances')
    eligible_grades = models.ManyToManyField(Grade, related_name='eligible_course_instances')
    eligible_classes = models.ManyToManyField(Class, related_name='eligible_course_instances')
    selected_students = models.ManyToManyField(User, related_name='selected_courses', blank=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, related_name='course_instances')
    is_finalized = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.daily_weight + self.final_weight != 100:
            raise ValueError("平时分和期末分的总和必须为100%")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.course_prototype.name} - {self.semester}"

class CourseSchedule(models.Model):
    course_instance = models.ForeignKey(CourseInstance, on_delete=models.CASCADE, related_name='schedules')
    
    DAY_PERIOD_CHOICES = [
        ('Monday', '星期一'),
        ('Tuesday', '星期二'),
        ('Wednesday', '星期三'),
        ('Thursday', '星期四'),
        ('Friday', '星期五'),
    ]
    
    PERIOD_CHOICES = [
        (1, '第一节'),
        (2, '第二节'),
        (3, '第三节'),
        (4, '第四节'),
        (5, '第五节'),
    ]
    
    day = models.CharField(max_length=10, choices=DAY_PERIOD_CHOICES)
    period = models.PositiveSmallIntegerField(choices=PERIOD_CHOICES)
    
    class Meta:
        unique_together = ('course_instance', 'day', 'period')  # 防止重复时间
    
    def __str__(self):
        return f"{self.get_day_display()} 第{self.get_period_display()}节 - {self.course_instance}"

class S_Grade(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='grades')
    course_instance = models.ForeignKey(CourseInstance, on_delete=models.CASCADE, related_name='grades')
    daily_score = models.FloatField(default=0.0)  # 平时分
    final_score = models.FloatField(default=0.0)  # 期末分
    total_score = models.FloatField(default=0.0)  # 总分

    class Meta:
        unique_together = ('student', 'course_instance')  # 确保每个学生在每个课程实例中只有一条成绩记录

    def save(self, *args, **kwargs):
        daily_weight = self.course_instance.daily_weight
        final_weight = self.course_instance.final_weight
        self.total_score = (self.daily_score * (daily_weight / 100)) + (self.final_score * (final_weight / 100))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.username} - {self.course_instance} - 总分: {self.total_score}"

class PunishmentRecord(models.Model):
    PUNISHMENT_TYPES = (
        ('DISCIPLINE', '纪律处分'),
        ('ACADEMIC', '学术处分'),
        ('OTHER', '其他'),
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='punishments')
    date = models.DateField(auto_now_add=True)
    type = models.CharField(max_length=20, choices=PUNISHMENT_TYPES)
    description = models.TextField()

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.get_type_display()}"

class RewardRecord(models.Model):
    REWARD_TYPES = (
        ('EXCELLENCE', '优秀学生'),
        ('OTHER', '其他'),
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='rewards')
    date = models.DateField(auto_now_add=True)
    type = models.CharField(max_length=20, choices=REWARD_TYPES)
    description = models.TextField()

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.get_type_display()}"
