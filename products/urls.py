from django.urls import path

from products.views import product_view,product_by_tag_view

app_name = "products"
urlpatterns = [
    path("", view=product_view, name="products_list"),
    path("<ownername>", view=product_view, name="owner_products_list"),
    path("tags/<tag>", view=product_by_tag_view, name="product_by_tag")
    ]
