from django import forms
from .models import Proveedor


class ProveedorForm(forms.ModelForm):
    """Form for creating and updating Proveedor instances."""

    class Meta:
        model = Proveedor
        fields = ['nombre', 'nit', 'telefono', 'email', 'direccion', 'contacto', 'esta_activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del proveedor'}),
            'nit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'NIT'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección'}),
            'contacto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Persona de contacto'}),
            'esta_activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }