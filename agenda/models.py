from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from datetime import date


class Disponibilidad(models.Model):
    """Modelo para representar un bloque de disponibilidad de un veterinario."""

    veterinario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='disponibilidades',
        limit_choices_to={'rol__nombre': 'Veterinario'},
        verbose_name='Veterinario',
    )
    fecha = models.DateField(verbose_name='Fecha')
    hora_inicio = models.TimeField(verbose_name='Hora de inicio')
    hora_fin = models.TimeField(verbose_name='Hora de fin')
    activa = models.BooleanField(default=True, verbose_name='Activa')

    class Meta:
        verbose_name = 'Disponibilidad'
        verbose_name_plural = 'Disponibilidades'
        db_table = 'agenda_disponibilidad'
        ordering = ['fecha', 'hora_inicio']

    def __str__(self):
        return f"{self.veterinario} — {self.fecha} {self.hora_inicio.strftime('%H:%M')}-{self.hora_fin.strftime('%H:%M')}"

    def clean(self):
        errors = {}
        # hora_inicio must be before hora_fin
        if self.hora_inicio and self.hora_fin and self.hora_inicio >= self.hora_fin:
            errors['hora_fin'] = 'La hora de fin debe ser posterior a la hora de inicio.'
        # fecha must not be in the past
        if self.fecha and self.fecha < date.today():
            errors['fecha'] = 'No se pueden crear disponibilidades en fechas pasadas.'
        # Overlap detection (only if time/date are valid)
        if not errors.get('hora_fin') and not errors.get('fecha') and self.veterinario_id and self.fecha and self.hora_inicio and self.hora_fin:
            qs = Disponibilidad.objects.filter(
                veterinario=self.veterinario,
                fecha=self.fecha,
                hora_inicio__lt=self.hora_fin,
                hora_fin__gt=self.hora_inicio,
            ).exclude(pk=self.pk)
            if qs.exists():
                errors['hora_inicio'] = 'Ya existe una disponibilidad que se superpone en este horario.'
        if errors:
            raise ValidationError(errors)
