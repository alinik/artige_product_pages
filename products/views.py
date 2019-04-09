from django.shortcuts import render

# Create your views here.
from artige_product_pages.users.models import User
from products.models import Product, Tag


def product_view(request, ownername=None):
    products = {}
    context = {}
    if ownername is None:
        products = Product.objects.all()
        context = {'products': products}
    else:
        products = Product.objects.filter(owner_id=ownername)
        user = User.objects.filter(id=ownername)
        print(user)
        for x in user:
            print(x)
        context = {'products': products,'owner_profile':user}
    return render(request, 'pages/product.html', context)


def product_by_tag_view(request,tag):
    print(tag[1:])
    products= {}
    # tags = Tag.object.filter(word=tag[1:])
    products = Product.objects.filter(tags__word=tag)
    context = {'products': products}
    return render(request, 'pages/product.html', context)
