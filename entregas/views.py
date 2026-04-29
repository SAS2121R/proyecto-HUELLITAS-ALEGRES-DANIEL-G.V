from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponse
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from xhtml2pdf import pisa
import io

from usuarios.models import ConfiguracionClinica
from usuarios.decorators import role_required
from .models import Pedido, ESTADO_CHOICES
from .forms import CambiarEstadoForm, EvidenciaForm, PedidoForm, PedidoItemFormSet, ReasignarDomiciliarioForm
from productos.models import Producto, MovimientoInventario


@login_required(login_url='/usuarios/login/')
def dashboard(request):
    """Dashboard domiciliario — shows pedidos assigned to current user.
    Admin sees all, Domiciliario sees only their own."""
    if request.user.rol.nombre == 'Cliente':
        raise PermissionDenied

    if request.user.rol.nombre == 'Administrador':
        pedidos = Pedido.objects.select_related('cliente', 'domiciliario').prefetch_related('items__producto')
    else:  # Domiciliario
        pedidos = Pedido.objects.filter(domiciliario=request.user).select_related('cliente', 'domiciliario').prefetch_related('items__producto')

    # Filter by estado
    estado = request.GET.get('estado', '').strip()
    if estado:
        pedidos = pedidos.filter(estado=estado)

    pedidos = pedidos.order_by('-fecha_creacion')
    paginator = Paginator(pedidos, 10)
    page = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.page(1)

    return render(request, 'entregas/dashboard.html', {
        'page_obj': page_obj,
        'estado_filter': estado,
        'estados': ESTADO_CHOICES,
    })


@login_required(login_url='/usuarios/login/')
def pedido_detalle(request, pk):
    """Detail view for a single pedido.
    Admin/Domiciliario see their pedidos with action buttons.
    Cliente sees their own pedidos (read-only, no action buttons)."""
    pedido = get_object_or_404(Pedido, pk=pk)

    # Cliente can only see their own pedidos
    if request.user.rol.nombre == 'Cliente' and pedido.cliente != request.user:
        raise PermissionDenied

    # Domiciliario can only see their own pedidos
    if request.user.rol.nombre == 'Domiciliario' and pedido.domiciliario != request.user:
        raise PermissionDenied

    # Determine valid next states for the state change form
    # Only show for Domiciliario and Admin (not Cliente)
    estado_form = None
    evidencia_form = None

    if request.user.rol.nombre != 'Cliente':
        if pedido.estado == 'pendiente' or pedido.estado == 'en_camino':
            estado_form = CambiarEstadoForm(estado_actual=pedido.estado)

        if pedido.estado == 'en_camino':
            evidencia_form = EvidenciaForm(instance=pedido)

    return render(request, 'entregas/detalle.html', {
        'pedido': pedido,
        'estado_form': estado_form,
        'evidencia_form': evidencia_form,
    })


