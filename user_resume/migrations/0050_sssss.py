# Generated by Django 4.2.6 on 2024-01-02 12:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0052_remove_project_saved_by_users'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('user_resume', '0049_delete_sssss'),
    ]

    operations = [
        migrations.CreateModel(
            name='sssss',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('saved_time', models.DateTimeField(auto_now_add=True, verbose_name='Saved At')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='project.project')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='project_saved', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'User Project Saved',
                'verbose_name_plural': 'User Projects saved',
                'ordering': ['-saved_time'],
                'unique_together': {('user', 'project')},
            },
        ),
    ]