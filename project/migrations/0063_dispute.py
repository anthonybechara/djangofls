# Generated by Django 4.2.6 on 2024-01-14 18:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('project', '0062_alter_projectfile_project_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dispute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(verbose_name='Dispute Description')),
                ('opened_at', models.DateTimeField(auto_now_add=True, verbose_name='Opened At')),
                ('is_resolved', models.BooleanField(default=False, verbose_name='Resolved')),
                ('opened_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_disputes', to=settings.AUTH_USER_MODEL, verbose_name='Opened By')),
                ('proposal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='disputes', to='project.chosenproposal')),
            ],
            options={
                'verbose_name': 'Dispute',
                'verbose_name_plural': 'Disputes',
                'unique_together': {('proposal', 'opened_by')},
            },
        ),
    ]
