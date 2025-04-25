from django.db import models
from cloudinary.models import CloudinaryField


class Category(models.Model):
    """
    A category that groups stock under a common theme.
    """
    class Meta:
        verbose_name_plural = 'Categories'

    name = models.CharField(max_length=254, default='')
    friendly_name = models.CharField(max_length=254, null=True, blank=True)

    def __str__(self):
        return self.name

    def get_friendly_name(self):
        """
        Return the friendly version of the category name.
        """
        return self.friendly_name


class Stock(models.Model):
    """
    A model to store individual stock items, including category,
    name, description, weight, colour, size, price and image.
    """
    class Meta:
        verbose_name_plural = 'Stock'

    category = models.ForeignKey('Category', null=True, blank=True,
                                 on_delete=models.SET_NULL)
    sku = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=200, blank=True)
    description = models.TextField()
    weight = models.JSONField(default=list, null=True, blank=True)
    colour = models.JSONField(default=list, null=True, blank=True)
    size = models.JSONField(default=list, null=True, blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = CloudinaryField(
        'image',
        default="https://res.cloudinary.com/dqgc8opao/image/upload/v1744536831/default_image_akymrn.jpg")

    def __str__(self):
        return self.name
