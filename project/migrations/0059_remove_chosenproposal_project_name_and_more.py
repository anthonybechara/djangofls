# Generated by Django 4.2.6 on 2024-01-08 14:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0058_chosenproposal_project_name_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chosenproposal',
            name='project_name',
        ),
        migrations.RemoveField(
            model_name='chosenproposal',
            name='selected_proposal_name',
        ),
    ]