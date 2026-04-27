from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError


CATEGORIAS_SERVICIO = [
    ('consulta', 'Consulta'),
    ('cirugia', 'Cirugía'),
    ('estetica', 'Estética y peluquería'),
    ('vacunacion', 'Vacunación'),
    ('laboratorio', 'Laboratorio'),
    ('imagenes', 'Imágenes diagnósticas'),
    ('hospitalizacion', 'Hospitalización'),
    ('otro', 'Otro'),
]


class ServicioManager(models.Manager):
    """Manager that filters out soft-deleted services by default."""

    def get_queryset(self):
        return super().get_queryset().filter(esta_activo=True)


class Servicio(models.Model):
    """Modelo para representar un servicio veterinario."""

    nombre = models.CharField(max_length=100, unique=True, verbose_name='Nombre')
    descripcion = models.TextField(blank=True, default='', verbose_name='Descripción')
    categoria = models.CharField(
        max_length=20,
        choices=CATEGORIAS_SERVICIO,
        default='consulta',
        verbose_name='Categoría',
    )
    tarifa = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0, message='La tarifa no puede ser negativa.')],
        verbose_name='Tarifa',
    )
    duracion_minutos = models.PositiveIntegerField(
        default=30,
        verbose_name='Duración (minutos)',
    )
    esta_activo = models.BooleanField(
        default=True,
        verbose_name='Activo',
        help_text='Soft delete. Desactivar en lugar de eliminar.',
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name='Última modificación')

    objects = ServicioManager()
    all_objects = models.Manager()

    class Meta:
        db_table = 'servicios_servicio'
        ordering = ['nombre']
        verbose_name = 'Servicio'
        verbose_name_plural = 'Servicios'

    def __str__(self):
        return self.nombre

    def clean(self):
        super().clean()
        if self.categoria and self.categoria not in dict(CATEGORIAS_SERVICIO):
            raise ValidationError({'categoria': 'Categoría no válida.'})