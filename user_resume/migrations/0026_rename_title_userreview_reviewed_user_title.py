# Generated by Django 4.2.6 on 2023-11-28 11:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_resume', '0025_userreview_title'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userreview',
            old_name='title',
            new_name='reviewed_user_title',
        ),
    ]