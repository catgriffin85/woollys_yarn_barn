from django.urls import path
from .import views

urlpatterns = [
    path('faqs/', views.faq_view, name='faqs'),
    path('contact/', views.contact, name='contact'),
    path('contact/thank-you/', views.contact_thank_you,
         name='contact_thank_you'),
]
