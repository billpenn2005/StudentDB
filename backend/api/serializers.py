# api/serializers.py

from rest_framework import serializers
from django.contrib.auth.models import User, Group
from .models import (
    Department, Specialty, Student,
    RewardPunishment, Course, Enrollment,
    Exam, RetakeExam
)
class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['name']

class UserSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True, read_only=True)

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

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'description']

class SpecialtySerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        source='department',
        write_only=True
    )

    class Meta:
        model = Specialty
        fields = ['id', 'name', 'description', 'department', 'department_id']

class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        source='department',
        write_only=True
    )
    specialty = SpecialtySerializer(read_only=True)
    specialty_id = serializers.PrimaryKeyRelatedField(
        queryset=Specialty.objects.all(),
        source='specialty',
        write_only=True
    )

    class Meta:
        model = Student
        fields = [
            'id', 'user', 'department', 'department_id',
            'specialty', 'specialty_id', 'age',
            'gender', 'id_number'
        ]

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        password = user_data.pop('password', None)
        user = User.objects.create(**user_data)
        if password:
            user.set_password(password)
            user.save()
        student = Student.objects.create(user=user, **validated_data)
        return student

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            user_serializer = UserSerializer(instance.user, data=user_data, partial=True)
            if user_serializer.is_valid():
                user_serializer.save()
        return super().update(instance, validated_data)

class RewardPunishmentSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(),
        source='student',
        write_only=True
    )

    class Meta:
        model = RewardPunishment
        fields = ['id', 'student', 'student_id', 'type', 'description', 'date']

class CourseSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        source='department',
        write_only=True
    )

    class Meta:
        model = Course
        fields = ['id', 'name', 'description', 'credits', 'department', 'department_id']

class EnrollmentSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(),
        source='student',
        write_only=True
    )
    course = CourseSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(),
        source='course',
        write_only=True
    )

    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'student_id', 'course', 'course_id', 'enrolled_at']

class ExamSerializer(serializers.ModelSerializer):
    enrollment = EnrollmentSerializer(read_only=True)
    enrollment_id = serializers.PrimaryKeyRelatedField(
        queryset=Enrollment.objects.all(),
        source='enrollment',
        write_only=True
    )

    class Meta:
        model = Exam
        fields = ['id', 'enrollment', 'enrollment_id', 'exam_type', 'score', 'date']

class RetakeExamSerializer(serializers.ModelSerializer):
    enrollment = EnrollmentSerializer(read_only=True)
    enrollment_id = serializers.PrimaryKeyRelatedField(
        queryset=Enrollment.objects.all(),
        source='enrollment',
        write_only=True
    )
    original_exam = ExamSerializer(read_only=True)
    original_exam_id = serializers.PrimaryKeyRelatedField(
        queryset=Exam.objects.all(),
        source='original_exam',
        write_only=True
    )

    class Meta:
        model = RetakeExam
        fields = ['id', 'enrollment', 'enrollment_id', 'original_exam', 'original_exam_id', 'new_score', 'date']
