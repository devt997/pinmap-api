# Generated by Django 3.0.4 on 2020-03-20 17:30

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20200316_1850'),
    ]

    operations = [
        migrations.AddField(
            model_name='pin',
            name='image',
            field=models.ImageField(null=True, upload_to=core.models.recipe_image_file_path),
        ),
    ]