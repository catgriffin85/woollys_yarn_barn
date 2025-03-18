from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):

    class Meta:
        verbose_name_plural = 'Categories'
        
    name = models.CharField(max_length=254, default='')
    friendly_name = models.CharField(max_length=254, null=True, blank=True)

    def __str__(self):
        return self.name

    def get_friendly_name(self):
        return self.friendly_name
    

class Stock(models.Model):

    class Meta:
        verbose_name_plural = 'Stock'

    category = models.ForeignKey('Category', null=True, blank=True, on_delete=models.SET_NULL)
    sku = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=200, blank=True)
    description = models.TextField()
    weight = models.JSONField(default=list, null=True, blank=True)
    colour = models.JSONField(default=list, null=True, blank=True)
    size = models.JSONField(default=list, null=True, blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    rating = models.IntegerField(validators=[MinValueValidator(1),
                                MaxValueValidator(5)])
    image = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.name

