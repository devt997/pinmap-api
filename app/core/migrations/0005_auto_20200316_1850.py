# Generated by Django 3.0.4 on 2020-03-16 18:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20200316_0819'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pin',
            name='date',
            field=models.DateField(auto_now_add=True),
        ),
    ]
