from django import forms
from decimal import Decimal, InvalidOperation
from .models import Servicio, CATEGORIAS_SERVICIO


class ServicioForm(forms.ModelForm):
    """Formulario para crear/editar servicios veterinarios."""

    tarifa = forms.CharField(
        label='Tarifa (COP)',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: 85.000',
            'inputmode': 'numeric',
        }),
        help_text='Escriba el valor con o sin puntos. Ej: 85.000 o 85000',
    )

    class Meta:
        model = Servicio
        fields = ['nombre', 'descripcion', 'categoria', 'tarifa', 'duracion_minutos']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'duracion_minutos': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If editing, format tarifa with dots for display
        if self.instance and self.instance.pk:
            self.initial['tarifa'] = f'{int(self.instance.tarifa):,}'.replace(',', '.')

    def clean_tarifa(self):
        """Remove dots from tarifa input and convert to Decimal.
        Allows user to type '85.000' or '85000' — both work."""
        raw = self.cleaned_data.get('tarifa', '')
        if isinstance(raw, str):
            # Remove dots (thousands separator in Colombia)
            raw = raw.replace('.', '').strip()
        try:
            value = Decimal(raw)
        except (ValueError, TypeError, InvalidOperation):
            raise forms.ValidationError('Ingrese un valor numérico válido. Ej: 85000 o 85.000')
        if value < 0:
            raise forms.ValidationError('La tarifa no puede ser negativa.')
        return value