from django.shortcuts import render
from django import http
from django.shortcuts import redirect
from django.urls import reverse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import *
import json
import io


def IndexPage(request):
    if request.session.get('is_login') != True:
        return http.HttpResponseRedirect(reverse('Auth:login'))
    template=loader.get_template('DataManager/index.html')
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
            course_info={}
            course_info['id']=i.course.id
            course_info['name']=i.course.name
            course_info['section']=i.course.section.name
            course_info['slots']=[]
            rel_slots=list(i.course.timeslots.all())
            for j in rel_slots:
                c_slot={}
                c_slot['week']=j.week
                c_slot['day']=j.day
                c_slot['slot']=int(j.slot)
                course_info['slots'].append(c_slot)
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
            course_info={}
            course_info['id']=i.course.id
            course_info['name']=i.course.name
            course_info['section']=i.course.section.name
            course_info['slots']=[]
            rel_slots=list(i.course.timeslots.all())
            for j in rel_slots:
                c_slot={}
                c_slot['week']=j.week
                c_slot['day']=j.day
                c_slot['slot']=int(j.slot)
                course_info['slots'].append(c_slot)
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
    if request.session.get('is_login') != True:
        result['state']='Failed'
        result['reason']='not logged in'
        return http.JsonResponse(result)
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
    if request.session.get('is_login') != True:
        result['state']='Failed'
        result['reason']='not logged in'
        return http.JsonResponse(result)
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

def SectionInfo(request):
    result={
        'state':'Failed'
    }
    if request.session.get('is_login') != True:
        result['state']='Failed'
        result['reason']='not logged in'
        return http.JsonResponse(result)
    if request.method=='GET' :
        result['reason']='GET request'
        return http.JsonResponse(result)
    result['state']='Success'
    sections=list(Section.objects.all())
    result['sections']=[]
    for i in sections:
        sec_obj={}
        sec_obj['id']=i.id
        sec_obj['name']=i.name
        sec_obj['start_date']=str(i.start_date)
        sec_obj['end_date']=str(i.end_date)
        result['sections'].append(sec_obj)
    return http.JsonResponse(result)

def DepartmentInfo(request):
    result={
        'state':'Failed'
    }
    if request.session.get('is_login') != True:
        result['state']='Failed'
        result['reason']='not logged in'
        return http.JsonResponse(result)
    if request.method=='GET' :
        result['reason']='GET request'
        return http.JsonResponse(result)
    result['state']='Success'
    result['departments']=[]
    departments=list(Department.objects.all())
    for i in departments:
        dep_obj={}
        dep_obj['id']=i.id
        dep_obj['name']=i.name
        result['departments'].append(dep_obj)
    return http.JsonResponse(result)


def ClassroomInfo(request):
    result={
        'state':'Failed'
    }
    if request.session.get('is_login') != True:
        result['state']='Failed'
        result['reason']='not logged in'
        return http.JsonResponse(result)
    if request.method=='GET' :
        result['reason']='GET request'
        return http.JsonResponse(result)
    result['state']='Success'
    result['classrooms']=[]
    classrooms=list(ClassRoom.objects.all())
    for i in classrooms:
        cls_obj={}
        cls_obj['id']=i.id
        cls_obj['rel_building_id']=i.related_building.id
        cls_obj['number']=i.number
        cls_obj['capacity']=i.capacity
        result['classrooms'].append(cls_obj)
    return http.JsonResponse(result)
    

