from django.db import models
from django.core.validators import MinValueValidator


class Proveedor(models.Model):
    """Modelo para gestionar proveedores de productos veterinarios."""

    nombre = models.CharField(max_length=200, unique=True, verbose_name='Nombre')
    nit = models.CharField(max_length=50, blank=True, default='', verbose_name='NIT')
    telefono = models.CharField(max_length=20, blank=True, default='', verbose_name='Teléfono')
    email = models.EmailField(blank=True, default='', verbose_name='Email')
    direccion = models.CharField(max_length=200, blank=True, default='', verbose_name='Dirección')
    contacto = models.CharField(max_length=100, blank=True, default='', verbose_name='Persona de contacto')
    esta_activo = models.BooleanField(default=True, verbose_name='Activo')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')

    class Meta:
        db_table = 'proveedores_proveedor'
        ordering = ['nombre']
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'

    def __str__(self):
        return self.nombre