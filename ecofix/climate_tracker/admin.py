# admin.py
from django.contrib import admin
from .models import UserProfile, ShopItem

admin.site.register(UserProfile)
admin.site.register(ShopItem)
