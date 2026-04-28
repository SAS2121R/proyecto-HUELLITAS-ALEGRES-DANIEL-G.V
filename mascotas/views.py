from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from usuarios.decorators import role_required
from .models import Mascota, ESPECIE_CHOICES
from .forms import MascotaForm


@login_required(login_url='/usuarios/login/')
def lista_mascotas(request):
    """Lista mascotas con filtrado por rol, búsqueda Q objects y filtro por especie."""
    q = request.GET.get('q', '').strip()
    especie = request.GET.get('especie', '').strip()

    if request.user.rol.nombre in ('Veterinario', 'Administrador'):
        mascotas_list = Mascota.objects.all()
    else:
        mascotas_list = Mascota.objects.filter(propietario=request.user)

    # Filter by search query (nombre, especie, cédula del propietario)
    if q:
        mascotas_list = mascotas_list.filter(
            Q(nombre__icontains=q)
            | Q(especie__icontains=q)
            | Q(propietario__cedula__icontains=q)
        )

    # Filter by especie — only filter if valid species choice
    valid_species = [choice[0] for choice in ESPECIE_CHOICES]
    if especie and especie in valid_species:
        mascotas_list = mascotas_list.filter(especie=especie)

    mascotas_list = mascotas_list.order_by('nombre')
    paginator = Paginator(mascotas_list, 10)
    page = request.GET.get('page', 1)
    try:
        mascotas = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        mascotas = paginator.page(1)

    return render(request, 'mascotas/mascota_list.html', {
        'mascotas': mascotas,
        'q': q,
        'especie': especie,
        'especie_choices': ESPECIE_CHOICES,
    })


@login_required(login_url='/usuarios/login/')
def crear_mascota(request):
    """Crear nueva mascota — Vet/Admin/Vet can create; Cliente gets forced propietario."""
    if request.method == 'POST':
        form = MascotaForm(request.POST, request.FILES)
        if form.is_valid():
            mascota = form.save(commit=False)
            # For Cliente role, always force propietario to request.user
            if request.user.rol.nombre == 'Cliente':
                mascota.propietario = request.user
            else:
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
        form = MascotaForm(request.POST, request.FILES, instance=mascota)
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


@login_required(login_url='/usuarios/login/')
def detalle_mascota(request, pk):
    """Detalle de mascota — Vet/Admin ven cualquier mascota, Cliente solo las propias."""
    mascota = get_object_or_404(Mascota, pk=pk)
    if request.user.rol.nombre == 'Cliente' and mascota.propietario != request.user:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    # Get last attended cita
    ultima_cita = mascota.citas.filter(estado='Atendida').order_by('-disponibilidad__fecha', '-disponibilidad__hora_inicio').first()
    return render(request, 'mascotas/mascota_detail.html', {
        'mascota': mascota,
        'ultima_cita': ultima_cita,
    })