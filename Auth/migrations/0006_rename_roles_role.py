# Generated by Django 5.1.3 on 2024-12-02 10:49

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("Auth", "0005_roles_authuser_role"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Roles",
            new_name="Role",
        ),
    ]
