from django.db import models


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
    product_name = models.TextField(blank=True, null=True)
    product_description = models.TextField(blank=True, null=True)
    product_foto = models.TextField(blank=True, null=True)
    product_price = models.FloatField(blank=True, null=True)


#  i gues it is should be many to many)))
class Order(models.Model):
    order_id = models.IntegerField(blank=True, null=True)
    product_ids = models.IntegerField(blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)


class Delivery(models.Model):
    delivery_id = models.IntegerField(blank=True, null=True)
    delivery_name = models.TextField(blank=True, null=True)