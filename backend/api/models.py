# backend/api/models.py

from django.db import models
from django.contrib.auth.models import User





class Department(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class CoursePrototype(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='course_prototypes')
    # 其他课程基础属性

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
    # 移除 department 字段，因为 Grade 已经关联到 Department

    def __str__(self):
        return self.name


class CourseInstance(models.Model):
    course_prototype = models.ForeignKey(CoursePrototype, on_delete=models.CASCADE, related_name='instances')
    semester = models.CharField(max_length=20)  # 如 "2024春"
    location = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField()
    selection_deadline = models.DateTimeField()
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='course_instances')

    # 上课时间：一天5大节课中的某大节
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

    # 可选课的选课对象（班级）
    eligible_departments = models.ManyToManyField(Department, related_name='eligible_course_instances')
    eligible_grades = models.ManyToManyField(Grade, related_name='eligible_course_instances')
    eligible_classes = models.ManyToManyField(Class, related_name='eligible_course_instances')

    # 已选学生
    selected_students = models.ManyToManyField(User, related_name='course_selected_courses', blank=True)

    # 课程最终化标志
    is_finalized = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.course_prototype.name} - {self.semester}"

class ClassInstance(models.Model):
    # 假设 ClassInstance 是不同于 CourseInstance 的一个模型，具体根据需求调整
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
    #specialty = models.ForeignKey(Specialty, related_name='students', on_delete=models.SET_NULL, null=True)
    age = models.PositiveIntegerField()
    student_class = models.ForeignKey(Class, related_name='students', on_delete=models.SET_NULL, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    id_number = models.CharField(max_length=18, unique=True)  # 身份证号码
    #major = models.CharField(max_length=100, default="NULL")  # 专业
    #grade = models.PositiveIntegerField(default=0)  # 年级
    
    def __str__(self):
        return self.user.get_full_name()