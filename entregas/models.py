from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from decimal import Decimal


ESTADO_CHOICES = [
    ('pendiente', 'Pendiente'),
    ('en_camino', 'En Camino'),
    ('entregado', 'Entregado'),
    ('cancelado', 'Cancelado'),
]

# Tamaño máximo para fotos de evidencia: 5 MB — reutiliza el mismo patrón que Adjunto
MAX_EVIDENCIA_SIZE = 5 * 1024 * 1024  # 5242880 bytes


def evidencia_upload_path(instance, filename):
    """Ruta de subida: media/evidencias/<pedido_pk>/<filename>"""
    return f'evidencias/{instance.pk}/{filename}'


def firma_upload_path(instance, filename):
    """Ruta de subida: media/firmas/<pedido_pk>/<filename>"""
    return f'firmas/{instance.pk}/{filename}'


class Pedido(models.Model):
    """Modelo para representar un pedido de entrega domiciliaria.

    Estados (reciclados de Cita):
        pendiente  → Pedido creado, esperando domiciliario
        en_camino  → Domiciliario en ruta de entrega
        entregado  → Pedido entregado exitosamente
        cancelado  → Pedido cancelado (requiere incidente_notas)

    Transiciones válidas:
        pendiente → en_camino, cancelado
        en_camino → entregado, cancelado
        entregado  → (ninguna — estado final)
        cancelado  → (ninguna — estado final)
    """

    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='pedidos_como_cliente',
        limit_choices_to={'rol__nombre': 'Cliente'},
        verbose_name='Cliente',
    )
    domiciliario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='pedidos_como_domiciliario',
        limit_choices_to={'rol__nombre': 'Domiciliario'},
        verbose_name='Domiciliario',
        null=True,
        blank=True,
        help_text='Se asigna automáticamente al crear el pedido, o el Admin puede reasignarlo después.',
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente',
        verbose_name='Estado',
    )
    direccion_entrega = models.CharField(
        max_length=200,
        verbose_name='Dirección de entrega',
    )
    telefono_contacto = models.CharField(
        max_length=15,
        verbose_name='Teléfono de contacto',
    )
    notas = models.TextField(
        blank=True,
        default='',
        verbose_name='Instrucciones especiales',
    )
    # Incidente (paso 7-8)
    incidente_notas = models.TextField(
        blank=True,
        default='',
        verbose_name='Notas de incidente',
    )
    incidente_fecha = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha del incidente',
    )
    # Evidencia (paso 11)
    foto_evidencia = models.ImageField(
        upload_to=evidencia_upload_path,
        blank=False,
        verbose_name='Foto de evidencia',
        help_text='Foto del paquete entregado. Obligatorio. Máximo 5MB.',
    )
    firma_imagen = models.ImageField(
        upload_to=firma_upload_path,
        blank=False,
        verbose_name='Firma del cliente',
        help_text='Imagen de la firma del cliente. Obligatorio. Máximo 5MB.',
    )
    # Marcas de tiempo
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación',
    )
    fecha_entrega = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de entrega',
    )

    class Meta:
        db_table = 'entregas_pedido'
        ordering = ['-fecha_creacion']
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'

    def __str__(self):
        return f"Pedido #{self.pk} — {self.get_estado_display()}"

    @property
    def total(self):
        """Suma de todos los subtotales de PedidoItem."""
        return sum((item.subtotal for item in self.items.all()), Decimal('0.00'))

    def clean(self):
        """Valida transiciones de estado y reglas de negocio."""
        errors = {}

        # Validación de transición de estado (refleja el patrón de Cita)
        if self.pk:
            try:
                old = Pedido.objects.get(pk=self.pk)
                # Entregado es final — no se puede cambiar
                if old.estado == 'entregado' and self.estado != 'entregado':
                    errors['estado'] = 'No se puede cambiar el estado de un pedido entregado.'
                # Cancelado es final — no se puede reactivar
                if old.estado == 'cancelado' and self.estado != 'cancelado':
                    errors['estado'] = 'No se puede reactivar un pedido cancelado.'
            except Pedido.DoesNotExist:
                pass

        # Cancelado requiere incidente_notas
        if self.estado == 'cancelado' and not self.incidente_notas:
            errors['incidente_notas'] = 'Debe indicar el motivo de la cancelación/incidente.'

        # Validación de tamaño de foto_evidencia (reutiliza patrón de Adjunto)
        if self.foto_evidencia and hasattr(self.foto_evidencia, 'size') and self.foto_evidencia.size > MAX_EVIDENCIA_SIZE:
            errors['foto_evidencia'] = (
                f'La foto excede el tamaño máximo permitido de {MAX_EVIDENCIA_SIZE // (1024*1024)} MB.'
            )

        # Validación de tamaño de firma_imagen (mismo patrón)
        if self.firma_imagen and hasattr(self.firma_imagen, 'size') and self.firma_imagen.size > MAX_EVIDENCIA_SIZE:
            errors['firma_imagen'] = (
                f'La firma excede el tamaño máximo permitido de {MAX_EVIDENCIA_SIZE // (1024*1024)} MB.'
            )

        if errors:
            raise ValidationError(errors)


class PedidoItem(models.Model):
    """Detalle de producto en un pedido — modelo pivot entre Pedido y Producto."""

    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Pedido',
    )
    producto = models.ForeignKey(
        'productos.Producto',
        on_delete=models.PROTECT,
        related_name='pedido_items',
        verbose_name='Producto',
    )
    cantidad = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1, message='La cantidad debe ser al menos 1.')],
        verbose_name='Cantidad',
    )

    class Meta:
        db_table = 'entregas_pedidoitem'
        verbose_name = 'Item del pedido'
        verbose_name_plural = 'Items del pedido'

    def __str__(self):
        return f"{self.producto.nombre} × {self.cantidad}"

    @property
    def subtotal(self):
        """precio × cantidad."""
        if self.producto_id and self.producto.precio:
            return self.producto.precio * self.cantidad
        return Decimal('0.00')