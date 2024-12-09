# api/utils.py

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    # 调用 DRF 默认的异常处理
    response = exception_handler(exc, context)

    if response is not None:
        custom_response = {
            'error': {
                'code': response.status_code,
                'message': response.data
            }
        }
        return Response(custom_response, status=response.status_code)

    # 对于未处理的异常，返回通用错误
    return Response({'error': {'code': 500, 'message': '服务器内部错误'}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
