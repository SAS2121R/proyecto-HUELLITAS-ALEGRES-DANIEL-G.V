from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect


def role_required(*roles):
    """Decorador que restringe el acceso a vistas basado en roles de usuario.
    
    Verifica is_authenticated primero — redirige usuarios no autenticados a login.
    Lanza PermissionDenied (403) si el rol del usuario no está en la lista de permitidos.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('usuarios:login')
            if request.user.rol.nombre not in roles:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


# Alias convenientes
veterinario_required = role_required('Veterinario')
admin_required = role_required('Administrador')