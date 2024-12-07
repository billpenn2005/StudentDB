# student_api/views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Student
from .serializers import StudentSerializer
from django.contrib.auth import get_user_model
from rest_framework import permissions
from django.shortcuts import get_object_or_404
class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.select_related('user').all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'username'  # 使用自定义的lookup_field

    def get_queryset(self):
        queryset = super().get_queryset()
        username = self.kwargs.get(self.lookup_field)
        if username:
            queryset = queryset.filter(user__username=username)
        return queryset

    def retrieve(self, request, *args, **kwargs):
        username = kwargs.get(self.lookup_field)
        student = get_object_or_404(Student, user__username=username)
        serializer = self.get_serializer(student)
        return Response(serializer.data)
