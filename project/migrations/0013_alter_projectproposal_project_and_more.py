# Generated by Django 4.2.6 on 2023-11-03 11:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0012_alter_chosenproposal_selected_proposal'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectproposal',
            name='project',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='project_proposal', to='project.project'),
        ),
        migrations.AlterField(
            model_name='projectproposal',
            name='submission_date',
            field=models.DateField(verbose_name='Submission Date'),
        ),
    ]