from django.urls import path
from .views import (
    lista_productos, create_product, edit_product, delete_product,
    entrada_inventario, kardex_producto, alertas_stock, inicio,
)

app_name = 'productos'

urlpatterns = [
    path('', lista_productos, name='lista'),
    path('nuevo/', create_product, name='nuevo'),
    path('editar/<int:pk>/', edit_product, name='editar'),
    path('eliminar/<int:pk>/', delete_product, name='eliminar'),
    path('entrada/', entrada_inventario, name='entrada'),
    path('kardex/<int:pk>/', kardex_producto, name='kardex'),
    path('alertas/', alertas_stock, name='alertas'),
]