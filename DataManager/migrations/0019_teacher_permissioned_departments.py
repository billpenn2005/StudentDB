# Generated by Django 5.1.3 on 2024-12-03 14:41

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("DataManager", "0018_majorpermission"),
    ]

    operations = [
        migrations.AddField(
            model_name="teacher",
            name="permissioned_departments",
            field=models.ManyToManyField(
                related_name="permissioned_departments",
                through="DataManager.DepartmentPermission",
                to="DataManager.department",
            ),
        ),
    ]