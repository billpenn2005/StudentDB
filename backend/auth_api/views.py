# auth_api/views.py
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny
from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

class KeepLoginStatusSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

class LoginView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer
    

    def post(self, request, *args, **kwargs):
        # 反序列化数据
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        try:
            # 获取用户
            user = get_user_model().objects.get(username=username)
        except get_user_model().DoesNotExist:
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

        # 检查密码
        if not user.check_password(password):
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

        # 生成 JWT Token
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        print(access_token)

        return Response({
            'access_token': access_token,
            'refresh_token': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
            }
        }, status=status.HTTP_200_OK)
