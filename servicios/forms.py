from django import forms
from .models import Servicio, CATEGORIAS_SERVICIO


class ServicioForm(forms.ModelForm):
    """Formulario para crear/editar servicios veterinarios."""

    class Meta:
        model = Servicio
        fields = ['nombre', 'descripcion', 'categoria', 'tarifa', 'duracion_minutos']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'duracion_minutos': forms.NumberInput(attrs={'min': 1}),
        }