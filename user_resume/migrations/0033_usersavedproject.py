# Generated by Django 4.2.6 on 2023-12-01 12:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0039_alter_project_max_price_alter_project_min_price'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('user_resume', '0032_delete_usersavedproject'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserSavedProject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('saved_time', models.DateTimeField(auto_now_add=True, verbose_name='Saved At')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='project.project')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='project_saved', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Project Saved',
                'verbose_name_plural': 'Projects saved',
            },
        ),
    ]
