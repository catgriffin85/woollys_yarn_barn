from django.urls import path
from .import views

urlpatterns = [
    path('', views.checkout, name='checkout'),
    path('order_complete/<order_number>/', views.order_complete, name='order_complete'),
]
