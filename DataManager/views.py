from django.shortcuts import render
from django import http
from django.shortcuts import redirect
from django.urls import reverse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from .models import *



# Create your views here.

def IndexPage(request):
    if request.session.get('is_login') != True:
        return http.HttpResponseRedirect(reverse('Auth:login'))
    template=loader.get_template('main_index.html')
    return http.HttpResponse(template.render(context=None,request=request))

@csrf_exempt
def BasicInfo(request):
    result={
        'state':'Failed'
    }
    if request.method=='GET':
        result['state']='Failed'
        result['reason']='GET request'
        return http.JsonResponse(result)
    if request.session.get('is_login') != True:
        result['state']='Failed'
        result['reason']='not logged in'
        return http.JsonResponse(result)
    if request.session.get('role')=='Student':
        rel_student=Student.objects.filter(related_auth_account_id=request.session.get('auth_id')).first()
        if rel_student:
            result['state']='Success'
            result['name']=rel_student.name
            result['role']='Student'
            result['student_id']=rel_student.student_id
        else:
            result['state']='Failed'
            result['reason']='No such student'
    elif request.session.get('role')=='Teacher':
        rel_teacher=Teacher.objects.filter(related_auth_account_id=request.session.get('auth_id')).first()
        if rel_teacher:
            result['state']='Success'
            result['role']='Teacher'
            result['name']=rel_teacher.name
            result['teacher_id']=rel_teacher.teacher_id
        else:
            result['state']='Failed'
            result['reason']='No such teacher'
    return http.JsonResponse(result)