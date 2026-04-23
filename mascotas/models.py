from django.db import models
from django.conf import settings


ESPECIE_CHOICES = [
    ('Canino', 'Canino'),
    ('Felino', 'Felino'),
    ('Ave', 'Ave'),
    ('Reptil', 'Reptil'),
    ('Roedor', 'Roedor'),
    ('Pez', 'Pez'),
    ('Otros', 'Otros'),
]

SEXO_CHOICES = [
    ('Macho', 'Macho'),
    ('Hembra', 'Hembra'),
]


class Mascota(models.Model):
    """Modelo para representar una mascota (paciente) de la clínica veterinaria."""

    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    especie = models.CharField(max_length=20, choices=ESPECIE_CHOICES, verbose_name='Especie')
    raza = models.CharField(max_length=100, blank=True, default='', verbose_name='Raza')
    sexo = models.CharField(max_length=10, choices=SEXO_CHOICES, verbose_name='Sexo')
    fecha_nacimiento = models.DateField(null=True, blank=True, verbose_name='Fecha de Nacimiento')
    propietario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mascotas',
        verbose_name='Propietario',
    )

    class Meta:
        verbose_name = 'Mascota'
        verbose_name_plural = 'Mascotas'
        db_table = 'mascotas_mascota'
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.especie})"
