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
    path('api/major/edit',views.EditMajor,name='editmajor'),
    path('api/department/edit',views.EditDepartment,name='editdepartment'),
    path('api/department/permission/grant',views.GrantDepartmentPermission,name='grantdepartmentpermission'),
    path('api/major/permission/grant',views.GrantMajorPermission,name='grantmajorpermission'),
    path('api/department/permission/revoke',views.RevokeDepartmentPermission,name='revokedepartmentpermission'),
    path('api/major/permission/revoke',views.RevokeMajorPermission,name='revokemajorpermission'),
    path('api/selection/info',views.SelectionInfo,name='selectioninfo'),
    path('api/selection/add',views.AddSelection,name='addselection'),
    path('api/selection/remove',views.RemoveSelection,name='removeselection'),
    path('api/selection/addcourse',views.AddSelectionCourse,name='addselectioncourse'),
    path('api/selection/removecourse',views.RemoveSelectionCourse,name='removeselectioncourse'),
    path('api/selection/select',views.SelectSelectionCourse,name='selectselectioncourse'),
    path('api/selection/deselect',views.DeselectSelectionCourse,name='deselectselectioncourse'),
    path('api/selection/check',views.CheckSelection,name='checkselectioncourse'),
]