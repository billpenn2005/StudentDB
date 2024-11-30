from django.shortcuts import render
from django import http
import random
from django.shortcuts import redirect
from django.template import loader
from .models import AuthUser
import hashlib
from django.views.decorators.csrf import csrf_exempt
import json




# Create your views here.
@csrf_exempt
def RequireSalt(request):
    has_salt=request.session.get('has_salt')
    if has_salt is None or has_salt==False:
        def generate_random_str(randomlength=16):
            """
            生成一个指定长度的随机字符串
            """
            random_str = ''
            base_str = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789'
            length = len(base_str) - 1
            for i in range(randomlength):
                random_str += base_str[random.randint(0, length)]
            return random_str
        salt={'salt':''}
        salt['salt']=generate_random_str(20)
        request.session['has_salt']=True
        request.session['salt']=salt
        return http.JsonResponse(salt)
    else:
        return http.JsonResponse(request.session['salt'])
    
def LoginPage(request):
    login_state=request.session.get('is_login')
    if login_state == True:
        return redirect('./index')
    else:
        template=loader.get_template('login.html')
        context={
            'salt':''
        }
        salt=request.session.get('salt')
        if salt is not None:
            context['salt']=salt['salt']
        return http.HttpResponse(template.render(context,request))
    
@csrf_exempt
def LoginApi(request):
    result={
        'state':''
    }
    if request.method=='GET':
        result['state']='Failed'
        result['reason']='GET request'
        return http.JsonResponse(result)
    else:
        username=request.POST.get('username')
        hashed_pwd=request.POST.get('password')
        if username is None or hashed_pwd is None:
            result['state']='Failed'
            result['reason']='no username or password'
            return http.JsonResponse(result)
        salt=request.session.get('salt')
        if salt is None:
            result['state']='Failed'
            result['reason']='no salt'
            return http.JsonResponse(result)
        salt=salt['salt']
        login_user=AuthUser.objects.filter(username=str(username)).first()
        if not login_user:
            result['state']='Failed'
            result['reason']='no such user:'+username
            return http.JsonResponse(result)
        auth_md5=hashlib.md5((login_user.pwd_md5+salt).encode()).hexdigest()
        if auth_md5 != hashed_pwd:
            result['state']='Failed'
            result['reason']='wrong password'
            return http.JsonResponse(result)
        result['state']='Success'
        request.session['has_salt']=False
        request.session['is_login']=True
        request.session['username']=username
        return http.JsonResponse(result)
    
@csrf_exempt
def LogoutApi(request):
    result={
        'state':''
    }
    if request.method=='GET':
        result['state']='Failed'
        result['reason']='GET request'
        return http.JsonResponse(result)
    elif request.session.get('is_login') is None or request.session.get('is_login')==False:
        result['state']='Failed'
        result['reason']='not logged in'
        return http.JsonResponse(result)
    else:
        result['state']='Success'
        request.session['is_login']=False
        request.session['has_salt']=False
        request.session.flush()
        return http.JsonResponse(result)

def IndexPage(request):
    login_state=request.session.get('is_login')
    if login_state != True:
        return redirect('./login/')
    template=loader.get_template('index.html')
    return http.HttpResponse(template.render(context=None,request=request))