# Generated by Django 5.1.4 on 2024-12-10 06:28

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Class",
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
                ("name", models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name="Department",
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
                ("name", models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name="ClassInstance",
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
                    "selected_students",
                    models.ManyToManyField(
                        blank=True,
                        related_name="class_selected_courses",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="CoursePrototype",
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
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField()),
                (
                    "department",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="course_prototypes",
                        to="api.department",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Grade",
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
                ("name", models.CharField(max_length=20)),
                (
                    "department",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="grades",
                        to="api.department",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="CourseInstance",
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
                ("semester", models.CharField(max_length=20)),
                ("location", models.CharField(max_length=100)),
                ("capacity", models.PositiveIntegerField()),
                ("selection_deadline", models.DateTimeField()),
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
                ("is_finalized", models.BooleanField(default=False)),
                (
                    "eligible_classes",
                    models.ManyToManyField(
                        related_name="eligible_course_instances", to="api.class"
                    ),
                ),
                (
                    "selected_students",
                    models.ManyToManyField(
                        blank=True,
                        related_name="course_selected_courses",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "course_prototype",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="instances",
                        to="api.courseprototype",
                    ),
                ),
                (
                    "department",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="course_instances",
                        to="api.department",
                    ),
                ),
                (
                    "eligible_departments",
                    models.ManyToManyField(
                        related_name="eligible_course_instances", to="api.department"
                    ),
                ),
                (
                    "eligible_grades",
                    models.ManyToManyField(
                        related_name="eligible_course_instances", to="api.grade"
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="class",
            name="grade",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="classes",
                to="api.grade",
            ),
        ),
        migrations.CreateModel(
            name="Student",
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
                ("age", models.PositiveIntegerField()),
                (
                    "gender",
                    models.CharField(
                        choices=[("M", "Male"), ("F", "Female"), ("O", "Other")],
                        max_length=1,
                    ),
                ),
                ("id_number", models.CharField(max_length=18, unique=True)),
                (
                    "department",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="students",
                        to="api.department",
                    ),
                ),
                (
                    "student_class",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="students",
                        to="api.class",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="student_profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
