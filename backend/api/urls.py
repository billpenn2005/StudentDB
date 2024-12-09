# backend/api/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import CourseViewSet, ClassInstanceViewSet, CourseSelectionViewSet, StudentViewSet, UserViewSet, CurrentUserView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'class-instances', ClassInstanceViewSet, basename='classinstance')
router.register(r'course-selections', CourseSelectionViewSet, basename='courseselection')
router.register(r'students', StudentViewSet, basename='student')

urlpatterns = [
    path('', include(router.urls)),
    path('user/', include([
        path('', include('rest_framework.urls', namespace='rest_framework')),
        path('current/', CurrentUserView.as_view(), name='current-user'),
    ])),
    path('token/', TokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
]
