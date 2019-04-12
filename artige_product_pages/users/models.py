from django.contrib.auth.models import AbstractUser
from django.db.models import *
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from phonenumber_field.formfields import PhoneNumberField

class User(AbstractUser):
    # First Name and Last Name do not cover name patterns
    # around the globe.
    name = CharField(_("Name of User"), blank=True, max_length=255)

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})


# class Company(Model):
#     owner = models.ForeignKey(User, on_delete=DO_NOTHING)
#     name = CharField(_('Name of Business'), max_length=255)
#     operators = models.ManyToManyField(User, related_name='operators')


class Account(Model):
    class Meta:
        abstract = True

    ENDPOINTS = ((0, 'artige'), (1, 'instagram'), (2, 'telegram'), (3, 'facebook'))
    endpoint = CharField('endpoint', max_length=10, blank=False, choices=ENDPOINTS)
    # company = models.ForeignKey(Company, on_delete=CASCADE)


class InstagramAccount(Account):
    insta_user = CharField('Instagram Username', max_length=100)
    insta_id = IntegerField('Instagram ID')

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.id:
            self.endpoint = 1
        super(InstagramAccount, self).save(force_insert, force_update, using, update_fields)

class TelegramAccount(Account):
    contact_mobile_number = PhoneNumberField(blank=True)
