# Generated by Django 4.2.6 on 2023-11-06 07:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0027_remove_chat_project'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectproposal',
            name='is_accepted',
            field=models.BooleanField(default=False),
        ),
    ]