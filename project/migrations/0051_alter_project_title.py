# Generated by Django 4.2.6 on 2023-12-11 12:14

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0050_projectproposal_is_date_adjusted'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='title',
            field=models.CharField(max_length=200, validators=[django.core.validators.RegexValidator(code='invalid_title', message='Only characters, numbers and spaces are allowed.', regex='^[A-Za-z0-9\\s]*$')], verbose_name='Project Title'),
        ),
    ]
