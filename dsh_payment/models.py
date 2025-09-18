from datetime import datetime

from django.db import models
from django.contrib.auth.models import User
from app_dsh.models import Product
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

# Create your models here.

class DeliveryAddress(models.Model):
    user =models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    delivery_full_name = models.CharField(max_length=100)
    delivery_email = models.CharField(max_length=100)
    delivery_address1 = models.CharField(max_length=255)
    delivery_address2 = models.CharField(max_length=255, null=True,blank=True)
    delivery_city = models.CharField(max_length=255)
    delivery_state = models.CharField(max_length=255, null=True, blank=True)
    delivery_code = models.CharField(max_length=255, null=True,blank=True)
    delivery_country = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = 'Delivery address'

    def __str__(self):
        return f'Delivery address - {str(self.id)}'

def create_delivery(sender, instance, created, **kwargs):
    if created:
        user_delivery = DeliveryAddress(user=instance)
        user_delivery.save()

post_save.connect(create_delivery, sender=User)

class Order(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    delivering_address = models.CharField(max_length=1000)
    amount_paid = models.DecimalField(max_digits=7, decimal_places=2)
    date_ordered =models.DateTimeField(auto_now_add=True)
    delivered =models.BooleanField(default=False)
    date_delivered = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f'Order - {str(self.id)}'

@receiver(pre_save, sender=Order)
def set_delivery_date_on_update(sender, instance,**kwargs):
    if instance.pk:
        time_now = datetime.now()
        obj  = sender._default_manager.get(pk=instance.pk)
        if instance.delivered and not obj.delivered:
            instance.date_delivered = time_now

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete= models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=7, decimal_places=2)

    def __str__(self):
        return f'Order item - {str(self.id)}'