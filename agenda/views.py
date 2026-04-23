from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from usuarios.decorators import role_required
from .models import Disponibilidad, Cita
from .forms import DisponibilidadForm, CitaForm


@login_required(login_url='/usuarios/login/')
def lista_disponibilidades(request):
    """Lista de disponibilidades (Vet=own, Admin=all, Cliente=403)."""
    if request.user.rol.nombre == 'Cliente':
        raise PermissionDenied
    if request.user.rol.nombre == 'Veterinario':
        qs = Disponibilidad.objects.filter(veterinario=request.user)
    else:  # Administrador
        qs = Disponibilidad.objects.all()
    paginator = Paginator(qs, 10)
    page = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.page(1)
    return render(request, 'agenda/disponibilidad_list.html', {'page_obj': page_obj})


@role_required('Veterinario', 'Administrador')
def crear_disponibilidad(request):
    """Crear nueva disponibilidad — Vet crea propia, Admin puede crear."""
    if request.method == 'POST':
        form = DisponibilidadForm(request.POST)
        form.instance.veterinario = request.user
        if form.is_valid():
            form.save()
            messages.success(request, 'Disponibilidad creada exitosamente.')
            return redirect('agenda:lista_disponibilidad')
    else:
        form = DisponibilidadForm()
    return render(request, 'agenda/disponibilidad_form.html', {'form': form})


@login_required(login_url='/usuarios/login/')
def editar_disponibilidad(request, pk):
    """Editar disponibilidad — Vet solo propia, Admin cualquiera, Cliente 403."""
    if request.user.rol.nombre == 'Cliente':
        raise PermissionDenied
    disponibilidad = get_object_or_404(Disponibilidad, pk=pk)
    if request.user.rol.nombre == 'Veterinario' and disponibilidad.veterinario != request.user:
        raise PermissionDenied
    if request.method == 'POST':
        form = DisponibilidadForm(request.POST, instance=disponibilidad)
        if form.is_valid():
            form.save()
            messages.success(request, 'Disponibilidad actualizada exitosamente.')
            return redirect('agenda:lista_disponibilidad')
    else:
        form = DisponibilidadForm(instance=disponibilidad)
    return render(request, 'agenda/disponibilidad_form.html', {'form': form})


@login_required(login_url='/usuarios/login/')
def eliminar_disponibilidad(request, pk):
    """Eliminar disponibilidad con confirmación — Vet solo propia, Admin cualquiera, Cliente 403."""
    if request.user.rol.nombre == 'Cliente':
        raise PermissionDenied
    disponibilidad = get_object_or_404(Disponibilidad, pk=pk)
    if request.user.rol.nombre == 'Veterinario' and disponibilidad.veterinario != request.user:
        raise PermissionDenied
    if request.method == 'POST':
        disponibilidad.delete()
        messages.success(request, 'Disponibilidad eliminada exitosamente.')
        return redirect('agenda:lista_disponibilidad')
    return render(request, 'agenda/disponibilidad_confirm_delete.html', {'disponibilidad': disponibilidad})


# ========================================
# Cita Views (stubs — real implementations in Blocks 3-4)
# ========================================

@login_required(login_url='/usuarios/login/')
def lista_citas(request):
    """Lista de citas (Vet=own, Admin=all, Cliente=own pets)."""
    if request.user.rol.nombre == 'Veterinario':
        qs = Cita.objects.filter(disponibilidad__veterinario=request.user)
    elif request.user.rol.nombre == 'Administrador':
        qs = Cita.objects.all()
    else:  # Cliente
        qs = Cita.objects.filter(mascota__propietario=request.user)
    qs = qs.select_related('mascota', 'disponibilidad', 'disponibilidad__veterinario')
    paginator = Paginator(qs, 10)
    page = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.page(1)
    return render(request, 'agenda/cita_list.html', {'page_obj': page_obj})


@role_required('Veterinario', 'Administrador')
def crear_cita(request):
    """Crear nueva cita — Vet/Admin only."""
    if request.method == 'POST':
        form = CitaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cita creada exitosamente.')
            return redirect('agenda:lista_citas')
    else:
        form = CitaForm()
    return render(request, 'agenda/cita_form.html', {'form': form})


@login_required(login_url='/usuarios/login/')
def editar_cita(request, pk):
    """Editar cita — Vet own only, Admin any, Cliente 403."""
    if request.user.rol.nombre == 'Cliente':
        raise PermissionDenied
    cita = get_object_or_404(Cita, pk=pk)
    if request.user.rol.nombre == 'Veterinario' and cita.disponibilidad.veterinario != request.user:
        raise PermissionDenied
    # Block editing of terminal states
    if cita.estado in ('Atendida', 'Cancelada'):
        messages.error(request, f'No se puede editar una cita en estado {cita.get_estado_display()}.')
        return redirect('agenda:lista_citas')
    if request.method == 'POST':
        form = CitaForm(request.POST, instance=cita)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cita actualizada exitosamente.')
            return redirect('agenda:lista_citas')
    else:
        form = CitaForm(instance=cita)
    return render(request, 'agenda/cita_form.html', {'form': form})


@login_required(login_url='/usuarios/login/')
def eliminar_cita(request, pk):
    """Cancelar cita — soft cancel (set estado='Cancelada'), NOT hard delete."""
    if request.user.rol.nombre == 'Cliente':
        raise PermissionDenied
    cita = get_object_or_404(Cita, pk=pk)
    if request.user.rol.nombre == 'Veterinario' and cita.disponibilidad.veterinario != request.user:
        raise PermissionDenied
    # Block cancel of Atendida citas (terminal state)
    if cita.estado == 'Atendida':
        messages.error(request, 'No se puede cancelar una cita que ya fue atendida.')
        return redirect('agenda:lista_citas')
    if request.method == 'POST':
        motivo = request.POST.get('motivo_cancelacion', '').strip()
        if not motivo:
            # Re-render confirmation page with error
            messages.error(request, 'Debe indicar el motivo de cancelación.')
            return render(request, 'agenda/cita_cancel.html', {'cita': cita})
        cita.estado = 'Cancelada'
        cita.motivo_cancelacion = motivo
        cita.save()
        messages.success(request, 'Cita cancelada exitosamente.')
        return redirect('agenda:lista_citas')
    return render(request, 'agenda/cita_cancel.html', {'cita': cita})
