# Generated by Django 4.2.6 on 2023-12-01 10:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0037_alter_chosenproposal_options_alter_project_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='max_price',
            field=models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Maximum Price'),
        ),
    ]
