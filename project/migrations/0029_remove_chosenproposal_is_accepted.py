# Generated by Django 4.2.6 on 2023-11-06 07:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0028_projectproposal_is_accepted'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chosenproposal',
            name='is_accepted',
        ),
    ]
