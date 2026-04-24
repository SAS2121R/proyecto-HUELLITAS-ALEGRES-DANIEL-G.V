from django.contrib import admin
from .models import HistorialClinico


@admin.register(HistorialClinico)
class HistorialClinicoAdmin(admin.ModelAdmin):
    list_display = ['mascota', 'veterinario', 'tipo_consulta', 'fecha_consulta']
    list_filter = ['tipo_consulta', 'fecha_consulta', 'veterinario']
    search_fields = ['mascota__nombre', 'diagnostico', 'veterinario__email']
    date_hierarchy = 'fecha_consulta'
    readonly_fields = ['fecha_consulta']
