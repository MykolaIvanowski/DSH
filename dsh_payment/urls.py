from django.urls import path, include
from . import views

urlpatterns = [
    path('billing_info', views.billing_info, name='billing_info'),
    path('checkout', views.checkout, name='checkout'),
    path('delivered_dashboard', views.delivered_dash, name='delivered_dashboard'),
    path('no_delivered_dashboard', views.not_delivered_dash, name='no_delivered_dashboard'),
    path('orders/<int:pk>', views.orders, name='orders'),
    path('payment_failed', views.payment_failed, name='payment_failed'),
    path('payment_success', views.payment_success, name='payment_success'),
    path('process_order', views.process_order, name='process_order'),
    path('paypal/webhook/', views.paypal_webhook, name='paypal_webhook'),
]