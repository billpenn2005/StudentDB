from django.urls import path

from . import views

app_name='DataManager'

urlpatterns = [
    path('',views.IndexPage,name='index'),
    path('api/basicinfo',views.BasicInfo,name='basicinfo'),
    path('api/courseinfo',views.CourseInfo,name='courseinfo'),
]