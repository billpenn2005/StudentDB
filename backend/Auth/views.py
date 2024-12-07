from django.shortcuts import render
from django import http
import random
from django.shortcuts import redirect
from django.template import loader
from .models import AuthUser
import hashlib
from django.views.decorators.csrf import csrf_exempt
import json
import base64




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
        return redirect('/')
    else:
        template=loader.get_template('Auth/login.html')
        context={
            'salt':''
        }
        salt=request.session.get('salt')
        if salt is not None:
            context['salt']=salt['salt']
        return http.HttpResponse(template.render(context,request))
    
#@csrf_exempt
def LoginApi(request):
    result={
        'state':''
    }
    if request.method=='GET':
        result['state']='Failed'
        result['reason']='GET request'
        return http.JsonResponse(result)
    elif request.session.get('is_login')==True:
        result['state']='Failed'
        result['reason']='Already logged in'
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
        request.session['role']=str(login_user.role)
        request.session['auth_id']=login_user.id
        return http.JsonResponse(result)
    
#@csrf_exempt
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
    template=loader.get_template('Auth/index.html')
    return http.HttpResponse(template.render(context=None,request=request))

def bytes_xor(s: bytes, k: bytes):
    k = (k * (len(s) // len(k) + 1))[0:len(s)]
    return bytes([a ^ b for a, b in zip(s, k)])

def ChangePassword(request):
    result={
        'state':'Failed'
    }
    login_state=request.session.get('is_login')
    if login_state != True:
        result['reason']='Not logged in'
        return http.JsonResponse(result)
    if request.session.get('has_salt')!=True:
        result['reason']='Requires salt'
        return http.JsonResponse(result)
    salt=request.session.get('salt').get('salt')
    old_pwd=request.POST.get('old_password')
    auth_user=AuthUser.objects.filter(id=request.session.get('auth_id')).first()
    first_auth=hashlib.md5((auth_user.pwd_md5+salt).encode()).hexdigest()
    #print(auth_user.pwd_md5)
    if first_auth!=old_pwd:
        result['reason']='Wrong old password'
        return http.JsonResponse(result)
    pwd_xor=request.POST.get('pwd_xor')
    try:
        pwd_xor=base64.b64decode(pwd_xor)
        old_pwd=bytes(auth_user.pwd_md5.encode())
        auth_user.pwd_md5=(bytes_xor(old_pwd,pwd_xor)).decode()
        auth_user.save()
        request.session['has_salt']=False
    except:
        result['reason']='Internal error'
        return http.JsonResponse(result)
    result['state']='Success'
    return http.JsonResponse(result)