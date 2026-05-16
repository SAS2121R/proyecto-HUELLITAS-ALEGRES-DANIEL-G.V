from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.db import transaction

from productos.models import Producto, CATEGORIAS
from entregas.models import Pedido, PedidoItem
from usuarios.decorators import role_required
from .models import Carrito, CarritoItem


# ============================================================
# Cart persistence helpers: session ↔ DB synchronization
# HU#3: «El carrito debe mantener su contenido incluso si el
# cliente cierra la sesión y vuelve a ingresar al sistema.»
# ============================================================

def _get_cart_count(request):
    """Return total items in cart (session + persistent)."""
    cart = request.session.get('cart', {})
    return sum(item.get('quantity', 0) for item in cart.values())


def _sync_session_to_db(request):
    """Sync session cart data into the DB-backed Carrito.

    Called when user adds/updates/removes items AND after login.
    Merges quantities: if a product exists in both session and DB,
    the session quantity wins (most recent action).
    """
    if not request.user.is_authenticated:
        return

    cart_data = request.session.get('cart', {})
    if not cart_data:
        # If session cart is empty, don't touch DB (user may have cleared session only)
        return

    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)

    for pk_str, item_data in cart_data.items():
        producto = Producto.objects.filter(pk=int(pk_str)).first()
        if not producto:
            continue
        db_item, created = CarritoItem.objects.get_or_create(
            carrito=carrito,
            producto=producto,
            defaults={'cantidad': item_data['quantity']},
        )
        if not created:
            # Update quantity from session
            db_item.cantidad = item_data['quantity']
            db_item.save(update_fields=['cantidad'])

    # Remove DB items NOT in session (user removed them)
    product_ids_in_session = [int(pk) for pk in cart_data.keys()]
    CarritoItem.objects.filter(carrito=carrito).exclude(
        producto_id__in=product_ids_in_session
    ).delete()


def _sync_db_to_session(request):
    """Load DB cart into session (called after login).

    If session has items too, merges (DB + session, session wins on conflict).
    """
    if not request.user.is_authenticated:
        return

    try:
        carrito = Carrito.objects.select_related('usuario').get(usuario=request.user)
    except Carrito.DoesNotExist:
        return

    session_cart = request.session.get('cart', {})

    for item in carrito.items.select_related('producto'):
        pk_str = str(item.producto_id)
        if pk_str in session_cart:
            # Session wins — keep session data
            continue
        # Add from DB
        session_cart[pk_str] = {
            'name': item.producto.nombre,
            'price': str(item.producto.precio),
            'quantity': item.cantidad,
        }

    request.session['cart'] = session_cart
    request.session.modified = True


def _clear_db_cart(request):
    """Remove all DB cart items (called on vaciar_carrito and checkout)."""
    if not request.user.is_authenticated:
        return
    CarritoItem.objects.filter(carrito__usuario=request.user).delete()


# ============================================================
# Views
# ============================================================

@login_required(login_url='/usuarios/login/')
def catalogo(request):
    """Tienda — product catalog for Cliente to browse and add to cart.

    Any authenticated user can browse, but only Cliente can add to cart.
    Shows only active products (esta_activo=True) via Producto.objects manager.
    """
    qs = Producto.objects.select_related().order_by('categoria', 'nombre')

    # Search by name or description
    search = request.GET.get('q', '').strip()
    if search:
        qs = qs.filter(
            Q(nombre__icontains=search) | Q(descripcion__icontains=search)
        )

    # Filter by category
    categoria = request.GET.get('categoria', '').strip()
    if categoria:
        qs = qs.filter(categoria=categoria)

    # Only show products with positive stock (optional: show all but mark out-of-stock)
    qs = qs.filter(cantidad_stock__gt=0)

    # Paginate — 12 per page (3×4 grid)
    paginator = Paginator(qs, 12)
    page = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.page(1)

    return render(request, 'tienda/catalogo.html', {
        'page_obj': page_obj,
        'search': search,
        'categoria': categoria,
        'categorias': CATEGORIAS,
        'cart_count': _get_cart_count(request),
    })


