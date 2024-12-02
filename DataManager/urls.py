from django.urls import path

from . import views

app_name='DataManager'

urlpatterns = [
    path('',views.IndexPage,name='index'),
]