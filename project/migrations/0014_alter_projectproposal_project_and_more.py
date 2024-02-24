# Generated by Django 4.2.6 on 2023-11-03 11:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('project', '0013_alter_projectproposal_project_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectproposal',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='project_proposals', to='project.project'),
        ),
        migrations.AlterField(
            model_name='projectproposal',
            name='proposer',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='user_proposals', to=settings.AUTH_USER_MODEL),
        ),
    ]
