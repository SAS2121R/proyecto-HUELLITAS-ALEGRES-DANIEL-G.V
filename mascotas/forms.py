from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Mascota


class MascotaForm(forms.ModelForm):
    class Meta:
        model = Mascota
        exclude = ['propietario']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
            'alergias': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Ej: Penicilina, Lactosa... Dejar "Ninguna" si no tiene alergias'}),
            'esterilizado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'foto': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

    def clean_fecha_nacimiento(self):
        fecha = self.cleaned_data.get('fecha_nacimiento')
        if fecha and fecha > timezone.localdate():
            raise ValidationError('La fecha de nacimiento no puede ser futura.')
        return fecha