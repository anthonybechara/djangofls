# Generated by Django 4.2.6 on 2023-11-02 10:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('project', '0005_multipleupload_remove_project_file_project_files'),
    ]

    operations = [
        migrations.AddField(
            model_name='multipleupload',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='user_files', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]