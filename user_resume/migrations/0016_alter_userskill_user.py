# Generated by Django 4.2.6 on 2023-11-27 09:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('user_resume', '0015_remove_userskill_skills_userskill_skills'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userskill',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]