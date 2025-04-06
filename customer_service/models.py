from django.db import models

import uuid


class Topic(models.Model):
        
    name = models.CharField(max_length=254, default='')
    friendly_name = models.CharField(max_length=254, null=True, blank=True)

    def __str__(self):
        return self.name

    def get_friendly_name(self):
        return self.friendly_name
    

class Faq(models.Model):

    topics = models.CharField(max_length=50, blank=True)
    question = models.CharField(max_length=200, blank=True)
    question_id = models.CharField(max_length=50, blank=True)
    answer = models.TextField()
    slug = models.SlugField(unique=True, blank=True)
    keywords = models.TextField(blank=True)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    views = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.question


class Contact(models.Model):

    TOPICS = [
        ('delivery', 'Delivery'),
        ('returns_refunds', 'Returns & Refunds'),
        ('order_issues', 'Help with my Order'),
        ('stock', 'Item or Stock Query'),
        ('payment_queries', 'Payments'),
    ]

    contact_id = models.CharField(max_length=32, null=False, editable=False)
    full_name = models.CharField(max_length=50, null=False, blank=False)
    email = models.EmailField(max_length=254, null=False, blank=False)
    topic = models.CharField(max_length=30, choices=TOPICS, default='delivery')
    customer_question = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    
    def _generate_contact_id(self):
        """
        Generate a random, unique contact ID number using UUID
        """
        return uuid.uuid4().hex.upper()
