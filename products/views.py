from django.shortcuts import render

# Create your views here.
from artige_product_pages.users.models import User
from products.models import Product, Tag


def product_view(request, ownername=None,product=None):
    print("==================================")
    print(ownername)
    print(product)
    print("==================================")
    products = {}
    context = {}
    if ownername is None:
        products = Product.objects.all()
        context = {'products': products}
    else:
        if product is None:
            products = Product.objects.filter(owner_id=ownername)
            user = User.objects.filter(id=ownername)
            context = {'products': products,'owner_profile':user[0]}
        else:
            products = Product.objects.filter(owner_id=ownername,product_id=product)
            user = User.objects.filter(id=ownername)
            context = {'products': products,'owner_profile':user[0]}
    return render(request, 'pages/product.html', context)


def product_by_tag_view(request,tag):
    print(tag[1:])
    products= {}
    # tags = Tag.object.filter(word=tag[1:])
    products = Product.objects.filter(tags__word=tag)
    context = {'products': products}
    return render(request, 'pages/product.html', context)
