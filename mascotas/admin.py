from django.contrib import admin
from .models import Mascota


@admin.register(Mascota)
class MascotaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'especie', 'raza', 'sexo', 'alergias', 'esterilizado', 'propietario']
    list_filter = ['especie', 'sexo', 'esterilizado']
    search_fields = ['nombre', 'raza', 'propietario__email', 'propietario__cedula']