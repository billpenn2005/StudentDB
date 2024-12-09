# backend/api/serializers.py

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Course, ClassInstance, CourseSelection, TimeSlot
from django.db import transaction

class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = ['id', 'period']

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'name', 'description']

class ClassInstanceSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(), write_only=True
    )
    time_slot = TimeSlotSerializer(read_only=True)
    time_slot_id = serializers.PrimaryKeyRelatedField(
        queryset=TimeSlot.objects.all(), write_only=True
    )
    enrolled_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = ClassInstance
        fields = ['id', 'course', 'course_id', 'group', 'time_slot', 'time_slot_id', 'teacher', 'capacity', 'enrolled_count']
        read_only_fields = ['id', 'course', 'time_slot', 'enrolled_count']

class CourseSelectionSerializer(serializers.ModelSerializer):
    class_instance = ClassInstanceSerializer(read_only=True)
    class_instance_id = serializers.PrimaryKeyRelatedField(
        queryset=ClassInstance.objects.all(), source='class_instance', write_only=True
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
        
        # 检查容量
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

class UserSerializer(serializers.ModelSerializer):
    groups = serializers.StringRelatedField(many=True, read_only=True)
    selected_courses = CourseSelectionSerializer(many=True, read_only=True, source='course_selections')

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'groups', 'selected_courses']
        read_only_fields = ['id', 'username', 'groups', 'selected_courses']

    def update(self, instance, validated_data):
        # 更新用户的基本信息
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.save()
        return instance
