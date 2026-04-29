from django import forms
from django.forms import inlineformset_factory
from .models import Pedido, PedidoItem, ESTADO_CHOICES


class PedidoForm(forms.ModelForm):
    """Form for Admin to create a new Pedido."""

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
        # Filter cliente and domiciliario by role
        from usuarios.models import Usuario
        self.fields['cliente'].queryset = Usuario.objects.filter(rol__nombre='Cliente')
        self.fields['domiciliario'].queryset = Usuario.objects.filter(rol__nombre='Domiciliario')


class PedidoItemForm(forms.ModelForm):
    """Form for a single pedido item (product + quantity)."""

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
    """Form for transitioning pedido estado — shows only valid next states."""
    nuevo_estado = forms.ChoiceField(
        choices=[],  # populated dynamically in __init__
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
        # Only show valid transitions based on current state
        valid_transitions = self._get_valid_transitions(estado_actual)
        self.fields['nuevo_estado'].choices = valid_transitions

    def _get_valid_transitions(self, estado_actual):
        """Return valid next states for the current estado."""
        transitions = {
            'pendiente': [('en_camino', '🛵 En Camino'), ('cancelado', '❌ Cancelado')],
            'en_camino': [('entregado', '📦 Entregado'), ('cancelado', '❌ Cancelado')],
            'entregado': [],   # final state
            'cancelado': [],   # final state
        }
        return transitions.get(estado_actual, [])

    def clean(self):
        cleaned = super().clean()
        nuevo = cleaned.get('nuevo_estado')
        # If transitioning to cancelado, incidente_notas is required
        if nuevo == 'cancelado' and not cleaned.get('incidente_notas'):
            self.add_error(
                'incidente_notas',
                'Debe indicar el motivo de la cancelación.'
            )
        return cleaned


class EvidenciaForm(forms.ModelForm):
    """Form for uploading delivery evidence (photo + optional signature)."""

    class Meta:
        model = Pedido
        fields = ['foto_evidencia', 'firma_imagen']
        widgets = {
            'foto_evidencia': forms.FileInput(attrs={
                'class': 'form-control form-control-lg',
                'accept': 'image/*',
            }),
            'firma_imagen': forms.FileInput(attrs={
                'class': 'form-control form-control-lg',
                'accept': 'image/*',
            }),
        }

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
    """Form for Admin to reassign domiciliario to a pedido."""
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
            rol__nombre='Domiciliario', is_active=True
        ).order_by('first_name')