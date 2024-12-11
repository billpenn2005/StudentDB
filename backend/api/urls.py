# backend/api/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import CurrentUserView, CoursePrototypeViewSet, CourseInstanceViewSet
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register(r'course-prototypes', CoursePrototypeViewSet, basename='course-prototype')
router.register(r'course-instances', CourseInstanceViewSet, basename='course-instance')

urlpatterns = [
    path('', include(router.urls)),
    path('user/', include([
        path('', include('rest_framework.urls', namespace='rest_framework')),
        path('current/', CurrentUserView.as_view(), name='current-user'),
    ])),
    path('token/', TokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
]
