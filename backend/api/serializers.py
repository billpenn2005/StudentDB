# backend/api/serializers.py

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Department, Grade, Class, CoursePrototype, CourseInstance, Student,
    CourseSchedule, Teacher, S_Grade, Semester, PunishmentRecord, RewardRecord
)
from django.db import transaction
#from django.contrib.auth import get_user_model

#User = get_user_model()

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name']

class ClassSerializer(serializers.ModelSerializer):
    grade = serializers.StringRelatedField()
    department = serializers.StringRelatedField()
    
    class Meta:
        model = Class
        fields = ['id', 'name', 'grade', 'department']

class GradeSerializer(serializers.ModelSerializer):
    department = serializers.StringRelatedField()
    
    class Meta:
        model = Grade
        fields = ['id', 'name', 'department']


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
    teacher_id = serializers.SerializerMethodField()
    student_id = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'groups', 'teacher_id', 'student_id']
        read_only_fields = ['id', 'username', 'groups', 'teacher_id', 'student_id']

    def update(self, instance, validated_data):
        # 更新用户的基本信息
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.save()
        return instance
    
    def get_teacher_id(self, obj):
        try:
            return obj.teacher_profile.id
        except Teacher.DoesNotExist:
            return None

    def get_student_id(self, obj):
        try:
            return obj.student_profile.id
        except Student.DoesNotExist:
            return None

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
    
class SemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semester
        fields = ['id', 'name', 'start_date', 'end_date', 'selection_start_week', 'selection_end_week', 'current_week']

class PunishmentRecordSerializer(serializers.ModelSerializer):
    student = serializers.StringRelatedField(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(), source='student', write_only=True
    )

    class Meta:
        model = PunishmentRecord
        fields = ['id', 'student', 'student_id', 'date', 'type', 'description']

class RewardRecordSerializer(serializers.ModelSerializer):
    student = serializers.StringRelatedField(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(), source='student', write_only=True
    )

    class Meta:
        model = RewardRecord
        fields = ['id', 'student', 'student_id', 'date', 'type', 'description']

class SemesterCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semester
        fields = '__all__'

class PunishmentRecordCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PunishmentRecord
        fields = ['id', 'student', 'type', 'description']

class RewardRecordCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RewardRecord
        fields = ['id', 'student', 'type', 'description']

class CourseInstanceSerializer(serializers.ModelSerializer):
    course_prototype = CoursePrototypeSerializer(read_only=True)
    semester = SemesterSerializer(read_only=True)
    semester_id = serializers.PrimaryKeyRelatedField(
        queryset=Semester.objects.all(), source='semester', write_only=True
    )
    department = DepartmentSerializer(read_only=True)
    eligible_departments = DepartmentSerializer(many=True, read_only=True)
    eligible_grades = GradeSerializer(many=True, read_only=True)
    eligible_classes = ClassSerializer(many=True, read_only=True)
    selected_students = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    schedules = CourseScheduleSerializer(many=True, read_only=True)
    teacher = TeacherSerializer(read_only=True)
    teacher_id = serializers.PrimaryKeyRelatedField(
        queryset=Teacher.objects.all(), source='teacher', write_only=True, allow_null=True, required=False
    )

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
    )

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
    user = UserSerializer(read_only=True)
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all())
    student_class = serializers.PrimaryKeyRelatedField(queryset=Class.objects.all())
    grade = serializers.PrimaryKeyRelatedField(queryset=Grade.objects.all())
    
    class Meta:
        model = Student
        fields = ['id', 'user', 'department', 'student_class', 'grade', 'age', 'gender', 'id_number']
        read_only_fields = ['department', 'student_class', 'grade', 'age', 'gender', 'id_number']  # 只允许更新邮箱


class S_GradeSerializer(serializers.ModelSerializer):
    student = serializers.StringRelatedField(read_only=True)
    course_instance = serializers.StringRelatedField(read_only=True)
    course_instance_id = serializers.PrimaryKeyRelatedField(
        queryset=CourseInstance.objects.all(), source='course_instance', write_only=True
    )
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(groups__name='Student'), source='student', write_only=True
    )
    is_published = serializers.SerializerMethodField()
    ranking = serializers.IntegerField(read_only=True)
    semester = serializers.CharField(source='course_instance.semester.name', read_only=True)
    class Meta:
        model = S_Grade
        fields = ['id', 'student', 'student_id', 'course_instance', 'course_instance_id', 'daily_score', 'final_score', 'total_score', 'is_published', 'ranking', 'semester']
        read_only_fields = ['id', 'student', 'course_instance', 'total_score']

    def validate(self, data):
        # 确保教师只能给自己授课的课程实例打分
        user = self.context['request'].user
        course_instance = data.get('course_instance')
        
        if not hasattr(user, 'teacher_profile'):
            raise serializers.ValidationError("用户没有教师配置文件。")
        
        if not CourseInstance.objects.filter(id=course_instance.id, teacher=user.teacher_profile).exists():
            raise serializers.ValidationError("您无权给该课程实例打分。")
        return data

    def create(self, validated_data):
        return S_Grade.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.daily_score = validated_data.get('daily_score', instance.daily_score)
        instance.final_score = validated_data.get('final_score', instance.final_score)
        instance.save()
        return instance
    
    def get_is_published(self, obj):
        return obj.course_instance.is_grades_published

    def get_ranking(self, obj):
        # 假设在queryset中已使用annotate标记了ranking字段
        # ranking计算逻辑在ViewSet中实现
        return getattr(obj, 'ranking', None)

