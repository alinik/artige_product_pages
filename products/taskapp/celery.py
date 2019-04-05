import os

from celery import Celery
from django.apps import apps, AppConfig
from django.conf import settings

if not settings.configured:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")  # pragma: no cover

app = Celery("product")
app.config_from_object("django.conf:settings", namespace="CELERY")


import django
django.setup()

class CeleryAppConfig(AppConfig):
    name = "products.taskapp"
    verbose_name = "Celery Config"

    def ready(self):
        installed_apps = [app_config.name for app_config in apps.get_app_configs()]
        app.autodiscover_tasks(lambda: installed_apps, force=True)


#
from artige_product_pages.users.models import User
from products.models import Product


@app.task()
# @app.task(bind=True)
def get_product():
    print(f"we will get some products via Telegram bot")
    u = User.objects.get(pk=1)
    a = Product(owner=u, description='Test model')
    a.save()
    return True


# How to use:
"""
manage.py shell
from products.taskapp.celery import get_product
get_product.delay()
"""
