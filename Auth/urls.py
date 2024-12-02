from django.urls import path

from . import views


app_name='Auth'
urlpatterns = [
    path('salt',views.RequireSalt,name='salt'),
    path('login',views.LoginPage,name='login'),
    path('index',views.IndexPage,name='index'),
    path('loginapi',views.LoginApi,name='loginapi'),
    path('logoutapi',views.LogoutApi,name='logoutapi'),
]