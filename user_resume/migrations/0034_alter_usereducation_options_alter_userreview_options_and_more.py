# Generated by Django 4.2.6 on 2023-12-01 12:48

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('project', '0039_alter_project_max_price_alter_project_min_price'),
        ('user_resume', '0033_usersavedproject'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='usereducation',
            options={'ordering': ['-start_date'], 'verbose_name': 'User Education', 'verbose_name_plural': 'User Educations'},
        ),
        migrations.AlterModelOptions(
            name='userreview',
            options={'ordering': ['-created_at'], 'verbose_name': 'User Review', 'verbose_name_plural': 'User Reviews'},
        ),
        migrations.AlterModelOptions(
            name='usersavedproject',
            options={'ordering': ['-saved_time'], 'verbose_name': 'Project Saved', 'verbose_name_plural': 'Projects saved'},
        ),
        migrations.AlterUniqueTogether(
            name='usersavedproject',
            unique_together={('user', 'project')},
        ),
    ]
