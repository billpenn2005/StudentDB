# backend/api/viewsets.py

from rest_framework import viewsets, permissions, mixins, generics
from django.contrib.auth.models import User
from .models import (
    CoursePrototype, CourseInstance, Student, Grade, Teacher, S_Grade,
    Semester, PunishmentRecord, RewardRecord, CourseSchedule, SelectionBatch
)
from .serializers import (
    CoursePrototypeSerializer, CourseInstanceSerializer, CourseInstanceCreateUpdateSerializer,
    UserSerializer, GradeSerializer, StudentSerializer, TeacherSerializer, S_GradeSerializer,
    SemesterSerializer, SemesterCreateUpdateSerializer,
    PunishmentRecordSerializer, RewardRecordSerializer,
    PunishmentRecordCreateSerializer, RewardRecordCreateSerializer,SelectionBatchSerializer,CourseScheduleSerializer
)
from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from django.utils import timezone
from .permissions import IsTeacherUser, IsStudentUser, IsAdminUser, IsTeacherOfCourse, IsOwnerStudent, IsAdminOrTeacher
from django.db.models import F, Window
from django.db.models.functions import Rank
from django_filters.rest_framework import DjangoFilterBackend
import csv
import io
from rest_framework.parsers import MultiPartParser, FormParser
from .permissions import IsAdminUser, IsTeacherUser, IsStudentUser, IsTeacherOfCourse, IsOwnerStudent
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

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def schedules_by_week(self, request, pk=None):
        course_instance = self.get_object()  # 从 CourseInstanceViewSet 获取当前对象
        
        week_number = request.query_params.get('week_number')
        if not week_number:
            return Response({'detail': '请提供week_number参数'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            week_number = int(week_number)
        except ValueError:
            return Response({'detail': 'week_number必须为整数'}, status=status.HTTP_400_BAD_REQUEST)

        # 拿到这门课程实例的所有排课
        schedules = course_instance.schedules.all()

        # 如果要判断某个周是否上课，可以在 serializer 里做，也可以在这里做过滤
        # 比如：只返回这个周有课的排课
        active_schedules = [s for s in schedules if s.is_active_in_week(week_number)]

        serializer = CourseScheduleSerializer(active_schedules, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsTeacherUser, IsTeacherOfCourse])
    def publish_grades(self, request, pk=None):
        course_instance = self.get_object()
        if not course_instance.is_finalized:
            return Response({'detail': '选课截止时间未到，无法发布成绩'}, status=status.HTTP_400_BAD_REQUEST)
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
            #is_finalized=False,
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
            enrolled_students = course_instance.selected_students.all()
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
        if timezone.now() > course_instance.selection_deadline or course_instance.is_finalized:
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
                schedules__period=schedule.period,
                semester=current_semester  # 添加学期过滤
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
        if timezone.now() > course_instance.selection_deadline or course_instance.is_finalized:
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
        
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated, IsTeacherUser])
    def retrieve_course_details(self, request, pk=None):
        """
        API 5: 获取某课程的详细信息
        """
        course_instance = self.get_object()
        week_number = request.query_params.get('week_number', None)
        serializer = self.get_serializer(course_instance, context={'week_number': week_number})
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
            #is_finalized=False  # 仅展示已最终化的选课
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



from .serializers import UserWithStudentSerializer

class CurrentUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserWithStudentSerializer
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
from django.db.models import Value
from django.db.models import F, Value, IntegerField
from django.db.models.functions import Coalesce

