# backend/api/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import (
    DepartmentViewSet, SpecialtyViewSet, StudentViewSet,
    RewardPunishmentViewSet, CourseViewSet, EnrollmentViewSet,
    ExamViewSet, RetakeExamViewSet, ClassViewSet, CourseSelectionViewSet
)
from .views import CurrentUserView
from .viewsets import GenerateStudentReportView,CustomTokenObtainPairView,LogoutView
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'specialties', SpecialtyViewSet, basename='specialty')
router.register(r'students', StudentViewSet, basename='student')
router.register(r'reward-punishments', RewardPunishmentViewSet, basename='rewardpunishment')
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'enrollments', EnrollmentViewSet, basename='enrollment')
router.register(r'exams', ExamViewSet, basename='exam')
router.register(r'retake-exams', RetakeExamViewSet, basename='retakeexam')
router.register(r'classes', ClassViewSet, basename='class')
router.register(r'course-selections', CourseSelectionViewSet, basename='courseselection')

urlpatterns = [
    path('', include(router.urls)),
    path('user/', CurrentUserView.as_view(), name='current-user'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('generate-student-report/', GenerateStudentReportView.as_view(), name='generate-student-report'),
]
