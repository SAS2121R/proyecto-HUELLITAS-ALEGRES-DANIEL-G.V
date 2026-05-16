from django.db import models
from django.conf import settings
from productos.models import Producto


class Carrito(models.Model):
    """HU#3: El carrito de compras debe mantener su contenido incluso si el
    cliente cierra la sesión y vuelve a ingresar al sistema en futuras visitas.

    Persiste el carrito en la base de datos vinculado al usuario.
    Al iniciar sesión, se sincroniza con el carrito de sesión.
    """

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='carrito',
        verbose_name='Usuario',
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación',
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Última actualización',
    )

    class Meta:
        db_table = 'tienda_carrito'
        verbose_name = 'Carrito'
        verbose_name_plural = 'Carritos'

    def __str__(self):
        return f'Carrito de {self.usuario.get_full_name() or self.usuario.email}'

    @property
    def total(self):
        """Calcula el total del carrito."""
        total = sum(item.subtotal for item in self.items.all())
        return total

    @property
    def cantidad_items(self):
        """Número total de productos en el carrito."""
        return sum(item.cantidad for item in self.items.all())


class CarritoItem(models.Model):
    """Item individual dentro de un carrito persistente."""

    carrito = models.ForeignKey(
        Carrito,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Carrito',
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        verbose_name='Producto',
    )
    cantidad = models.PositiveIntegerField(
        default=1,
        verbose_name='Cantidad',
    )

    class Meta:
        db_table = 'tienda_carrito_item'
        verbose_name = 'Item del carrito'
        verbose_name_plural = 'Items del carrito'
        unique_together = ('carrito', 'producto')

    def __str__(self):
        return f'{self.cantidad}x {self.producto.nombre}'

    @property
    def subtotal(self):
        """Subtotal para este item (precio × cantidad)."""
        return self.producto.precio * self.cantidad