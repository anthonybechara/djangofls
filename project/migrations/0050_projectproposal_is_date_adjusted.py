# Generated by Django 4.2.6 on 2023-12-07 14:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0049_projectproposal_is_price_adjusted'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectproposal',
            name='is_date_adjusted',
            field=models.BooleanField(default=False, verbose_name='Adjust Date'),
        ),
    ]
