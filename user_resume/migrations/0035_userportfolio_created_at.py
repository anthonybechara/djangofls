# Generated by Django 4.2.6 on 2023-12-03 22:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_resume', '0034_alter_usereducation_options_alter_userreview_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userportfolio',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Created At'),
            preserve_default=False,
        ),
    ]
