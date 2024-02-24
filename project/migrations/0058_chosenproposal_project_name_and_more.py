# Generated by Django 4.2.6 on 2024-01-08 14:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0057_projectproposal_proposer_username'),
    ]

    operations = [
        migrations.AddField(
            model_name='chosenproposal',
            name='project_name',
            field=models.CharField(blank=True, max_length=200, verbose_name='Project Name'),
        ),
        migrations.AddField(
            model_name='chosenproposal',
            name='selected_proposal_name',
            field=models.CharField(blank=True, max_length=200, verbose_name='Selected Proposal Name'),
        ),
    ]
