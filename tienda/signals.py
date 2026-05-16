"""Signals for tienda app.

HU#3: On login, sync the DB-backed cart into the session so that
a client's cart persists across sessions.
"""

from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.contrib.auth import get_user_model

Usuario = get_user_model()


@receiver(user_logged_in)
def sync_cart_on_login(sender, request, user, **kwargs):
    """After login, load the DB cart into the session.

    If the session already has cart items (from anonymous browsing),
    the session data wins on conflict (most recent action).
    """
    from .models import Carrito, CarritoItem

    try:
        carrito = Carrito.objects.get(usuario=user)
    except Carrito.DoesNotExist:
        # No DB cart — nothing to merge
        return

    session_cart = request.session.get('cart', {})

    for item in carrito.items.select_related('producto'):
        pk_str = str(item.producto_id)
        if pk_str in session_cart:
            # Session data is more recent — keep it
            continue
        # Load DB item into session
        session_cart[pk_str] = {
            'name': item.producto.nombre,
            'price': str(item.producto.precio),
            'quantity': item.cantidad,
        }

    request.session['cart'] = session_cart
    request.session.modified = True