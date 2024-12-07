# authapp/serializers.py

from rest_framework import serializers
from .models import AuthUser

class AuthUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthUser
        fields = ['id', 'username', 'password', 'role']  # 根据需要调整字段
