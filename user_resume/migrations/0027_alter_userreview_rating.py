# Generated by Django 4.2.6 on 2023-11-28 12:16

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_resume', '0026_rename_title_userreview_reviewed_user_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userreview',
            name='rating',
            field=models.DecimalField(decimal_places=1, max_digits=2, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)], verbose_name='Rating'),
        ),
    ]