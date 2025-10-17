from django.urls import path
from . import views

urlpatterns = [
    path('checkout', views.checkout, name='checkout'),
    path('payment_failed', views.payment_failed, name='payment_failed'),
    path('payment_success', views.payment_success, name='payment_success'),
    path('paypal/webhook/', views.paypal_webhook, name='paypal_webhook'),
    path('dashboard', views.order_dashboard_view, name='dashboard'),
    path('order_items/<int:item_id>/', views.order_item_view, name='order_item'),
    path('delivery_info/', views.delivery_info_view, name='delivery_info'),
    path('order_success/', views.order_success_view, name='order_success'),
    path('payment/<int:order_id>', views.payment_paypal_view, name = 'payment_view')
]