from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import transaction
from django.db.models import Q

from usuarios.decorators import role_required
from .models import HistorialClinico, Adjunto
from .forms import HistorialClinicoForm, AtenderCitaForm, AdjuntoForm
from agenda.models import Cita, Disponibilidad
from mascotas.models import Mascota


@login_required(login_url='/usuarios/login/')
def lista_historiales(request):
    """Lista de historiales clínicos con búsqueda y paginación.

    - Veterinario: ve solo sus historiales
    - Administrador: ve todos
    - Cliente: ve historiales de sus mascotas
    """
    if request.user.rol.nombre == 'Veterinario':
        qs = HistorialClinico.objects.filter(veterinario=request.user)
    elif request.user.rol.nombre == 'Administrador':
        qs = HistorialClinico.objects.all()
    else:  # Cliente
        qs = HistorialClinico.objects.filter(mascota__propietario=request.user)

    search = request.GET.get('q', '').strip()
    if search:
        qs = qs.filter(
            Q(mascota__nombre__icontains=search)
            | Q(diagnostico__icontains=search)
            | Q(observaciones__icontains=search)
            | Q(veterinario__email__icontains=search)
        )

    qs = qs.select_related('mascota', 'veterinario').order_by('-fecha_consulta')
    paginator = Paginator(qs, 10)
    page = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.page(1)

    return render(request, 'historial/historial_list.html', {
        'page_obj': page_obj,
        'search': search,
    })


@role_required('Veterinario', 'Administrador')
def crear_historial(request):
    """Crear historial clínico directamente (no desde cita). Solo Vet/Admin."""
    if request.method == 'POST':
        form = HistorialClinicoForm(request.POST)
        if form.is_valid():
            historial = form.save(commit=False)
            historial.veterinario = request.user
            historial.save()
            messages.success(request, 'Historial clínico creado exitosamente.')
            return redirect('historial:lista')
    else:
        form = HistorialClinicoForm()
    return render(request, 'historial/historial_form.html', {'form': form})


@login_required(login_url='/usuarios/login/')
def detalle_historial(request, pk):
    """Ver detalle de un historial clínico. Object-level permissions."""
    historial = get_object_or_404(
        HistorialClinico.objects.select_related('mascota', 'veterinario', 'cita'),
        pk=pk
    )

    # Object-level permission check
    if request.user.rol.nombre == 'Veterinario' and historial.veterinario != request.user:
        raise PermissionDenied
    if request.user.rol.nombre == 'Cliente' and historial.mascota.propietario != request.user:
        raise PermissionDenied
    # Administrador can view any

    return render(request, 'historial/historial_detail.html', {'historial': historial})


@login_required(login_url='/usuarios/login/')
def editar_historial(request, pk):
    """Editar un historial clínico. Vet can only edit own, Admin any, Cliente never."""
    historial = get_object_or_404(HistorialClinico, pk=pk)

    # Permission: Cliente cannot edit (403)
    if request.user.rol.nombre == 'Cliente':
        raise PermissionDenied
    # Permission: Vet can only edit own
    if request.user.rol.nombre == 'Veterinario' and historial.veterinario != request.user:
        raise PermissionDenied
    # Administrador can edit any

    if request.method == 'POST':
        form = HistorialClinicoForm(request.POST, instance=historial)
        if form.is_valid():
            form.save()
            messages.success(request, 'Historial clínico actualizado exitosamente.')
            return redirect('historial:detalle', pk=historial.pk)
    else:
        form = HistorialClinicoForm(instance=historial)
    return render(request, 'historial/historial_form.html', {
        'form': form,
        'historial': historial,
    })


@login_required(login_url='/usuarios/login/')
def historial_por_mascota(request, mascota_pk):
    """Ver historial clínico de una mascota específica."""
    mascota = get_object_or_404(Mascota, pk=mascota_pk)

    # Permission: Cliente can only view own pets
    if request.user.rol.nombre == 'Cliente' and mascota.propietario != request.user:
        raise PermissionDenied
    # Veterinario and Administrador can view any

    historiales = HistorialClinico.objects.filter(
        mascota=mascota
    ).select_related('veterinario').order_by('-fecha_consulta')

    return render(request, 'historial/historial_por_mascota.html', {
        'mascota': mascota,
        'historiales': historiales,
    })


