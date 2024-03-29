# Generated by Django 4.2.6 on 2023-11-03 11:49

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0015_alter_projectproposal_proposer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='max_price',
            field=models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(10.0)], verbose_name='Maximum Price'),
        ),
        migrations.AlterField(
            model_name='project',
            name='min_price',
            field=models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(5.0)], verbose_name='Minimum Price'),
        ),
        migrations.AlterField(
            model_name='projectproposal',
            name='proposed_price',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True, validators=[django.core.validators.MinValueValidator(5.0)], verbose_name='Proposed Price'),
        ),
    ]
