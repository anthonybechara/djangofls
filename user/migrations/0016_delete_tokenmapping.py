# Generated by Django 4.2.6 on 2023-12-12 13:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0015_tokenmapping'),
    ]

    operations = [
        migrations.DeleteModel(
            name='TokenMapping',
        ),
    ]