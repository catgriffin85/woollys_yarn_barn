import uuid

from django.db import models
from django.db.models import Sum
from django.conf import settings

from stock.models import Stock
from profiles.models import UserProfile
from decimal import Decimal, ROUND_HALF_UP


class Order(models.Model):
    order_number = models.CharField(max_length=32, null=False, editable=False)
    user_profile = models.ForeignKey(UserProfile, on_delete=models.SET_NULL,
                                     null=True, blank=True, related_name='orders')
    full_name = models.CharField(max_length=50, null=False, blank=False)
    email = models.EmailField(max_length=254, null=False, blank=False)
    phone_number = models.CharField(max_length=20, null=False, blank=False)
    street_address1 = models.CharField(max_length=80, null=False, blank=False)
    town_or_city = models.CharField(max_length=40, null=False, blank=False)
    street_address2 = models.CharField(max_length=80, null=True, blank=True)
    county = models.CharField(max_length=80, null=True, blank=True)
    country = models.CharField(max_length=40, null=False, blank=False)
    postcode = models.CharField(max_length=20, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    delivery_cost = models.DecimalField(max_digits=6, decimal_places=2,
                                        null=False, default=0)
    order_total = models.DecimalField(max_digits=10, decimal_places=2,
                                      null=False, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2,
                                      null=False, default=0)
    original_cart = models.TextField(null=False, blank=False, default='')
    stripe_pid = models.CharField(max_length=254, null=False, blank=False,
                                  default='')
    email_sent = models.BooleanField(default=False)

    def _generate_order_number(self):
        """
        Generate a random, unique order number using UUID
        """
        return uuid.uuid4().hex[:8].upper()
    
    def update_total(self):
        self.order_total = self.lineitems.aggregate(Sum('lineitem_total'))['lineitem_total__sum'] or 0

        if self.order_total < settings.FREE_DELIVERY_THRESHOLD:
            raw_delivery = self.order_total * settings.STANDARD_DELIVERY_PERCENTAGE / 100
            self.delivery_cost = Decimal(raw_delivery).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        else:
            self.delivery_cost = Decimal('0.00')

        self.grand_total = (self.order_total + self.delivery_cost).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        self.save()

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the order number
        if it hasn't been set already.
        """
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number


STOCK_WEIGHT_CHOICES = [
    ("dk", "Double Knitting"),
    ("aran", "Aran"),
    ("chunky", "Chunky"),
    ("super_chunky", "Super Chunky"),
]

STOCK_COLOUR_CHOICES = [
    ("red", "Red"),
    ("pink", "Pink"),
    ("blue", "Blue"),
    ("green", "Green"),
    ("white", "White"),
    ("black", "Black"),
    ("grey", "Grey"),
    ("yellow", "Yellow"),
]

   
class OrderLineItem(models.Model):
    order = models.ForeignKey(Order, null=False, blank=False, on_delete=models.CASCADE, related_name='lineitems')
    stock = models.ForeignKey(Stock, null=False, blank=False, on_delete=models.CASCADE)
    stock_weight = models.CharField(max_length=20, choices=STOCK_WEIGHT_CHOICES, null=True, blank=True)
    stock_colour = models.CharField(max_length=20, choices=STOCK_COLOUR_CHOICES, null=True, blank=True)
    stock_size = models.JSONField(default=list, null=True, blank=True)
    quantity = models.IntegerField(null=False, blank=False, default=0)
    lineitem_total = models.DecimalField(max_digits=6, decimal_places=2, null=False, blank=False, editable=False)

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the lineitem total
        and update the order total.
        """
        self.lineitem_total = self.stock.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f'SKU {self.stock.sku} on order {self.order.order_number}'

