from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from PIL import Image
import io

# Tamaño máximo para imágenes de producto: 5 MB (coherente con evidencias y perfiles)
MAX_PRODUCTO_IMAGEN_SIZE = 5 * 1024 * 1024  # 5242880 bytes
# Resolución máxima: la imagen se redimensiona automáticamente si excede estos valores
PRODUCTO_IMAGEN_MAX_WIDTH = 800
PRODUCTO_IMAGEN_MAX_HEIGHT = 800
# Calidad de compresión JPEG al redimensionar (1-95)
PRODUCTO_IMAGEN_CALIDAD = 85


def producto_imagen_upload_path(instance, filename):
    """Ruta: media/productos/<producto_pk>/<filename>"""
    return f'productos/{instance.pk or "nuevo"}/{filename}'


CATEGORIAS = [
    ('vacunas', 'Vacunas'),
    ('medicamentos', 'Medicamentos'),
    ('alimentos', 'Alimentos'),
    ('insumos', 'Insumos médicos'),
    ('higiene', 'Higiene y cuidado'),
    ('servicios', 'Servicios'),
    ('otros', 'Otros'),
]

TIPO_MOVIMIENTO_CHOICES = [
    ('entrada', 'Entrada'),
    ('salida', 'Salida'),
    ('ajuste', 'Ajuste'),
]


class ProductoManager(models.Manager):
    """Gestor que filtra productos eliminados suavemente por defecto."""

    def get_queryset(self):
        return super().get_queryset().filter(esta_activo=True)


class Producto(models.Model):
    """Modelo para representar un producto del inventario veterinario."""

    nombre = models.CharField(max_length=100, unique=True, verbose_name='Nombre')
    descripcion = models.TextField(blank=True, default='', verbose_name='Descripción')
    imagen = models.ImageField(
        upload_to=producto_imagen_upload_path,
        blank=True,
        null=True,
        verbose_name='Imagen del producto',
        help_text='Foto de referencia del producto. Opcional.',
    )
    categoria = models.CharField(
        max_length=20,
        choices=CATEGORIAS,
        default='otros',
        verbose_name='Categoría',
    )
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Precio unitario',
    )
    cantidad_stock = models.IntegerField(
        default=0,
        verbose_name='Cantidad en stock',
        help_text='Puede ser negativo para registrar inconsistencias.',
    )
    stock_minimo = models.IntegerField(
        default=10,
        validators=[MinValueValidator(0, message='El stock mínimo no puede ser negativo.')],
        verbose_name='Stock mínimo',
        help_text='Umbral de alerta.stock ≤ stock_minimo*1.5 = amarillo, stock = 0 = rojo.',
    )
    proveedor = models.ForeignKey(
        'proveedores.Proveedor',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Proveedor',
    )
    esta_activo = models.BooleanField(
        default=True,
        verbose_name='Activo',
        help_text='Soft delete. Desactivar en lugar de eliminar.',
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    fecha_ultima_modificacion = models.DateTimeField(auto_now=True, verbose_name='Última modificación')

    # Gestores: objects filtra esta_activo=True, all_objects devuelve todo
    objects = ProductoManager()
    all_objects = models.Manager()

    class Meta:
        db_table = 'productos'
        ordering = ['nombre']
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'

    def __str__(self):
        return self.nombre

    def clean(self):
        """Valida tamaño de imagen antes de guardar."""
        super().clean()
        if self.imagen and hasattr(self.imagen, 'size') and self.imagen.size > MAX_PRODUCTO_IMAGEN_SIZE:
            raise ValidationError({
                'imagen': f'La imagen excede el tamaño máximo permitido de {MAX_PRODUCTO_IMAGEN_SIZE // (1024*1024)} MB.'
            })

    def save(self, *args, **kwargs):
        """Redimensiona automáticamente imágenes de producto para optimizar carga y almacenamiento.

        Si la imagen excede 800x800px, se redimensiona manteniendo proporción.
        Se comprime a JPEG calidad 85 para reducir peso sin pérdida visible.
        """
        super().save(*args, **kwargs)

        if self.imagen:
            should_resize = False
            try:
                img = Image.open(self.imagen.path)
                img = img.convert('RGB')  # Asegurar formato compatible

                if img.width > PRODUCTO_IMAGEN_MAX_WIDTH or img.height > PRODUCTO_IMAGEN_MAX_HEIGHT:
                    img.thumbnail((PRODUCTO_IMAGEN_MAX_WIDTH, PRODUCTO_IMAGEN_MAX_HEIGHT), Image.LANCZOS)
                    should_resize = True

                if should_resize:
                    img.save(self.imagen.path, 'JPEG', quality=PRODUCTO_IMAGEN_CALIDAD, optimize=True)
            except Exception:
                pass  # Si falla resize, la imagen original queda guardada

    @property
    def estado_stock(self):
        """Retorna color del semáforo: 'verde', 'amarillo', o 'rojo'."""
        if self.cantidad_stock <= 0:
            return 'rojo'
        if self.cantidad_stock <= self.stock_minimo * 1.5:
            return 'amarillo'
        return 'verde'


class MovimientoInventario(models.Model):
    """Modelo para el Kardex — registro de entradas, salidas y ajustes de inventario."""

    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name='movimientos',
        verbose_name='Producto',
    )
    tipo_movimiento = models.CharField(
        max_length=10,
        choices=TIPO_MOVIMIENTO_CHOICES,
        verbose_name='Tipo de movimiento',
    )
    cantidad = models.IntegerField(
        validators=[MinValueValidator(1, message='La cantidad debe ser al menos 1.')],
        verbose_name='Cantidad',
    )
    fecha = models.DateTimeField(auto_now_add=True, verbose_name='Fecha')
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Usuario',
    )
    historial_clinico = models.ForeignKey(
        'historial.HistorialClinico',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movimientos_inventario',
        verbose_name='Historial clínico',
    )
    motivo = models.CharField(
        max_length=200,
        blank=True,
        default='',
        verbose_name='Motivo',
    )

    class Meta:
        db_table = 'productos_movimientoinventario'
        ordering = ['-fecha']
        verbose_name = 'Movimiento de inventario'
        verbose_name_plural = 'Movimientos de inventario'

    def __str__(self):
        return f"{self.get_tipo_movimiento_display()} - {self.producto.nombre} ({self.cantidad})"