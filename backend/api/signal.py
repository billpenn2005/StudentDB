# backend/api/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from .models import Student
import logging
logger = logging.getLogger(__name__)
@receiver(post_save, sender=Student)
def add_user_to_student_group(sender, instance, created, **kwargs):
    if created:
        try:
            student_group = Group.objects.get(name='Student')
            instance.user.groups.add(student_group)
            instance.user.save()
            logger.debug(f"用户 '{instance.user.username}' 通过信号加入 'Student' 组。")
        except Group.DoesNotExist:
            logger.error("组 'Student' 不存在，请先创建。")