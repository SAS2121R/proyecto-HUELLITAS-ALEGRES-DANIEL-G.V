from django import forms
from .models import Producto, MovimientoInventario


class ProductoForm(forms.ModelForm):
    """Form for creating and updating products."""

    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio', 'cantidad_stock',
                   'categoria', 'stock_minimo', 'proveedor']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'proveedor': forms.Select(attrs={'class': 'form-select'}),
        }


class MovimientoInventarioForm(forms.ModelForm):
    """Form for manual inventory movements (Kardex entries).

    usuario is set from request.user in the view.
    historial_clinico is only set via signal, not manually.
    """

    class Meta:
        model = MovimientoInventario
        fields = ['producto', 'tipo_movimiento', 'cantidad', 'motivo']
        widgets = {
            'motivo': forms.Textarea(attrs={'rows': 2}),
        }