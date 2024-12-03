from django.contrib import admin
from .models import *

# Register your models here.

@admin.action(description="Set all time slots.")
def set_time_slot(modeladmin, request, queryset):
    for w in range(20):
        for i in range(7):
            for j in range(5):
                TimeSlot.objects.create(slot=str(j),day=i+1,week=w+1)


class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ["id","day", "slot"]
    ordering = ["week","day","slot"]
    actions = [set_time_slot]



admin.site.register(Department)
admin.site.register(Building)
admin.site.register(ClassRoom)
admin.site.register(Student)
admin.site.register(Teacher)
admin.site.register(Section)
admin.site.register(Course)
admin.site.register(StudentTake)
admin.site.register(TeacherTeach)
admin.site.register(TimeSlot,TimeSlotAdmin)
admin.site.register(CourseTimeSlot)
admin.site.register(Major)
admin.site.register(Reward)
admin.site.register(StudentReward)
admin.site.register(Punishment)
admin.site.register(StudentPunish)
admin.site.register(DepartmentPermission)
admin.site.register(MajorPermission)