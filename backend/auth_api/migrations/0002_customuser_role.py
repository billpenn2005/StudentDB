# Generated by Django 5.1.3 on 2024-12-07 06:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("auth_api", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="customuser",
            name="role",
            field=models.CharField(
                choices=[
                    ("admin", "Admin"),
                    ("student", "Student"),
                    ("teacher", "Teacher"),
                ],
                default="student",
                max_length=10,
            ),
        ),
    ]
