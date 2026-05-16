from django import forms
from django.core.exceptions import ValidationError
from .models import Cita, Disponibilidad
from mascotas.models import Mascota


class DisponibilidadForm(forms.ModelForm):
    """Formulario para crear/editar bloques de disponibilidad."""

    class Meta:
        model = Disponibilidad
        exclude = ['veterinario']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time'}),
            'hora_fin': forms.TimeInput(attrs={'type': 'time'}),
            'activa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        # Admin can choose which vet to assign; Vet auto-assigns to themselves
        if user and user.rol.nombre == 'Administrador':
            self.fields['veterinario'] = forms.ModelChoiceField(
                queryset=user.__class__.objects.filter(rol__nombre='Veterinario'),
                required=True,
                label='Veterinario',
            )
            # If editing, pre-select current vet
            if self.instance and self.instance.veterinario_id:
                self.initial['veterinario'] = self.instance.veterinario_id

    def clean(self):
        cleaned_data = super().clean()
        # Build instance for model validation
        instance = Disponibilidad(**{
            k: v for k, v in cleaned_data.items()
            if k not in ('veterinario',)
        })
        # Set veterinario: Admin chose it from the form field; Vet is set by the view
        vet = cleaned_data.get('veterinario')
        if vet:
            instance.veterinario = vet
        elif self.instance and self.instance.veterinario_id:
            instance.veterinario = self.instance.veterinario
        if self.instance.pk:
            instance.pk = self.instance.pk
        try:
            instance.clean()
        except ValidationError as e:
            for field, msgs in e.message_dict.items():
                for msg in msgs:
                    if field in self.fields:
                        self.add_error(field, msg)
                    else:
                        self.add_error(None, msg)
        return cleaned_data

    def save(self, commit=True):
        """Override save to handle veterinario for Admin users."""
        # veterinario is in Meta.exclude, so ModelForm won't save it.
        # If Admin submitted it via the dynamic field, set it manually.
        if 'veterinario' in self.cleaned_data:
            self.instance.veterinario = self.cleaned_data['veterinario']
        return super().save(commit=commit)


class CitaForm(forms.ModelForm):
    """Formulario para crear/editar citas veterinarias (Vet/Admin)."""

    class Meta:
        model = Cita
        fields = ['mascota', 'disponibilidad', 'estado', 'motivo_cancelacion', 'motivo']
        widgets = {
            'motivo': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describa el motivo de la consulta'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter disponibilidad to active & unoccupied slots
        available_ids = Disponibilidad.objects.filter(
            activa=True
        ).exclude(
            pk__in=Cita.objects.filter(
                estado__in=['Programada', 'Atendida']
            ).values('disponibilidad_id')
        ).values_list('pk', flat=True)
        self.fields['disponibilidad'].queryset = Disponibilidad.objects.filter(
            pk__in=available_ids
        )
        # If editing, include the current instance's disponibilidad in queryset
        if self.instance and self.instance.pk:
            current_disp = self.instance.disponibilidad
            if current_disp and current_disp.pk not in self.fields['disponibilidad'].queryset:
                self.fields['disponibilidad'].queryset = (
                    self.fields['disponibilidad'].queryset
                    | Disponibilidad.objects.filter(pk=current_disp.pk)
                )
        # Exclude estado on creation, show on edit
        if not (self.instance and self.instance.pk):
            self.fields.pop('estado')
        # motivo_cancelacion always visible but not always required
        self.fields['motivo_cancelacion'].required = False

    def clean(self):
        cleaned_data = super().clean()
        # Create instance with form data for model validation
        instance = Cita(**cleaned_data)
        if self.instance and self.instance.pk:
            instance.pk = self.instance.pk
        try:
            instance.clean()
        except ValidationError as e:
            for field, msgs in e.message_dict.items():
                for msg in msgs:
                    if field in self.fields:
                        self.add_error(field, msg)
                    else:
                        self.add_error(None, msg)
        return cleaned_data


class SolicitarCitaForm(forms.ModelForm):
    """Formulario para que el Cliente solicite una cita.
    Filters mascota to request.user's own, disponibilidad to available slots.
    Includes optional veterinario filter — HU#5 criterion:
    «El sistema debe mostrar una lista de profesionales veterinarios disponibles».
    """

    veterinario = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label='— Todos los veterinarios —',
        label='Veterinario (opcional)',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = Cita
        fields = ['mascota', 'veterinario', 'disponibilidad', 'motivo']
        widgets = {
            'motivo': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describa el motivo de la consulta (vacunación, control, etc.)',
            }),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter mascota to user's own
        if user:
            self.fields['mascota'].queryset = Mascota.objects.filter(propietario=user).order_by('nombre')

        # Veterinarios con disponibilidades futuras
        from django.utils import timezone as dj_tz
        from django.contrib.auth import get_user_model
        Usuario = get_user_model()

        vets_with_slots = Disponibilidad.objects.filter(
            activa=True,
            fecha__gte=dj_tz.localdate(),
        ).exclude(
            pk__in=Cita.objects.filter(
                estado__in=['Programada', 'Atendida']
            ).values('disponibilidad_id')
        ).values_list('veterinario_id', flat=True).distinct()

        self.fields['veterinario'].queryset = Usuario.objects.filter(
            pk__in=vets_with_slots
        ).order_by('first_name')

        # Filter disponibilidad to active & unoccupied slots with future dates
        available_qs = Disponibilidad.objects.filter(
            activa=True,
            fecha__gte=dj_tz.localdate(),
        ).exclude(
            pk__in=Cita.objects.filter(
                estado__in=['Programada', 'Atendida']
            ).values('disponibilidad_id')
        ).order_by('fecha', 'hora_inicio')

        # If a veterinario is selected in GET/POST data, filter disponibilidad by that vet
        vet_id = None
        if data := (kwargs.get('data') or (args[0] if args else None)):
            vet_id = data.get('veterinario') if hasattr(data, 'get') else None
        if not vet_id and self.initial.get('veterinario'):
            vet_id = self.initial['veterinario']

        # Filter disponibilidad queryset by selected vet (if any)
        if vet_id:
            try:
                vet_id = int(vet_id)
                available_qs = available_qs.filter(veterinario_id=vet_id)
            except (ValueError, TypeError):
                pass

        self.fields['disponibilidad'].queryset = available_qs
        self.fields['mascota'].empty_label = '— Seleccione su mascota —'
        self.fields['disponibilidad'].empty_label = '— Seleccione fecha y hora —'

    def clean(self):
        cleaned_data = super().clean()
        # veterinario is not saved on the Cita model — it's derived from disponibilidad.veterinario
        # Remove it from cleaned_data before model validation
        cleaned_data.pop('veterinario', None)
        return cleaned_data


