from django.db import models

# Create your models here.

class AuthUser(models.Model):
    username=models.CharField('username',max_length=40)
    pwd_md5=models.CharField('pwd_md5',max_length=40)
    #salt=models.CharField('salt',max_length=20,null=True)