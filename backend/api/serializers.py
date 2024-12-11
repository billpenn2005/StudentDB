# backend/api/serializers.py

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Department, Grade, Class, CoursePrototype, CourseInstance, Student
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

class CourseInstanceSerializer(serializers.ModelSerializer):
    course_prototype = CoursePrototypeSerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)
    eligible_departments = DepartmentSerializer(many=True, read_only=True)
    eligible_grades = GradeSerializer(many=True, read_only=True)
    eligible_classes = ClassSerializer(many=True, read_only=True)
    selected_students = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = CourseInstance
        fields = '__all__'

class CourseInstanceCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseInstance
        fields = '__all__'

class StudentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    grade = GradeSerializer(read_only=True)
    student_class = ClassSerializer(read_only=True)

    class Meta:
        model = Student
        fields = ['user', 'student_id', 'grade', 'student_class']

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
