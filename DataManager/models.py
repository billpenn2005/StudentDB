from django.db import models
from Auth.models import AuthUser
from django.utils import timezone
import random
# Create your models here.


class Department(models.Model):
    name=models.CharField('name',max_length=40)
    def __str__(self):
        return self.name
    
class Major(models.Model):
    name=models.CharField('name',max_length=40)
    related_department=models.ForeignKey(Department,on_delete=models.CASCADE)
    def __str__(self):
        return self.name

class Building(models.Model):
    name=models.CharField('name',max_length=40)
    related_department=models.ForeignKey(Department,on_delete=models.CASCADE,null=True)
    def __str__(self):
        return self.name

class ClassRoom(models.Model):
    related_building=models.ForeignKey(Building,on_delete=models.CASCADE)
    number=models.CharField('number',max_length=40)
    capacity=models.IntegerField('capacity')
    def __str__(self):
        return self.related_building.name+' '+self.number
    

class TimeSlot(models.Model):
    # 定义时间段和它们的显示名称
    TIME_SLOTS = [
        ('0', '8:00-10:00'),
        ('1', '10:10-12:00'),
        ('2', '14:00-15:50'),
        ('3', '16:10-18:00'),
        ('4', '19:00-20:50'),
    ]
    
    # 使用CharField来存储时间段的标识，并限制为选择列表中的值
    slot = models.CharField('slot',max_length=10, choices=TIME_SLOTS,primary_key=False,unique=False)
    day=models.IntegerField('day',primary_key=False,unique=False,null=True)
    week=models.IntegerField('week',primary_key=False,unique=False,null=True)
    def __str__(self):
        return 'week '+str(self.week)+' day '+str(self.day)+' '+self.TIME_SLOTS[int(self.slot)][1]

class Section(models.Model):
    name=models.CharField('name',max_length=40,null=True)
    start_date = models.DateTimeField()  # 学期的开始日期
    end_date = models.DateTimeField()    # 学期的结束日期
    def __str__(self):
        return self.name

class Course(models.Model):
    name=models.CharField('name',max_length=40,null=True)
    department=models.ForeignKey(Department,on_delete=models.SET_NULL,null=True)
    classroom=models.ForeignKey(ClassRoom,on_delete=models.SET_NULL,null=True)
    section=models.ForeignKey(Section,on_delete=models.SET_NULL,null=True)
    timeslots=models.ManyToManyField(TimeSlot,through='CourseTimeSlot')
    def __str__(self):
        return self.section.name+' '+self.name

class CourseTimeSlot(models.Model):
    course=models.ForeignKey(Course,on_delete=models.CASCADE)
    time_slot=models.ForeignKey(TimeSlot,on_delete=models.CASCADE)
    def __str__(self):
        return str(self.course)+' on '+str(self.time_slot)


class Reward(models.Model):
    name=models.CharField('name',max_length=40)
    time=models.DateField(null=True)
    detail=models.CharField('detail',max_length=200)

class Punishment(models.Model):
    name=models.CharField('name',max_length=40)
    time=models.DateField(null=True)
    detail=models.CharField('detail',max_length=200)


class Student(models.Model):
    related_auth_account=models.ForeignKey(AuthUser,on_delete=models.CASCADE)
    name=models.CharField('name',max_length=40,null=True)
    student_id=models.CharField('student_id',max_length=40,null=True,unique=True)
    department=models.ForeignKey(Department,on_delete=models.SET_NULL,null=True)
    major=models.ForeignKey(Major,on_delete=models.SET_NULL,null=True)
    grade=models.IntegerField('grade')
    courses=models.ManyToManyField(Course,through='StudentTake')
    SEXS = [
        ('0', 'Male'),
        ('1', 'Female'),
    ]
    sex=models.CharField('sex',max_length=10,choices=SEXS,primary_key=False,unique=False)
    identity_id=models.CharField('identity_id',max_length=20)
    brithday=models.DateField('birthday',null=True)
    rewards=models.ManyToManyField(to=Reward,through='StudentReward')
    punishments=models.ManyToManyField(to=Punishment,through='StudentPunish')
    def __str__(self):
        return self.name
    