def OpenCourse(request):
    result={
        'state':'Failed'
    }
    if request.session.get('is_login') != True:
        result['state']='Failed'
        result['reason']='not logged in'
        return http.JsonResponse(result)
    if request.method=='GET' :
        result['reason']='GET request'
        return http.JsonResponse(result)
    elif request.session.get('role')!='Teacher' and request.session.get('role')!='Admin':
        result['reason']='Not teacher'
        return http.JsonResponse(result)
    elif request.session.get('role')=='Teacher':
        course_section=request.POST.get('section')
        course_name=request.POST.get('name')
        course_department=request.POST.get('department')
        course_classroom=request.POST.get('classroom')
        rel_teacher=Teacher.objects.filter(related_auth_account_id=request.session.get('auth_id')).first()
        if course_section is None or course_name is None or course_department is None or course_classroom is None:
            result['state']='Failed'
            result['reason']='wrong param'
            return http.JsonResponse(result)
        c_name=str(course_name)
        c_dep=Department.objects.filter(id=int(course_department)).first()
        c_rom=ClassRoom.objects.filter(id=int(course_classroom)).first()
        c_sec=Section.objects.filter(id=int(course_section)).first()
        if c_dep is None:
            result['state']='Failed'
            result['reason']='department not exist'
            return http.JsonResponse(result)
        if c_rom is None:
            result['state']='Failed'
            result['reason']='classroom not exist'
            return http.JsonResponse(result)
        if c_sec is None:
            result['state']='Failed'
            result['reason']='section not exist'
            return http.JsonResponse(result)
        new_course=Course.objects.create(name=c_name,department=c_dep,classroom=c_rom,section=c_sec)
        TeacherTeach.objects.create(teacher=rel_teacher,course=new_course)
        result['state']='Success'
        return http.JsonResponse(result)
    else:
        course_section=request.POST.get('section')
        course_name=request.POST.get('name')
        course_department=request.POST.get('department')
        course_classroom=request.POST.get('classroom')
        if course_section is None or course_name is None or course_department is None or course_classroom is None:
            result['state']='Failed'
            result['reason']='wrong param'
            return http.JsonResponse(result)
        c_name=str(course_name)
        c_dep=Department.objects.filter(id=int(course_department)).first()
        c_rom=ClassRoom.objects.filter(id=int(course_classroom)).first()
        c_sec=Section.objects.filter(id=int(course_section)).first()
        if c_dep is None:
            result['state']='Failed'
            result['reason']='department not exist'
            return http.JsonResponse(result)
        if c_rom is None:
            result['state']='Failed'
            result['reason']='classroom not exist'
            return http.JsonResponse(result)
        if c_sec is None:
            result['state']='Failed'
            result['reason']='section not exist'
            return http.JsonResponse(result)
        new_course=Course.objects.create(name=c_name,department=c_dep,classroom=c_rom,section=c_sec)
        #TeacherTeach.objects.create(teacher=rel_teacher,course=new_course)
        result['state']='Success'
        return http.JsonResponse(result)

def TimeSlotInfo(request):
    result={
        'state':'Failed'
    }
    if request.session.get('is_login') != True:
        result['state']='Failed'
        result['reason']='not logged in'
        return http.JsonResponse(result)
    if request.method=='GET' :
        result['reason']='GET request'
        return http.JsonResponse(result)
    result['state']='Success'
    result['slots']=[]
    slots=list(TimeSlot.objects.all())
    for i in slots:
        s_obj={}
        s_obj['id']=i.id
        s_obj['week']=i.week
        s_obj['day']=i.day
        s_obj['slot']=int(i.slot)
        result['slots'].append(s_obj)
    return http.JsonResponse(result)


def MajorInfo(request):
    result={
        'state':'Failed'
    }
    if request.session.get('is_login') != True:
        result['state']='Failed'
        result['reason']='not logged in'
        return http.JsonResponse(result)
    if request.method=='GET' :
        result['reason']='GET request'
        return http.JsonResponse(result)
    result['state']='Success'
    result['majors']=[]
    majors=list(Major.objects.all())
    for i in majors:
        s_obj={}
        s_obj['id']=i.id
        s_obj['name']=i.name
        s_obj['department_id']=i.related_department.id
        result['majors'].append(s_obj)
    return http.JsonResponse(result)
    
def AddCourseSlot(request):
    result={
        'state':'Failed'
    }
    if request.session.get('is_login') != True:
        result['state']='Failed'
        result['reason']='not logged in'
        return http.JsonResponse(result)
    if request.method=='GET' :
        result['reason']='GET request'
        return http.JsonResponse(result)
    elif request.session.get('role')!='Teacher' and request.session.get('role')!='Admin':
        result['reason']='Permission denied'
        return http.JsonResponse(result)
    else:
        POST=None
        try:
            POST=json.loads(request.body)
        except:
            result['state']='Failed'
            result['reason']='wrong param'
            return http.JsonResponse(result)
        c_id=POST.get('course')
        slots=POST.get('slots')
        if not isinstance(slots,list) or not isinstance(c_id,int):
            try:
                slots=list(slots)
                c_id=int(c_id)
            except:
                result['state']='Failed'
                result['reason']='wrong param'
                return http.JsonResponse(result)
        if c_id is None or slots is None or (not isinstance(slots,list)):
            result['state']='Failed'
            result['reason']='wrong param'
            return http.JsonResponse(result)
        rel_c=Course.objects.filter(id=c_id).first()
        if rel_c is None:
            result['state']='Failed'
            result['reason']='no such course'
            return http.JsonResponse(result)
        rel_teacher=None
        if request.session.get('role')=='Teacher':
            rel_teacher=Teacher.objects.filter(related_auth_account_id=request.session.get('auth_id')).first()
            rel_tec=TeacherTeach.objects.filter(teacher=rel_teacher,course=rel_c).first()
            if rel_tec is None:
                result['state']='Failed'
                result['reason']='permission denied'
                return http.JsonResponse(result)
        for i in slots:
            i_id=None
            try:
                i_id=int(i)
            except:
                result['state']='Failed'
                result['reason']='wrong param'
                return http.JsonResponse(result)
            rel_slot=TimeSlot.objects.filter(id=i_id).first()
            if rel_slot is not None:
                if rel_c.timeslots.filter(id=i_id).first() is None:
                    CourseTimeSlot.objects.create(course=rel_c,time_slot=rel_slot)
        result['state']='Success'
        return http.JsonResponse(result)
    
