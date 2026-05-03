from django.db import models
from django.conf import settings
from django.utils import timezone


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
    alergias = models.TextField(default='Ninguna', blank=True, verbose_name='Alergias')
    esterilizado = models.BooleanField(default=False, verbose_name='Esterilizado')
    foto = models.ImageField(upload_to='mascotas/', blank=True, null=True, verbose_name='Foto')

    class Meta:
        verbose_name = 'Mascota'
        verbose_name_plural = 'Mascotas'
        db_table = 'mascotas_mascota'
        ordering = ['nombre']

    def get_edad(self):
        """Calcula la edad dinámica de la mascota en español.

        Returns:
            str: 'X años, Y meses', '1 año', '2 meses', 'Recién nacido', o 'Edad desconocida'
        """
        if self.fecha_nacimiento is None:
            return 'Edad desconocida'

        today = timezone.localdate()
        birth = self.fecha_nacimiento

        if birth > today:
            return 'Edad desconocida'

        years = today.year - birth.year
        months = today.month - birth.month

        # Ajustar si el cumpleaños no ha ocurrido este mes
        if today.day < birth.day:
            months -= 1

        if months < 0:
            years -= 1
            months += 12

        # Nacido hoy
        if years == 0 and months == 0:
            return 'Recién nacido'

        # Construir la cadena con singular/plural correcto
        parts = []
        if years > 0:
            parts.append(f'{years} año{"s" if years != 1 else ""}')
        if months > 0:
            parts.append(f'{months} mes{"es" if months != 1 else ""}')

        return ', '.join(parts)

    def __str__(self):
        return f"{self.nombre} ({self.especie})"