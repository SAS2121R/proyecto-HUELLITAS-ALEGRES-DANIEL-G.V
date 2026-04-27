from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse
from django.template.loader import render_to_string

from xhtml2pdf import pisa
import io

from agenda.models import Cita
from historial.models import HistorialClinico
from productos.models import Producto
from servicios.models import Servicio
from mascotas.models import Mascota


def _render_to_pdf(template_path, context):
    """Render a Django template to a PDF HttpResponse."""
    html = render_to_string(template_path, context)
    buf = io.BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=buf)
    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)
    buf.seek(0)
    return HttpResponse(buf.read(), content_type='application/pdf')


def _export_inventario_excel(queryset):
    """Export Producto queryset to an Excel HttpResponse."""
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment

    wb = Workbook()
    ws = wb.active
    ws.title = 'Inventario'

    headers = ['Nombre', 'Categoria', 'Precio', 'Stock', 'Stock Minimo', 'Proveedor', 'Estado']
    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=h)
        cell.font = Font(bold=True)

    for row, p in enumerate(queryset, 2):
        estado = 'OK' if p.estado_stock == 'verde' else ('Bajo' if p.estado_stock == 'amarillo' else 'Critico')
        ws.cell(row=row, column=1, value=p.nombre)
        ws.cell(row=row, column=2, value=p.get_categoria_display())
        ws.cell(row=row, column=3, value=float(p.precio))
        ws.cell(row=row, column=4, value=p.cantidad_stock)
        ws.cell(row=row, column=5, value=p.stock_minimo)
        ws.cell(row=row, column=6, value=p.proveedor or '-')
        ws.cell(row=row, column=7, value=estado)

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    response = HttpResponse(buf.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="inventario.xlsx"'
    return response


@login_required
@permission_required('agenda.view_cita', raise_exception=True)
def reporte_citas(request):
    citas = Cita.objects.select_related('mascota', 'disponibilidad__veterinario').order_by('-disponibilidad__fecha')
    estado = request.GET.get('estado')
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    if estado:
        citas = citas.filter(estado=estado)
    if fecha_desde:
        citas = citas.filter(disponibilidad__fecha__gte=fecha_desde)
    if fecha_hasta:
        citas = citas.filter(disponibilidad__fecha__lte=fecha_hasta)
    total = citas.count()
    confirmadas = citas.filter(estado='confirmada').count()
    pendientes = citas.filter(estado='pendiente').count()
    canceladas = citas.filter(estado='cancelada').count()
    context = {
        'citas': citas,
        'total': total,
        'confirmadas': confirmadas,
        'pendientes': pendientes,
        'canceladas': canceladas,
    }
    return _render_to_pdf('reportes/reporte_citas.html', context)


@login_required
@permission_required('historial.view_historialclinico', raise_exception=True)
def reporte_historial(request, mascota_pk):
    mascota = get_object_or_404(Mascota, pk=mascota_pk)
    historiales = HistorialClinico.objects.filter(mascota=mascota).select_related('veterinario').order_by('-fecha')
    context = {
        'mascota': mascota,
        'historiales': historiales,
    }
    return _render_to_pdf('reportes/reporte_historial.html', context)


@login_required
@permission_required('productos.view_producto', raise_exception=True)
def reporte_inventario(request):
    productos = Producto.objects.all().order_by('categoria', 'nombre')
    stock_bajo = request.GET.get('stock_bajo')
    if stock_bajo:
        productos = productos.filter(cantidad_stock__lt=5)
    total_productos = productos.count()
    total_valor = sum(p.precio * p.cantidad_stock for p in productos)
    critico = sum(1 for p in productos if p.estado_stock == 'rojo')
    bajo = sum(1 for p in productos if p.estado_stock == 'amarillo')
    context = {
        'productos': productos,
        'total_productos': total_productos,
        'total_valor': total_valor,
        'critico': critico,
        'bajo': bajo,
    }
    fmt = request.GET.get('format', 'pdf')
    if fmt == 'excel':
        return _export_inventario_excel(productos)
    return _render_to_pdf('reportes/reporte_inventario.html', context)


@login_required
@permission_required('servicios.view_servicio', raise_exception=True)
def reporte_servicios(request):
    servicios = Servicio.objects.all().order_by('categoria', 'nombre')
    categoria = request.GET.get('categoria')
    if categoria:
        servicios = servicios.filter(categoria=categoria)
    total = servicios.count()
    activos = servicios.filter(esta_activo=True).count()
    context = {
        'servicios': servicios,
        'total': total,
        'activos': activos,
    }
    return _render_to_pdf('reportes/reporte_servicios.html', context)
