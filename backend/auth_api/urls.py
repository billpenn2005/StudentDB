# auth_api/urls.py
from django.urls import path
from .views import LoginView

urlpatterns = [
    path('api/', LoginView.as_view(), name='login'),
]
