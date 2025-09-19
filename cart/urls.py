from django.urls import path
from .import views

urlpatterns = [
    path('', views.cart_basic, name='cart'),
    path('add/', views.cart_add, name='cart_add'),
    path('delete/', views.cart_delete, name='cart_delete'),
    path('update/', views.cart_update, name='cart_update'),
    path('status/', views.cart_status, name='cart_status'),

]