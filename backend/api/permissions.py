# api/permissions.py

from rest_framework import permissions
from .models import CourseInstance
class IsAdminUser(permissions.BasePermission):
    """
    仅允许管理员用户访问
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff)

class IsTeacherUser(permissions.BasePermission):
    """
    仅允许教师用户访问
    假设教师属于 'Teacher' 组
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.groups.filter(name='Teacher').exists())

class IsAdminOrTeacher(permissions.BasePermission):
    """
    允许管理员（is_staff=True）或在Teacher组里的用户访问
    """

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and (
                user.is_staff or  # 管理员
                user.groups.filter(name='Teacher').exists()  # 教师
            )
        )

class IsStudentUser(permissions.BasePermission):
    """
    仅允许学生用户访问
    假设学生属于 'Student' 组
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.groups.filter(name='Student').exists())

class IsTeacherOfCourse(permissions.BasePermission):
    """
    仅允许课程实例的教师进行某些操作
    """

    def has_object_permission(self, request, view, obj):
        # 确保 obj 是 CourseInstance 的实例
        if not isinstance(obj, CourseInstance):
            return False
        # 检查请求用户是否为该课程实例的教师
        return obj.teacher == request.user.teacher_profile

class IsOwnerStudent(permissions.BasePermission):
    """
    只有成绩所属的学生可以查看
    """

    def has_object_permission(self, request, view, obj):
        return obj.student.user == request.user