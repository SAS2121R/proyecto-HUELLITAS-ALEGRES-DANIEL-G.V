from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect


def role_required(*roles):
    """Decorator factory that restricts view access based on user roles.
    
    Checks is_authenticated first — redirects unauthenticated users to login.
    Raises PermissionDenied (403) if the user's role is not in the allowed list.
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


# Convenience aliases
veterinario_required = role_required('Veterinario')
admin_required = role_required('Administrador')
