# Generated by Django 4.2.6 on 2024-01-02 12:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_resume', '0045_alter_userexperience_options_and_more'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='usersavedproject',
            table='user_resume_usersavedproject',
        ),
    ]
