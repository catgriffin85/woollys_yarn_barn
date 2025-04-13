from django.db import models


class NewsletterSignup(models.Model):
    email = models.EmailField()
    date_subscribed = models.DateTimeField(auto_now_add=True)
    unsubscribed = models.BooleanField(default=False)
    date_unsubscribed = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.email
