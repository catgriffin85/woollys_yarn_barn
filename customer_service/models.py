from django.db import models


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

