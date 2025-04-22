from django.contrib import admin
from .models import Faq, Topic, Contact


class FaqAdmin(admin.ModelAdmin):
    list_display = (
        'topics',
        'question_id',
        'question',
        'answer',
        'views',
    )

    ordering = ('topics',)


class TopicAdmin(admin.ModelAdmin):
    list_display = (
        'friendly_name',
        'name',
    )

    ordering = ('friendly_name',)


class ContactAdmin(admin.ModelAdmin):
    list_display = (
        'contact_id',
        'full_name',
        'email',
        'topic',
        'created_on')
    search_fields = (
        'full_name',
        'email',
        'topic',
    )

    ordering = ('contact_id',)


admin.site.register(Faq, FaqAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Contact, ContactAdmin)
