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

#@csrf_exempt
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
            result['sex']=rel_student.SEXS[int(rel_student.sex)][1]
            result['student_id']=rel_student.student_id
            result['identity_id']=rel_student.identity_id
            if rel_student.brithday is not None:
                result['birthday']=str(rel_student.brithday)
                birth=rel_student.brithday
                today = timezone.datetime.today()
                age = today.year - birth.year
                if today.month < birth.month:
                    age -= 1
                elif today.month == birth.month and today.day < birth.day:
                    age -= 1
                result['age']=int(age)
            result['grade']=rel_student.grade
            result['department']=str(rel_student.department)
            result['major']=str(rel_student.major)
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
            request.session['teacher_id']=rel_teacher.teacher_id
        else:
            result['state']='Failed'
            result['reason']='No such teacher'
    return http.JsonResponse(result)


#@csrf_exempt
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
                course_info['week']=j.week
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
    elif request.session.get('role')=='Teacher':
        now_time=timezone.now()
        if request.POST.get('timestamp') is not None:
            now_time=timezone.datetime.fromtimestamp(int(request.POST.get('timestamp')))
        if request.session.get('teacher_id') is None:
            rel_teacher=Teacher.objects.filter(related_auth_account_id=request.session.get('auth_id')).first()
            request.session['teacher_id']=rel_teacher.teacher_id
        result['courses']=[]
        rel_courses=list(TeacherTeach.objects.filter(teacher__teacher_id=request.session['teacher_id'],course__section__start_date__lte=now_time,course__section__end_date__gte=now_time))
        for i in rel_courses:
            rel_slots=list(i.course.timeslots.all())
            for j in rel_slots:
                course_info={}
                course_info['name']=i.course.name
                course_info['week']=j.week
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
    
#@csrf_exempt
def RewardInfo(request):
    result={
        'state':'Failed'
    }
    if request.method=='GET' :
        result['reason']='GET request'
        return http.JsonResponse(result)
    elif request.session.get('role')!='Student':
        result['reason']='Not student'
        return http.JsonResponse(result)
    else:
        with_detail=bool(request.POST.get('detailed')!=None)
        rel_student=Student.objects.filter(related_auth_account_id=request.session.get('auth_id')).first()
        rel_rewards=list(StudentReward.objects.filter(student=rel_student))
        result['rewards']=[]
        for i in rel_rewards:
            reward={}
            reward['name']=i.reward.name
            if with_detail:
                reward['detail']=i.reward.detail
            result['rewards'].append(reward)
        result['state']='Success'
        return http.JsonResponse(result)
    
#@csrf_exempt
def PunishmentInfo(request):
    result={
        'state':'Failed'
    }
    if request.method=='GET' :
        result['reason']='GET request'
        return http.JsonResponse(result)
    elif request.session.get('role')!='Student':
        result['reason']='Not student'
        return http.JsonResponse(result)
    else:
        with_detail=bool(request.POST.get('detailed')!=None)
        rel_student=Student.objects.filter(related_auth_account_id=request.session.get('auth_id')).first()
        rel_punishments=list(StudentPunish.objects.filter(student=rel_student))
        result['punishments']=[]
        for i in rel_punishments:
            punishment={}
            punishment['name']=i.punish.name
            if with_detail:
                punishment['detail']=i.punish.detail
            result['punishments'].append(punishment)
        result['state']='Success'
        return http.JsonResponse(result)