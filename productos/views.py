from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.exceptions import PermissionDenied

from usuarios.decorators import role_required
from .models import Producto, MovimientoInventario, CATEGORIAS
from .forms import ProductoForm, MovimientoInventarioForm


@role_required('Veterinario', 'Administrador')
def lista_productos(request):
    """Lista productos activos con búsqueda y filtro por categoría.

    Solo Vet y Admin pueden gestionar productos. El Cliente usa la Tienda.
    """
    qs = Producto.objects.select_related().order_by('nombre')

    search = request.GET.get('q', '').strip()
    if search:
        qs = qs.filter(
            Q(nombre__icontains=search)
            | Q(proveedor__nombre__icontains=search)
        )

    categoria = request.GET.get('categoria', '').strip()
    if categoria:
        qs = qs.filter(categoria=categoria)

    paginator = Paginator(qs, 10)
    page = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.page(1)

    # Productos con alertas de stock para la barra lateral
    alert_products = [p for p in Producto.objects.all() if p.estado_stock != 'verde']

    return render(request, 'productos/product_list.html', {
        'page_obj': page_obj,
        'search': search,
        'categoria': categoria,
        'categorias': CATEGORIAS,
        'alert_products': alert_products,
    })


@role_required('Veterinario', 'Administrador')
def create_product(request):
    """Crear nuevo producto. Requiere rol Vet o Admin."""
    form = ProductoForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Producto creado exitosamente.')
        return redirect('productos:lista')
    return render(request, 'productos/product_form.html', {'form': form})


@role_required('Veterinario', 'Administrador')
def edit_product(request, pk):
    """Editar producto existente. Requiere rol Vet o Admin."""
    prod = get_object_or_404(Producto.all_objects, pk=pk)
    form = ProductoForm(request.POST or None, request.FILES or None, instance=prod)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Producto actualizado exitosamente.')
        return redirect('productos:lista')
    return render(request, 'productos/product_form.html', {'form': form, 'producto': prod})


@role_required('Veterinario', 'Administrador')
def delete_product(request, pk):
    """Eliminar suavemente un producto (establece esta_activo=False). Requiere rol Vet o Admin."""
    prod = get_object_or_404(Producto.all_objects, pk=pk)
    if request.method == 'POST':
        prod.esta_activo = False
        prod.save()
        messages.success(request, f'Producto "{prod.nombre}" desactivado exitosamente.')
        return redirect('productos:lista')
    return render(request, 'productos/product_confirm_delete.html', {'producto': prod})


@role_required('Veterinario', 'Administrador')
def entrada_inventario(request):
    """Entrada manual de stock. Crea MovimientoInventario y actualiza el stock."""
    form = MovimientoInventarioForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        mov = form.save(commit=False)
        mov.usuario = request.user
        mov.tipo_movimiento = 'entrada'  # Forzar entrada para esta vista
        mov.save()
        # Actualizar stock
        producto = mov.producto
        producto.cantidad_stock += mov.cantidad
        producto.save(update_fields=['cantidad_stock'])
        messages.success(request, f'Entrada de {mov.cantidad} unidades de "{producto.nombre}" registrada.')
        return redirect('productos:lista')
    return render(request, 'productos/movimiento_form.html', {
        'form': form,
        'tipo': 'Entrada',
    })


@role_required('Veterinario', 'Administrador')
def kardex_producto(request, pk):
    """Kardex — historial de movimientos de un producto específico. Solo Vet/Admin."""
    producto = get_object_or_404(Producto.all_objects, pk=pk)
    movimientos = MovimientoInventario.objects.filter(
        producto=producto
    ).select_related('usuario', 'historial_clinico').order_by('-fecha')

    paginator = Paginator(movimientos, 15)
    page = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.page(1)

    return render(request, 'productos/kardex.html', {
        'producto': producto,
        'page_obj': page_obj,
    })


@role_required('Veterinario', 'Administrador')
def alertas_stock(request):
    """Mostrar productos con alertas de stock (estado_stock != 'verde'). Solo Vet/Admin."""
    alert_products = [p for p in Producto.objects.all() if p.estado_stock != 'verde']
    return render(request, 'productos/alertas.html', {
        'alert_products': alert_products,
    })


@login_required(login_url='/usuarios/login/')
def inicio(request):
    """Vista para la página de inicio de productos."""
    context = {
        'tienda': 'huellitas_alegres',
        'descripcion': 'Venta de productos para clinica veterinaria',
        'usuario': request.user,
    }
    return render(request, 'inicio.html', context)