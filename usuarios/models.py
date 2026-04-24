from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class Rol(models.Model):
    """Modelo de Rol para el sistema de autorización."""
    nombre = models.CharField(max_length=50, unique=True, verbose_name='Nombre')
    descripcion = models.TextField(blank=True, default='', verbose_name='Descripción')

    class Meta:
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'
        db_table = 'usuarios_rol'

    def __str__(self):
        return self.nombre


# Modelo personalizado de Usuario que extiende AbstractUser
class Usuario(AbstractUser):
    email = models.EmailField(unique=True, verbose_name='Correo Electrónico')
    fecha_registro = models.DateTimeField(default=timezone.now, verbose_name='Fecha de Registro')
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    telefono = models.CharField(max_length=15, blank=True, default='', verbose_name='Teléfono')
    cedula = models.CharField(max_length=20, blank=True, default='', db_index=True, verbose_name='Cédula')
    rol = models.ForeignKey(
        Rol, on_delete=models.PROTECT, verbose_name='Rol',
        related_name='usuarios'
    )
    
    # Usar email como campo de autenticación en lugar de username
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        db_table = 'usuarios_usuario'
    
    def __str__(self):
        return f'{self.email} - {self.username}'
