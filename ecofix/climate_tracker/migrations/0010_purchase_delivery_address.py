# Generated by Django 5.1.4 on 2025-02-27 20:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('climate_tracker', '0009_shopitem_description_shopitem_image_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchase',
            name='delivery_address',
            field=models.TextField(blank=True, null=True),
        ),
    ]
