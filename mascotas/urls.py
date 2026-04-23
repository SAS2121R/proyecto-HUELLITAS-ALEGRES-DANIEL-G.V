from django.urls import path
from .views import lista_mascotas, crear_mascota, editar_mascota, eliminar_mascota

urlpatterns = [
    path('', lista_mascotas, name='lista'),
    path('nuevo/', crear_mascota, name='nuevo'),
    path('editar/<int:pk>/', editar_mascota, name='editar'),
    path('eliminar/<int:pk>/', eliminar_mascota, name='eliminar'),
]
