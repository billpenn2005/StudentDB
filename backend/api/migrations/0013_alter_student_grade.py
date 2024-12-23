# Generated by Django 5.1.4 on 2024-12-21 08:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0012_semester_punishmentrecord_rewardrecord_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="student",
            name="grade",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="students",
                to="api.grade",
            ),
        ),
    ]