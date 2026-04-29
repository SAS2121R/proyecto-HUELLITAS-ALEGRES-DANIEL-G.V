from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages

from .models import Proveedor
from .forms import ProveedorForm


@login_required
def lista_proveedores(request):
    """Admin-only list of all suppliers."""
    if request.user.rol.nombre != 'Administrador':
        raise PermissionDenied
    proveedores = Proveedor.objects.all().order_by('-esta_activo', 'nombre')
    return render(request, 'proveedores/lista.html', {'proveedores': proveedores})


@login_required
def crear_proveedor(request):
    """Admin-only create supplier."""
    if request.user.rol.nombre != 'Administrador':
        raise PermissionDenied
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            proveedor = form.save()
            messages.success(request, f'Proveedor "{proveedor.nombre}" creado exitosamente.')
            return redirect('proveedores:lista')
    else:
        form = ProveedorForm()
    return render(request, 'proveedores/form.html', {'form': form, 'titulo': 'Crear Proveedor'})


@login_required
def editar_proveedor(request, pk):
    """Admin-only edit supplier."""
    if request.user.rol.nombre != 'Administrador':
        raise PermissionDenied
    proveedor = get_object_or_404(Proveedor, pk=pk)
    if request.method == 'POST':
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            form.save()
            messages.success(request, f'Proveedor "{proveedor.nombre}" actualizado exitosamente.')
            return redirect('proveedores:lista')
    else:
        form = ProveedorForm(instance=proveedor)
    return render(request, 'proveedores/form.html', {'form': form, 'titulo': f'Editar: {proveedor.nombre}'})


@login_required
def toggle_proveedor(request, pk):
    """Admin-only toggle supplier active status."""
    if request.user.rol.nombre != 'Administrador':
        raise PermissionDenied
    if request.method != 'POST':
        raise PermissionDenied
    proveedor = get_object_or_404(Proveedor, pk=pk)
    proveedor.esta_activo = not proveedor.esta_activo
    proveedor.save(update_fields=['esta_activo'])
    estado = 'activado' if proveedor.esta_activo else 'desactivado'
    messages.success(request, f'Proveedor "{proveedor.nombre}" {estado}.')
    return redirect('proveedores:lista')