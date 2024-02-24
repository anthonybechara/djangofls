# Generated by Django 4.2.6 on 2023-12-05 10:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('payment', '0002_alter_bid_user_alter_point_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='point',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='points', to=settings.AUTH_USER_MODEL),
        ),
    ]
