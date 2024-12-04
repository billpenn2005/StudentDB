from django.urls import path

from . import views


app_name='Auth'
urlpatterns = [
    path('api/salt',views.RequireSalt,name='salt'),
    path('login',views.LoginPage,name='login'),
    path('index',views.IndexPage,name='index'),
    path('api/login',views.LoginApi,name='loginapi'),
    path('api/logout',views.LogoutApi,name='logoutapi'),
    path('api/changepassword',views.ChangePassword,name='changepassword')
] 