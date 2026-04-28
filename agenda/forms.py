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
    Filters mascota to request.user's own, disponibilidad to available slots."""

    class Meta:
        model = Cita
        fields = ['mascota', 'disponibilidad', 'motivo']
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
        # Filter disponibilidad to active & unoccupied slots with future dates
        from datetime import date as date_cls
        available_ids = Disponibilidad.objects.filter(
            activa=True,
            fecha__gte=date_cls.today(),
        ).exclude(
            pk__in=Cita.objects.filter(
                estado__in=['Programada', 'Atendida']
            ).values('disponibilidad_id')
        ).values_list('pk', flat=True)
        self.fields['disponibilidad'].queryset = Disponibilidad.objects.filter(
            pk__in=available_ids
        ).order_by('fecha', 'hora_inicio')
        self.fields['mascota'].empty_label = '— Seleccione su mascota —'
        self.fields['disponibilidad'].empty_label = '— Seleccione fecha y hora —'
