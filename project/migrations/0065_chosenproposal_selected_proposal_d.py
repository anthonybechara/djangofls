# Generated by Django 4.2.6 on 2024-01-16 12:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0064_dispute_opened_by_username'),
    ]

    operations = [
        migrations.AddField(
            model_name='chosenproposal',
            name='selected_proposal_d',
            field=models.CharField(blank=True, max_length=200, verbose_name='Selected Proposal'),
        ),
    ]
