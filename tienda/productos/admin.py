from django.contrib import admin
from .models import Producto, Comentario

@admin.register(Producto,Comentario)
class AuthorAdmin(admin.ModelAdmin):
    pass