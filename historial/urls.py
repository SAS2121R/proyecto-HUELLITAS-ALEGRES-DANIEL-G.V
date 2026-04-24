from django.urls import path
from . import views

app_name = 'historial'

urlpatterns = [
    path('', views.lista_historiales, name='lista'),
    path('nuevo/', views.crear_historial, name='crear'),
    path('<int:pk>/', views.detalle_historial, name='detalle'),
    path('<int:pk>/editar/', views.editar_historial, name='editar'),
    path('mascota/<int:mascota_pk>/', views.historial_por_mascota, name='por_mascota'),
    path('atender/<int:cita_pk>/', views.atender_cita, name='atender_cita'),
]
