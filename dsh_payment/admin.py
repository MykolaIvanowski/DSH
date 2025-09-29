from django.contrib import admin
from .models import Order, OrderLog, OrderItem

# Register your models here.

admin.site.register(OrderItem)
admin.site.register(OrderLog)
admin.site.register(Order)

# Register your models here.
