from django.contrib import admin
from .models import NewsletterSignup


class NewsletterAdmin(admin.ModelAdmin):
    list_display = (
        'email',
        'date_subscribed',
    )

admin.site.register(NewsletterSignup, NewsletterAdmin)
