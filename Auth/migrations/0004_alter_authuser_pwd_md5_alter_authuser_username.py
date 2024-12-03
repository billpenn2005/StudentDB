# Generated by Django 5.1.3 on 2024-11-30 07:12

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Auth", "0003_remove_authuser_salt"),
    ]

    operations = [
        migrations.AlterField(
            model_name="authuser",
            name="pwd_md5",
            field=models.CharField(max_length=40, verbose_name="pwd_md5"),
        ),
        migrations.AlterField(
            model_name="authuser",
            name="username",
            field=models.CharField(max_length=40, verbose_name="username"),
        ),
    ]