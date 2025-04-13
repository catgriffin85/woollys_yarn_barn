from django.db import models


class Topic(models.Model):
        
    name = models.CharField(max_length=254, default='')
    friendly_name = models.CharField(max_length=254, null=True, blank=True)

    def __str__(self):
        return self.name

    def get_friendly_name(self):
        return self.friendly_name


class Faq(models.Model):

    topics = models.CharField(max_length=100, blank=True)
    question = models.CharField(max_length=250, blank=True)
    question_id = models.CharField(max_length=100, blank=True)
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

    def save(self, *args, **kwargs):
        if not self.contact_id:
            last_contact = Contact.objects.exclude(contact_id='').order_by('-id').first()
            if not last_contact or not last_contact.contact_id[1:].isdigit():
                new_id = 'C0001'
            else:
                last_id = int(last_contact.contact_id[1:])
                new_id = f'C{last_id + 1:04d}'
            self.contact_id = new_id
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.full_name} - {self.contact_id}"
