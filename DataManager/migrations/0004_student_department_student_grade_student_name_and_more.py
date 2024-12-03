# Generated by Django 5.1.3 on 2024-12-02 12:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Auth", "0006_rename_roles_role"),
        ("DataManager", "0003_student"),
    ]

    operations = [
        migrations.AddField(
            model_name="student",
            name="department",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="DataManager.department",
            ),
        ),
        migrations.AddField(
            model_name="student",
            name="grade",
            field=models.IntegerField(default=2023, verbose_name="grade"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="student",
            name="name",
            field=models.CharField(max_length=40, null=True, verbose_name="number"),
        ),
        migrations.AddField(
            model_name="student",
            name="student_id",
            field=models.CharField(max_length=40, null=True, verbose_name="student_id"),
        ),
        migrations.CreateModel(
            name="Teacher",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(max_length=40, null=True, verbose_name="number"),
                ),
                (
                    "teacher_id",
                    models.CharField(
                        max_length=40, null=True, verbose_name="student_id"
                    ),
                ),
                (
                    "department",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="DataManager.department",
                    ),
                ),
                (
                    "related_auth_account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="Auth.authuser"
                    ),
                ),
            ],
        ),
    ]