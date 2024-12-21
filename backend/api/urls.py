# backend/api/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import CurrentUserView, CoursePrototypeViewSet, CourseInstanceViewSet, S_GradeViewSet,TeacherViewSet, DepartmentViewSet, ClassViewSet, GradeViewSet, CurrentStudentProfileView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .viewsets import BulkImportViewSet, GenerateReportView,ChangePasswordView,PunishmentRecordViewSet, RewardRecordViewSet, SelectionBatchViewSet
from .viewsets import StudentViewSet
router = DefaultRouter()
router.register(r'course-prototypes', CoursePrototypeViewSet, basename='course-prototype')
router.register(r'course-instances', CourseInstanceViewSet, basename='course-instance')
router.register(r's-grades', S_GradeViewSet)  # 添加这一行
router.register(r'teachers', TeacherViewSet)  # 添加这一行
router.register(r'departments', DepartmentViewSet)
router.register(r'classes', ClassViewSet)
router.register(r'grades', GradeViewSet)
router.register(r'bulk-import', BulkImportViewSet, basename='bulk-import')
router.register(r'punishment-record', PunishmentRecordViewSet, basename='punishment-record')
router.register(r'reward-record', RewardRecordViewSet, basename='reward-record')
router.register(r'students', StudentViewSet, basename='student')
router.register(r'selection-batches', SelectionBatchViewSet, basename='selection-batch')

urlpatterns = [
    path('', include(router.urls)),
    path('user/', include([
        path('', include('rest_framework.urls', namespace='rest_framework')),
        path('current/', CurrentUserView.as_view(), name='current-user'),
    ])),
    path('token/', TokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('old_students/current/', CurrentStudentProfileView.as_view(), name='current-student-profile'),
    
    path('generate-report/', GenerateReportView.as_view(), name='generate-report'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
]
