from django.contrib import admin
from .models import Producto, MovimientoInventario


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'precio', 'cantidad_stock', 'stock_minimo', 'estado_stock', 'esta_activo')
    list_filter = ('categoria', 'esta_activo')
    search_fields = ('nombre', 'proveedor')
    readonly_fields = ('estado_stock', 'fecha_creacion', 'fecha_ultima_modificacion')
    list_editable = ('esta_activo',)
    ordering = ('nombre',)

    def estado_stock(self, obj):
        return obj.estado_stock
    estado_stock.short_description = 'Estado Stock'


@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = ('producto', 'tipo_movimiento', 'cantidad', 'fecha', 'usuario', 'motivo')
    list_filter = ('tipo_movimiento', 'producto__categoria')
    search_fields = ('producto__nombre', 'motivo')
    readonly_fields = ('fecha',)
    ordering = ('-fecha',)
    raw_id_fields = ('producto', 'historial_clinico')