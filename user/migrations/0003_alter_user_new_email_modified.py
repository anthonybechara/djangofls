# Generated by Django 4.2.6 on 2023-11-01 15:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_remove_user_email_verified_user_new_email_modified'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='new_email_modified',
            field=models.DateTimeField(verbose_name='New Email Verification'),
        ),
    ]
