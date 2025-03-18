from django.urls import path
from .import views

urlpatterns = [
    path('', views.shop_all, name='stock'),
    path('<stock_id>', views.stock_detail, name='stock_detail'),
]
