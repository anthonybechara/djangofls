# Generated by Django 4.2.6 on 2023-12-04 14:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0043_alter_chosenproposal_project_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectfile',
            name='project',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='project_files', to='project.project'),
        ),
    ]
