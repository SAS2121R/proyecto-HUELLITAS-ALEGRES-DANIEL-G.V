from django.contrib import admin
from .models import Proveedor


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'nit', 'telefono', 'email', 'esta_activo')
    list_filter = ('esta_activo',)
    search_fields = ('nombre', 'nit')