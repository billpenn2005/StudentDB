# api/serializers.py

from rest_framework import serializers
from django.contrib.auth.models import User, Group
from .models import (
    Department, Specialty, Student,
    RewardPunishment, Course, Enrollment,
<<<<<<< HEAD
    Exam, RetakeExam, TimeSlot,Class,CourseSelection,ClassInstance
)
from django.db import transaction

=======
    Exam, RetakeExam
)
>>>>>>> d621f73d01ec5b48ecc1852ea58fa51b1dcd7957
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

<<<<<<< HEAD


=======
>>>>>>> d621f73d01ec5b48ecc1852ea58fa51b1dcd7957
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

<<<<<<< HEAD
class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = ['id', 'period']

=======
>>>>>>> d621f73d01ec5b48ecc1852ea58fa51b1dcd7957
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
<<<<<<< HEAD


class ClassSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(), source='course', write_only=True
    )
    time_slot = TimeSlotSerializer(read_only=True)
    time_slot_id = serializers.PrimaryKeyRelatedField(
        queryset=TimeSlot.objects.all(), source='time_slot', write_only=True
    )

    class Meta:
        model = Class
        fields = ['id', 'course', 'course_id', 'group', 'time_slot', 'time_slot_id', 'teacher']
#TODO:: 检查classselection模型是否正确
class CourseSelectionSerializer(serializers.ModelSerializer):
    class_instance = ClassSerializer(read_only=True)
    class_instance_id = serializers.PrimaryKeyRelatedField(
        queryset=Class.objects.all(), source='class_instance', write_only=True
    )

    class Meta:
        model = CourseSelection
        fields = ['id', 'class_instance', 'class_instance_id', 'user', 'selected_at']
        read_only_fields = ['id', 'user', 'selected_at']

    def validate(self, data):
        user = self.context['request'].user
        class_instance = data['class_instance']

        # 检查是否已经选过该课程
        if CourseSelection.objects.filter(user=user, class_instance=class_instance).exists():
            raise serializers.ValidationError("您已经选过该课程。")

        # 检查时间冲突
        existing_selections = CourseSelection.objects.filter(user=user).select_related('class_instance__time_slot')
        for selection in existing_selections:
            if selection.class_instance.time_slot == class_instance.time_slot:
                raise serializers.ValidationError(
                    f"课程时间与已选课程 '{selection.class_instance.course.name}' 冲突。"
                )
        
        if class_instance.enrolled_count >= class_instance.capacity:
            raise serializers.ValidationError("该班级已达到最大容量，无法再选取。")
        
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        class_instance = validated_data['class_instance']
        
        with transaction.atomic():
            # 锁定当前班级记录，防止其他事务修改
            class_instance = ClassInstance.objects.select_for_update().get(id=class_instance.id)
            
            if class_instance.enrolled_count >= class_instance.capacity:
                raise serializers.ValidationError("该班级已达到最大容量，无法再选取。")
            
            course_selection = CourseSelection.objects.create(
                user=user,
                class_instance=class_instance
            )
        
        return course_selection
=======
>>>>>>> d621f73d01ec5b48ecc1852ea58fa51b1dcd7957