@login_required(login_url='/usuarios/login/')
def cambiar_estado(request, pk):
    """Change pedido estado — POST only. Handles transitions and evidence."""
    if request.method != 'POST':
        return redirect('entregas:detalle', pk=pk)

    if request.user.rol.nombre == 'Cliente':
        raise PermissionDenied

    pedido = get_object_or_404(Pedido, pk=pk)

    # Domiciliario can only modify their own pedidos
    if request.user.rol.nombre == 'Domiciliario' and pedido.domiciliario != request.user:
        raise PermissionDenied

    nuevo_estado = request.POST.get('nuevo_estado', '').strip()
    incidente_notas = request.POST.get('incidente_notas', '').strip()

    # Validate transition
    valid_transitions = {
        'pendiente': ['en_camino', 'cancelado'],
        'en_camino': ['entregado', 'cancelado'],
    }

    if nuevo_estado not in valid_transitions.get(pedido.estado, []):
        messages.error(request, f'Transición no válida: {pedido.get_estado_display()} → {nuevo_estado}')
        return redirect('entregas:detalle', pk=pk)

    # Handle evidence photos for entregado
    if nuevo_estado == 'entregado':
        evidencia_form = EvidenciaForm(request.POST, request.FILES, instance=pedido)
        if evidencia_form.is_valid():
            evidencia_form.save()
        else:
            for field, errors in evidencia_form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
            return redirect('entregas:detalle', pk=pk)

    # Handle cancellation requires incidente_notas
    if nuevo_estado == 'cancelado' and not incidente_notas:
        messages.error(request, 'Debe indicar el motivo de la cancelación.')
        return redirect('entregas:detalle', pk=pk)

    # Apply state change
    pedido.estado = nuevo_estado
    if nuevo_estado == 'cancelado':
        pedido.incidente_notas = incidente_notas
        pedido.incidente_fecha = timezone.now()
    if nuevo_estado == 'entregado':
        pedido.fecha_entrega = timezone.now()
        # Deduct stock from each item's product
        for item in pedido.items.select_related('producto'):
            producto = item.producto
            producto.cantidad_stock -= item.cantidad
            producto.save()
            MovimientoInventario.objects.create(
                producto=producto,
                tipo_movimiento='salida',
                cantidad=item.cantidad,
                usuario=request.user,
                motivo=f'Entrega Pedido #{pedido.pk}',
            )
    pedido.save()

    estado_labels = {'pendiente': 'Pendiente', 'en_camino': 'En Camino', 'entregado': 'Entregado', 'cancelado': 'Cancelado'}
    messages.success(request, f'Pedido #{pedido.pk} actualizado a {estado_labels.get(nuevo_estado, nuevo_estado)}')
    return redirect('entregas:dashboard')


@role_required('Administrador')
def crear_pedido(request):
    """Admin-only view to create a new Pedido with items."""
    if request.method == 'POST':
        form = PedidoForm(request.POST)
        formset = PedidoItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            pedido = form.save()
            formset.instance = pedido
            items = formset.save()
            messages.success(request, f'Pedido #{pedido.pk} creado exitosamente.')
            return redirect('entregas:detalle', pk=pedido.pk)
    else:
        form = PedidoForm()
        formset = PedidoItemFormSet()
    return render(request, 'entregas/pedido_form.html', {
        'form': form,
        'formset': formset,
    })


@login_required(login_url='/usuarios/login/')
def resumen(request):
    """Daily summary of delivered pedidos — Domiciliario sees own, Admin sees all."""
    if request.user.rol.nombre == 'Cliente':
        raise PermissionDenied

    today = timezone.now().date()
    if request.user.rol.nombre == 'Administrador':
        pedidos = Pedido.objects.filter(estado='entregado', fecha_entrega__date=today)
    else:  # Domiciliario
        pedidos = Pedido.objects.filter(estado='entregado', fecha_entrega__date=today, domiciliario=request.user)

    pedidos = pedidos.select_related('cliente', 'domiciliario').prefetch_related('items__producto').order_by('-fecha_entrega')
    total_entregas = pedidos.count()
    total_dia = sum(p.total for p in pedidos) if pedidos else 0

    return render(request, 'entregas/resumen.html', {
        'pedidos_entregados': pedidos,
        'total_entregas': total_entregas,
        'total_dia': total_dia,
        'fecha': today,
    })


@login_required(login_url='/usuarios/login/')
def mis_pedidos(request):
    """Cliente sees their own pedidos only."""
    if request.user.rol.nombre != 'Cliente':
        raise PermissionDenied

    pedidos = Pedido.objects.filter(cliente=request.user).select_related('domiciliario').prefetch_related('items__producto').order_by('-fecha_creacion')
    paginator = Paginator(pedidos, 10)
    page = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.page(1)

    return render(request, 'entregas/mis_pedidos.html', {
        'page_obj': page_obj,
    })


@role_required('Administrador')
def editar_pedido(request, pk):
    """Admin-only view to edit a pedido (reassign domiciliario, change address)."""
    pedido = get_object_or_404(Pedido, pk=pk)

    if request.method == 'POST':
        form = PedidoForm(request.POST, instance=pedido)
        if form.is_valid():
            form.save()
            messages.success(request, f'Pedido #{pedido.pk} actualizado exitosamente.')
            return redirect('entregas:detalle', pk=pedido.pk)
    else:
        form = PedidoForm(instance=pedido)

    return render(request, 'entregas/editar_pedido.html', {
        'form': form,
        'pedido': pedido,
    })