@login_required(login_url='/usuarios/login/')
def detalle_producto(request, pk):
    """Tienda — product detail page for a single product.

    HU#3 / CU#8: «El sistema muestra información detallada del producto,
    incluyendo descripción, precio, disponibilidad y opciones de compra.»
    """
    producto = get_object_or_404(Producto, pk=pk, esta_activo=True)

    cart = request.session.get('cart', {})
    in_cart = str(pk) in cart
    cart_quantity = cart.get(str(pk), {}).get('quantity', 0) if in_cart else 0

    return render(request, 'tienda/detalle_producto.html', {
        'producto': producto,
        'cart_count': _get_cart_count(request),
        'in_cart': in_cart,
        'cart_quantity': cart_quantity,
    })


@role_required('Cliente')
def agregar_carrito(request, pk):
    """Add a product to the session cart. POST only.

    HU#3: Syncs to DB cart for cross-session persistence.
    Cart structure in session:
        {'<product_id>': {'name': str, 'price': str, 'quantity': int}}
    """
    if request.method != 'POST':
        return redirect('tienda:catalogo')

    producto = get_object_or_404(Producto, pk=pk)

    # Don't allow adding out-of-stock products
    if producto.cantidad_stock <= 0:
        messages.error(request, f'"{producto.nombre}" no está disponible.')
        return redirect('tienda:catalogo')

    cart = request.session.get('cart', {})
    product_key = str(pk)

    if product_key in cart:
        # Increase quantity but not beyond available stock
        current_qty = cart[product_key]['quantity']
        if current_qty >= producto.cantidad_stock:
            messages.warning(request, f'No hay más stock disponible de "{producto.nombre}".')
            return redirect('tienda:catalogo')
        cart[product_key]['quantity'] = current_qty + 1
    else:
        cart[product_key] = {
            'name': producto.nombre,
            'price': str(producto.precio),
            'quantity': 1,
        }

    request.session['cart'] = cart
    request.session.modified = True

    # HU#3: Sync to DB cart for persistence
    _sync_session_to_db(request)

    messages.success(request, f'"{producto.nombre}" agregado al carrito.')
    return redirect('tienda:catalogo')


@role_required('Cliente')
def carrito(request):
    """View and manage the shopping cart contents."""
    cart = request.session.get('cart', {})
    items = []
    total = Decimal('0.00')

    for pk_val, item_data in cart.items():
        producto = Producto.objects.filter(pk=int(pk_val)).first()
        if producto:
            subtotal = Decimal(item_data['price']) * item_data['quantity']
            items.append({
                'producto': producto,
                'quantity': item_data['quantity'],
                'price': Decimal(item_data['price']),
                'subtotal': subtotal,
            })
            total += subtotal

    return render(request, 'tienda/carrito.html', {
        'items': items,
        'total': total,
        'cart_count': _get_cart_count(request),
    })


@role_required('Cliente')
def actualizar_cantidad(request, pk):
    """Update quantity of a cart item. POST only."""
    if request.method != 'POST':
        return redirect('tienda:carrito')

    cart = request.session.get('cart', {})
    product_key = str(pk)

    if product_key not in cart:
        messages.error(request, 'Producto no encontrado en el carrito.')
        return redirect('tienda:carrito')

    producto = get_object_or_404(Producto, pk=pk)
    new_qty = int(request.POST.get('quantity', 1))

    if new_qty <= 0:
        # Remove from cart
        del cart[product_key]
        request.session['cart'] = cart
        request.session.modified = True
        _sync_session_to_db(request)
        messages.info(request, f'"{producto.nombre}" eliminado del carrito.')
    elif new_qty > producto.cantidad_stock:
        messages.error(request, f'Solo hay {producto.cantidad_stock} unidades de "{producto.nombre}".')
    else:
        cart[product_key]['quantity'] = new_qty
        request.session['cart'] = cart
        request.session.modified = True
        _sync_session_to_db(request)
        messages.success(request, f'Cantidad de "{producto.nombre}" actualizada.')

    return redirect('tienda:carrito')