class StudentReward(models.Model):
    student=models.ForeignKey(Student,on_delete=models.CASCADE)
    reward=models.ForeignKey(Reward,on_delete=models.CASCADE)

class StudentPunish(models.Model):
    student=models.ForeignKey(Student,on_delete=models.CASCADE)
    punish=models.ForeignKey(Punishment,on_delete=models.CASCADE)

class Teacher(models.Model):
    related_auth_account=models.ForeignKey(AuthUser,on_delete=models.CASCADE)
    name=models.CharField('name',max_length=40,null=True)
    teacher_id=models.CharField('teacher_id',max_length=40,null=True,unique=True)
    department=models.ForeignKey(Department,on_delete=models.SET_NULL,null=True)
    courses=models.ManyToManyField(Course,through='TeacherTeach')
    permissioned_departments=models.ManyToManyField(Department,through='DepartmentPermission',related_name='permissioned_departments')
    permissioned_majors=models.ManyToManyField(Major,through='MajorPermission',related_name='permissioned_majors')
    def __str__(self):
        return self.name
    
class DepartmentPermission(models.Model):
    department=models.ForeignKey(Department,on_delete=models.CASCADE)
    teacher=models.ForeignKey(Teacher,on_delete=models.CASCADE)

class MajorPermission(models.Model):
    major=models.ForeignKey(Major,on_delete=models.CASCADE)
    teacher=models.ForeignKey(Teacher,on_delete=models.CASCADE)

class StudentTake(models.Model):
    student=models.ForeignKey(Student,on_delete=models.CASCADE)
    course=models.ForeignKey(Course,on_delete=models.CASCADE)
    def __str__(self):
        return self.student.name+' takes '+self.course.name

class TeacherTeach(models.Model):
    teacher=models.ForeignKey(Teacher,on_delete=models.CASCADE)
    course=models.ForeignKey(Course,on_delete=models.CASCADE)
    def __str__(self):
        return self.teacher.name+' teaches '+self.course.name

class Selection(models.Model):
    name=models.CharField('name',max_length=40)
    courses=models.ManyToManyField(Course,through='CourseSelection')
    start_date=models.DateTimeField(default=timezone.datetime.fromtimestamp(0))
    end_date=models.DateTimeField(default=timezone.datetime.fromtimestamp(0))
    def CheckAll(self,student):
        if timezone.now()<=self.end_date:
            return
        s_s_obj=StudentSelection.objects.filter(student=student,selection__id=self.id).first()
        if s_s_obj is not None and s_s_obj.checked is False:
            s_c=list(s_s_obj.selected_courses.all())
            for i in s_c:
                c_s=CourseSelection.objects.filter(course=i,selection=self).first()
                if c_s is not None:
                    if c_s.capacity is None or c_s.capacity>=c_s.num:
                        if StudentTake.objects.filter(student=student,course=i).first() is None:
                            StudentTake.objects.create(student=student,course=i)
                    else:
                        rnd=random.randrange(1,c_s.num+1)
                        if rnd<=c_s.capacity and c_s.capacity>0:
                            if StudentTake.objects.filter(student=student,course=s_c).first() is None:
                                StudentTake.objects.create(student=student,course=s_c)
                            c_s.num-=1
                            c_s.capacity-=1
                            c_s.save()
                        else:
                            c_s.num-=1
                            c_s.save()
            s_s_obj.checked=True
            s_s_obj.save()
    def __str__(self):
        return self.name

class StudentSelection(models.Model):
    student=models.ForeignKey(Student,on_delete=models.CASCADE)
    selection=models.ForeignKey(Selection,on_delete=models.CASCADE)
    selected_courses=models.ManyToManyField(Course,through='StudentSelectionCourse')
    checked=models.BooleanField(default=False)

class CourseSelection(models.Model):
    selection=models.ForeignKey(Selection,on_delete=models.CASCADE)
    course=models.ForeignKey(Course,on_delete=models.CASCADE)
    capacity=models.IntegerField(null=True)
    num=models.IntegerField(default=0)

class StudentSelectionCourse(models.Model):
    studentselection=models.ForeignKey(StudentSelection,on_delete=models.CASCADE)
    course=models.ForeignKey(Course,on_delete=models.CASCADE)