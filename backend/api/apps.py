# backend/api/apps.py

from django.apps import AppConfig

class ApiConfig(AppConfig):
    name = 'api'

    def ready(self):
        import api.signal  # 确保 signals.py 被导入