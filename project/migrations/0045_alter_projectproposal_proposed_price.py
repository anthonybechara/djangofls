# Generated by Django 4.2.6 on 2023-12-04 14:20

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0044_alter_projectfile_project'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectproposal',
            name='proposed_price',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(10)], verbose_name='Proposed Price'),
        ),
    ]