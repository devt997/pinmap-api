# Generated by Django 3.0.4 on 2020-03-16 08:19

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_pin'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pin',
            name='created_at',
        ),
        migrations.AddField(
            model_name='pin',
            name='date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
