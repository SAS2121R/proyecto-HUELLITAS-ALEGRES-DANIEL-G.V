from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone

from usuarios.decorators import role_required
from .models import Pedido, ESTADO_CHOICES
from .forms import CambiarEstadoForm, EvidenciaForm, PedidoForm, PedidoItemFormSet


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
    """Detail view for a single pedido."""
    if request.user.rol.nombre == 'Cliente':
        raise PermissionDenied

    pedido = get_object_or_404(Pedido, pk=pk)

    # Domiciliario can only see their own pedidos
    if request.user.rol.nombre == 'Domiciliario' and pedido.domiciliario != request.user:
        raise PermissionDenied

    # Determine valid next states for the state change form
    estado_form = None
    evidencia_form = None

    if pedido.estado == 'pendiente' or pedido.estado == 'en_camino':
        estado_form = CambiarEstadoForm(estado_actual=pedido.estado)

    if pedido.estado == 'en_camino':
        # Show evidence form when transitioning to entregado
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
    if nuevo_estado == 'entregado':
        pedido.fecha_entrega = timezone.now()
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