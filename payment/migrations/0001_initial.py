# Generated by Django 4.2.6 on 2023-12-05 10:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Point',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('balance', models.IntegerField(default=0, verbose_name='Balance')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='points', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Point',
                'verbose_name_plural': 'Points',
            },
        ),
        migrations.CreateModel(
            name='Bid',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('no_bid', models.IntegerField(default=5, verbose_name='Number of Bids')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bids', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Bid',
                'verbose_name_plural': 'Bids',
            },
        ),
    ]