@role_required('Cliente')
def eliminar_carrito(request, pk):
    """Remove a product from the cart. POST only."""
    if request.method != 'POST':
        return redirect('tienda:carrito')

    cart = request.session.get('cart', {})
    product_key = str(pk)

    if product_key in cart:
        producto = Producto.objects.filter(pk=int(pk)).first()
        name = producto.nombre if producto else 'Producto'
        del cart[product_key]
        request.session['cart'] = cart
        request.session.modified = True
        _sync_session_to_db(request)
        messages.info(request, f'"{name}" eliminado del carrito.')

    return redirect('tienda:carrito')


@role_required('Cliente')
def vaciar_carrito(request):
    """Empty the entire cart. POST only."""
    if request.method != 'POST':
        return redirect('tienda:carrito')

    request.session['cart'] = {}
    request.session.modified = True
    _clear_db_cart(request)
    messages.info(request, 'Carrito vaciado.')
    return redirect('tienda:carrito')


@login_required(login_url='/usuarios/login/')
def checkout(request):
    """Checkout: create a Pedido from the cart contents.

    Only Cliente can place orders. Address and phone are pre-filled
    from the user's profile. Domiciliario is auto-assigned (first available,
    or left blank for Admin to reassign).
    """
    if request.user.rol.nombre != 'Cliente':
        raise PermissionDenied

    cart = request.session.get('cart', {})

    if not cart:
        messages.warning(request, 'Tu carrito está vacío.')
        return redirect('tienda:catalogo')

    # Build cart items for display
    items = []
    total = Decimal('0.00')
    for pk_val, item_data in cart.items():
        producto = Producto.objects.filter(pk=int(pk_val)).first()
        if producto:
            subtotal = Decimal(item_data['price']) * item_data['quantity']
            items.append({
                'producto': producto,
                'quantity': item_data['quantity'],
                'price': Decimal(item_data['price']),
                'subtotal': subtotal,
            })
            total += subtotal

    if request.method == 'POST':
        direccion = request.POST.get('direccion_entrega', '').strip()
        telefono = request.POST.get('telefono_contacto', '').strip()
        notas = request.POST.get('notas', '').strip()

        if not direccion:
            messages.error(request, 'La dirección de entrega es obligatoria.')
            return render(request, 'tienda/checkout.html', {
                'items': items,
                'total': total,
                'cart_count': _get_cart_count(request),
                'direccion': direccion,
                'telefono': telefono,
            })

        if not telefono:
            messages.error(request, 'El teléfono de contacto es obligatorio.')
            return render(request, 'tienda/checkout.html', {
                'items': items,
                'total': total,
                'cart_count': _get_cart_count(request),
                'direccion': direccion,
                'telefono': telefono,
            })

        from usuarios.models import Usuario
        from entregas.views import asignar_domiciliario_disponible

        # Round-robin: assign to available domiciliario with least active orders
        domiciliario = asignar_domiciliario_disponible()

        # Create Pedido
        pedido = Pedido.objects.create(
            cliente=request.user,
            domiciliario=domiciliario,
            direccion_entrega=direccion,
            telefono_contacto=telefono,
            notas=notas,
            estado='pendiente',
        )

        # Create PedidoItems from cart
        for pk_val, item_data in cart.items():
            producto = Producto.objects.filter(pk=int(pk_val)).first()
            if producto:
                PedidoItem.objects.create(
                    pedido=pedido,
                    producto=producto,
                    cantidad=item_data['quantity'],
                )

        # Clear both session and DB cart
        request.session['cart'] = {}
        request.session.modified = True
        _clear_db_cart(request)

        messages.success(request, f'¡Pedido #{pedido.pk} creado exitosamente! Tu domiciliario asignado es {domiciliario.get_full_name() if domiciliario else "pendiente de asignación"}.')
        if not domiciliario:
            messages.warning(request, 'No hay domiciliarios disponibles en este momento. Un administrador asignará uno pronto.')
        return redirect('entregas:mis_pedidos')

    return render(request, 'tienda/checkout.html', {
        'items': items,
        'total': total,
        'cart_count': _get_cart_count(request),
    })