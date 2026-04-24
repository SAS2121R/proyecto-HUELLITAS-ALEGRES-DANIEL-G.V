from django.urls import path
from . import views

app_name = 'agenda'
urlpatterns = [
    path('', views.dashboard_vet, name='dashboard_vet'),
    path('disponibilidades/', views.lista_disponibilidades, name='lista_disponibilidad'),
    path('disponibilidades/nuevo/', views.crear_disponibilidad, name='crear_disponibilidad'),
    path('disponibilidades/editar/<int:pk>/', views.editar_disponibilidad, name='editar_disponibilidad'),
    path('disponibilidades/eliminar/<int:pk>/', views.eliminar_disponibilidad, name='eliminar_disponibilidad'),
    path('citas/', views.lista_citas, name='lista_citas'),
    path('citas/nueva/', views.crear_cita, name='crear_cita'),
    path('citas/editar/<int:pk>/', views.editar_cita, name='editar_cita'),
    path('citas/eliminar/<int:pk>/', views.eliminar_cita, name='eliminar_cita'),
]
