# Generated by Django 4.2.6 on 2023-11-06 07:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0026_remove_chat_participants_chat_participants'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chat',
            name='project',
        ),
    ]
