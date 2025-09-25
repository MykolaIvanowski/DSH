from django.core.exceptions import ValidationError
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator, EmailValidator
from app_dsh.models import Product


STATUS_CHOICES = [
    ('created', 'Created'),
    ('approved', 'Approved'),
    ('shipped', 'Shipped'),
    ('delivered', 'Delivered'),
]


class Order(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, validators=[EmailValidator()])
    phone = models.CharField(
        max_length=20,
        validators=[RegexValidator(r'^\+?[0-9\s\-()]+$', message='Invalid phone number')]
    )

    amount_paid = models.DecimalField(max_digits=7, decimal_places=2)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='created')

    date_ordered = models.DateTimeField(auto_now_add=True)
    date_delivered = models.DateTimeField(blank=True, null=True)

    delivery_street_home = models.CharField(max_length=255)
    delivery_city = models.CharField(max_length=255)
    delivery_state = models.CharField(max_length=255, blank=True, null=True)
    delivery_code = models.CharField(max_length=255, blank=True, null=True)
    delivery_country = models.CharField(max_length=100)

    class Meta:
        ordering = ['-date_ordered']

    def __str__(self):
        return f'Order #{self.id}'

    def mark_as_delivered(self):
        if self.status != 'delivered':
            self.status = 'delivered'
            self.date_delivered = timezone.now()
            self.save()
            OrderLog.objects.create(order=self, status='delivered', note='Delivered manually')

@receiver(pre_save, sender=Order)
def set_delivery_date_on_update(sender, instance,**kwargs):
    if instance.pk:
        time_now = timezone.now()
        obj  = sender._default_manager.get(pk=instance.pk)
        if instance.delivered and not obj.delivered:
            instance.date_delivered = time_now

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=7, decimal_places=2)

    def __str__(self):
        return f'OrderItem #{self.id} ({self.product.name})'

    def clean(self):
        if self.product and self.product.stock < self.quantity:
            raise ValidationError(f"Not enough products: {self.product.name}")


class OrderLog(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='logs')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    status_time = models.DateTimeField(auto_now=True)
    note = models.TextField(blank=True)

    def __str__(self):
        return f'Log #{self.id} for Order #{self.order.id}'

@receiver(post_save, sender=Order)
def log_order_created(sender, instance, created, **kwargs):
    if created:
        OrderLog.objects.create(order=instance, status='created', note='Order created')