class SelectionBatchViewSet(viewsets.ModelViewSet):
    """
    选课批次管理的 ViewSet
    """
    queryset = SelectionBatch.objects.all()
    serializer_class = SelectionBatchSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def course_instances(self, request, pk=None):
        """
        获取特定选课批次的课程实例
        """
        try:
            selection_batch = SelectionBatch.objects.get(pk=pk)
        except SelectionBatch.DoesNotExist:
            return Response({'detail': '选课批次不存在'}, status=status.HTTP_404_NOT_FOUND)

        course_instances = selection_batch.course_instances.all()
        serializer = CourseInstanceSerializer(course_instances, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated, IsStudentUser])
    def selected_courses(self, request, pk=None):
        """
        获取给定学生在此批次中的已选课程
        """
        try:
            selection_batch = SelectionBatch.objects.get(pk=pk)
        except SelectionBatch.DoesNotExist:
            return Response({'detail': '选课批次不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        user = request.user
        try:
            student = Student.objects.get(user=user)
        except Student.DoesNotExist:
            return Response({'detail': '学生信息不存在'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取已选课程
        selected_courses = selection_batch.course_instances.filter(selected_students=user)
        selected_serializer = CourseInstanceSerializer(selected_courses, many=True)
        
        return Response({
            'selected_courses': selected_serializer.data
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated, IsStudentUser])
    def available_courses(self, request, pk=None):
        """
        获取给定学生在此批次中的可选课程
        """
        try:
            selection_batch = SelectionBatch.objects.get(pk=pk)
        except SelectionBatch.DoesNotExist:
            return Response({'detail': '选课批次不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        user = request.user
        try:
            student = Student.objects.get(user=user)
        except Student.DoesNotExist:
            return Response({'detail': '学生信息不存在'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取可选课程
        now = timezone.now()
        available_courses = selection_batch.course_instances.annotate(
            selected_count=Count('selected_students')
        ).filter(
            selection_deadline__gte=now,
            selected_count__lt=F('capacity'),
            eligible_classes=student.student_class
        ).exclude(selected_students=user)
        
        available_serializer = CourseInstanceSerializer(available_courses, many=True)
        
        return Response({
            'available_courses': available_serializer.data
        }, status=status.HTTP_200_OK)
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
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsStudentUser])
    def my_all_grades(self, request):
        """
        API 9: 获取当前学生本学期和历史学期的所有成绩
        """
        user = request.user
        try:
            student = Student.objects.get(user=user)
        except Student.DoesNotExist:
            return Response({'detail': '学生信息不存在'}, status=status.HTTP_400_BAD_REQUEST)
        
        grades = S_Grade.objects.filter(
            student=user,
            course_instance__is_grades_published=True
        ).select_related('course_instance__course_prototype', 'course_instance__semester').order_by('course_instance__semester__start_date')
        
        serializer = self.get_serializer(grades, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsOwnerStudent])
    def my_rankings(self, request):
        """
        API 9: 获取当前学生本学期和历史学期的所有成绩
        """
        user = request.user
        try:
            student = Student.objects.get(user=user)
        except Student.DoesNotExist:
            return Response({'detail': '学生信息不存在'}, status=status.HTTP_400_BAD_REQUEST)
        
        grades = S_Grade.objects.filter(
            student=user,
            course_instance__is_grades_published=True
        ).select_related('course_instance__course_prototype', 'course_instance__semester').order_by('course_instance__semester__start_date')
        
        # 子查询：计算每门课程中，比当前学生总分更高的学生数量
        subquery = S_Grade.objects.filter(
            course_instance=OuterRef('course_instance'),
            total_score__gt=OuterRef('total_score')
        ).values('course_instance').annotate(
            higher_count=Count('id')
        ).values('higher_count')[:1]
        
        # 主查询：仅包含成绩已发布的课程实例，并使用Coalesce处理NULL值
        ranked_grades = S_Grade.objects.filter(
            course_instance__in=grades.values('course_instance'),
            student=user,
            course_instance__is_grades_published=True
        ).annotate(
            higher_count=Subquery(subquery, output_field=IntegerField()),
            rank=Coalesce(F('higher_count'), Value(0)) + 1
        ).values(
            'course_instance__course_prototype__name',
            'course_instance__semester__name',
            'daily_score',
            'final_score',
            'total_score',
            'rank'
        )
        
        # 构建返回的数据格式
        rankings = [
            {
                'course_instance': f"{grade['course_instance__course_prototype__name']} - {grade['course_instance__semester__name']}",
                'daily_score': grade.get('daily_score'),
                'final_score': grade.get('final_score'),
                'total_score': grade['total_score'],
                'rank': grade['rank'],
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
        
        updated_grades = []
        errors = []
        
        try:
            with transaction.atomic():
                for entry in data:
                    student_id = entry.get('student_id')
                    daily_score = entry.get('daily_score')
                    final_score = entry.get('final_score')

                    if not all([student_id is not None, daily_score is not None, final_score is not None]):
                        errors.append({'student_id': student_id, 'detail': '每个条目必须包含student_id、daily_score和final_score。'})
                        continue
                    
                    try:
                        student = User.objects.get(id=student_id, groups__name='Student')
                    except User.DoesNotExist:
                        errors.append({'student_id': student_id, 'detail': '用户不存在或不是学生。'})
                        continue
                    
                    # 获取或创建 S_Grade 实例
                    s_grade, created = S_Grade.objects.get_or_create(student=student, course_instance=course_instance)
                    s_grade.daily_score = daily_score
                    s_grade.final_score = final_score
                    s_grade.save()  # 这将自动更新 total_score
                    updated_grades.append(S_GradeSerializer(s_grade).data)
        except Exception as e:
            return Response({'detail': f'发生错误: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        response_data = {
            'updated_grades': updated_grades,
            'errors': errors
        }
        
        status_code = status.HTTP_200_OK if not errors else status.HTTP_207_MULTI_STATUS
        
        return Response(response_data, status=status_code)

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


class SemesterViewSet(viewsets.ModelViewSet):
    """
    学期（批次）管理的 ViewSet
    """
    queryset = Semester.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = SemesterSerializer
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return SemesterCreateUpdateSerializer
        return SemesterSerializer
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def current(self, request):
        """
        获取当前学期的信息
        """
        try:
            current_semester = Semester.objects.get(is_current=True)
            serializer = self.get_serializer(current_semester)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Semester.DoesNotExist:
            return Response({'detail': '当前学期未设置'}, status=status.HTTP_404_NOT_FOUND)
        except Semester.MultipleObjectsReturned:
            return Response({'detail': '存在多个当前学期，请检查数据'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


from rest_framework.exceptions import PermissionDenied

class PunishmentRecordViewSet(viewsets.ModelViewSet):
    queryset = PunishmentRecord.objects.all()
    serializer_class = PunishmentRecordSerializer
    # 改为允许管理员或教师
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PunishmentRecordCreateSerializer
        return PunishmentRecordSerializer

    def get_queryset(self):
        user = self.request.user
        # 根据需求限制教师只能看自己部门的学生，或者其他逻辑
        if user.is_staff:
            return PunishmentRecord.objects.all()
        elif user.groups.filter(name='Teacher').exists():
            return PunishmentRecord.objects.filter(
                student__department__in=user.teacher_profile.departments.all()
            )
        elif user.groups.filter(name='Student').exists():
            # 学生只能查看自己的记录
            return PunishmentRecord.objects.filter(student__user=user)
        else:
            return PunishmentRecord.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        # 如果教师想添加奖惩，需要检查一下学生是否属于自己管理范围
        # 以下仅做示例：和上面 get_queryset 的逻辑一致
        if user.groups.filter(name='Teacher').exists():
            student_obj = serializer.validated_data['student']
            # 如果该学生不在教师的部门下，则拒绝
            if not student_obj.department or \
               student_obj.department not in user.teacher_profile.departments.all():
                raise PermissionDenied("您无法为不属于您所在部门的学生添加奖惩记录。")

        serializer.save()  # 正常创建

class RewardRecordViewSet(viewsets.ModelViewSet):
    """
    奖励记录管理的 ViewSet
    """
    queryset = RewardRecord.objects.all()
    serializer_class = RewardRecordSerializer
    permission_classes = [IsAuthenticated, IsAdminOrTeacher]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RewardRecordCreateSerializer
        return RewardRecordSerializer  # 正确返回读取序列化器

    def get_queryset(self):
        user = self.request.user
        # 根据需求限制教师只能看自己部门的学生，或者其他逻辑
        if user.is_staff:
            return RewardRecord.objects.all()
        elif user.groups.filter(name='Teacher').exists():
            # 示例：只查看同部门学生的奖惩
            return RewardRecord.objects.filter(
                student__department__in=user.teacher_profile.departments.all()
            )
        elif user.groups.filter(name='Student').exists():
            # 学生只能查看自己的记录
            return RewardRecord.objects.filter(student__user=user)
        else:
            return RewardRecord.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        # 如果教师想添加奖惩，需要检查一下学生是否属于自己管理范围
        # 以下仅做示例：和上面 get_queryset 的逻辑一致
        if user.groups.filter(name='Teacher').exists():
            student_obj = serializer.validated_data['student']
            # 如果该学生不在教师的部门下，则拒绝
            if not student_obj.department or \
            student_obj.department not in user.teacher_profile.departments.all():
                raise PermissionDenied("您无法为不属于您所在部门的学生添加奖惩记录。")

        serializer.save()  # 正常创建


class BulkImportViewSet(viewsets.ViewSet):
    """
    批量导入的 ViewSet
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated, IsAdminUser])
    def import_course_prototypes(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'detail': '未上传文件'}, status=status.HTTP_400_BAD_REQUEST)
        
        decoded_file = file.read().decode('utf-8')
        io_string = io.StringIO(decoded_file)
        reader = csv.DictReader(io_string)
        
        created = 0
        errors = []
        for row in reader:
            try:
                course_prototype = CoursePrototype.objects.create(
                    name=row['name'],
                    description=row['description'],
                    department_id=row['department_id'],
                    credits=int(row['credits'])
                )
                created += 1
            except Exception as e:
                errors.append({'row': row, 'error': str(e)})
        
        return Response({'created': created, 'errors': errors}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated, IsAdminUser])
    def import_course_instances(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'detail': '未上传文件'}, status=status.HTTP_400_BAD_REQUEST)
        
        decoded_file = file.read().decode('utf-8')
        io_string = io.StringIO(decoded_file)
        reader = csv.DictReader(io_string)
        
        created = 0
        errors = []
        for row in reader:
            try:
                with transaction.atomic():
                    course_prototype = CoursePrototype.objects.get(id=row['course_prototype_id'])
                    semester = Semester.objects.get(id=row['semester_id'])
                    teacher = Teacher.objects.get(id=row['teacher_id']) if row.get('teacher_id') else None
                    course_instance = CourseInstance.objects.create(
                        course_prototype=course_prototype,
                        semester=semester,
                        location=row['location'],
                        capacity=int(row['capacity']),
                        selection_deadline=row['selection_deadline'],
                        department_id=row['department_id'],
                        daily_weight=int(row['daily_weight']),
                        final_weight=int(row['final_weight']),
                        teacher=teacher,
                        is_finalized=row.get('is_finalized', False)
                    )
                    # 处理 eligible_departments, eligible_grades, eligible_classes
                    eligible_departments = row['eligible_departments'].split(';') if row.get('eligible_departments') else []
                    eligible_grades = row['eligible_grades'].split(';') if row.get('eligible_grades') else []
                    eligible_classes = row['eligible_classes'].split(';') if row.get('eligible_classes') else []
                    course_instance.eligible_departments.set(eligible_departments)
                    course_instance.eligible_grades.set(eligible_grades)
                    course_instance.eligible_classes.set(eligible_classes)
                    # 处理 schedules
                    schedules = row['schedules'].split('|') if row.get('schedules') else []
                    for schedule in schedules:
                        day, period = schedule.split('-')
                        CourseSchedule.objects.create(course_instance=course_instance, day=day, period=int(period))
                    created += 1
            except Exception as e:
                errors.append({'row': row, 'error': str(e)})
        
        return Response({'created': created, 'errors': errors}, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated, IsTeacherUser, IsTeacherOfCourse])
    def bulk_update_grades(self, request):
        """
        批量更新/创建课程实例中学生的成绩，
        现在允许传入 attempt 表示是首考/补考/重修。
        期望接收一个列表，每个对象包含：
        {
           "student_id": <int>,
           "daily_score": <float>,
           "final_score": <float>,
           "attempt": <int, optional>
        }
        """
        data = request.data
        if not isinstance(data, list):
            return Response({'detail': '预期接收一个成绩条目列表(list)。'}, status=status.HTTP_400_BAD_REQUEST)
        
        course_instance_id = request.query_params.get('course_instance_id')
        if not course_instance_id:
            return Response({'detail': '需要提供 course_instance_id 查询参数。'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            course_instance = CourseInstance.objects.get(id=course_instance_id)
        except CourseInstance.DoesNotExist:
            return Response({'detail': f'id={course_instance_id} 的课程实例不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        # 确保教师拥有该课程实例的权限
        user = request.user
        if course_instance.teacher != user.teacher_profile:
            return Response({'detail': '您没有权限修改该课程实例的成绩。'}, status=status.HTTP_403_FORBIDDEN)

        updated_grades = []
        errors = []

        try:
            with transaction.atomic():
                for entry in data:
                    student_id = entry.get('student_id')
                    daily_score = entry.get('daily_score')
                    final_score = entry.get('final_score')
                    attempt = entry.get('attempt', 1)  # 若前端没传，默认为首考(1)

                    if any(x is None for x in [student_id, daily_score, final_score]):
                        errors.append({
                            'student_id': student_id,
                            'detail': 'student_id / daily_score / final_score 为必填字段'
                        })
                        continue

                    # 1. 获取学生
                    try:
                        student_user = User.objects.get(id=student_id, groups__name='Student')
                    except User.DoesNotExist:
                        errors.append({
                            'student_id': student_id,
                            'detail': '用户不存在或不是学生'
                        })
                        continue

                    # 2. 获取/创建 S_Grade
                    #   注意现在 unique_together = (student, course_instance, attempt)
                    #   因此如果本轮 attempt 已存在，就更新；否则新建
                    s_grade, created = S_Grade.objects.get_or_create(
                        student=student_user,
                        course_instance=course_instance,
                        attempt=attempt
                    )
                    s_grade.daily_score = daily_score
                    s_grade.final_score = final_score
                    s_grade.save()  # 这会自动计算 total_score

                    updated_grades.append(S_GradeSerializer(s_grade).data)

        except Exception as e:
            return Response({'detail': f'发生错误: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        response_data = {
            'updated_grades': updated_grades,
            'errors': errors
        }
        status_code = status.HTTP_200_OK if not errors else status.HTTP_207_MULTI_STATUS
        return Response(response_data, status=status_code)

    # 类似的方法可以为 CoursePrototype 和 CourseInstance 实现
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.rl_config import TTFSearchPath
import os

# 注册中文字体
font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'SimSun.ttf')  # 确保字体文件路径正确
pdfmetrics.registerFont(TTFont('SimSun', font_path))
TTFSearchPath.append(os.path.join(os.path.dirname(__file__), 'fonts'))


class GenerateReportView(APIView):
    """
    扩展后的报表生成接口
    可根据用户角色返回不同的报表
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        通过 'type' 指明要生成的报表类型
         - 'my_transcript': 学生自己的成绩单
         - 'teacher_course': 教师的课程相关报表
         - 也可保留之前 'students'/'grades'/'courses' 等管理员用
        """
        report_type = request.data.get('type')
        if not report_type:
            return Response({'detail': '请指定报表类型'}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user

        if report_type == 'my_transcript':
            # 只允许学生
            if not user.groups.filter(name='Student').exists():
                return Response({'detail': '只有学生可以生成个人成绩单报表'}, status=status.HTTP_403_FORBIDDEN)
            return self.generate_my_transcript(user)

        elif report_type == 'teacher_course':
            # 只允许教师
            if not user.groups.filter(name='Teacher').exists():
                return Response({'detail': '只有教师可以生成所授课程报表'}, status=status.HTTP_403_FORBIDDEN)
            # 前端传课程ID进来
            course_id = request.data.get('course_id')
            if not course_id:
                return Response({'detail': '缺少 course_id 参数'}, status=status.HTTP_400_BAD_REQUEST)
            return self.generate_teacher_course_report(user, course_id)

        # 如果还想保留原先的 'students'/'grades'/'courses' 给管理员用，可以写：
        elif report_type == 'students':
            if not user.is_staff:
                return Response({'detail': '只有管理员可以生成学生信息报表'}, status=status.HTTP_403_FORBIDDEN)
            return self.generate_student_report()

        elif report_type == 'grades':
            if not user.is_staff:
                return Response({'detail': '只有管理员可以生成全部成绩报表'}, status=status.HTTP_403_FORBIDDEN)
            return self.generate_grades_report()

        elif report_type == 'courses':
            if not user.is_staff:
                return Response({'detail': '只有管理员可以生成课程报表'}, status=status.HTTP_403_FORBIDDEN)
            return self.generate_courses_report()

        else:
            return Response({'detail': f'未知的报表类型: {report_type}'}, status=status.HTTP_400_BAD_REQUEST)

    def generate_my_transcript(self, user):
        """
        学生生成自己的成绩单
        """
        # 查找该 user 对应的 Student
        try:
            student = user.student_profile
        except Student.DoesNotExist:
            return Response({'detail': '未找到该学生'}, status=status.HTTP_404_NOT_FOUND)

        # 获取此学生所有已发布的成绩
        grades = S_Grade.objects.filter(
            student=user, 
            course_instance__is_grades_published=True
        ).select_related('course_instance__course_prototype', 'course_instance__semester')

        # 开始生成 PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{user.username}_transcript.pdf"'

        p = canvas.Canvas(response)
        p.setFont("SimSun", 16)
        p.drawString(100, 800, f"{student.user.get_full_name()} 的成绩单")

        y = 760
        p.setFont("SimSun", 12)
        for g in grades:
            line = f"课程: {g.course_instance.course_prototype.name}, 学期: {g.course_instance.semester.name}, 平时分: {g.daily_score}, 期末分: {g.final_score}, 总分: {g.total_score}"
            p.drawString(100, y, line)
            y -= 20
            if y < 50:
                p.showPage()
                # 重新绘制标题
                p.setFont("SimSun", 16)
                p.drawString(100, 800, f"{student.user.get_full_name()} 的成绩单")
                y = 760
                p.setFont("SimSun", 12)

        p.showPage()
        p.save()
        return response

    def generate_teacher_course_report(self, user, course_id):
        """
        教师生成所授课程报表（如学生名单+成绩信息 等）
        """
        # 获取该 user 对应的 Teacher
        try:
            teacher = user.teacher_profile
        except Teacher.DoesNotExist:
            return Response({'detail': '未找到该教师'}, status=status.HTTP_404_NOT_FOUND)

        # 拿到指定课程
        try:
            course = CourseInstance.objects.get(id=course_id, teacher=teacher)
        except CourseInstance.DoesNotExist:
            return Response({'detail': '您没有权限或该课程不存在'}, status=status.HTTP_404_NOT_FOUND)

        # 取出此课程所有已选学生 + 成绩
        grades = S_Grade.objects.filter(course_instance=course).select_related('student')

        response = HttpResponse(content_type='application/pdf')
        filename = f"{course.course_prototype.name}_report.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        p = canvas.Canvas(response)
        p.setFont("SimSun", 16)
        p.drawString(100, 800, f"课程报表: {course.course_prototype.name}({course.semester.name})")

        y = 760
        p.setFont("SimSun", 12)
        for g in grades:
            student_name = g.student.get_full_name() if g.student.first_name else g.student.username
            line = f"学生: {student_name}, 平时分: {g.daily_score}, 期末分: {g.final_score}, 总分: {g.total_score}"
            p.drawString(100, y, line)
            y -= 20
            if y < 50:
                p.showPage()
                # 重新绘制标题
                p.setFont("SimSun", 16)
                p.drawString(100, 800, f"课程报表: {course.course_prototype.name}({course.semester.name})")
                y = 760
                p.setFont("SimSun", 12)

        p.showPage()
        p.save()
        return response

    
    def generate_student_report(self):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="student_report.pdf"'

        p = canvas.Canvas(response)
        p.setFont("SimSun", 16)
        p.drawString(100, 800, "学生信息报表")

        students = Student.objects.all()
        y = 750
        p.setFont("SimSun", 12)
        for student in students:
            text = f"姓名: {student.user.get_full_name()}, 单位: {student.department.name if student.department else 'N/A'}, 年龄: {student.age}, 性别: {student.get_gender_display()}, 身份证号码: {student.id_number}"
            p.drawString(100, y, text)
            y -= 20
            if y < 50:
                p.showPage()
                # 重新绘制标题
                p.setFont("SimSun", 16)
                p.drawString(100, 800, "学生信息报表")
                y = 750
                p.setFont("SimSun", 12)

        p.showPage()
        p.save()
        return response

    def generate_grades_report(self):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="grades_report.pdf"'

        p = canvas.Canvas(response)
        p.setFont("SimSun", 16)
        p.drawString(100, 800, "成绩报表")

        grades = S_Grade.objects.filter(course_instance__is_finalized=True)
        y = 750
        p.setFont("SimSun", 12)
        for grade in grades:
            text = f"学生: {grade.student.user.get_full_name()}, 课程: {grade.course_instance.course_prototype.name}, 平时分: {grade.daily_score}, 期末分: {grade.final_score}, 总分: {grade.total_score}"
            p.drawString(100, y, text)
            y -= 20
            if y < 50:
                p.showPage()
                # 重新绘制标题
                p.setFont("SimSun", 16)
                p.drawString(100, 800, "成绩报表")
                y = 750
                p.setFont("SimSun", 12)

        p.showPage()
        p.save()
        return response

    def generate_courses_report(self):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="courses_report.pdf"'

        p = canvas.Canvas(response)
        p.setFont("SimSun", 16)
        p.drawString(100, 800, "课程报表")

        courses = CourseInstance.objects.all()
        y = 750
        p.setFont("SimSun", 12)
        for course in courses:
            text = f"课程: {course.course_prototype.name}, 学期: {course.semester.name}, 教师: {course.teacher.user.get_full_name() if course.teacher else 'N/A'}, 已选人数: {course.selected_students.count()}/{course.capacity}, 是否最终化: {'是' if course.is_finalized else '否'}"
            p.drawString(100, y, text)
            y -= 20
            if y < 50:
                p.showPage()
                # 重新绘制标题
                p.setFont("SimSun", 16)
                p.drawString(100, 800, "课程报表")
                y = 750
                p.setFont("SimSun", 12)

        p.showPage()
        p.save()
        return response
    

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')

        if not old_password or not new_password or not confirm_password:
            return Response({'detail': '所有字段都是必填的'}, status=status.HTTP_400_BAD_REQUEST)
        
        if new_password != confirm_password:
            return Response({'detail': '新密码和确认密码不一致'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not user.check_password(old_password):
            return Response({'detail': '旧密码不正确'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            validate_password(new_password, user=user)
        except ValidationError as e:
            return Response({'detail': e.messages}, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(new_password)
        user.save()
        return Response({'detail': '密码修改成功'}, status=status.HTTP_200_OK)
    



class StudentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    学生管理的 ViewSet
    提供学生的列表和详细信息
    """
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated, IsAdminOrTeacher]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Student.objects.all()
        elif user.groups.filter(name='Teacher').exists():
            # 假设教师只能看到自己部门的学生
            return Student.objects.filter(department__in=user.teacher_profile.departments.all())
        else:
            return Student.objects.none()