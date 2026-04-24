"""
Signal: Auto stock deduction on HistorialClinico creation.

When a HistorialClinico is created with producto_aplicado set, and the product's
categoria is NOT 'servicios', automatically:
1. Deduct 1 from producto.cantidad_stock
2. Create a MovimientoInventario(tipo='salida', cantidad=1)

Uses transaction.atomic() for integrity.
Medical priority: NEVER block clinical record creation — stock CAN go negative.
"""
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from productos.models import MovimientoInventario


@receiver(post_save, sender='historial.HistorialClinico')
def deduct_stock_on_historial_create(sender, instance, created, **kwargs):
    """
    On HistorialClinico creation with producto_aplicado:
    - Skip if not created (updates don't deduct)
    - Skip if producto_aplicado is None
    - Skip if producto.categoria == 'servicios'
    - Deduct 1 from producto.cantidad_stock (can go negative)
    - Create MovimientoInventario(tipo='salida', cantidad=1)
    
    Medical priority: NEVER block the clinical record.
    Stock can go negative — that's an inventory problem, not a medical one.
    """
    if not created:
        return

    producto = instance.producto_aplicado
    if producto is None:
        return

    if producto.categoria == 'servicios':
        return

    with transaction.atomic():
        producto.cantidad_stock -= 1
        producto.save(update_fields=['cantidad_stock'])

        MovimientoInventario.objects.create(
            producto=producto,
            tipo_movimiento='salida',
            cantidad=1,
            usuario=instance.veterinario,
            historial_clinico=instance,
            motivo=f'Uso en consulta: {instance.get_tipo_consulta_display()}',
        )