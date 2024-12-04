from django.urls import path

from . import views

app_name='DataManager'

urlpatterns = [
    path('',views.IndexPage,name='index'),
    path('api/basic/info',views.BasicInfo,name='basicinfo'),
    path('api/course/info',views.CourseInfo,name='courseinfo'),
    path('api/reward/info',views.RewardInfo,name='rewardinfo'),
    path('api/punish/info',views.PunishmentInfo,name='punishinfo'),
    path('api/course/add',views.OpenCourse,name='addcourse'),
    path('api/course/remove',views.RemoveCourse,name='removecourse'),
    path('api/section/info',views.SectionInfo,name='sectioninfo'),
    path('api/department/info',views.DepartmentInfo,name='departmentinfo'),
    path('api/major/info',views.MajorInfo,name='majorinfo'),
    path('api/classroom/info',views.ClassroomInfo,name='classroominfo'),
    path('api/timeslot/info',views.TimeSlotInfo,name='timeslotinfo'),
    path('api/course/addslot',views.AddCourseSlot,name='addcourseslot'),
    path('api/course/removeslot',views.RemoveCourseSlot,name='removecourseslot'),
    path('api/department/add',views.AddDepartment,name='adddepartment'),
    path('api/major/add',views.AddMajor,name='addmajor'),
    path('api/department/remove',views.RemoveDepartment,name='removedepartment'),
    path('api/major/remove',views.RemoveMajor,name='removemajor'),
]