from django.urls import path
from .import views

urlpatterns = [
    path('newsletter/signup/', views.newsletter_signup, name='newsletter_signup'),
    path('newsletter/unsubscribe/', views.newsletter_unsubscribe, name='newsletter_unsubscribe'),
]
