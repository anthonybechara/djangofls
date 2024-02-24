# Generated by Django 4.2.6 on 2023-11-03 12:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0019_alter_chosenproposal_project_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chosenproposal',
            name='project',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='project.project'),
        ),
        migrations.AlterField(
            model_name='chosenproposal',
            name='selected_proposal',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='selected_projects', to='project.projectproposal'),
        ),
    ]
