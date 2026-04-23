from django import forms
from django.core.exceptions import ValidationError
from datetime import date
from .models import Mascota


class MascotaForm(forms.ModelForm):
    class Meta:
        model = Mascota
        exclude = ['propietario']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_fecha_nacimiento(self):
        fecha = self.cleaned_data.get('fecha_nacimiento')
        if fecha and fecha > date.today():
            raise ValidationError('La fecha de nacimiento no puede ser futura.')
        return fecha
