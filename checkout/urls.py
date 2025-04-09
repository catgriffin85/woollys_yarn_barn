from django.urls import path
from .import views

urlpatterns = [
    path('', views.checkout, name='checkout'),
    path('checkout/complete/<order_number>/', views.order_complete, name='order_complete'),

]
