from django.urls import path
from . import views

app_name = 'agenda'
urlpatterns = [
    path('disponibilidades/', views.lista_disponibilidades, name='lista_disponibilidad'),
    path('disponibilidades/nuevo/', views.crear_disponibilidad, name='crear_disponibilidad'),
    path('disponibilidades/editar/<int:pk>/', views.editar_disponibilidad, name='editar_disponibilidad'),
    path('disponibilidades/eliminar/<int:pk>/', views.eliminar_disponibilidad, name='eliminar_disponibilidad'),
]
