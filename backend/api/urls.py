# backend/api/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import CurrentUserView, CoursePrototypeViewSet, CourseInstanceViewSet, S_GradeViewSet,TeacherViewSet, DepartmentViewSet, ClassViewSet, GradeViewSet, CurrentStudentProfileView, GenerateStudentReportView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register(r'course-prototypes', CoursePrototypeViewSet, basename='course-prototype')
router.register(r'course-instances', CourseInstanceViewSet, basename='course-instance')
router.register(r's-grades', S_GradeViewSet)  # 添加这一行
router.register(r'teachers', TeacherViewSet)  # 添加这一行
router.register(r'departments', DepartmentViewSet)
router.register(r'classes', ClassViewSet)
router.register(r'grades', GradeViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('user/', include([
        path('', include('rest_framework.urls', namespace='rest_framework')),
        path('current/', CurrentUserView.as_view(), name='current-user'),
    ])),
    path('token/', TokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('students/current/', CurrentStudentProfileView.as_view(), name='current-student-profile'),
    path('generate-report/', GenerateStudentReportView.as_view(), name='generate-student-report'),

]
