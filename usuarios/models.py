from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ValidationError


MAX_PERFIL_FOTO_SIZE = 5 * 1024 * 1024  # 5MB — reuse Adjunto pattern


def perfil_foto_path(instance, filename):
    return f'perfiles/{instance.usuario_id}/{filename}'


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
    is_disponible = models.BooleanField(
        default=True,
        verbose_name='Disponible para entregas',
        help_text='Solo aplica para Domiciliarios. Desmárcalo si el domiciliario no está disponible (moto en taller, enfermo, etc.).',
    )
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


class Perfil(models.Model):
    """Modelo para el perfil de usuario con foto y bio."""

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='perfil',
        verbose_name='Usuario'
    )
    foto = models.ImageField(
        upload_to=perfil_foto_path,
        blank=True,
        default='',
        verbose_name='Foto de perfil'
    )
    bio = models.TextField(blank=True, default='', verbose_name='Biografía')

    class Meta:
        db_table = 'usuarios_perfil'
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfiles'

    def __str__(self):
        return f'Perfil de {self.usuario.email}'

    def clean(self):
        super().clean()
        if self.foto and hasattr(self.foto, 'size') and self.foto.size > MAX_PERFIL_FOTO_SIZE:
            raise ValidationError(f'La foto excede el tamaño máximo permitido de {MAX_PERFIL_FOTO_SIZE // (1024*1024)} MB.')


class ConfiguracionClinica(models.Model):
    """Modelo singleton para la configuración de la clínica.

    Solo debe existir una instancia. Use ConfiguracionClinica.get_config() para obtenerla.
    Almacena información de la clínica usada en comprobantes PDF y reportes.
    """

    nombre = models.CharField(
        max_length=200,
        default='Huellitas Alegres',
        verbose_name='Nombre de la clínica',
    )
    nit = models.CharField(
        max_length=50,
        default='901.234.567-8',
        verbose_name='NIT',
    )
    direccion = models.CharField(
        max_length=200,
        default='Calle 10 # 25-30, Bogotá',
        verbose_name='Dirección',
    )
    telefono = models.CharField(
        max_length=50,
        default='601-555-0123',
        verbose_name='Teléfono',
    )
    email = models.EmailField(
        default='info@huellitasalegres.com',
        verbose_name='Email',
    )

    class Meta:
        db_table = 'usuarios_configuracionclinica'
        verbose_name = 'Configuración de Clínica'
        verbose_name_plural = 'Configuración de Clínica'

    def __str__(self):
        return self.nombre

    @classmethod
    def get_config(cls):
        """Obtiene la instancia singleton de configuración, creándola si es necesario."""
        config, _ = cls.objects.get_or_create(pk=1)
        return config