class ReprogramarCitaForm(forms.ModelForm):
    """Formulario para que el Cliente reprogreme una cita existente.

    HU#5: «En caso de que el cliente necesite cambiar una cita,
    el sistema debe ofrecer opciones claras para llevar a cabo estas acciones.»
    Muestra solo disponibilidades futuras disponibles (excluyendo la cita actual).
    """

    veterinario = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label='— Todos los veterinarios —',
        label='Veterinario (opcional)',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = Cita
        fields = ['disponibilidad', 'motivo']
        widgets = {
            'motivo': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describa el motivo de la consulta (vacunación, control, etc.)',
            }),
        }

    def __init__(self, *args, cita_actual=None, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.cita_actual = cita_actual

        # Veterinarios con disponibilidades futuras
        from django.utils import timezone as dj_tz
        from django.contrib.auth import get_user_model
        Usuario = get_user_model()

        vets_with_slots = Disponibilidad.objects.filter(
            activa=True,
            fecha__gte=dj_tz.localdate(),
        ).exclude(
            pk__in=Cita.objects.filter(
                estado__in=['Programada', 'Atendida']
            ).values('disponibilidad_id')
        ).values_list('veterinario_id', flat=True).distinct()

        self.fields['veterinario'].queryset = Usuario.objects.filter(
            pk__in=vets_with_slots
        ).order_by('first_name')

        # Filter disponibilidad: available slots excluding the current cita's slot
        available_qs = Disponibilidad.objects.filter(
            activa=True,
            fecha__gte=dj_tz.localdate(),
        ).exclude(
            pk__in=Cita.objects.filter(
                estado__in=['Programada', 'Atendida']
            ).values('disponibilidad_id')
        )

        # Include the current cita's disponibilidad in the queryset
        if cita_actual and cita_actual.disponibilidad:
            available_qs = available_qs | Disponibilidad.objects.filter(
                pk=cita_actual.disponibilidad_id
            )

        available_qs = available_qs.order_by('fecha', 'hora_inicio')

        # Filter by vet if selected
        vet_id = None
        if data := (kwargs.get('data') or (args[0] if args else None)):
            vet_id = data.get('veterinario') if hasattr(data, 'get') else None

        if vet_id:
            try:
                vet_id = int(vet_id)
                available_qs = available_qs.filter(veterinario_id=vet_id)
            except (ValueError, TypeError):
                pass

        self.fields['disponibilidad'].queryset = available_qs
        self.fields['disponibilidad'].empty_label = '— Seleccione nueva fecha y hora —'

        # Pre-fill motivo with current value
        if cita_actual and not self.initial.get('motivo'):
            self.initial['motivo'] = cita_actual.motivo

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data.pop('veterinario', None)

        # Validate: new disponibilidad must be different from current
        if self.cita_actual and cleaned_data.get('disponibilidad'):
            if cleaned_data['disponibilidad'].pk == self.cita_actual.disponibilidad_id:
                raise ValidationError(
                    'Debe seleccionar una fecha y hora diferente a la actual.'
                )
        return cleaned_data