def RemoveCourseSlot(request):
    result={
        'state':'Failed'
    }
    if request.session.get('is_login') != True:
        result['state']='Failed'
        result['reason']='not logged in'
        return http.JsonResponse(result)
    if request.method=='GET' :
        result['reason']='GET request'
        return http.JsonResponse(result)
    elif request.session.get('role')!='Teacher' and request.session.get('role')!='Admin':
        result['reason']='Permission denied'
        return http.JsonResponse(result)
    else:
        POST=None
        try:
            POST=json.loads(request.body)
        except:
            result['state']='Failed'
            result['reason']='wrong param'
            return http.JsonResponse(result)
        c_id=POST.get('course')
        slots=POST.get('slots')
        if not isinstance(slots,list) or not isinstance(c_id,int):
            try:
                slots=list(slots)
                c_id=int(c_id)
            except:
                result['state']='Failed'
                result['reason']='wrong param'
                return http.JsonResponse(result)
        if c_id is None or slots is None or (not isinstance(slots,list)):
            result['state']='Failed'
            result['reason']='wrong param'
            return http.JsonResponse(result)
        rel_c=Course.objects.filter(id=c_id).first()
        if rel_c is None:
            result['state']='Failed'
            result['reason']='no such course'
            return http.JsonResponse(result)
        rel_teacher=None
        if request.session.get('role')=='Teacher':
            rel_teacher=Teacher.objects.filter(related_auth_account_id=request.session.get('auth_id')).first()
            rel_tec=TeacherTeach.objects.filter(teacher=rel_teacher,course=rel_c).first()
            if rel_tec is None:
                result['state']='Failed'
                result['reason']='permission denied'
                return http.JsonResponse(result)
        for i in slots:
            i_id=None
            try:
                i_id=int(i)
            except:
                result['state']='Failed'
                result['reason']='wrong param'
                return http.JsonResponse(result)
            rel_slot=TimeSlot.objects.filter(id=i_id).first()
            if rel_slot is not None:
                if rel_c.timeslots.filter(id=i_id).first() is not None:
                    CourseTimeSlot.objects.filter(course=rel_c,time_slot=rel_slot).delete()
        result['state']='Success'
        return http.JsonResponse(result)
    

def RemoveCourse(request):
    result={
        'state':'Failed'
    }
    if request.session.get('is_login') != True:
        result['state']='Failed'
        result['reason']='not logged in'
        return http.JsonResponse(result)
    if request.method=='GET' :
        result['reason']='GET request'
        return http.JsonResponse(result)
    elif request.session.get('role')!='Teacher' and request.session.get('role')!='Admin':
        result['reason']='Permission denied'
        return http.JsonResponse(result)
    c_id=request.POST.get('course')
    if c_id is None:
        result['state']='Failed'
        result['reason']='wrong param'
        return http.JsonResponse(result)
    c_id=int(c_id)
    rel_c=Course.objects.filter(id=c_id).first()
    if rel_c is None:
        result['state']='Failed'
        result['reason']='no such course'
        return http.JsonResponse(result)
    if request.session.get('role')=='Teacher':
        rel_teacher=Teacher.objects.filter(related_auth_account_id=request.session.get('auth_id')).first()
        rel_tec=TeacherTeach.objects.filter(teacher=rel_teacher,course=rel_c).first()
        if rel_tec is None:
            result['state']='Failed'
            result['reason']='permission denied'
            return http.JsonResponse(result)
    rel_c.delete()
    result['state']='Success'
    return http.JsonResponse(result)

def AddDepartment(request):
    result={
        'state':'Failed'
    }
    if request.session.get('is_login') != True:
        result['state']='Failed'
        result['reason']='not logged in'
        return http.JsonResponse(result)
    if request.method=='GET' :
        result['reason']='GET request'
        return http.JsonResponse(result)
    elif request.session.get('role')!='Admin':
        result['reason']='Permission denied'
        return http.JsonResponse(result)
    d_name=request.POST.get('name')
    try:
        d_name=str(d_name)
    except:
        result['reason']='Wrong param'
        return http.JsonResponse(result)
    result['state']='Success'
    if Department.objects.filter(name=d_name).first() is None:
        Department.objects.create(name=d_name)
    return http.JsonResponse(result)

