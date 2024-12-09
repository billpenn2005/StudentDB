# backend/api/viewsets.py

from rest_framework import viewsets, permissions, mixins, generics
from django.contrib.auth.models import User
from .models import Course, ClassInstance, CourseSelection, Student
from .serializers import (
    CourseSerializer,
    ClassInstanceSerializer,
    CourseSelectionSerializer,
    UserSerializer,
)
from django.db import transaction

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    自定义权限类，只有管理员可以编辑，其他人只能读取。
    """

    def has_permission(self, request, view):
        # 允许所有人进行安全的方法（GET、HEAD、OPTIONS）
        if request.method in permissions.SAFE_METHODS:
            return True
        # 只有管理员可以进行其他操作
        return request.user and request.user.is_staff
    
class StudentViewSet(viewsets.ModelViewSet):
    """
    ViewSet 用于查看和编辑学生实例。
    """
    queryset = Student.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            print("swagger_fake_view")
            return CourseSelection.objects.none()

        # 确保在非 swagger 文档生成请求中再去判断用户
        if not self.request.user.is_authenticated:
            return CourseSelection.objects.none()
        
        return CourseSelection.objects.filter(user=self.request.user).select_related(
            'class_instance__course',
            'class_instance__time_slot'
        )

class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet 用于查看和编辑课程实例。
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            print("swagger_fake_view")
            return CourseSelection.objects.none()

        # 确保在非 swagger 文档生成请求中再去判断用户
        if not self.request.user.is_authenticated:
            return CourseSelection.objects.none()
        
        return CourseSelection.objects.filter(user=self.request.user).select_related(
            'class_instance__course',
            'class_instance__time_slot'
        )

class ClassInstanceViewSet(viewsets.ModelViewSet):
    """
    ViewSet 用于查看和编辑班级实例。
    """
    queryset = ClassInstance.objects.all()
    serializer_class = ClassInstanceSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            print("swagger_fake_view")
            return CourseSelection.objects.none()

        # 确保在非 swagger 文档生成请求中再去判断用户
        if not self.request.user.is_authenticated:
            return CourseSelection.objects.none()
        
        return CourseSelection.objects.filter(user=self.request.user).select_related(
            'class_instance__course',
            'class_instance__time_slot'
        )

class CourseSelectionViewSet(viewsets.ModelViewSet):
    """
    ViewSet 用于查看和创建课程选课记录。
    """
    queryset = CourseSelection.objects.all()
    serializer_class = CourseSelectionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            print("swagger_fake_view")
            return CourseSelection.objects.none()

        # 确保在非 swagger 文档生成请求中再去判断用户
        if not self.request.user.is_authenticated:
            return CourseSelection.objects.none()
        
        return CourseSelection.objects.filter(user=self.request.user).select_related(
            'class_instance__course',
            'class_instance__time_slot'
        )

    def perform_create(self, serializer):
        # 将当前用户关联到选课记录
        serializer.save(user=self.request.user)

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet 用于查看用户信息，仅允许读取。
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]  # 仅管理员可以查看所有用户

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            print("swagger_fake_view")
            return CourseSelection.objects.none()

        # 确保在非 swagger 文档生成请求中再去判断用户
        if not self.request.user.is_authenticated:
            return CourseSelection.objects.none()
        
        return CourseSelection.objects.filter(user=self.request.user).select_related(
            'class_instance__course',
            'class_instance__time_slot'
        )

# class CourseSelectionCreateView(generics.CreateAPIView):

from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from django.http import HttpResponse
from reportlab.pdfgen import canvas

class GenerateStudentReportView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, format=None):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="student_report.pdf"'

        p = canvas.Canvas(response)
        p.setFont("Helvetica", 16)
        p.drawString(100, 800, "学生信息报表")

        students = Student.objects.all()
        y = 750
        p.setFont("Helvetica", 12)
        for student in students:
            text = f"姓名: {student.user.get_full_name()}, 单位: {student.department.name if student.department else 'N/A'}, 年龄: {student.age}, 性别: {student.get_gender_display()}, 身份证号码: {student.id_number}"
            p.drawString(100, y, text)
            y -= 20
            if y < 50:
                p.showPage()
                y = 800

        p.showPage()
        p.save()
        return response


class CurrentUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
    
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"detail": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)