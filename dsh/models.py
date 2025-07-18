from django.contrib.auth.models import AbstractUser, Permission, Group
from django.db import models


class User(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='dsh_user_permissions',
        blank=True
    )
    groups = models.ManyToManyField(
        Group,
        related_name='dsh_user_groups',
        blank=True
    )


    def __str__(self):
        return self.username


class Product(models.Model):
    name = models.CharField(max_length = 255)
    description = models.TextField()
    price = models.DecimalField(max_digits = 10, decimal_places=2)
    stock = models.PositiveIntegerField()
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS_CHOICES=[
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    order_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Order{self.id} by {self.user.username}'


