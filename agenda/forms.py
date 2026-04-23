from django import forms
from django.core.exceptions import ValidationError
from .models import Cita, Disponibilidad


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

    def clean(self):
        cleaned_data = super().clean()
        # Create instance with form data to validate via model's clean()
        instance = Disponibilidad(**cleaned_data)
        if self.instance.pk:
            instance.pk = self.instance.pk
        # If veterinario is set on the form instance (from view), pass it through
        if hasattr(self, 'instance') and self.instance.veterinario_id:
            instance.veterinario = self.instance.veterinario
        try:
            # Use clean() instead of full_clean() to avoid FK limit_choices_to
            # validation and unique checks. Field validation is already done
            # by the form; we only need business logic validation.
            instance.clean()
        except ValidationError as e:
            for field, msgs in e.message_dict.items():
                for msg in msgs:
                    if field in self.fields:
                        self.add_error(field, msg)
                    else:
                        self.add_error(None, msg)
        return cleaned_data


class CitaForm(forms.ModelForm):
    """Formulario para crear/editar citas veterinarias."""

    class Meta:
        model = Cita
        fields = ['mascota', 'disponibilidad', 'estado', 'motivo_cancelacion']

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