@role_required('Veterinario', 'Administrador')
def atender_cita(request, cita_pk):
    """Atender una cita programada y crear historial clínico (atomic transaction).

    Critical business rules:
    1. Cita must be in 'Programada' state
    2. Transaction must be atomic (both succeed or both fail)
    3. Pre-fills data from cita (motivo, tipo_consulta inference)
    """
    cita = get_object_or_404(
        Cita.objects.select_related('mascota', 'disponibilidad__veterinario'),
        pk=cita_pk
    )

    # State validation
    if cita.estado == 'Atendida':
        messages.error(request, 'Esta cita ya fue atendida.')
        return redirect('agenda:lista_citas')
    if cita.estado == 'Cancelada':
        messages.error(request, 'No se puede atender una cita cancelada.')
        return redirect('agenda:lista_citas')

    if request.method == 'POST':
        form = AtenderCitaForm(request.POST, cita=cita)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Lock cita row to prevent race conditions
                    cita_locked = Cita.objects.select_for_update().get(pk=cita.pk)

                    # Double-check state (race condition protection)
                    if cita_locked.estado != 'Programada':
                        raise Exception('Esta cita ya fue atendida.')

                    # Create historial
                    historial = form.save(commit=False)
                    historial.mascota = cita.mascota
                    historial.cita = cita
                    historial.veterinario = request.user
                    historial.save()

                    # Update cita state
                    cita_locked.estado = 'Atendida'
                    cita_locked.save()

                messages.success(request, 'Cita atendida e historial creado exitosamente.')
                return redirect('historial:detalle', pk=historial.pk)
            except Exception as e:
                messages.error(request, str(e))
                return redirect('agenda:lista_citas')
    else:
        form = AtenderCitaForm(cita=cita)

    return render(request, 'historial/atender_cita_form.html', {
        'form': form,
        'cita': cita,
    })


# ========================================
# Adjunto Views (file uploads)
# ========================================

@role_required('Veterinario', 'Administrador')
def subir_adjunto(request, pk):
    """Upload a file attachment to a HistorialClinico record.

    Only the vet who created the historial or an Admin can upload.
    File size must not exceed MAX_ADJUNTO_SIZE (5MB).
    """
    historial = get_object_or_404(HistorialClinico, pk=pk)

    # Permission check: only own vet or admin
    if request.user.rol.nombre == 'Veterinario' and historial.veterinario != request.user:
        raise PermissionDenied

    if request.method == 'POST':
        form = AdjuntoForm(request.POST, request.FILES)
        if form.is_valid():
            adjunto = form.save(commit=False)
            adjunto.historial_clinico = historial
            adjunto.subido_por = request.user
            adjunto.save()
            messages.success(request, f'Archivo "{adjunto.archivo.name.split("/")[-1]}" subido exitosamente.')
            return redirect('historial:detalle', pk=historial.pk)
    else:
        form = AdjuntoForm()

    return render(request, 'historial/adjunto_form.html', {
        'form': form,
        'historial': historial,
    })


@role_required('Veterinario', 'Administrador')
def eliminar_adjunto(request, pk):
    """Delete a file attachment.

    Only the vet who uploaded it or an Admin can delete.
    POST required (no GET delete).
    """
    adjunto = get_object_or_404(Adjunto, pk=pk)

    # Permission check: only the uploader (vet) or admin
    if request.user.rol.nombre == 'Veterinario' and adjunto.subido_por != request.user:
        raise PermissionDenied

    if request.method == 'POST':
        historial_pk = adjunto.historial_clinico_id
        # Delete the actual file from storage
        adjunto.archivo.delete(save=False)
        adjunto.delete()
        messages.success(request, 'Archivo eliminado exitosamente.')
        return redirect('historial:detalle', pk=historial_pk)

    return render(request, 'historial/adjunto_confirm_delete.html', {
        'adjunto': adjunto,
    })