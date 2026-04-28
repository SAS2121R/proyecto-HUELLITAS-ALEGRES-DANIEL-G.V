"""
URL configuration for huellitas_alegres project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static

# Función para redirigir la página principal al sistema de autenticación
def redirect_to_auth(request):
    return redirect('usuarios:auth')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', redirect_to_auth, name='inicio'),
    path('usuarios/', include(('usuarios.urls', 'usuarios'), namespace='usuarios')),
    path('productos/', include(('productos.urls', 'productos'), namespace='productos')),
    path('mascotas/', include(('mascotas.urls', 'mascotas'), namespace='mascotas')),
    path('agenda/', include(('agenda.urls', 'agenda'), namespace='agenda')),
    path('historial/', include(('historial.urls', 'historial'), namespace='historial')),
    
    path('reportes/', include(('reportes.urls', 'reportes'), namespace='reportes')),
path('entregas/', include(('entregas.urls', 'entregas'), namespace='entregas')),
    path('servicios/', include(('servicios.urls', 'servicios'), namespace='servicios')),
    path('tienda/', include(('tienda.urls', 'tienda'), namespace='tienda')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
