# Generated by Django 4.2.6 on 2023-12-05 06:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0045_alter_projectproposal_proposed_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectproposal',
            name='project',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='project_proposals', to='project.project'),
        ),
    ]
