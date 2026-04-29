from django.urls import path
from . import views

app_name = 'reportes'

urlpatterns = [
    path('citas/', views.reporte_citas, name='citas'),
    path('historial/<int:mascota_pk>/', views.reporte_historial, name='historial'),
    path('inventario/', views.reporte_inventario, name='inventario'),
    path('servicios/', views.reporte_servicios, name='servicios'),
    path('admin/metricas/', views.admin_metricas, name='admin_metricas'),
    path('admin/metricas/pdf/', views.admin_metricas_pdf, name='admin_metricas_pdf'),
    path('admin/metricas/excel/', views.admin_metricas_excel, name='admin_metricas_excel'),
]
