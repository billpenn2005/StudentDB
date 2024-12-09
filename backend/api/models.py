<<<<<<< HEAD
# backend/api/models.py

from django.db import models
from django.contrib.auth.models import User

class TimeSlot(models.Model):
    PERIOD_CHOICES = [
        (1, '第一节'),
        (2, '第二节'),
        (3, '第三节'),
        (4, '第四节'),
        (5, '第五节'),
    ]
    period = models.IntegerField(choices=PERIOD_CHOICES, unique=True)

    def __str__(self):
        return f"第{self.period}节"

class Course(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    # 其他课程相关字段

    def __str__(self):
        return self.name

class Class(models.Model):
    course = models.ForeignKey(Course, related_name='classes', on_delete=models.CASCADE)
    group = models.CharField(max_length=50)  # 班级名称，例如 "A班"
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    teacher = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField(default=30)  # 容量字段
    # 其他班级相关字段，如教室、容量等

    def __str__(self):
        return f"{self.course.name} - {self.group} - {self.time_slot}"

    class Meta:
        unique_together = ('group', 'time_slot')  # 确保同一班级在同一时间只有一个课程

    @property
    def enrolled_count(self):
        return self.course_selections.count()

class CourseSelection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_selections')
    class_instance = models.ForeignKey(Class, on_delete=models.CASCADE)
    selected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'class_instance')  # 确保用户不能重复选同一课程

    def __str__(self):
        return f"{self.user.username} - {self.class_instance.course.name} - {self.class_instance.group}"

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True, blank=True)
    specialty = models.ForeignKey('Specialty', on_delete=models.SET_NULL, null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('M', '男'), ('F', '女')])
    age = models.PositiveIntegerField()
    id_number = models.CharField(max_length=20, unique=True)
    # 其他学生相关字段

    def __str__(self):
        return self.user.get_full_name()

class Department(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Specialty(models.Model):
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='specialties')

    def __str__(self):
        return self.name

class RewardPunishment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='rewards_punishments')
    description = models.TextField()
    date = models.DateField()
    type = models.CharField(max_length=20, choices=[('reward', '奖励'), ('punishment', '惩罚')])

    def __str__(self):
        return f"{self.student.user.username} - {self.type} - {self.date}"

class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')  # 确保学生不能重复选同一课程

    def __str__(self):
        return f"{self.student.user.username} - {self.course.name}"

class Exam(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='exams')
    exam_type = models.CharField(max_length=20, choices=[('midterm', '期中'), ('final', '期末')])
    date = models.DateField()
    score = models.FloatField()

    def __str__(self):
        return f"{self.enrollment.student.user.username} - {self.exam_type} - {self.course.name}"

class RetakeExam(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='retake_exams')
    original_exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='retake_exams')
    date = models.DateField()
    new_score = models.FloatField()

    def __str__(self):
        return f"{self.enrollment.student.user.username} - {self.original_exam.exam_type} - {self.original_exam.course.name} - Retake"

=======
>>>>>>> d621f73d01ec5b48ecc1852ea58fa51b1dcd7957
# api/models.py

from django.db import models
from django.contrib.auth.models import User

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)  # 院系描述

    def __str__(self):
        return self.name

class Specialty(models.Model):
    department = models.ForeignKey(Department, related_name='specialties', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)  # 专业方向描述

    class Meta:
        unique_together = ('department', 'name')

    def __str__(self):
        return f"{self.department.name} - {self.name}"

class Student(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    department = models.ForeignKey(Department, related_name='students', on_delete=models.SET_NULL, null=True)
    specialty = models.ForeignKey(Specialty, related_name='students', on_delete=models.SET_NULL, null=True)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    id_number = models.CharField(max_length=18, unique=True)  # 身份证号码
    major = models.CharField(max_length=100)  # 专业
    grade = models.PositiveIntegerField()  # 年级
    
    def __str__(self):
        return self.user.get_full_name()

class RewardPunishment(models.Model):
    REWARD_PUNISHMENT_CHOICES = (
        ('R', 'Reward'),
        ('P', 'Punishment'),
    )
    student = models.ForeignKey(Student, related_name='rewards_punishments', on_delete=models.CASCADE)
    type = models.CharField(max_length=1, choices=REWARD_PUNISHMENT_CHOICES)
    description = models.TextField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_type_display()} - {self.student.user.get_full_name()}"

class Course(models.Model):
    name = models.CharField(max_length=100, unique=True)
    department = models.ForeignKey(Department, related_name='courses', on_delete=models.SET_NULL, null=True)
    description = models.TextField(blank=True, null=True)
    credits = models.PositiveIntegerField(default=3)  # 学分

    def __str__(self):
        return self.name

class Enrollment(models.Model):
    student = models.ForeignKey(Student, related_name='enrollments', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='enrollments', on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.course.name}"

class Exam(models.Model):
    EXAM_TYPE_CHOICES = (
        ('U', 'Unit'),
        ('M', 'Midterm'),
        ('F', 'Final'),
    )
    enrollment = models.ForeignKey(Enrollment, related_name='exams', on_delete=models.CASCADE)
    exam_type = models.CharField(max_length=1, choices=EXAM_TYPE_CHOICES)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    date = models.DateField()

    def __str__(self):
        return f"{self.get_exam_type_display()} - {self.enrollment.course.name} - {self.enrollment.student.user.get_full_name()}"

class RetakeExam(models.Model):
    enrollment = models.ForeignKey(Enrollment, related_name='retakes', on_delete=models.CASCADE)
    original_exam = models.ForeignKey(Exam, related_name='retakes', on_delete=models.CASCADE)
    new_score = models.DecimalField(max_digits=5, decimal_places=2)
    date = models.DateField()

    def __str__(self):
        return f"Retake - {self.enrollment.course.name} - {self.enrollment.student.user.get_full_name()}"
