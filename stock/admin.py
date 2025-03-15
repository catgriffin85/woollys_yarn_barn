from django.contrib import admin
from .models import Stock, Category


class StockAdmin(admin.ModelAdmin):
    list_display = (
        'category',
        'sub_category',
        'sku',
        'name',
        'price',
        'rating',
        'image',
    )

    ordering = ('sku',)

class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'friendly_name',
        'category',
    )

admin.site.register(Stock, StockAdmin)
admin.site.register(Category, CategoryAdmin)