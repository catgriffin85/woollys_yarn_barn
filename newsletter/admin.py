from django.contrib import admin
from .models import NewsletterSignup


@admin.register(NewsletterSignup)
class NewsletterSignupAdmin(admin.ModelAdmin):
    list_display = ('email', 'date_subscribed', 'unsubscribed',)
    search_fields = ('email',)
