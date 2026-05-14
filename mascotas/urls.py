from django.urls import path
from .views import lista_mascotas, crear_mascota, editar_mascota, eliminar_mascota, detalle_mascota, cliente_dashboard

urlpatterns = [
    path('', lista_mascotas, name='lista'),
    path('dashboard/', cliente_dashboard, name='dashboard'),
    path('nuevo/', crear_mascota, name='nuevo'),
    path('detalle/<int:pk>/', detalle_mascota, name='detalle'),
    path('editar/<int:pk>/', editar_mascota, name='editar'),
    path('eliminar/<int:pk>/', eliminar_mascota, name='eliminar'),
]