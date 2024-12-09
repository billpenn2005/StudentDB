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
