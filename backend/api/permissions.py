# api/permissions.py

from rest_framework import permissions

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

class IsStudentUser(permissions.BasePermission):
    """
    仅允许学生用户访问
    假设学生属于 'Student' 组
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.groups.filter(name='Student').exists())
