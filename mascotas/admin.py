from django.contrib import admin
from .models import Mascota


@admin.register(Mascota)
class MascotaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'especie', 'raza', 'sexo', 'propietario']
    list_filter = ['especie', 'sexo']
    search_fields = ['nombre', 'raza', 'propietario__email']