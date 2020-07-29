from django.contrib.auth.models import AbstractUser
from django.db.models import CharField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Default user for tienda.
    """

    #: First and last name do not cover name patterns around the globe
    telefono = CharField("telefono",blank=True, max_length=255)


    
