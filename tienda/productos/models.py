from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
class Producto(models.Model):
    nombre = models.CharField(max_length=300)
    descripcion = models.CharField(max_length=300)
    precio = models.IntegerField()

    def __str__(self):
        return "producto: {} precio: $ {}".format(self.nombre, self.precio)