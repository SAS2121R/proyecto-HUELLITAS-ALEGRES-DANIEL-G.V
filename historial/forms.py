import re
from datetime import date

from django import forms
from django.core.exceptions import ValidationError

from .models import HistorialClinico


class HistorialClinicoForm(forms.ModelForm):
    class Meta:
        model = HistorialClinico
        fields = [
            'mascota', 'tipo_consulta',
            'motivo_consulta', 'diagnostico', 'tratamiento',
            'observaciones', 'peso', 'temperatura',
            'frecuencia_cardiaca', 'frecuencia_respiratoria',
            'vacuna_aplicada', 'proxima_vacunacion',
        ]
        widgets = {
            'tipo_consulta': forms.Select(attrs={'class': 'form-select'}),
            'motivo_consulta': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'diagnostico': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tratamiento': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'peso': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Ej: 25.50'}),
            'temperatura': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'Ej: 38.5'}),
            'frecuencia_cardiaca': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 120'}),
            'frecuencia_respiratoria': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 24'}),
            'vacuna_aplicada': forms.TextInput(attrs={'class': 'form-control'}),
            'proxima_vacunacion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def clean_proxima_vacunacion(self):
        fecha = self.cleaned_data.get('proxima_vacunacion')
        if fecha and fecha < date.today():
            raise ValidationError('La próxima vacunación debe ser una fecha futura.')
        return fecha


class AtenderCitaForm(forms.ModelForm):
    """Form for attending a Cita — excludes mascota (auto-set from cita),
    pre-fills motivo_consulta from cita.motivo, and auto-selects tipo_consulta."""

    class Meta:
        model = HistorialClinico
        fields = [
            'tipo_consulta', 'motivo_consulta', 'diagnostico',
            'tratamiento', 'observaciones', 'peso', 'temperatura',
            'frecuencia_cardiaca', 'frecuencia_respiratoria',
            'vacuna_aplicada', 'proxima_vacunacion',
        ]
        widgets = {
            'tipo_consulta': forms.Select(attrs={'class': 'form-select'}),
            'motivo_consulta': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'diagnostico': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tratamiento': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'peso': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Ej: 25.50'}),
            'temperatura': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'Ej: 38.5'}),
            'frecuencia_cardiaca': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 120'}),
            'frecuencia_respiratoria': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 24'}),
            'vacuna_aplicada': forms.TextInput(attrs={'class': 'form-control'}),
            'proxima_vacunacion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, cita=None, **kwargs):
        super().__init__(*args, **kwargs)
        if cita:
            self.fields['motivo_consulta'].initial = cita.motivo
            self.fields['tipo_consulta'].initial = self._infer_tipo_consulta(cita.motivo)

    @staticmethod
    def _infer_tipo_consulta(motivo):
        """Infer tipo_consulta from motivo text. Case-insensitive and accent-robust."""
        if not motivo:
            return 'consulta'
        motivo_lower = motivo.lower()
        if re.search(r'vacun|vacuna|vacunar', motivo_lower):
            return 'vacunacion'
        if re.search(r'cirug|oper', motivo_lower):
            return 'cirugia'
        if re.search(r'urgencia|emergencia', motivo_lower):
            return 'urgencia'
        if re.search(r'control|seguimiento', motivo_lower):
            return 'control'
        if re.search(r'laboratorio|examen|analisis', motivo_lower):
            return 'laboratorio'
        return 'consulta'

    def clean_proxima_vacunacion(self):
        fecha = self.cleaned_data.get('proxima_vacunacion')
        if fecha and fecha < date.today():
            raise ValidationError('La próxima vacunación debe ser una fecha futura.')
        return fecha
