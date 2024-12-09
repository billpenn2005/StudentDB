# backend/api/viewsets.py
# backend/api/viewsets.py

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import serializers
from django.contrib.auth.models import User, Group
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics

from .models import (
    Department, Specialty, Student,
    RewardPunishment, Course, Enrollment,
    Exam, RetakeExam, Class, CourseSelection
)
from .serializers import (
    DepartmentSerializer, SpecialtySerializer, StudentSerializer,
    RewardPunishmentSerializer, CourseSerializer, EnrollmentSerializer,
    ExamSerializer, RetakeExamSerializer, ClassSerializer,
    CourseSelectionSerializer, UserSerializer
)
from .permissions import IsAdminUser, IsTeacherUser, IsStudentUser

from django.http import HttpResponse
from reportlab.pdfgen import canvas


# 自定义权限类已经在 serializers 中定义
# 这里不需要额外定义

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

class SpecialtyViewSet(viewsets.ModelViewSet):
    queryset = Specialty.objects.all()
    serializer_class = SpecialtySerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['department', 'specialty', 'gender', 'age']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'id_number']
    ordering_fields = ['age', 'user__username']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

class RewardPunishmentViewSet(viewsets.ModelViewSet):
    queryset = RewardPunishment.objects.all()
    serializer_class = RewardPunishmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['department', 'credits']
    search_fields = ['name']
    ordering_fields = ['credits', 'name']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsTeacherUser | IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['student', 'course']
    search_fields = ['student__user__username', 'course__name']
    ordering_fields = ['enrolled_at']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsTeacherUser | IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['enrollment', 'exam_type']
    search_fields = ['enrollment__student__user__username', 'enrollment__course__name']
    ordering_fields = ['date', 'score']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsTeacherUser | IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

class RetakeExamViewSet(viewsets.ModelViewSet):
    queryset = RetakeExam.objects.all()
    serializer_class = RetakeExamSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['enrollment', 'original_exam']
    search_fields = ['enrollment__student__user__username', 'original_exam__course__name']
    ordering_fields = ['date', 'new_score']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsTeacherUser | IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

# backend/api/viewsets.py

class ClassViewSet(viewsets.ModelViewSet):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['course']
    search_fields = ['group', 'teacher']
    ordering_fields = ['group', 'teacher']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsTeacherUser | IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def by_course(self, request):
        course_id = request.query_params.get('course_id')
        if course_id is not None:
            classes = self.queryset.filter(course__id=course_id)
            serializer = self.get_serializer(classes, many=True)
            return Response(serializer.data)
        else:
            return Response({"detail": "course_id 参数缺失"}, status=status.HTTP_400_BAD_REQUEST)

# backend/api/viewsets.py

class CourseSelectionViewSet(viewsets.ModelViewSet):
    queryset = CourseSelection.objects.all()
    serializer_class = CourseSelectionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CourseSelection.objects.filter(user=self.request.user).select_related('class_instance__course', 'class_instance__time_slot')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CustomTokenObtainPairSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    user_id = serializers.IntegerField(read_only=True)
    email = serializers.EmailField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)

    def validate(self, attrs):
        from django.contrib.auth import authenticate
        username = attrs.get('username')
        password = attrs.get('password')

        user = authenticate(username=username, password=password)
        if user is None:
            raise serializers.ValidationError('Invalid username or password')

        refresh = RefreshToken.for_user(user)

        return {
            'username': user.username,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user_id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        }

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

# 注销视图
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
        

# backend/api/viewsets.py


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