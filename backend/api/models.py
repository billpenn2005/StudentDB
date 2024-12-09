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


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    department_id = models.IntegerField()
    def __str__(self):
        return self.name


class Specialty(models.Model):
    name = models.CharField(max_length=100, unique=True)
    department = models.ForeignKey(Department, related_name='specialties', on_delete=models.CASCADE)
    Specialty_id = models.IntegerField()

    def __str__(self):
        return self.name
    


# api/models.py

from django.db import models
from django.contrib.auth.models import User


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
    major = models.CharField(max_length=100, default="NULL")  # 专业
    grade = models.PositiveIntegerField(default=0)  # 年级
    
    def __str__(self):
        return self.user.get_full_name()



class Course(models.Model):
    name = models.CharField(max_length=100, unique=True)
    department = models.ForeignKey(Department, related_name='courses', on_delete=models.SET_NULL, null=True)
    description = models.TextField(blank=True, null=True)
    credits = models.PositiveIntegerField(default=3)  # 学分
    course_id = models.IntegerField()

    def __str__(self):
        return self.name

class ClassInstance(models.Model):
    course = models.ForeignKey(Course, related_name='classes', on_delete=models.CASCADE)
    group = models.CharField(max_length=50)  # 班级名称，例如 "A班"
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    teacher = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField(default=50)  # 课程容量
    enrolled_count = models.PositiveIntegerField(default=0)  # 已选人数
    selected_students = models.ManyToManyField(User, through='CourseSelection', related_name='selected_courses')  # 已选学生

    # 其他班级相关字段

    def __str__(self):
        return f"{self.course.name} - {self.group} - {self.time_slot}"

    class Meta:
        unique_together = ('group', 'time_slot')  # 确保同一班级在同一时间只有一个课程

class CourseSelection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_selections')
    class_instance = models.ForeignKey(ClassInstance, on_delete=models.CASCADE)
    selected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'class_instance')  # 确保用户不能重复选同一课程

    def __str__(self):
        return f"{self.user.username} - {self.class_instance.course.name} - {self.class_instance.group}"