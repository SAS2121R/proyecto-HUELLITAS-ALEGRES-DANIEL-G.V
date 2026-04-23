from django import forms
from django.core.exceptions import ValidationError
from .models import Disponibilidad


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
