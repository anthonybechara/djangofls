# Generated by Django 4.2.6 on 2023-11-08 10:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0034_delete_projectcommunication'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('in_progress', 'In Progress'), ('completed', 'Completed'), ('canceled', 'Canceled'), ('expired', 'Expired')], default='active', max_length=20, verbose_name='Project Status'),
        ),
    ]
