# Generated by Django 4.2.6 on 2024-01-08 14:27

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('project', '0054_remove_project_saved_by_users'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='published_user',
            field=models.ForeignKey(null=True, on_delete=models.SET('sa'), related_name='user_projects', to=settings.AUTH_USER_MODEL),
        ),
    ]
