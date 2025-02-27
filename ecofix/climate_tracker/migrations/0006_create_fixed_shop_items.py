from django.db import migrations

def create_fixed_shop_items(apps, schema_editor):
    ShopItem = climate_tracker.get_model('climate_tracker', 'ShopItem')  # Replace 'climate_tracker' with your app name
    ShopItem.objects.bulk_create([
        ShopItem(name="Gym Shaker (Black)", description="Durable gym shaker bottle in black.", points_required=50),
        ShopItem(name="T-Shirt (Black)", description="Comfortable black T-shirt made from eco-friendly materials.", points_required=100),
        ShopItem(name="T-Shirt (White)", description="Comfortable white T-shirt made from eco-friendly materials.", points_required=100),
        ShopItem(name="Bag", description="Reusable tote bag for shopping or daily use.", points_required=75),
        ShopItem(name="Sticker", description="Cool eco-themed sticker for your devices.", points_required=25),
    ])

class Migration(migrations.Migration):
    dependencies = [
        ('climate_tracker', '0005_environmentalobservation_latitude_and_more'),  # Replace 'climate_tracker' with your app name
    ]

    operations = [
        migrations.RunPython(create_fixed_shop_items),
    ]