from django.contrib import admin
from .models import Order, OrderLineItem


class OrderLineItemInline(admin.TabularInline):
    model = OrderLineItem
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    inlines = (OrderLineItemInline,)

    readonly_fields = ('order_number', 'order_total', 'delivery_cost', 'grand_total', 'date',)
    fields = ('full_name', 'email', 'phone_number', 'country', 'postcode',
              'town_or_city', 'street_address1', 'street_address2',
              'county', 'order_number', 'order_total', 'delivery_cost',
              'grand_total', 'date',)

    list_display = ('order_number', 'full_name', 'date', 'order_total', 'delivery_cost', 
                    'grand_total',)

    ordering = ('-date',)


admin.site.register(Order, OrderAdmin)