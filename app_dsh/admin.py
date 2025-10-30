from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product

# Register your models here.

admin.site.register(Category)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display =  ['name', 'image_preview', 'image_url']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" />', obj.image.url)
    image_preview.short_description = 'Preview'

    def image_url(self, obj):
        if obj.image:
            return format_html('<a href="{0}" target="_blank">{0}</a>', obj.image.url)

    image_url.short_description = 'Image url'