def AddMajor(request):
    result={
        'state':'Failed'
    }
    if request.session.get('is_login') != True:
        result['state']='Failed'
        result['reason']='not logged in'
        return http.JsonResponse(result)
    if request.method=='GET' :
        result['reason']='GET request'
        return http.JsonResponse(result)
    elif request.session.get('role')!='Admin' and request.session.get('role')!='Teacher':
        result['reason']='Permission denied'
        return http.JsonResponse(result)
    if request.session.get('role')=='Admin':
        m_name=request.POST.get('name')
        m_dep=request.POST.get('department')
        try:
            m_name=str(m_name)
            m_dep=int(m_dep)
        except:
            result['reason']='Wrong param'
            return http.JsonResponse(result)
        result['state']='Success'
        rel_dep=Department.objects.filter(id=m_dep).first()
        if Major.objects.filter(name=m_name).first() is None:
            Major.objects.create(name=m_name,related_department=rel_dep)
        return http.JsonResponse(result)
    else:
        m_name=request.POST.get('name')
        m_dep=request.POST.get('department')
        m_dep=int(m_dep)
        try:
            m_name=str(m_name)
        except:
            result['reason']='Wrong param'
            return http.JsonResponse(result)
        rel_teacher=Teacher.objects.filter(related_auth_account_id=request.session.get('auth_id')).first()
        if DepartmentPermission.objects.filter(teacher=rel_teacher,department__id=m_dep).first() is None:
            result['reason']='Permission denied'
            return http.JsonResponse(result)
        result['state']='Success'
        rel_dep=Department.objects.filter(id=m_dep).first()
        if Major.objects.filter(name=m_name).first() is None:
            major_obj=Major.objects.create(name=m_name,related_department=rel_dep)
            MajorPermission.objects.create(major=major_obj,teacher=rel_teacher)
        return http.JsonResponse(result)

def RemoveDepartment(request):
    result={
        'state':'Failed'
    }
    if request.session.get('is_login') != True:
        result['state']='Failed'
        result['reason']='not logged in'
        return http.JsonResponse(result)
    if request.method=='GET' :
        result['reason']='GET request'
        return http.JsonResponse(result)
    elif request.session.get('role')!='Admin' and request.session.get('role')!='Teacher':
        result['reason']='Permission denied'
        return http.JsonResponse(result)
    d_id=request.POST.get('department')
    try:
        d_id=int(d_id)
    except:
        result['reason']='Wrong param'
        return http.JsonResponse(result)
    result['state']='Success'
    if request.session.get('role')=='Teacher':
        rel_teacher=Teacher.objects.filter(related_auth_account_id=request.session.get('auth_id')).first()
        if DepartmentPermission.objects.filter(teacher=rel_teacher,department__id=d_id).first() is None:
            result['reason']='Permission denied'
            return http.JsonResponse(result)
    if Department.objects.filter(id=d_id).first() is not None:
        Department.objects.filter(id=d_id).first().delete()
    return http.JsonResponse(result)

def RemoveMajor(request):
    result={
        'state':'Failed'
    }
    if request.session.get('is_login') != True:
        result['state']='Failed'
        result['reason']='not logged in'
        return http.JsonResponse(result)
    if request.method=='GET' :
        result['reason']='GET request'
        return http.JsonResponse(result)
    elif request.session.get('role')!='Admin' and request.session.get('role')!='Teacher':
        result['reason']='Permission denied'
        return http.JsonResponse(result)
    m_id=request.POST.get('major')
    try:
        m_id=int(m_id)
    except:
        result['reason']='Wrong param'
        return http.JsonResponse(result)
    result['state']='Success'
    rel_maj=Major.objects.filter(id=m_id).first()
    if rel_maj is None:
        result['reason']='No such major'
        return http.JsonResponse(result)
    if request.session.get('role')=='Teacher':
        rel_teacher=Teacher.objects.filter(related_auth_account_id=request.session.get('auth_id')).first()
        if MajorPermission.objects.filter(teacher=rel_teacher,major__id=m_id).first() is None and DepartmentPermission.objects.filter(teacher=rel_teacher,department__id=rel_maj.related_department.id).first() is None:
            result['reason']='Permission denied'
            return http.JsonResponse(result)
    rel_maj.delete()
    return http.JsonResponse(result)