# Generated by Django 5.1.4 on 2024-12-17 04:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0003_remove_courseinstance_day_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="CourseSchedule",
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
                    "day",
                    models.CharField(
                        choices=[
                            ("Monday", "星期一"),
                            ("Tuesday", "星期二"),
                            ("Wednesday", "星期三"),
                            ("Thursday", "星期四"),
                            ("Friday", "星期五"),
                        ],
                        max_length=10,
                    ),
                ),
                (
                    "period",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (1, "第一节"),
                            (2, "第二节"),
                            (3, "第三节"),
                            (4, "第四节"),
                            (5, "第五节"),
                        ]
                    ),
                ),
                (
                    "course_instance",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="schedules",
                        to="api.courseinstance",
                    ),
                ),
            ],
            options={
                "unique_together": {("course_instance", "day", "period")},
            },
        ),
    ]
