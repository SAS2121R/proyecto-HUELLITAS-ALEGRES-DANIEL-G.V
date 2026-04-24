from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from datetime import date


ESTADO_CHOICES = [
    ('Programada', 'Programada'),
    ('Atendida', 'Atendida'),
    ('Cancelada', 'Cancelada'),
]


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

    @property
    def esta_ocupada(self):
        """True if slot has a Programada or Atendida cita."""
        return self.citas.filter(estado__in=['Programada', 'Atendida']).exists()

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


class Cita(models.Model):
    """Modelo para representar una cita veterinaria."""

    mascota = models.ForeignKey(
        'mascotas.Mascota',
        on_delete=models.PROTECT,
        related_name='citas',
        verbose_name='Mascota',
    )
    disponibilidad = models.ForeignKey(
        Disponibilidad,
        on_delete=models.PROTECT,
        related_name='citas',
        verbose_name='Disponibilidad',
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='Programada',
        verbose_name='Estado',
    )
    motivo = models.CharField(
        max_length=200,
        blank=True,
        default='',
        verbose_name='Motivo de consulta',
    )
    motivo_cancelacion = models.TextField(
        blank=True,
        default='',
        verbose_name='Motivo de cancelación',
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación',
    )

    class Meta:
        verbose_name = 'Cita'
        verbose_name_plural = 'Citas'
        db_table = 'agenda_cita'
        ordering = ['disponibilidad__fecha', 'disponibilidad__hora_inicio']

    def __str__(self):
        return f"Cita: {self.mascota} — {self.disponibilidad} [{self.estado}]"

    @property
    def veterinario(self):
        return self.disponibilidad.veterinario

    def clean(self):
        errors = {}
        # Double-booking prevention
        if self.disponibilidad_id and self.estado != 'Cancelada':
            existing = Cita.objects.filter(
                disponibilidad=self.disponibilidad
            ).exclude(estado='Cancelada').exclude(pk=self.pk)
            if existing.exists():
                errors['disponibilidad'] = 'Este horario ya tiene una cita programada o atendida.'

        # State transition validation
        if self.pk:
            try:
                old = Cita.objects.get(pk=self.pk)
                if old.estado == 'Atendida' and self.estado != 'Atendida':
                    errors['estado'] = 'No se puede cambiar el estado de una cita atendida.'
                if old.estado == 'Cancelada' and self.estado != 'Cancelada':
                    errors['estado'] = 'No se puede reactivar una cita cancelada.'
            except Cita.DoesNotExist:
                pass

        # Motivo cancelación required when cancelling
        if self.estado == 'Cancelada' and not self.motivo_cancelacion:
            errors['motivo_cancelacion'] = 'Debe indicar el motivo de cancelación.'

        if errors:
            raise ValidationError(errors)
