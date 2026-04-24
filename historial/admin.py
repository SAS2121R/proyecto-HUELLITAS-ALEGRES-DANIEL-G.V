from django.contrib import admin
from .models import HistorialClinico, Adjunto


@admin.register(HistorialClinico)
class HistorialClinicoAdmin(admin.ModelAdmin):
    list_display = ['mascota', 'veterinario', 'tipo_consulta', 'fecha_consulta']
    list_filter = ['tipo_consulta', 'fecha_consulta', 'veterinario']
    search_fields = ['mascota__nombre', 'diagnostico', 'veterinario__email']
    date_hierarchy = 'fecha_consulta'
    readonly_fields = ['fecha_consulta']


@admin.register(Adjunto)
class AdjuntoAdmin(admin.ModelAdmin):
    list_display = ['historial_clinico', 'tipo', 'descripcion', 'subido_por', 'fecha_subida']
    list_filter = ['tipo', 'fecha_subida']
    search_fields = ['descripcion', 'historial_clinico__mascota__nombre']
    readonly_fields = ['fecha_subida']
