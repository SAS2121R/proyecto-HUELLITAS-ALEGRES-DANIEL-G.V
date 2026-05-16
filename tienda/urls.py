from django.urls import path
from . import views

app_name = 'tienda'

urlpatterns = [
    path('', views.catalogo, name='catalogo'),
    path('producto/<int:pk>/', views.detalle_producto, name='detalle_producto'),
    path('agregar/<int:pk>/', views.agregar_carrito, name='agregar_carrito'),
    path('carrito/', views.carrito, name='carrito'),
    path('carrito/actualizar/<int:pk>/', views.actualizar_cantidad, name='actualizar_cantidad'),
    path('carrito/eliminar/<int:pk>/', views.eliminar_carrito, name='eliminar_carrito'),
    path('carrito/vaciar/', views.vaciar_carrito, name='vaciar_carrito'),
    path('checkout/', views.checkout, name='checkout'),
]