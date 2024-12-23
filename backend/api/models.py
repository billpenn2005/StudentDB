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
    total_weeks = models.PositiveIntegerField(default=20, help_text="学期总周数")
    is_current = models.BooleanField(default=False)  # 新增字段，用于标识当前学期

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.is_current:
            # 将其他学期的 is_current 设为 False
            Semester.objects.filter(is_current=True).update(is_current=False)
        super().save(*args, **kwargs)
    
class SelectionBatch(models.Model):
    name = models.CharField(max_length=100, unique=True)
    start_selection_date = models.DateTimeField()
    end_selection_date = models.DateTimeField()
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='selection_batches')

    def __str__(self):
        return f"{self.name} ({self.semester.name})"

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
    selection_batch = models.ForeignKey(SelectionBatch, on_delete=models.CASCADE, related_name='course_instances', null=True, blank=True)

    def save(self, *args, **kwargs):
        # 当保存课程实例时，同步选课批次的时间
        if self.selection_batch:
            self.selection_deadline = self.selection_batch.end_selection_date
            # 假设你有一个开始选课时间字段，可以类似设置
            # self.selection_start_date = self.selection_batch.start_selection_date
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
    start_week = models.PositiveIntegerField(default=1, help_text="课程开始的周数")
    end_week = models.PositiveIntegerField(help_text="课程结束的周数", default=1)
    frequency = models.PositiveSmallIntegerField(default=1, help_text="上课频率（如1表示每周一次，2表示每两周一次）")
    exceptions = models.JSONField(default=list, blank=True, help_text="例外周数，课程在这些周不进行")
    class Meta:
        unique_together = ('course_instance', 'day', 'period', 'start_week', 'frequency')
        verbose_name = "课程时间安排"
        verbose_name_plural = "课程时间安排"    
    def __str__(self):
        return f"{self.get_day_display()} 第{self.get_period_display()}节 - {self.course_instance}"
    def is_active_in_week(self, week_number):
        """
        判断该课程在指定的周数是否有课。
        """
        if week_number < self.start_week or week_number > self.end_week:
            return False
        if (week_number - self.start_week) % self.frequency != 0:
            return False
        if week_number in self.exceptions:
            return False
        return True
# backend/api/models.py (示例节选)

class S_Grade(models.Model):
    """
    学生成绩表，用于记录每个学生在每门课程实例下的成绩。
    现在新增 attempt 字段，以区分首考、补考、重修等多次考试。
    """

    ATTEMPT_CHOICES = [
        (1, '首考'),
        (2, '补考'),
        (3, '重修'),
        # 如果需要更多次数，还可继续添加
    ]

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='grades')
    course_instance = models.ForeignKey(CourseInstance, on_delete=models.CASCADE, related_name='grades')

    # 新增字段：表示第几次考试，默认为 1（首考）
    attempt = models.PositiveSmallIntegerField(
        choices=ATTEMPT_CHOICES,
        default=1,
        verbose_name='考试轮次'
    )

    daily_score = models.FloatField(default=0.0)  # 平时分
    final_score = models.FloatField(default=0.0)  # 期末分
    total_score = models.FloatField(default=0.0)  # 总分

    # 原有的 unique_together = ('student', 'course_instance') 不再适用，
    # 因为要允许同一个学生在同一门课下出现多条记录（不同的 attempt）。
    # 因此改为包含 attempt:
    class Meta:
        unique_together = ('student', 'course_instance', 'attempt')  
        # 这样可以确保 (学生, 课程, 考试轮次) 的唯一性

    def save(self, *args, **kwargs):
        # 自动计算 total_score
        daily_weight = self.course_instance.daily_weight
        final_weight = self.course_instance.final_weight
        self.total_score = (
            self.daily_score * (daily_weight / 100.0)
            + self.final_score * (final_weight / 100.0)
        )
        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.student.username} - {self.course_instance} - "
            f"总分: {self.total_score} (attempt={self.attempt})"
        )


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


