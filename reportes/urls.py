from django.urls import path
from . import views

app_name = 'reportes'

urlpatterns = [
    path('citas/', views.reporte_citas, name='citas'),
    path('historial/<int:mascota_pk>/', views.reporte_historial, name='historial'),
    path('inventario/', views.reporte_inventario, name='inventario'),
    path('servicios/', views.reporte_servicios, name='servicios'),
]
