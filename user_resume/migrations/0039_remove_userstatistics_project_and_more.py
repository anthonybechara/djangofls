# Generated by Django 4.2.6 on 2023-12-04 10:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_resume', '0038_userstatistics'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userstatistics',
            name='project',
        ),
        migrations.RemoveField(
            model_name='userstatistics',
            name='proposals',
        ),
    ]
