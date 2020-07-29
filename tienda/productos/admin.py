from django.contrib import admin
from .models import Producto

@admin.register(Producto)
class AuthorAdmin(admin.ModelAdmin):
    pass