# Generated by Django 4.2.6 on 2023-11-27 09:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('education', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='skill',
            name='description',
        ),
        migrations.AlterField(
            model_name='degree',
            name='name',
            field=models.CharField(max_length=100, unique=True, verbose_name='Degree'),
        ),
        migrations.AlterField(
            model_name='major',
            name='name',
            field=models.CharField(max_length=100, unique=True, verbose_name='Major'),
        ),
        migrations.AlterField(
            model_name='skill',
            name='name',
            field=models.CharField(max_length=100, unique=True, verbose_name='Skill'),
        ),
        migrations.AlterField(
            model_name='university',
            name='name',
            field=models.CharField(max_length=100, unique=True, verbose_name='University'),
        ),
    ]
