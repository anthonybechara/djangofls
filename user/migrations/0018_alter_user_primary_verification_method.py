# Generated by Django 4.2.6 on 2023-12-14 08:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0017_user_email_verification_enabled_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='primary_verification_method',
            field=models.CharField(choices=[('EMAIL', 'Email'), ('OTP', 'One-Time Password')], default=None, max_length=10, verbose_name='Verification Method'),
        ),
    ]