# student_api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StudentViewSet

# 创建路由器
router = DefaultRouter()

# 注册视图集
router.register(r'students', StudentViewSet, basename='student')

urlpatterns = [
    path('api/', include(router.urls)),  # 默认的路由器 URL
]