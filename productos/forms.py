from django import forms
from .models import Producto, MovimientoInventario


class ProductoForm(forms.ModelForm):
    """Formulario para crear y actualizar productos."""

    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio', 'cantidad_stock',
                   'categoria', 'stock_minimo', 'proveedor']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'proveedor': forms.Select(attrs={'class': 'form-select'}),
        }


class MovimientoInventarioForm(forms.ModelForm):
    """Formulario para movimientos manuales de inventario (entradas de Kardex).

    usuario se establece desde request.user en la vista.
    historial_clinico solo se establece mediante señal, no manualmente.
    """

    class Meta:
        model = MovimientoInventario
        fields = ['producto', 'tipo_movimiento', 'cantidad', 'motivo']
        widgets = {
            'motivo': forms.Textarea(attrs={'rows': 2}),
        }