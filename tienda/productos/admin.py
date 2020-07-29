from django.contrib import admin
from .models import Producto, Comentario, ImagenesProducto

@admin.register(Producto,Comentario,ImagenesProducto)
class AuthorAdmin(admin.ModelAdmin):
    pass