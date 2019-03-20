from django.contrib import admin

from sorl.thumbnail.admin import AdminImageMixin
# Register your models here.
from .models import Product, Pic


# @admin.register(Pic)
class PictureInline(AdminImageMixin,admin.TabularInline):
    model = Pic


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    model = Product
    inlines = [PictureInline,]
