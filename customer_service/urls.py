from django.urls import path
from .import views

urlpatterns = [
    path('faqs/', views.faq_view, name='faqs'),
    path('contact/', views.contact, name='contact'),
    path('faq/thank-you/', views.faq_thank_you, name='faq_thank_you'),
]
