from tkinter.font import names

from django.urls import path, include
from . import views

urlpatterns = [
    path('checkout', views.checkout, name='checkout'),
    path('delivered_dashboard', views.delivered_dash, name='delivered_dashboard'),
    path('no_delivered_dashboard', views.not_delivered_dash, name='no_delivered_dashboard'),
    path('orders/<int:pk>', views.orders, name='orders'),
    path('payment_failed', views.payment_failed, name='payment_failed'),
    path('payment_success', views.payment_success, name='payment_success'),
    path('paypal/webhook/', views.paypal_webhook, name='paypal_webhook'),
    path('dashboard', views.order_dashboard_view, name='dashboard'),
    path('order_items/<int:item_id>/', views.order_item_view, name='order_item'),
    path('delivery_info/', views.delivery_info_view, name='delivery_info')
]