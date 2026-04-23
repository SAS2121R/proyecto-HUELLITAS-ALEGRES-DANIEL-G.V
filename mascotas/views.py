from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from usuarios.decorators import role_required
from .models import Mascota
from .forms import MascotaForm


@login_required(login_url='/usuarios/login/')
def lista_mascotas(request):
    """Lista mascotas con filtrado por rol: Vet/Admin ven todas, Cliente solo las propias."""
    if request.user.rol.nombre in ('Veterinario', 'Administrador'):
        mascotas_list = Mascota.objects.all()
    else:
        mascotas_list = Mascota.objects.filter(propietario=request.user)
    mascotas_list = mascotas_list.order_by('nombre')
    paginator = Paginator(mascotas_list, 10)
    page = request.GET.get('page', 1)
    try:
        mascotas = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        mascotas = paginator.page(1)
    return render(request, 'mascotas/mascota_list.html', {'mascotas': mascotas})


@role_required('Veterinario', 'Administrador')
def crear_mascota(request):
    """Crear nueva mascota — solo Veterinario y Administrador."""
    if request.method == 'POST':
        form = MascotaForm(request.POST)
        if form.is_valid():
            mascota = form.save(commit=False)
            mascota.propietario = request.user
            mascota.save()
            messages.success(request, 'Mascota creada exitosamente.')
            return redirect('mascotas:lista')
    else:
        form = MascotaForm()
    return render(request, 'mascotas/mascota_form.html', {'form': form})


@login_required(login_url='/usuarios/login/')
def editar_mascota(request, pk):
    """Editar mascota — Vet/Admin editan cualquiera, Cliente solo las propias."""
    mascota = get_object_or_404(Mascota, pk=pk)
    # Ownership check for Cliente role
    if request.user.rol.nombre == 'Cliente' and mascota.propietario != request.user:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    if request.method == 'POST':
        form = MascotaForm(request.POST, instance=mascota)
        if form.is_valid():
            form.save()
            messages.success(request, 'Mascota actualizada exitosamente.')
            return redirect('mascotas:lista')
    else:
        form = MascotaForm(instance=mascota)
    return render(request, 'mascotas/mascota_form.html', {'form': form})


@role_required('Veterinario', 'Administrador')
def eliminar_mascota(request, pk):
    """Eliminar mascota — solo Veterinario y Administrador."""
    mascota = get_object_or_404(Mascota, pk=pk)
    if request.method == 'POST':
        mascota.delete()
        messages.success(request, 'Mascota eliminada exitosamente.')
        return redirect('mascotas:lista')
    return render(request, 'mascotas/mascota_confirm_delete.html', {'mascota': mascota})
