from django.shortcuts import render
from django import http
from django.shortcuts import redirect
from django.urls import reverse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
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
            request.session['student_id']=rel_student.student_id
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
            request.session['teacher_id']=rel_student.teacher_id
        else:
            result['state']='Failed'
            result['reason']='No such teacher'
    return http.JsonResponse(result)


@csrf_exempt
def CourseInfo(request):
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
        now_time=timezone.now()
        if request.POST.get('timestamp') is not None:
            now_time=timezone.datetime.fromtimestamp(int(request.POST.get('timestamp')))
        if request.session.get('student_id') is None:
            rel_student=Student.objects.filter(related_auth_account_id=request.session.get('auth_id')).first()
            request.session['student_id']=rel_student.student_id
        result['courses']=[]
        rel_courses=list(StudentTake.objects.filter(student__student_id=request.session['student_id'],course__section__start_date__lte=now_time,course__section__end_date__gte=now_time))
        for i in rel_courses:
            rel_slots=list(i.course.timeslots.all())
            for j in rel_slots:
                course_info={}
                course_info['name']=i.course.name
                course_info['day']=j.day
                course_info['slot']=int(j.slot)
                rel_teachers=list(TeacherTeach.objects.filter(course=i.course))
                concat_str=''
                for k in rel_teachers:
                    concat_str+=k.teacher.name+' '
                course_info['teacher']=concat_str
                result['courses'].append(course_info)
        result['state']='Success'
        return http.JsonResponse(result)