# Generated by Django 4.2.6 on 2023-12-14 13:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0022_alter_user_email_base32_alter_user_otp_base32'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='otp_auth_url',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
