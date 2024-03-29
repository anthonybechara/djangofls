# Generated by Django 4.2.6 on 2023-11-03 11:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0011_chosenproposal_chosen_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chosenproposal',
            name='selected_proposal',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='selected_for_project', to='project.projectproposal'),
        ),
    ]
