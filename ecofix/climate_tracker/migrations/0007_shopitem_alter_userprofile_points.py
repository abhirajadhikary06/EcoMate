# Generated by Django 5.1.4 on 2025-02-27 18:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('climate_tracker', '0006_userprofile_points_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShopItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('shaker_black', 'Gym Shaker (Black)'), ('tshirt_black', 'T-Shirt (Black)'), ('tshirt_white', 'T-Shirt (White)'), ('bag', 'Bag'), ('sticker', 'Sticker')], max_length=50, unique=True)),
                ('points_cost', models.PositiveIntegerField()),
            ],
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='points',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
