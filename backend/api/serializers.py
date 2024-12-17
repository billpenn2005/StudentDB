# backend/api/serializers.py

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Department, Grade, Class, CoursePrototype, CourseInstance, Student, CourseSchedule, Teacher,S_Grade
from django.db import transaction
#from django.contrib.auth import get_user_model

#User = get_user_model()

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

class GradeSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    
    class Meta:
        model = Grade
        fields = '__all__'

class ClassSerializer(serializers.ModelSerializer):
    grade = GradeSerializer(read_only=True)
    # 移除 department 字段，因为 Grade 已经关联到 Department

    class Meta:
        model = Class
        fields = '__all__'

class CoursePrototypeSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)

    class Meta:
        model = CoursePrototype
        fields = '__all__'
# backend/api/serializers.py

class CourseScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseSchedule
        fields = ['id', 'day', 'period']


class UserSerializer(serializers.ModelSerializer):
    groups = serializers.StringRelatedField(many=True, read_only=True)
    #selected_courses = CourseSelectionSerializer(many=True, read_only=True, source='course_selections')

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'groups']
        read_only_fields = ['id', 'username', 'groups']

    def update(self, instance, validated_data):
        # 更新用户的基本信息
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.save()
        return instance

class TeacherSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    departments = DepartmentSerializer(many=True, read_only=True)
    department_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Department.objects.all(), write_only=True, source='departments'
    )

    class Meta:
        model = Teacher
        fields = ['id', 'user', 'departments', 'department_ids']
        read_only_fields = ['id', 'user', 'departments']

    def update(self, instance, validated_data):
        departments = validated_data.pop('departments', None)
        if departments is not None:
            instance.departments.set(departments)
        return super().update(instance, validated_data)
    
class CourseInstanceSerializer(serializers.ModelSerializer):
    course_prototype = CoursePrototypeSerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)
    eligible_departments = DepartmentSerializer(many=True, read_only=True)
    eligible_grades = GradeSerializer(many=True, read_only=True)
    eligible_classes = ClassSerializer(many=True, read_only=True)
    selected_students = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    schedules = CourseScheduleSerializer(many=True, read_only=True)  # 新增字段
    teacher = TeacherSerializer(read_only=True)  # 添加只读字段
    teacher_id = serializers.PrimaryKeyRelatedField(
        queryset=Teacher.objects.all(), source='teacher', write_only=True, allow_null=True, required=False
    )  # 新增字段
    class Meta:
        model = CourseInstance
        fields = '__all__'

class CourseInstanceCreateUpdateSerializer(serializers.ModelSerializer):
    schedules = CourseScheduleSerializer(many=True)
    selected_students = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all(), required=False
    )
    eligible_classes = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Class.objects.all(), required=False
    )
    teacher_id = serializers.PrimaryKeyRelatedField(
        queryset=Teacher.objects.all(), source='teacher', write_only=True, allow_null=True, required=False
    )  # 新增字段
    class Meta:
        model = CourseInstance
        fields = '__all__'
    
    def create(self, validated_data):
        schedules_data = validated_data.pop('schedules')
        selected_students = validated_data.pop('selected_students', [])
        eligible_classes = validated_data.pop('eligible_classes', [])
        course_instance = CourseInstance.objects.create(**validated_data)
        course_instance.selected_students.set(selected_students)
        course_instance.eligible_classes.set(eligible_classes)
        for schedule_data in schedules_data:
            CourseSchedule.objects.create(course_instance=course_instance, **schedule_data)
        return course_instance
    
    def update(self, instance, validated_data):
        schedules_data = validated_data.pop('schedules', None)
        selected_students = validated_data.pop('selected_students', None)
        eligible_classes = validated_data.pop('eligible_classes', None)
    
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
    
        if schedules_data is not None:
            instance.schedules.all().delete()
            for schedule_data in schedules_data:
                CourseSchedule.objects.create(course_instance=instance, **schedule_data)
    
        if selected_students is not None:
            instance.selected_students.set(selected_students)
                
        if eligible_classes is not None:
            instance.eligible_classes.set(eligible_classes)
    
        return instance
    

    def validate(self, data):
        daily_weight = data.get('daily_weight', 50)
        final_weight = data.get('final_weight', 50)
        if daily_weight + final_weight != 100:
            raise serializers.ValidationError("平时分和期末分的总和必须为100%")
        return data

class StudentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    grade = GradeSerializer(read_only=True)
    student_class = ClassSerializer(read_only=True)

    class Meta:
        model = Student
        fields = ['user', 'student_id', 'grade', 'student_class']


class S_GradeSerializer(serializers.ModelSerializer):
    student = serializers.StringRelatedField(read_only=True)
    course_instance = serializers.StringRelatedField(read_only=True)
    course_instance_id = serializers.PrimaryKeyRelatedField(
        queryset=CourseInstance.objects.all(), source='course_instance', write_only=True
    )
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(groups__name='Student'), source='student', write_only=True
    )

    class Meta:
        model = S_Grade
        fields = ['id', 'student', 'student_id', 'course_instance', 'course_instance_id', 'daily_score', 'final_score', 'total_score']
        read_only_fields = ['id', 'student', 'course_instance', 'total_score']

    def validate(self, data):
        # 确保教师只能给自己授课的课程实例打分
        user = self.context['request'].user
        course_instance = data.get('course_instance')
        if not CourseInstance.objects.filter(id=course_instance.id, department__in=user.departments.all()).exists():
            raise serializers.ValidationError("您无权给该课程实例打分。")
        return data

    def create(self, validated_data):
        return Grade.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.daily_score = validated_data.get('daily_score', instance.daily_score)
        instance.final_score = validated_data.get('final_score', instance.final_score)
        instance.save()
        return instance

