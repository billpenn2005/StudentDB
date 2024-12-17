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

class IsTeacherOfCourse(permissions.BasePermission):
    """
    只有负责该课程实例的教师可以修改成绩
    """

    def has_object_permission(self, request, view, obj):
        if not request.user.groups.filter(name='Teacher').exists():
            return False
        # 假设教师关联到部门，通过部门关联到课程实例
        teacher_departments = request.user.teacher_profile.departments.all()
        return obj.course_instance.department in teacher_departments

class IsOwnerStudent(permissions.BasePermission):
    """
    只有成绩所属的学生可以查看
    """

    def has_object_permission(self, request, view, obj):
        return obj.student == request.user