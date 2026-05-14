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

from django.db.models import Count, Q
from usuarios.models import ConfiguracionClinica, Usuario
from usuarios.decorators import role_required
from .models import Pedido, ESTADO_CHOICES
from .forms import CambiarEstadoForm, EvidenciaForm, PedidoForm, PedidoItemFormSet, ReasignarDomiciliarioForm
from productos.models import Producto, MovimientoInventario


def asignar_domiciliario_disponible():
    """Asigna el domiciliario disponible con MENOS pedidos activos (pendiente + en_camino).
    Round-robin justo: el que menos carga tiene recibe el pedido nuevo.
    Retorna None si no hay domiciliarios disponibles."""
    domiciliarios = Usuario.objects.filter(
        rol__nombre='Domiciliario',
        is_active=True,
        is_disponible=True,
    ).annotate(
        pedidos_activos=Count(
            'pedidos_como_domiciliario',
            filter=Q(pedidos_como_domiciliario__estado__in=['pendiente', 'en_camino']),
        )
    ).order_by('pedidos_activos', 'id')
    return domiciliarios.first()


@login_required(login_url='/usuarios/login/')
def dashboard(request):
    """Dashboard domiciliario — muestra pedidos asignados al usuario actual.
    Admin ve todos, Domiciliario ve solo los suyos."""
    if request.user.rol.nombre == 'Cliente':
        raise PermissionDenied

    if request.user.rol.nombre == 'Administrador':
        pedidos = Pedido.objects.select_related('cliente', 'domiciliario').prefetch_related('items__producto')
    else:  # Domiciliario
        pedidos = Pedido.objects.filter(domiciliario=request.user).select_related('cliente', 'domiciliario').prefetch_related('items__producto')

    # Filtrar por estado
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
    """Vista de detalle para un solo pedido.
    Admin/Domiciliario ven sus pedidos con botones de acción.
    Cliente ve sus propios pedidos (solo lectura, sin botones de acción)."""
    pedido = get_object_or_404(Pedido, pk=pk)

    # Cliente solo puede ver sus propios pedidos
    if request.user.rol.nombre == 'Cliente' and pedido.cliente != request.user:
        raise PermissionDenied

    # Domiciliario solo puede ver sus propios pedidos
    if request.user.rol.nombre == 'Domiciliario' and pedido.domiciliario != request.user:
        raise PermissionDenied

    # Determinar los próximos estados válidos para el formulario de cambio de estado
    # Solo mostrar para Domiciliario y Admin (no Cliente)
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
    """Cambiar estado del pedido — solo POST. Maneja transiciones y evidencia."""
    if request.method != 'POST':
        return redirect('entregas:detalle', pk=pk)

    if request.user.rol.nombre == 'Cliente':
        raise PermissionDenied

    pedido = get_object_or_404(Pedido, pk=pk)

    # Domiciliario solo puede modificar sus propios pedidos
    if request.user.rol.nombre == 'Domiciliario' and pedido.domiciliario != request.user:
        raise PermissionDenied

    nuevo_estado = request.POST.get('nuevo_estado', '').strip()
    incidente_notas = request.POST.get('incidente_notas', '').strip()

    # Validar transición
    valid_transitions = {
        'pendiente': ['en_camino', 'cancelado'],
        'en_camino': ['entregado', 'cancelado'],
    }

    if nuevo_estado not in valid_transitions.get(pedido.estado, []):
        messages.error(request, f'Transición no válida: {pedido.get_estado_display()} → {nuevo_estado}')
        return redirect('entregas:detalle', pk=pk)

    # Manejar fotos de evidencia para entregado (AMBAS obligatorias)
    if nuevo_estado == 'entregado':
        foto = request.FILES.get('foto_evidencia')
        firma = request.FILES.get('firma_imagen')
        if not foto or not firma:
            messages.error(request, '¡Error! Es obligatorio cargar tanto la foto de evidencia como la firma del cliente.')
            return redirect('entregas:detalle', pk=pk)
        evidencia_form = EvidenciaForm(request.POST, request.FILES, instance=pedido)
        if evidencia_form.is_valid():
            evidencia_form.save()
        else:
            for field, errors in evidencia_form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
            return redirect('entregas:detalle', pk=pk)

    # Manejar cancelación requiere incidente_notas
    if nuevo_estado == 'cancelado' and not incidente_notas:
        messages.error(request, 'Debe indicar el motivo de la cancelación.')
        return redirect('entregas:detalle', pk=pk)

    # Aplicar cambio de estado
    pedido.estado = nuevo_estado
    if nuevo_estado == 'cancelado':
        pedido.incidente_notas = incidente_notas
        pedido.incidente_fecha = timezone.now()
        # Marcar domiciliario como no disponible si tenía uno asignado
        if pedido.domiciliario:
            pedido.domiciliario.is_disponible = False
            pedido.domiciliario.save(update_fields=['is_disponible'])
            messages.warning(request, f'{pedido.domiciliario.get_full_name() or pedido.domiciliario.email} marcado como No Disponible. Puede reincorporarlo desde la Torre de Control.')
    if nuevo_estado == 'entregado':
        pedido.fecha_entrega = timezone.now()
        # Descontar stock del producto de cada item
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
    """Vista solo para Admin para crear un nuevo Pedido con items.
    Si no se selecciona domiciliario, se asigna automáticamente al disponible con menos carga."""
    if request.method == 'POST':
        form = PedidoForm(request.POST)
        formset = PedidoItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            pedido = form.save(commit=False)
            # Asignar domiciliario automático si no se seleccionó uno
            if not pedido.domiciliario_id:
                dom = asignar_domiciliario_disponible()
                if dom:
                    pedido.domiciliario = dom
                    messages.info(request, f'Domiciliario asignado automáticamente: {dom.get_full_name() or dom.email}')
                else:
                    messages.warning(request, 'No hay domiciliarios disponibles. El pedido quedó sin domiciliario asignado.')
            pedido.save()
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
    """Resumen diario de pedidos entregados — Domiciliario ve los suyos, Admin ve todos."""
    if request.user.rol.nombre == 'Cliente':
        raise PermissionDenied

    today = timezone.localdate()
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
    """Cliente ve solo sus propios pedidos."""
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
    """Vista solo para Admin para editar un pedido (reasignar domiciliario, cambiar dirección)."""
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
    """Generar PDF comprobante para un pedido entregado.
    Solo disponible cuando estado == 'entregado'.
    Admin/Domiciliario ven cualquiera; Cliente ve solo los suyos."""
    pedido = get_object_or_404(Pedido, pk=pk)

    # Solo pedidos entregados tienen comprobante
    if pedido.estado != 'entregado':
        raise Http404('Comprobante solo disponible para pedidos entregados.')

    # Cliente solo puede ver sus propios comprobantes
    if request.user.rol.nombre == 'Cliente' and pedido.cliente != request.user:
        raise Http404('Pedido no encontrado.')

    # Domiciliario solo puede ver sus propios comprobantes
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
        return HttpResponse('Error al generar PDF', status=500)
    buf.seek(0)
    response = HttpResponse(buf.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'filename="comprobante_pedido_{pedido.pk}.pdf"'
    return response


@login_required(login_url='/usuarios/login/')
@role_required('Administrador')
def torre_control(request):
    """Torre de Control — Vista global solo para Admin de todos los pedidos con capacidad de reasignar.

    Muestra todos los pedidos con filtros por estado y búsqueda por cliente.
    Permite reasignación inline del domiciliario para pedidos pendiente/en_camino.
    """
    from django.db.models import Q as DbQ
    pedidos = Pedido.objects.select_related('cliente', 'domiciliario').prefetch_related('items__producto').order_by('-fecha_creacion')

    # Filtrar por estado
    estado = request.GET.get('estado', '').strip()
    if estado:
        pedidos = pedidos.filter(estado=estado)

    # Buscar por nombre de cliente o # de pedido
    search = request.GET.get('q', '').strip()
    if search:
        pedidos = pedidos.filter(
            DbQ(cliente__first_name__icontains=search)
            | DbQ(cliente__email__icontains=search)
            | DbQ(pk__icontains=search)
            | DbQ(direccion_entrega__icontains=search)
        )

    # Estadísticas resumidas
    total_pedidos = pedidos.count()
    pendientes = Pedido.objects.filter(estado='pendiente').count()
    en_camino = Pedido.objects.filter(estado='en_camino').count()
    entregados = Pedido.objects.filter(estado='entregado').count()
    cancelados = Pedido.objects.filter(estado='cancelado').count()

    # Manejar POST de reasignación
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

    # Obtener TODOS los domiciliarios (para mostrar estado de disponibilidad)
    from usuarios.models import Usuario
    domiciliarios = Usuario.objects.filter(
        rol__nombre='Domiciliario', is_active=True
    ).annotate(
        pedidos_activos=Count(
            'pedidos_como_domiciliario',
            filter=Q(pedidos_como_domiciliario__estado__in=['pendiente', 'en_camino']),
        )
    ).order_by('first_name')
    domiciliarios_disponibles = domiciliarios.filter(is_disponible=True)

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
        'domiciliarios_disponibles': domiciliarios_disponibles,
    })


