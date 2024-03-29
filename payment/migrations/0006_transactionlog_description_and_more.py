# Generated by Django 4.2.6 on 2023-12-07 10:04

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0005_alter_transactionlog_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='transactionlog',
            name='description',
            field=models.CharField(default=django.utils.timezone.now, max_length=100, verbose_name='Description'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='transactionlog',
            name='transaction_type',
            field=models.CharField(choices=[('POINTS_SPENT', 'Points Spent'), ('POINTS_RECEIVED', 'Points Received'), ('SUPER_POINTS_SPENT', 'Super Points Spent'), ('SUPER_POINTS_RECEIVED', 'Super Points Received'), ('BIDS_SPENT', 'Bids Spent'), ('BIDS_RECEIVED', 'Bids Received')], max_length=25, verbose_name='Transaction Type'),
        ),
    ]
