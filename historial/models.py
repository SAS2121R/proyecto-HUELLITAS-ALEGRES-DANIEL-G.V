from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

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


# Maximum file size for attachments: 5 MB
MAX_ADJUNTO_SIZE = 5 * 1024 * 1024  # 5242880 bytes

TIPO_ADJUNTO_CHOICES = [
    ('radiografia', 'Radiografía'),
    ('laboratorio', 'Laboratorio'),
    ('foto', 'Fotografía'),
    ('otro', 'Otro'),
]


def adjunto_upload_path(instance, filename):
    """Upload path: media/adjuntos/<historial_pk>/<filename>"""
    return f'adjuntos/{instance.historial_clinico_id}/{filename}'


class Adjunto(models.Model):
    """Archivo adjunto a un registro de historial clínico."""

    historial_clinico = models.ForeignKey(
        HistorialClinico,
        on_delete=models.PROTECT,
        related_name='adjuntos',
        verbose_name='Historial clínico',
    )
    archivo = models.FileField(
        upload_to=adjunto_upload_path,
        verbose_name='Archivo',
    )
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_ADJUNTO_CHOICES,
        default='otro',
        verbose_name='Tipo de archivo',
    )
    descripcion = models.CharField(
        max_length=200,
        blank=True,
        default='',
        verbose_name='Descripción',
    )
    fecha_subida = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de subida',
    )
    subido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Subido por',
    )

    class Meta:
        db_table = 'historial_adjunto'
        ordering = ['-fecha_subida']
        verbose_name = 'Adjunto'
        verbose_name_plural = 'Adjuntos'

    def __str__(self):
        tipo_display = self.get_tipo_display()
        filename = self.archivo.name.split('/')[-1] if self.archivo.name else 'Sin archivo'
        return f"{tipo_display} — {filename}"

    def clean(self):
        """Validate file size does not exceed MAX_ADJUNTO_SIZE."""
        super().clean()
        if self.archivo and self.archivo.size > MAX_ADJUNTO_SIZE:
            raise ValidationError(
                f'El archivo excede el tamaño máximo permitido de {MAX_ADJUNTO_SIZE // (1024*1024)} MB.'
            )
