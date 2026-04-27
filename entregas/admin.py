from django.contrib import admin
from .models import Pedido, PedidoItem


class PedidoItemInline(admin.TabularInline):
    model = PedidoItem
    extra = 1


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ['id', 'cliente', 'domiciliario', 'estado', 'direccion_entrega', 'fecha_creacion']
    list_filter = ['estado', 'fecha_creacion']
    search_fields = ['direccion_entrega', 'telefono_contacto']
    inlines = [PedidoItemInline]
    readonly_fields = ['fecha_creacion', 'fecha_entrega']