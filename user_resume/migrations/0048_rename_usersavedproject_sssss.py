# Generated by Django 4.2.6 on 2024-01-02 12:28

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('project', '0052_remove_project_saved_by_users'),
        ('user_resume', '0047_alter_usersavedproject_table'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='UserSavedProject',
            new_name='sssss',
        ),
    ]