@login_required(login_url='/usuarios/login/')
def comprobante_pdf(request, pk):
    """Generate PDF comprobante for an entregado pedido.
    Only available when estado == 'entregado'.
    Admin/Domiciliario see any; Cliente sees only their own."""
    pedido = get_object_or_404(Pedido, pk=pk)

    # Only entregado pedidos have a comprobante
    if pedido.estado != 'entregado':
        raise Http404('Comprobante solo disponible para pedidos entregados.')

    # Cliente can only see their own comprobantes
    if request.user.rol.nombre == 'Cliente' and pedido.cliente != request.user:
        raise Http404('Pedido no encontrado.')

    # Domiciliario can only see their own comprobantes
    if request.user.rol.nombre == 'Domiciliario' and pedido.domiciliario != request.user:
        raise PermissionDenied

    context = {
        'pedido': pedido,
        'items': pedido.items.select_related('producto').all(),
        'config': ConfiguracionClinica.get_config(),
    }
    html = render_to_string('entregas/comprobante_pdf.html', context)
    buf = io.BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=buf)
    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)
    buf.seek(0)
    response = HttpResponse(buf.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'filename="comprobante_pedido_{pedido.pk}.pdf"'
    return response


@login_required(login_url='/usuarios/login/')
@role_required('Administrador')
def torre_control(request):
    """Control Tower — Admin-only global view of all pedidos with reassign capability.

    Shows all pedidos with filters by estado and search by client.
    Allows inline reassignment of domiciliario for pendiente/en_camino pedidos.
    """
    from django.db.models import Q as DbQ
    pedidos = Pedido.objects.select_related('cliente', 'domiciliario').prefetch_related('items__producto').order_by('-fecha_creacion')

    # Filter by estado
    estado = request.GET.get('estado', '').strip()
    if estado:
        pedidos = pedidos.filter(estado=estado)

    # Search by client name or pedido #
    search = request.GET.get('q', '').strip()
    if search:
        pedidos = pedidos.filter(
            DbQ(cliente__first_name__icontains=search)
            | DbQ(cliente__email__icontains=search)
            | DbQ(pk__icontains=search)
            | DbQ(direccion_entrega__icontains=search)
        )

    # Summary stats
    total_pedidos = pedidos.count()
    pendientes = Pedido.objects.filter(estado='pendiente').count()
    en_camino = Pedido.objects.filter(estado='en_camino').count()
    entregados = Pedido.objects.filter(estado='entregado').count()
    cancelados = Pedido.objects.filter(estado='cancelado').count()

    # Handle reassign POST
    if request.method == 'POST':
        pedido_pk = request.POST.get('pedido_pk')
        new_dom_pk = request.POST.get('domiciliario')
        if pedido_pk and new_dom_pk:
            from usuarios.models import Usuario
            pedido = get_object_or_404(Pedido, pk=pedido_pk)
            new_dom = get_object_or_404(Usuario, pk=new_dom_pk, rol__nombre='Domiciliario')
            if pedido.estado in ('pendiente', 'en_camino'):
                pedido.domiciliario = new_dom
                pedido.save(update_fields=['domiciliario'])
                messages.success(request, f'Domiciliario de Pedido #{pedido.pk} reasignado a {new_dom.get_full_name()}.')
            else:
                messages.error(request, 'Solo se puede reasignar pedidos pendientes o en camino.')
        return redirect('entregas:torre_control')

    paginator = Paginator(pedidos, 15)
    page = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.page(1)

    # Get domiciliarios for the reassign dropdown
    from usuarios.models import Usuario
    domiciliarios = Usuario.objects.filter(rol__nombre='Domiciliario', is_active=True).order_by('first_name')

    return render(request, 'entregas/torre_control.html', {
        'page_obj': page_obj,
        'estado': estado,
        'search': search,
        'estados': ESTADO_CHOICES,
        'total_pedidos': total_pedidos,
        'pendientes': pendientes,
        'en_camino': en_camino,
        'entregados': entregados,
        'cancelados': cancelados,
        'domiciliarios': domiciliarios,
    })