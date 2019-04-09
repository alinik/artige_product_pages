from django.contrib import admin

from sorl.thumbnail.admin import AdminImageMixin
# Register your models here.
from .models import Product, Pic, Tag


# @admin.register(Pic)
class PictureInline(AdminImageMixin,admin.TabularInline):
    model = Pic

class TagsInline(AdminImageMixin,admin.TabularInline):
    model = Tag


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    model = Product
    inlines = [PictureInline,TagsInline]
