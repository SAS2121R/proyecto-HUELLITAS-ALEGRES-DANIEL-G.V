from django import forms
from django.forms import inlineformset_factory
from .models import Pedido, PedidoItem, ESTADO_CHOICES


class PedidoForm(forms.ModelForm):
    """Formulario para que Admin cree un nuevo Pedido."""

    class Meta:
        model = Pedido
        fields = ['cliente', 'domiciliario', 'direccion_entrega', 'telefono_contacto', 'notas']
        widgets = {
            'direccion_entrega': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Calle 10 # 25-30, Apartamento 3B',
            }),
            'telefono_contacto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '300 123 4567',
            }),
            'notas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Instrucciones especiales de entrega...',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar cliente y domiciliario por rol
        from usuarios.models import Usuario
        self.fields['cliente'].queryset = Usuario.objects.filter(rol__nombre='Cliente')
        self.fields['domiciliario'].queryset = Usuario.objects.filter(
            rol__nombre='Domiciliario', is_active=True, is_disponible=True
        ).order_by('first_name')
        self.fields['domiciliario'].empty_label = '— Asignar automáticamente (menos cargado) —'


class PedidoItemForm(forms.ModelForm):
    """Formulario para un solo item de pedido (producto + cantidad)."""

    class Meta:
        model = PedidoItem
        fields = ['producto', 'cantidad']
        widgets = {
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'value': 1,
            }),
        }


PedidoItemFormSet = inlineformset_factory(
    Pedido,
    PedidoItem,
    form=PedidoItemForm,
    extra=1,
    can_delete=True,
    min_num=0,
    validate_min=False,
)


class CambiarEstadoForm(forms.Form):
    """Formulario para transición de estado del pedido — muestra solo los próximos estados válidos."""
    nuevo_estado = forms.ChoiceField(
        choices=[],  # se llena dinámicamente en __init__
        widget=forms.Select(attrs={'class': 'form-select form-select-lg'}),
    )
    incidente_notas = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Describa el motivo del incidente o cancelación...',
        }),
    )

    def __init__(self, *args, estado_actual=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.estado_actual = estado_actual
        # Solo mostrar transiciones válidas según el estado actual
        valid_transitions = self._get_valid_transitions(estado_actual)
        self.fields['nuevo_estado'].choices = valid_transitions

    def _get_valid_transitions(self, estado_actual):
        """Retorna los próximos estados válidos para el estado actual."""
        transitions = {
            'pendiente': [('en_camino', '🛵 En Camino'), ('cancelado', '❌ Cancelado')],
            'en_camino': [('entregado', '📦 Entregado'), ('cancelado', '❌ Cancelado')],
            'entregado': [],   # estado final
            'cancelado': [],   # estado final
        }
        return transitions.get(estado_actual, [])

    def clean(self):
        cleaned = super().clean()
        nuevo = cleaned.get('nuevo_estado')
        # Si transiciona a cancelado, incidente_notas es requerido
        if nuevo == 'cancelado' and not cleaned.get('incidente_notas'):
            self.add_error(
                'incidente_notas',
                'Debe indicar el motivo de la cancelación.'
            )
        return cleaned


class EvidenciaForm(forms.ModelForm):
    """Formulario para subir evidencia de entrega (foto + firma obligatorias)."""

    foto_evidencia = forms.ImageField(
        required=True,
        widget=forms.FileInput(attrs={
            'class': 'form-control form-control-lg',
            'accept': 'image/*',
            'required': True,
        }),
        error_messages={'required': 'La foto de evidencia es obligatoria.'},
    )
    firma_imagen = forms.ImageField(
        required=True,
        widget=forms.FileInput(attrs={
            'class': 'form-control form-control-lg',
            'accept': 'image/*',
            'required': True,
        }),
        error_messages={'required': 'La firma del cliente es obligatoria.'},
    )

    class Meta:
        model = Pedido
        fields = ['foto_evidencia', 'firma_imagen']

    def clean_foto_evidencia(self):
        foto = self.cleaned_data.get('foto_evidencia')
        if foto and hasattr(foto, 'size') and foto.size > 5 * 1024 * 1024:
            raise forms.ValidationError('La foto de evidencia no puede exceder 5MB.')
        return foto

    def clean_firma_imagen(self):
        firma = self.cleaned_data.get('firma_imagen')
        if firma and hasattr(firma, 'size') and firma.size > 5 * 1024 * 1024:
            raise forms.ValidationError('La imagen de firma no puede exceder 5MB.')
        return firma


class ReasignarDomiciliarioForm(forms.Form):
    """Formulario para que Admin reasigne domiciliario a un pedido."""
    pedido_pk = forms.IntegerField(widget=forms.HiddenInput())
    domiciliario = forms.ModelChoiceField(
        queryset=None,
        label='Domiciliario',
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from usuarios.models import Usuario
        self.fields['domiciliario'].queryset = Usuario.objects.filter(
            rol__nombre='Domiciliario', is_active=True, is_disponible=True
        ).order_by('first_name')