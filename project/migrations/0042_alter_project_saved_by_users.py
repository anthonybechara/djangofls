# Generated by Django 4.2.6 on 2023-12-04 11:17

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('project', '0041_alter_project_saved_by_users'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='saved_by_users',
            field=models.ManyToManyField(blank=True, related_name='user_saved_projects', to=settings.AUTH_USER_MODEL),
        ),
    ]
