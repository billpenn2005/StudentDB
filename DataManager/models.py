from django.db import models
from Auth.models import AuthUser
# Create your models here.


class Department(models.Model):
    name=models.CharField('name',max_length=40)
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
    
class Student(models.Model):
    related_auth_account=models.ForeignKey(AuthUser,on_delete=models.CASCADE)
    name=models.CharField('name',max_length=40,null=True)
    student_id=models.CharField('student_id',max_length=40,null=True)
    department=models.ForeignKey(Department,on_delete=models.SET_NULL,null=True)
    grade=models.IntegerField('grade')

class Teacher(models.Model):
    related_auth_account=models.ForeignKey(AuthUser,on_delete=models.CASCADE)
    name=models.CharField('name',max_length=40,null=True)
    teacher_id=models.CharField('student_id',max_length=40,null=True)
    department=models.ForeignKey(Department,on_delete=models.SET_NULL,null=True)

