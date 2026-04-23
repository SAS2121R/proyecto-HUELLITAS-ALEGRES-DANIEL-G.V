from django.contrib import admin
from django.utils.html import format_html
from .models import Disponibilidad, Cita


@admin.register(Disponibilidad)
class DisponibilidadAdmin(admin.ModelAdmin):
    list_display = ['veterinario', 'fecha', 'hora_inicio', 'hora_fin', 'activa']
    list_filter = ['activa', 'fecha']
    search_fields = ['veterinario__email', 'veterinario__username']


@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ['mascota', 'disponibilidad', 'colored_estado', 'fecha_creacion']
    list_filter = ['estado', 'fecha_creacion']
    search_fields = ['mascota__nombre', 'disponibilidad__veterinario__username']

    def colored_estado(self, obj):
        colors = {'Programada': 'orange', 'Atendida': 'green', 'Cancelada': 'red'}
        color = colors.get(obj.estado, 'gray')
        return format_html(
            '<span style="background:{}; color:white; padding:4px 12px; border-radius:4px; font-weight:bold;">{}</span>',
            color, obj.get_estado_display()
        )
    colored_estado.short_description = 'Estado'
    colored_estado.admin_order_field = 'estado'
