from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

TIPO_CONSULTA_CHOICES = [
    ('consulta', 'Consulta general'),
    ('vacunacion', 'Vacunación'),
    ('cirugia', 'Cirugía'),
    ('urgencia', 'Urgencia'),
    ('control', 'Control'),
    ('laboratorio', 'Laboratorio'),
]


class HistorialClinico(models.Model):
    """Modelo para representar un registro de historial clínico veterinario."""

    mascota = models.ForeignKey(
        'mascotas.Mascota',
        on_delete=models.PROTECT,
        related_name='historiales',
        verbose_name='Mascota',
    )
    cita = models.ForeignKey(
        'agenda.Cita',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='historiales',
        verbose_name='Cita',
    )
    veterinario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='historiales',
        limit_choices_to={'rol__nombre': 'Veterinario'},
        verbose_name='Veterinario',
    )
    tipo_consulta = models.CharField(
        max_length=20,
        choices=TIPO_CONSULTA_CHOICES,
        default='consulta',
        verbose_name='Tipo de consulta',
    )
    motivo_consulta = models.TextField(
        verbose_name='Motivo de consulta',
    )
    diagnostico = models.TextField(
        verbose_name='Diagnóstico',
    )
    tratamiento = models.TextField(
        blank=True,
        default='',
        verbose_name='Tratamiento',
    )
    observaciones = models.TextField(
        blank=True,
        default='',
        verbose_name='Observaciones',
    )
    peso = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(0.01, message='El peso debe ser mayor a 0 kg.'),
            MaxValueValidator(999.99, message='El peso máximo es 999.99 kg.'),
        ],
        verbose_name='Peso (kg)',
    )
    temperatura = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(34.0, message='La temperatura mínima es 34.0 °C.'),
            MaxValueValidator(43.0, message='La temperatura máxima es 43.0 °C.'),
        ],
        verbose_name='Temperatura (°C)',
    )
    frecuencia_cardiaca = models.IntegerField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(40, message='La frecuencia cardíaca mínima es 40 lpm.'),
            MaxValueValidator(300, message='La frecuencia cardíaca máxima es 300 lpm.'),
        ],
        verbose_name='Frecuencia cardíaca (lpm)',
    )
    frecuencia_respiratoria = models.IntegerField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(5, message='La frecuencia respiratoria mínima es 5 rpm.'),
            MaxValueValidator(60, message='La frecuencia respiratoria máxima es 60 rpm.'),
        ],
        verbose_name='Frecuencia respiratoria (rpm)',
    )
    vacuna_aplicada = models.CharField(
        max_length=100,
        blank=True,
        default='',
        verbose_name='Vacuna aplicada',
    )
    producto_aplicado = models.ForeignKey(
        'productos.Producto',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='historiales_clinicos',
        verbose_name='Producto aplicado',
        help_text='Producto del inventario utilizado en esta consulta.',
    )
    proxima_vacunacion = models.DateField(
        null=True,
        blank=True,
        verbose_name='Próxima vacunación',
    )
    fecha_consulta = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de consulta',
    )

    class Meta:
        db_table = 'historial_historialclinico'
        ordering = ['-fecha_consulta']
        verbose_name = 'Historial Clínico'
        verbose_name_plural = 'Historiales Clínicos'

    def __str__(self):
        return f"{self.mascota} - {self.get_tipo_consulta_display()} ({self.fecha_consulta.strftime('%d/%m/%Y')})"
