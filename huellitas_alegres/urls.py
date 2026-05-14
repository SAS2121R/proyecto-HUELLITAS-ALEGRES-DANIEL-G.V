"""
URL configuration for huellitas_alegres project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from usuarios.views import landing_page
from productos.views import inicio as dashboard_home


urlpatterns = [
    path('admin/', admin.site.urls),
    # Landing Page (pública) → anónimos ven la landing, autenticados van al dashboard
    path('', landing_page, name='landing'),
    # Dashboard autenticado (renderiza inicio.html con sidebar por rol)
    path('inicio/', dashboard_home, name='inicio'),
    path('usuarios/', include(('usuarios.urls', 'usuarios'), namespace='usuarios')),
    path('productos/', include(('productos.urls', 'productos'), namespace='productos')),
    path('mascotas/', include(('mascotas.urls', 'mascotas'), namespace='mascotas')),
    path('agenda/', include(('agenda.urls', 'agenda'), namespace='agenda')),
    path('historial/', include(('historial.urls', 'historial'), namespace='historial')),
    path('reportes/', include(('reportes.urls', 'reportes'), namespace='reportes')),
    path('entregas/', include(('entregas.urls', 'entregas'), namespace='entregas')),
    path('servicios/', include(('servicios.urls', 'servicios'), namespace='servicios')),
    path('tienda/', include(('tienda.urls', 'tienda'), namespace='tienda')),
    path('proveedores/', include(('proveedores.urls', 'proveedores'), namespace='proveedores')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)