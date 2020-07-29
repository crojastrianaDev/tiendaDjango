from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
class Producto(models.Model):
    nombre = models.CharField(max_length=300)
    descripcion = models.CharField(max_length=300)
    precio = models.IntegerField()

    def __str__(self):
        return "producto: {} precio: $ {}".format(self.nombre, self.precio)

class Comentario(models.Model):
    comentario = models.CharField(max_length=300)
    usuario = models.CharField(max_length=300)
    fecha = models.DateTimeField(auto_now_add=True)
    producto = models.ForeignKey(Producto, related_name="producto_comentarios",on_delete=models.CASCADE)

    def __str__(self):
        return "{} {}".format(self.comentario, self.producto)


class ImagenesProducto(models.Model):
    descripcion = models.CharField(max_length=300)
    producto = models.ForeignKey(Producto, related_name="producto_imagenes",on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='imagenes_producto')

    def __str__(self):
        return "{}".format(self.descripcion)