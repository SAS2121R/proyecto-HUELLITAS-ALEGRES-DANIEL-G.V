from django.contrib import admin
from .models import Disponibilidad


@admin.register(Disponibilidad)
class DisponibilidadAdmin(admin.ModelAdmin):
    list_display = ['veterinario', 'fecha', 'hora_inicio', 'hora_fin', 'activa']
    list_filter = ['activa', 'fecha']
    search_fields = ['veterinario__email', 'veterinario__username']
