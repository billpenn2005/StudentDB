from django.db import models

# Create your models here.

# Create your models here.
class Role(models.Model):
    role_name=models.CharField('role_name',max_length=40)
    def __str__(self):
        return self.role_name

class AuthUser(models.Model):
    username=models.CharField('username',max_length=40)
    pwd_md5=models.CharField('pwd_md5',max_length=40)
    role=models.ForeignKey(Role,on_delete=models.SET_NULL,null=True)
    def __str__(self):
        return self.username
    #salt=models.CharField('salt',max_length=20,null=True)