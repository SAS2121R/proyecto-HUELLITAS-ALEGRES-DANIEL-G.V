from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

from productos.models import Producto, CATEGORIAS
from entregas.models import Pedido, PedidoItem
from usuarios.decorators import role_required


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

    # Get cart item count for badge
    cart = request.session.get('cart', {})
    cart_count = sum(item.get('quantity', 0) for item in cart.values())

    return render(request, 'tienda/catalogo.html', {
        'page_obj': page_obj,
        'search': search,
        'categoria': categoria,
        'categorias': CATEGORIAS,
        'cart_count': cart_count,
    })


@role_required('Cliente')
def agregar_carrito(request, pk):
    """Add a product to the session cart. POST only.

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
    messages.success(request, f'"{producto.nombre}" agregado al carrito.')
    return redirect('tienda:catalogo')


@role_required('Cliente')
def carrito(request):
    """View and manage the shopping cart contents."""
    cart = request.session.get('cart', {})
    items = []
    total = Decimal('0.00')

    for pk, item_data in cart.items():
        producto = Producto.objects.filter(pk=int(pk)).first()
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
        'cart_count': sum(item_data.get('quantity', 0) for item_data in cart.values()),
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
        messages.info(request, f'"{producto.nombre}" eliminado del carrito.')
    elif new_qty > producto.cantidad_stock:
        messages.error(request, f'Solo hay {producto.cantidad_stock} unidades de "{producto.nombre}".')
    else:
        cart[product_key]['quantity'] = new_qty
        request.session['cart'] = cart
        request.session.modified = True
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
        messages.info(request, f'"{name}" eliminado del carrito.')

    return redirect('tienda:carrito')


@role_required('Cliente')
def vaciar_carrito(request):
    """Empty the entire cart. POST only."""
    if request.method != 'POST':
        return redirect('tienda:carrito')

    request.session['cart'] = {}
    request.session.modified = True
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
    for pk, item_data in cart.items():
        producto = Producto.objects.filter(pk=int(pk)).first()
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
                'cart_count': sum(i.get('quantity', 0) for i in cart.values()),
                'direccion': direccion,
                'telefono': telefono,
            })

        if not telefono:
            messages.error(request, 'El teléfono de contacto es obligatorio.')
            return render(request, 'tienda/checkout.html', {
                'items': items,
                'total': total,
                'cart_count': sum(i.get('quantity', 0) for i in cart.values()),
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
        for pk, item_data in cart.items():
            producto = Producto.objects.filter(pk=int(pk)).first()
            if producto:
                PedidoItem.objects.create(
                    pedido=pedido,
                    producto=producto,
                    cantidad=item_data['quantity'],
                )

        # Clear the cart
        request.session['cart'] = {}
        request.session.modified = True

        messages.success(request, f'¡Pedido #{pedido.pk} creado exitosamente! Tu domiciliario asignado es {domiciliario.get_full_name() if domiciliario else "pendiente de asignación"}.')
        if not domiciliario:
            messages.warning(request, 'No hay domiciliarios disponibles en este momento. Un administrador asignará uno pronto.')
        return redirect('entregas:mis_pedidos')

    return render(request, 'tienda/checkout.html', {
        'items': items,
        'total': total,
        'cart_count': sum(i.get('quantity', 0) for i in cart.values()),
    })