from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'categories'


class Product(models.Model):
    name = models.CharField(max_length = 255)
    description = models.TextField()
    article = models.CharField(max_length=30, unique=True,blank=True,null=True)
    price = models.DecimalField(max_digits = 10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    is_sale = models.BooleanField(default=False)
    sale_price  = models.DecimalField(default=0, decimal_places=2, max_digits=6)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

    @property
    def has_image(self):
        return self.image and self.image.name and self.image.storage.exists(self.image.name)
