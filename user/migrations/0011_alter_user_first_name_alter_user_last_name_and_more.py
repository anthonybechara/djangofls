# Generated by Django 4.2.6 on 2023-12-11 12:14

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0010_alter_user_is_admin'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(max_length=30, validators=[django.core.validators.RegexValidator(message='Enter a valid name. This value may contain only letters and score (-).', regex="^[a-zA-Z'\\'\\- ]+$")], verbose_name='First name'),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_name',
            field=models.CharField(max_length=30, validators=[django.core.validators.RegexValidator(message='Enter a valid name. This value may contain only letters and score (-).', regex="^[a-zA-Z'\\'\\- ]+$")], verbose_name='Last name'),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=100, unique=True, validators=[django.core.validators.RegexValidator(message='Enter a valid username. This value may contain only letters, numbers, and (@ _ .) characters.', regex='^[\\w.@]+$')], verbose_name='Username'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='middle_name',
            field=models.CharField(blank=True, max_length=30, validators=[django.core.validators.RegexValidator(message='Enter a valid name. This value may contain only letters and score (-).', regex="^[a-zA-Z'\\'\\- ]+$")], verbose_name='Middle Name'),
        ),
    ]