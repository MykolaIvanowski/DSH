from django.db import models
from django.utils.translation.template import blankout


# Create your models here.
class Keyword(models.Model):
    keyword_id = models.IntegerField(blank=True, null=True)
    keyword = models.TextField(blank=True, null=True)
    category_id = models.IntegerField(blank=True, null=True)


class Category(models.Model):
    category_id = models.IntegerField(blank=True, null=True)
    category_name = models.TextField(blank=True, null=True)
    parent_category_id = models.IntegerField(blank=True, null=True)


class Product(models.Model):
    product_id = models.IntegerField(blank=True, null=True)
    category_id = models.IntegerField(blank=True, null=True)
    product_title = models.TextField(blank=True, null=True)
    product_description = models.TextField(blank=True, null=True)
    image = models.ImageField()
    product_price = models.FloatField(blank=True, null=True)
    is_active = models.BooleanField(default=True)


#  i gues it is should be many to many)))
class Order(models.Model):
    order_id = models.IntegerField(blank=True, null=True)
    product_ids = models.IntegerField(blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)


class Delivery(models.Model):
    delivery_id = models.IntegerField(blank=True, null=True)
    delivery_name = models.TextField(blank=True, null=True)


class User(models.Model):
    name = models.CharField(blank=True, null=True)
    lastname = models.CharField(blank=True, null=True)
