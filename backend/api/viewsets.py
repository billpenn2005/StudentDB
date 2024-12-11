# backend/api/viewsets.py

from rest_framework import viewsets, permissions, mixins, generics
from django.contrib.auth.models import User
from .models import CoursePrototype, CourseInstance, Student
from .serializers import (
    CoursePrototypeSerializer, CourseInstanceSerializer, CourseInstanceCreateUpdateSerializer,
    UserSerializer,
)
from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from django.utils import timezone
from .permissions import IsStudentUser, IsTeacherUser, IsAdminUser


class CoursePrototypeViewSet(viewsets.ModelViewSet):
    """
    课程原型的 ViewSet
    """
    queryset = CoursePrototype.objects.all()
    serializer_class = CoursePrototypeSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]  # 假设只有管理员可以管理课程原型

class CourseInstanceViewSet(viewsets.ModelViewSet):
    """
    课程实例的 ViewSet
    """
    queryset = CourseInstance.objects.all()
    serializer_class = CourseInstanceSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CourseInstanceCreateUpdateSerializer
        return CourseInstanceSerializer

    def get_permissions(self):
        if self.action in [
            'enroll', 'drop', 'list_available_courses',
            'retrieve_course_details', 'list_selected_courses'
        ]:
            permission_classes = [IsAuthenticated, IsStudentUser]
        elif self.action in ['view_enrolled_students']:
            permission_classes = [IsAuthenticated, IsTeacherUser]
        elif self.action in ['finalize_selection', 'start_selection']:
            permission_classes = [IsAuthenticated, IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsStudentUser])
    def list_available_courses(self, request):
        """
        API 1: 展示给定学生可选课程
        """
        user = request.user
        try:
            student = Student.objects.get(user=user)
        except Student.DoesNotExist:
            return Response({'detail': '学生信息不存在'}, status=status.HTTP_400_BAD_REQUEST)
        
        now = timezone.now()
        available_courses = CourseInstance.objects.filter(
            selection_deadline__gte=now,
            is_finalized=False,
            eligible_departments=student.grade.department,
            eligible_grades=student.grade,
            eligible_classes=student.student_class
        ).exclude(
            selected_students=user
        )

        serializer = self.get_serializer(available_courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsStudentUser])
    def enroll(self, request, pk=None):
        """
        API 2: 选课
        """
        user = request.user
        try:
            student = Student.objects.get(user=user)
        except Student.DoesNotExist:
            return Response({'detail': '学生信息不存在'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            course_instance = self.get_object()
        except CourseInstance.DoesNotExist:
            return Response({'detail': '课程实例不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        # 检查选课时间是否已过
        if timezone.now() > course_instance.selection_deadline:
            return Response({'detail': '选课时间已截止'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查课程容量
        if course_instance.selected_students.count() >= course_instance.capacity:
            return Response({'detail': '课程容量已满'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查学生是否符合选课条件
        if not course_instance.eligible_departments.filter(id=student.grade.department.id).exists():
            return Response({'detail': '您所在学院无法选此课程'}, status=status.HTTP_403_FORBIDDEN)
        
        if not course_instance.eligible_grades.filter(id=student.grade.id).exists():
            return Response({'detail': '您所在年级无法选此课程'}, status=status.HTTP_403_FORBIDDEN)
        
        if not course_instance.eligible_classes.filter(id=student.student_class.id).exists():
            return Response({'detail': '您所在班级无法选此课程'}, status=status.HTTP_403_FORBIDDEN)
        
        # 检查时间冲突
        student_selected_courses = CourseInstance.objects.filter(
            selected_students=user,
            day=course_instance.day,
            period=course_instance.period,
            is_finalized=False  # 只考虑未最终化的课程
        )
        if student_selected_courses.exists():
            return Response({'detail': '课程时间与已选课程冲突'}, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            # 再次检查课程容量，防止并发问题
            course_instance = CourseInstance.objects.select_for_update().get(id=course_instance.id)
            if course_instance.selected_students.count() >= course_instance.capacity:
                return Response({'detail': '课程容量已满'}, status=status.HTTP_400_BAD_REQUEST)
            course_instance.selected_students.add(user)
        
        return Response({'detail': '选课成功'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsStudentUser])
    def drop(self, request, pk=None):
        """
        API 3: 退选
        """
        user = request.user
        try:
            student = Student.objects.get(user=user)
        except Student.DoesNotExist:
            return Response({'detail': '学生信息不存在'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            course_instance = self.get_object()
        except CourseInstance.DoesNotExist:
            return Response({'detail': '课程实例不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        # 检查选课时间是否已过
        if timezone.now() > course_instance.selection_deadline:
            return Response({'detail': '选课时间已截止，无法退课'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not course_instance.selected_students.filter(id=user.id).exists():
            return Response({'detail': '您未选此课程'}, status=status.HTTP_400_BAD_REQUEST)
        
        course_instance.selected_students.remove(user)
        
        return Response({'detail': '退课成功'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated, IsTeacherUser])
    def view_enrolled_students(self, request, pk=None):
        """
        API 4: 查看某个课程实例的所有选课学生
        """
        course_instance = self.get_object()
        enrolled_students = course_instance.selected_students.all()
        serializer = StudentSerializer(
            Student.objects.filter(user__in=enrolled_students),
            many=True
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated, IsStudentUser])
    def retrieve_course_details(self, request, pk=None):
        """
        API 5: 获取某课程的详细信息
        """
        course_instance = self.get_object()
        serializer = self.get_serializer(course_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsAdminUser])
    def finalize_selection(self, request, pk=None):
        """
        API 6: 截止选课（管理员权限）
        """
        course_instance = self.get_object()
        
        if course_instance.is_finalized:
            return Response({'detail': '该课程选课已最终化'}, status=status.HTTP_400_BAD_REQUEST)
        
        if timezone.now() < course_instance.selection_deadline:
            return Response({'detail': '选课截止时间未到'}, status=status.HTTP_400_BAD_REQUEST)
        
        course_instance.is_finalized = True
        course_instance.save()
        
        return Response({'detail': '课程选课已最终化'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsAdminUser])
    def start_selection(self, request, pk=None):
        """
        API 7: 开始一门课程实例的选课（管理员权限）
        """
        course_instance = self.get_object()
        
        if course_instance.is_finalized:
            return Response({'detail': '该课程选课已最终化，无法重新开始'}, status=status.HTTP_400_BAD_REQUEST)
        
        if timezone.now() > course_instance.selection_deadline:
            return Response({'detail': '选课截止时间已过，无法重新开始'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 可以根据需求重置某些字段或执行其他操作
        # 例如，清空已选学生
        course_instance.selected_students.clear()
        course_instance.is_finalized = False
        course_instance.save()
        
        return Response({'detail': '课程选课已重新开始'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsStudentUser])
    def list_selected_courses(self, request):
        """
        API 8: 展示给定学生的所有已选课程
        """
        user = request.user
        try:
            student = Student.objects.get(user=user)
        except Student.DoesNotExist:
            return Response({'detail': '学生信息不存在'}, status=status.HTTP_400_BAD_REQUEST)
        
        selected_courses = CourseInstance.objects.filter(
            selected_students=user,
            is_finalized=True  # 仅展示已最终化的选课
        )

        serializer = self.get_serializer(selected_courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


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