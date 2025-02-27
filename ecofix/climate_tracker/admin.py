from django.contrib import admin
from .models import ShopItem

class ShopItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'points_required')
    readonly_fields = ('name', 'description', 'points_required')  # Make fields read-only

admin.site.register(ShopItem, ShopItemAdmin)