# Generated by Django 4.2.6 on 2023-11-10 20:17

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0004_chatroom_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatroom',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
