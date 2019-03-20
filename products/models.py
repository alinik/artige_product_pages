from django.db.models import *
from sorl.thumbnail import ImageField

# Create your models here.
from artige_product_pages.users.models import User
from config.settings.base import MEDIA_ROOT


class Product(Model):
    owner = ForeignKey(User, on_delete=CASCADE)
    description = CharField(max_length=1024)
    created_date = DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.owner.name}- Product [{self.description[:20]}] ({self.images.count()})'


class Pic(Model):
    product = ForeignKey(Product, on_delete=CASCADE, related_name='images')
    image = ImageField(upload_to='media')

    def __str__(self):
        return f'Image of {self.product}'
