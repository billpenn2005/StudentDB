# backend/api/viewsets.py

from rest_framework import viewsets, permissions, mixins, generics
from django.contrib.auth.models import User
from .models import CoursePrototype, CourseInstance, Student, Grade, Teacher,S_Grade
from .serializers import (
    CoursePrototypeSerializer, CourseInstanceSerializer, CourseInstanceCreateUpdateSerializer,
    UserSerializer,GradeSerializer,StudentSerializer,TeacherSerializer,S_GradeSerializer
)
from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from django.utils import timezone
from .permissions import IsStudentUser, IsTeacherUser, IsAdminUser, IsTeacherOfCourse, IsOwnerStudent
from django.db.models import F, Window
from django.db.models.functions import Rank
from django_filters.rest_framework import DjangoFilterBackend
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
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['teacher']  # 允许通过teacher字段过滤

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsTeacherUser, IsTeacherOfCourse])
    def publish_grades(self, request, pk=None):
        course_instance = self.get_object()
        if course_instance.is_grades_published:
            return Response({'detail': '成绩已发布，无需重复操作'}, status=status.HTTP_400_BAD_REQUEST)
    
        # 根据需要，可以检查是否所有成绩都已录入
        # 如果无其他逻辑，直接发布
        course_instance.is_grades_published = True
        course_instance.save()
        return Response({'detail': '成绩已发布'}, status=status.HTTP_200_OK)

    #撤回成绩
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsTeacherUser, IsTeacherOfCourse])
    def withdraw_grades(self, request, pk=None):
        course_instance = self.get_object()
        if not course_instance.is_grades_published:
            return Response({'detail': '成绩未发布，无需撤回'}, status=status.HTTP_400_BAD_REQUEST)
        course_instance.is_grades_published = False
        course_instance.save()
        return Response({'detail': '成绩已撤回'}, status=status.HTTP_200_OK)
    

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CourseInstanceCreateUpdateSerializer
        return CourseInstanceSerializer

    def get_permissions(self):
        if self.action in ['enroll', 'drop', 'list_available_courses',
                          'retrieve_course_details', 'list_selected_courses']:
            permission_classes = [IsAuthenticated, IsStudentUser]
        elif self.action in ['view_enrolled_students']:
            permission_classes = [IsAuthenticated, IsTeacherUser]
        elif self.action in ['finalize_selection', 'start_selection']:
            permission_classes = [IsAuthenticated, IsAdminUser]
        elif self.action in ['set_grade_weights']:
            permission_classes = [IsAuthenticated, IsTeacherUser, IsTeacherOfCourse]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated, IsTeacherUser, IsTeacherOfCourse])
    def set_grade_weights(self, request, pk=None):
        """
        API: 设置成绩分数占比
        """
        course_instance = self.get_object()
        daily_weight = request.data.get('daily_weight')
        final_weight = request.data.get('final_weight')

        if daily_weight is None or final_weight is None:
            return Response({'detail': '平时分和期末分占比均为必填项'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            daily_weight = int(daily_weight)
            final_weight = int(final_weight)
        except ValueError:
            return Response({'detail': '平时分和期末分占比必须为整数'}, status=status.HTTP_400_BAD_REQUEST)

        if daily_weight + final_weight != 100:
            return Response({'detail': '平时分和期末分的总和必须为100%'}, status=status.HTTP_400_BAD_REQUEST)

        course_instance.daily_weight = daily_weight
        course_instance.final_weight = final_weight

        try:
            course_instance.save()
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({'detail': '服务器内部错误'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'detail': '成绩分数占比设置成功'}, status=status.HTTP_200_OK)

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
            #eligible_departments=student.grade.department,
            #eligible_grades=student.grade,
            eligible_classes=student.student_class
        ).exclude(
            selected_students=user
        )

        serializer = self.get_serializer(available_courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated, IsTeacherUser])
    def enrolled_students(self, request, pk=None):
        try:
            course_instance = self.get_object()
            enrolled_students = course_instance.enrolled_students.all()  # 假设有相关的关联
            serializer = UserSerializer(enrolled_students, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CourseInstance.DoesNotExist:
            return Response({'detail': '课程实例不存在。'}, status=status.HTTP_404_NOT_FOUND)

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
        #if not course_instance.eligible_departments.filter(id=student.grade.department.id).exists():
            #return Response({'detail': '您所在学院无法选此课程'}, status=status.HTTP_403_FORBIDDEN)
        
        #if not course_instance.eligible_grades.filter(id=student.grade.id).exists():
            #return Response({'detail': '您所在年级无法选此课程'}, status=status.HTTP_403_FORBIDDEN)
        
        if not course_instance.eligible_classes.filter(id=student.student_class.id).exists():
            return Response({'detail': '您所在班级无法选此课程'}, status=status.HTTP_403_FORBIDDEN)
        
        # 检查时间冲突
        course_schedules = course_instance.schedules.all()
        for schedule in course_schedules:
            conflict = CourseInstance.objects.filter(
                selected_students=user,
                is_finalized=False,
                schedules__day=schedule.day,
                schedules__period=schedule.period
            ).exists()
            if conflict:
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
        try:
            course_instance = self.get_object()
            selected_students = course_instance.selected_students.all()  # 修正为 selected_students
            serializer = UserSerializer(selected_students, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CourseInstance.DoesNotExist:
            return Response({'detail': '课程实例不存在。'}, status=status.HTTP_404_NOT_FOUND)

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
            is_finalized=False  # 仅展示已最终化的选课
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
        
from django.db.models import OuterRef, Subquery, IntegerField
from django.db.models.functions import Rank
from django.db.models import Count
from django.db.models import F
from django.db.models import Window
from django.db.models.functions import DenseRank

class S_GradeViewSet(viewsets.ModelViewSet):
    """
    成绩管理的 ViewSet
    """
    queryset = S_Grade.objects.all()
    serializer_class = S_GradeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['course_instance']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'bulk_update_grades']:
            permission_classes = [IsAuthenticated, IsTeacherUser, IsTeacherOfCourse]
        elif self.action in ['retrieve', 'list']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsOwnerStudent])
    def my_rankings(self, request):
        user = request.user
        # 过滤出当前用户的成绩
        student_grades = S_Grade.objects.filter(student=user)
        # 获取这些成绩对应的课程实例
        course_instances = student_grades.values_list('course_instance', flat=True)

        # 子查询：计算每门课程中，比当前学生总分更高的学生数量
        subquery = S_Grade.objects.filter(
            course_instance=OuterRef('course_instance'),
            total_score__gt=OuterRef('total_score')
        ).values('course_instance').annotate(
            higher_count=Count('id')
        ).values('higher_count')[:1]

        # 主查询：仅包含成绩已发布的课程实例
        ranked_grades = S_Grade.objects.filter(
            course_instance__in=course_instances,
            student=user,
            course_instance__is_grades_published=True  # 添加成绩已发布的条件
        ).annotate(
            rank=Subquery(subquery, output_field=IntegerField()) + 1
        ).values(
            'course_instance__course_prototype__name',
            'course_instance__semester',
            'daily_score',
            'final_score',
            'total_score',
            'rank'
        )

        # 构建返回的数据格式
        rankings = [
            {
                'course_instance': f"{grade['course_instance__course_prototype__name']} - {grade['course_instance__semester']}",
                'daily_score': grade.get('daily_score'),
                'final_score': grade.get('final_score'),
                'total_score': grade['total_score'],
                'rank': grade['rank'],
                # 'is_published' 已不需要，因为只查询已发布的成绩
            }
            for grade in ranked_grades
        ]
        return Response(rankings, status=status.HTTP_200_OK)
    
    def get_queryset(self):
            user = self.request.user
            queryset = S_Grade.objects.all()
            
            course_instance_id = self.request.query_params.get('course_instance', None)
            if course_instance_id:
                try:
                    ci = CourseInstance.objects.get(id=course_instance_id)
                    queryset = queryset.filter(course_instance=ci)

                    # 当成绩已发布时计算排名
                    if ci.is_grades_published:
                        queryset = queryset.annotate(
                            ranking=Window(
                                expression=DenseRank(),
                                partition_by=[F('course_instance')],
                                order_by=F('total_score').desc()
                            )
                        )
                    else:
                        # 未发布时不添加ranking注释，ranking在serializer中会返回None
                        pass

                except CourseInstance.DoesNotExist:
                    # 找不到课程实例则查询结果为空
                    queryset = queryset.none()

            # 学生仅可看自己的成绩
            if user.groups.filter(name='Student').exists():
                queryset = queryset.filter(student=user)
            # 教师仅可看自己授课课程的成绩
            elif user.groups.filter(name='Teacher').exists():
                queryset = queryset.filter(course_instance__teacher=user.teacher_profile)

            return queryset

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated, IsTeacherUser, IsTeacherOfCourse])
    def bulk_update_grades(self, request):
        """
        批量更新课程实例中学生的成绩。
        期望接收一个包含'student_id'、'daily_score'和'final_score'的对象列表。
        """
        data = request.data
        if not isinstance(data, list):
            return Response({'detail': '预期接收一个成绩条目列表。'}, status=status.HTTP_400_BAD_REQUEST)
        
        course_instance_id = request.query_params.get('course_instance_id')
        if not course_instance_id:
            return Response({'detail': '需要提供course_instance_id查询参数。'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            course_instance = CourseInstance.objects.get(id=course_instance_id)
        except CourseInstance.DoesNotExist:
            return Response({'detail': f'id为 {course_instance_id} 的课程实例不存在。'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 确保教师拥有该课程实例的权限
        if course_instance.teacher != request.user.teacher_profile:
            return Response({'detail': '您没有权限修改该课程实例的成绩。'}, status=status.HTTP_403_FORBIDDEN)
        
        grades_to_update = []
        for entry in data:
            student_id = entry.get('student_id')
            daily_score = entry.get('daily_score')
            final_score = entry.get('final_score')

            if not all([student_id is not None, daily_score is not None, final_score is not None]):
                return Response({'detail': '每个条目必须包含student_id、daily_score和final_score。'}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                student = User.objects.get(id=student_id, groups__name='Student')
            except User.DoesNotExist:
                return Response({'detail': f'id为 {student_id} 的用户不存在或不是学生。'}, status=status.HTTP_400_BAD_REQUEST)
            
            grade, created = S_Grade.objects.get_or_create(student=student, course_instance=course_instance)
            grade.daily_score = daily_score
            grade.final_score = final_score
            grade.total_score = daily_score + final_score
            grades_to_update.append(grade)
        
        try:
            with transaction.atomic():
                S_Grade.objects.bulk_update(grades_to_update, ['daily_score', 'final_score', 'total_score'])
            return Response({'detail': '成绩更新成功。'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': f'发生错误: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TeacherViewSet(viewsets.ModelViewSet):
    """
    教师管理的 ViewSet
    """
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherUser]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Teacher').exists():
            # 仅返回当前教师的配置文件
            return Teacher.objects.filter(user=user)
        return Teacher.objects.none()

    def perform_update(self, serializer):
        serializer.save()

from .models import Department, Class, Grade
from .serializers import DepartmentSerializer, ClassSerializer, GradeSerializer
from django.http import Http404

class DepartmentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    提供部门列表和详细信息的 API
    """
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]

class ClassViewSet(viewsets.ReadOnlyModelViewSet):
    """
    提供班级列表和详细信息的 API
    """
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    permission_classes = [IsAuthenticated]

class GradeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    提供年级列表和详细信息的 API
    """
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [IsAuthenticated]

class CurrentStudentProfileView(generics.RetrieveUpdateAPIView):
    """
    获取和更新当前学生的个人资料
    """
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated, IsStudentUser]

    def get_object(self):
        try:
            return Student.objects.get(user=self.request.user)
        except Student.DoesNotExist:
            raise Http404