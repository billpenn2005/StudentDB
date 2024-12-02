# Generated by Django 5.1.3 on 2024-12-02 13:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("DataManager", "0006_section_course_studenttake_student_courses_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="TimeSlot",
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
                    "slot",
                    models.CharField(
                        choices=[
                            ("0", "8:00-10:00"),
                            ("1", "10:10-12:00"),
                            ("2", "14:00-15:50"),
                            ("3", "16:10-18:00"),
                            ("4", "19:00-20:50"),
                        ],
                        max_length=8,
                        unique=True,
                    ),
                ),
                ("day", models.IntegerField(verbose_name="day")),
            ],
        ),
        migrations.CreateModel(
            name="CourseTimeSlot",
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
                    "course",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="DataManager.course",
                    ),
                ),
                (
                    "time_slot",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="DataManager.timeslot",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="course",
            name="timeslots",
            field=models.ManyToManyField(
                through="DataManager.CourseTimeSlot", to="DataManager.timeslot"
            ),
        ),
    ]