@role_required('Administrador')
def toggle_disponibilidad(request, pk):
    """Vista para que Admin habilite/deshabilite un domiciliario.
    POST only — redirige de vuelta a torre de control."""
    if request.method != 'POST':
        return redirect('entregas:torre_control')

    domiciliario = get_object_or_404(Usuario, pk=pk, rol__nombre='Domiciliario')
    domiciliario.is_disponible = not domiciliario.is_disponible
    domiciliario.save(update_fields=['is_disponible'])
    estado = 'disponible' if domiciliario.is_disponible else 'no disponible'
    messages.success(request, f'{domiciliario.get_full_name() or domiciliario.email} ahora está {estado}.')
    return redirect('entregas:torre_control')


@login_required(login_url='/usuarios/login/')
def toggle_mi_disponibilidad(request):
    """Vista para que un Domiciliario cambie SU PROPIA disponibilidad.
    POST only — redirige de vuelta al dashboard de entregas.
    Permite que el domiciliario se ponga 'no disponible' cuando está fuera
    de turno, enfermo, o con la moto en taller, evitando que el sistema
    le siga asignando pedidos (desbalanceo de carga)."""
    if request.user.rol.nombre != 'Domiciliario':
        raise PermissionDenied

    if request.method != 'POST':
        return redirect('entregas:dashboard')

    request.user.is_disponible = not request.user.is_disponible
    request.user.save(update_fields=['is_disponible'])
    estado = 'disponible' if request.user.is_disponible else 'no disponible'
    messages.success(request, f'Ahora estás {estado} para recibir pedidos.')
    return redirect('entregas:dashboard')