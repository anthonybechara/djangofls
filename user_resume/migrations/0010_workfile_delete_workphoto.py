# Generated by Django 4.2.6 on 2023-11-24 09:42

from django.db import migrations, models
import django.db.models.deletion
import user_resume.models


class Migration(migrations.Migration):

    dependencies = [
        ('user_resume', '0009_alter_userpreviouswork_work_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to=user_resume.models.PortfolioFile.portfolio_file_upload_path)),
                ('previous_work', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='photos', to='user_resume.userpreviouswork')),
            ],
        ),
        migrations.DeleteModel(
            name='WorkPhoto',
        ),
    ]
