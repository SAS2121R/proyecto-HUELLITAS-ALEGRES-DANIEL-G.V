from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from usuarios.decorators import role_required
from .models import Disponibilidad
from .forms import DisponibilidadForm


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
