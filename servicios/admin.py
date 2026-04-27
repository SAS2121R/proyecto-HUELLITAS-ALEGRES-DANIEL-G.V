from django.contrib import admin
from .models import Servicio


@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'tarifa', 'duracion_minutos', 'esta_activo')
    list_filter = ('categoria', 'esta_activo')
    search_fields = ('nombre', 'descripcion')