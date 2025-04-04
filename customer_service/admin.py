from django.contrib import admin
from .models import Faq, Topic


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


admin.site.register(Faq, FaqAdmin)
admin.site.register(Topic, TopicAdmin)
