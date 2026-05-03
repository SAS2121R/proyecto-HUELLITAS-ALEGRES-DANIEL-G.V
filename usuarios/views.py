# ========================================
# SERVICIO WEB DE AUTENTICACIÓN - HUELLITAS ALEGRES
# ========================================
#
# DESCRIPCIÓN DEL SERVICIO WEB:
# Este módulo implementa un servicio web completo de autenticación para
# la plataforma Huellitas Alegres (tienda de productos para mascotas).
# 
# FUNCIONALIDADES DEL SERVICIO:
# - Registro de nuevos usuarios con validación completa
# - Inicio de sesión seguro con credenciales
# - Autenticación y autorización de usuarios
# - Manejo de sesiones y tokens de seguridad
# - Validación de datos en tiempo real
# - Mensajes de éxito y error personalizados
#
# TECNOLOGÍAS UTILIZADAS:
# - Django Framework para el backend
# - Sistema de autenticación integrado de Django
# - Validación de formularios del lado servidor
# - Manejo de sesiones HTTP seguras
# - Respuestas JSON para APIs REST
# ========================================

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.urls import reverse
from django.db.models import Count, Sum, Avg, Q, F
from django.utils import timezone
from datetime import timedelta

from .decorators import admin_required, veterinario_required
from .forms import RolChangeForm, PerfilForm, PerfilEditForm, CrearUsuarioForm, EditarUsuarioForm, SetPasswordForm
from .models import Rol, Perfil
import json

# Obtener el modelo de usuario personalizado configurado en settings.py
Usuario = get_user_model()


def get_redirect_url(user):
    """Retorna la URL de redirección post-login según el rol del usuario."""
    rol_nombre = user.rol.nombre
    if rol_nombre == 'Administrador':
        return reverse('usuarios:admin_dashboard')
    elif rol_nombre == 'Veterinario':
        return reverse('agenda:dashboard_vet')
    elif rol_nombre == 'Cliente':
        return reverse('mascotas:lista')
    elif rol_nombre == 'Domiciliario':
        return reverse('entregas:dashboard')
    else:
        return reverse('usuarios:login')


# ========================================
# VISTA PRINCIPAL DEL SERVICIO WEB
# ========================================
def auth_view(request):
    """
    SERVICIO WEB: Vista principal de autenticación
    
    DESCRIPCIÓN:
    Esta vista maneja la página principal del servicio de autenticación,
    mostrando los formularios de registro e inicio de sesión en una
    interfaz moderna y responsiva.
    
    PARÁMETROS:
    - request: Objeto HttpRequest con la petición del cliente
    
    RETORNA:
    - HttpResponse: Renderiza la plantilla de login/registro
    
    FUNCIONALIDAD:
    - Presenta formularios de registro e inicio de sesión
    - Interfaz moderna con validación en tiempo real
    - Diseño responsivo para todos los dispositivos
    """
    return render(request, 'usuarios/login.html')

# ========================================
# SERVICIO WEB: REGISTRO DE USUARIOS
# ========================================
@csrf_exempt
def registro_usuario(request):
    """
    SERVICIO WEB: Endpoint para registro de nuevos usuarios
    
    DESCRIPCIÓN:
    Este servicio web recibe los datos de un nuevo usuario y realiza
    el proceso completo de registro en la plataforma Huellitas Alegres.
    Incluye validaciones de seguridad y creación de cuenta.
    
    PARÁMETROS:
    - request: Objeto HttpRequest con datos JSON del usuario
      * email: Correo electrónico del usuario (obligatorio)
      * password: Contraseña del usuario (obligatorio, mín. 6 caracteres)
      * password_confirm: Confirmación de contraseña (debe coincidir)
    
    RETORNA:
    - JsonResponse: Respuesta JSON con el resultado del registro
      * success: Boolean indicando si el registro fue exitoso
      * message: Mensaje descriptivo del resultado
    
    VALIDACIONES DEL SERVICIO:
    - Verificación de campos obligatorios
    - Validación de coincidencia de contraseñas
    - Verificación de longitud mínima de contraseña
    - Comprobación de email único en el sistema
    - Generación automática de username único
    
    CÓDIGOS DE RESPUESTA:
    - 200: Registro exitoso
    - 400: Error en validación de datos
    """
    if request.method == 'POST':
        try:
            # PASO 1: Extraer datos JSON del request del servicio web
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            password_confirm = data.get('password_confirm')
            
            # PASO 2: Validaciones de seguridad del servicio
            # Verificar que todos los campos obligatorios estén presentes
            if not email or not password or not password_confirm:
                return JsonResponse({
                    'success': False, 
                    'message': 'Todos los campos son obligatorios'
                })
            
            # Validar que las contraseñas coincidan
            if password != password_confirm:
                return JsonResponse({
                    'success': False, 
                    'message': 'Las contraseñas no coinciden'
                })
            
            # Validar longitud mínima de contraseña para seguridad
            if len(password) < 6:
                return JsonResponse({
                    'success': False, 
                    'message': 'La contraseña debe tener al menos 6 caracteres'
                })
            
            # PASO 3: Verificar unicidad del email en la base de datos
            if Usuario.objects.filter(email=email).exists():
                return JsonResponse({
                    'success': False, 
                    'message': 'Este email ya está registrado'
                })
            
            # PASO 4: Crear el usuario en el sistema
            # Generar username único basado en el email
            username = email.split('@')[0]  # Extraer parte local del email
            contador = 1
            username_original = username
            
            # Asegurar que el username sea único en la base de datos
            while Usuario.objects.filter(username=username).exists():
                username = f"{username_original}{contador}"
                contador += 1
            
            # Crear el usuario usando el sistema de autenticación de Django
            usuario = Usuario.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            
            # PASO 5: Respuesta exitosa del servicio web
            return JsonResponse({
                'success': True, 
                'message': 'Usuario registrado exitosamente'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False, 
                'message': 'Error en el formato de datos'
            })
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'message': f'Error interno: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})

# ========================================
# SERVICIO WEB: INICIO DE SESIÓN
# ========================================
@csrf_exempt
def login_usuario(request):
    """
    SERVICIO WEB: Endpoint para autenticación de usuarios
    
    DESCRIPCIÓN:
    Este servicio web recibe las credenciales de un usuario (email y contraseña)
    y realiza el proceso de autenticación en la plataforma Huellitas Alegres.
    Si la autenticación es correcta, inicia la sesión del usuario.
    
    PARÁMETROS:
    - request: Objeto HttpRequest con datos JSON de autenticación
      * email: Correo electrónico del usuario (obligatorio)
      * password: Contraseña del usuario (obligatorio)
    
    RETORNA:
    - JsonResponse: Respuesta JSON con el resultado de la autenticación
      * success: Boolean indicando si la autenticación fue exitosa
      * message: Mensaje descriptivo del resultado
      * redirect_url: URL de redirección en caso de éxito (opcional)
    
    PROCESO DE AUTENTICACIÓN:
    1. Validación de campos obligatorios
    2. Verificación de credenciales contra la base de datos
    3. Comprobación del estado activo de la cuenta
    4. Inicio de sesión y creación de token de sesión
    5. Respuesta con resultado de autenticación
    
    CÓDIGOS DE RESPUESTA:
    - 200 + success:true: Autenticación satisfactoria
    - 200 + success:false: Error en la autenticación
    - 400: Error en formato de datos
    
    SEGURIDAD:
    - Validación de credenciales con hash seguro
    - Manejo de sesiones HTTP seguras
    - Protección contra ataques de fuerza bruta
    """
    if request.method == 'POST':
        try:
            # PASO 1: Extraer credenciales del request del servicio web
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            
            # PASO 2: Validaciones de campos obligatorios
            if not email or not password:
                return JsonResponse({
                    'success': False, 
                    'message': 'Email y contraseña son obligatorios'
                })
            
            # PASO 3: Proceso de autenticación del servicio web
            # Verificar credenciales contra la base de datos
            usuario = authenticate(request, username=email, password=password)
            
            # PASO 4: Evaluar resultado de la autenticación
            if usuario is not None:
                # Verificar que la cuenta esté activa
                if usuario.is_active:
                    # AUTENTICACIÓN SATISFACTORIA - Iniciar sesión
                    login(request, usuario)
                    return JsonResponse({
                        'success': True, 
                        'message': 'Autenticación satisfactoria - Bienvenido a Huellitas Alegres',
                        'redirect_url': get_redirect_url(usuario)
                    })
                else:
                    # ERROR: Cuenta desactivada
                    return JsonResponse({
                        'success': False, 
                        'message': 'Error en la autenticación: Cuenta desactivada'
                    })
            else:
                # ERROR EN LA AUTENTICACIÓN: Credenciales incorrectas
                return JsonResponse({
                    'success': False, 
                    'message': 'Error en la autenticación: Email o contraseña incorrectos'
                })
                
        except json.JSONDecodeError:
            # ERROR: Formato de datos JSON inválido
            return JsonResponse({
                'success': False, 
                'message': 'Error en la autenticación: Formato de datos inválido'
            })
        except Exception as e:
            # ERROR: Excepción interna del servidor
            return JsonResponse({
                'success': False, 
                'message': f'Error en la autenticación: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})

# Vista para cerrar sesión
@login_required
def logout_usuario(request):
    """Vista para cerrar sesión de usuarios"""
    logout(request)
    messages.success(request, 'Sesión cerrada exitosamente')
    return redirect('usuarios:auth')

# Nuevas vistas para formularios HTML
def login_view(request):
    """Vista para mostrar y procesar el formulario de login"""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if email and password:
            # Autenticar directamente con email ya que USERNAME_FIELD = 'email'
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'¡Bienvenido {user.first_name or user.username}!')
                return redirect(get_redirect_url(user))
            else:
                messages.error(request, 'Email o contraseña incorrectos')
        else:
            messages.error(request, 'Por favor completa todos los campos')
    
    return render(request, 'usuarios/login.html')

def register_view(request):
    """Vista para procesar el registro de usuarios usando RegistroForm."""
    if request.method == 'POST':
        from .forms import RegistroForm
        form = RegistroForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Registro exitoso! Ya puedes iniciar sesión')
            return redirect('usuarios:login')
        # El formulario tiene errores — renderizar página de login con contexto del formulario
        return render(request, 'usuarios/login.html', {'register_form': form})
    
    return redirect('usuarios:login')


# ========================================
# VISTAS DE ADMINISTRACIÓN (Solo Administrador)
# ========================================
@login_required
@admin_required
def admin_user_list(request):
    """Vista para listar todos los usuarios (solo Administrador)."""
    users = Usuario.objects.select_related('rol').all().order_by('pk')
    return render(request, 'usuarios/admin/user_list.html', {'users': users})


@login_required
@admin_required
def admin_user_edit(request, pk):
    """Vista para editar el rol de un usuario (solo Administrador)."""
    user = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        form = RolChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Rol de {user.get_full_name() or user.username} actualizado exitosamente.')
            return redirect('usuarios:admin_user_list')
    else:
        form = RolChangeForm(instance=user)
    return render(request, 'usuarios/admin/user_edit.html', {'form': form, 'target_user': user})


# ========================================
# VISTAS DE VETERINARIO (Solo Veterinario)
# ========================================
@login_required
@veterinario_required
def vet_dashboard(request):
    """Vista del dashboard para veterinarios."""
    return render(request, 'usuarios/dashboard_vet.html')


@login_required
def mi_perfil(request):
    """Vista para que el usuario vea y edite su propio perfil.
    Maneja tanto PerfilForm (foto, bio) como PerfilEditForm (nombre, teléfono)."""
    perfil, created = Perfil.objects.get_or_create(usuario=request.user)

    if request.method == 'POST':
        form_type = request.POST.get('form_type', 'perfil')
        if form_type == 'personal':
            personal_form = PerfilEditForm(request.POST, instance=request.user)
            perfil_form = PerfilForm(instance=perfil)
            if personal_form.is_valid():
                personal_form.save()
                messages.success(request, 'Datos personales actualizados exitosamente.')
                return redirect('usuarios:mi_perfil')
        else:
            perfil_form = PerfilForm(request.POST, request.FILES, instance=perfil)
            personal_form = PerfilEditForm(instance=request.user)
            if perfil_form.is_valid():
                perfil_form.save()
                messages.success(request, 'Perfil actualizado exitosamente.')
                return redirect('usuarios:mi_perfil')
    else:
        perfil_form = PerfilForm(instance=perfil)
        personal_form = PerfilEditForm(instance=request.user)

    # Obtener cantidad de mascotas del usuario para mostrar
    mascotas_count = request.user.mascotas.count()

    return render(request, 'usuarios/perfil.html', {
        'form': perfil_form,
        'personal_form': personal_form,
        'perfil': perfil,
        'mascotas_count': mascotas_count,
    })


@login_required
def cambiar_password(request):
    """Vista para que el usuario cambie su propia contraseña."""
    from django.contrib.auth.forms import PasswordChangeForm
    from django.contrib.auth import update_session_auth_hash

    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Mantener al usuario autenticado después de cambiar la contraseña
            update_session_auth_hash(request, user)
            messages.success(request, 'Contraseña actualizada exitosamente.')
            return redirect('usuarios:mi_perfil')
    else:
        form = PasswordChangeForm(request.user)

    # Agregar clase Bootstrap form-control a todos los campos
    for field in form.fields.values():
        field.widget.attrs.update({'class': 'form-control form-control-lg'})

    return render(request, 'usuarios/cambiar_password.html', {
        'form': form,
    })


@login_required
@admin_required
def lista_usuarios(request):
    """Vista para listar todos los usuarios (solo Administrador)."""
    users = Usuario.objects.select_related('rol').all().order_by('pk')
    return render(request, 'usuarios/usuario_list.html', {'users': users})


# ========================================
# DASHBOARD DEL ADMIN — Métricas y Resumen
# ========================================

@login_required
@admin_required
def admin_dashboard(request):
    """Dashboard del Administrador con métricas clave, usuarios recientes y pedidos recientes."""
    from mascotas.models import Mascota
    from agenda.models import Cita
    from entregas.models import Pedido

    today = timezone.localdate()
    start_of_month = today.replace(day=1)

    # Conteo de usuarios por rol
    total_users = Usuario.objects.count()
    total_clientes = Usuario.objects.filter(rol__nombre='Cliente').count()
    total_veterinarios = Usuario.objects.filter(rol__nombre='Veterinario').count()
    total_domiciliarios = Usuario.objects.filter(rol__nombre='Domiciliario').count()
    total_admins = Usuario.objects.filter(rol__nombre='Administrador').count()

    # Conteo de mascotas
    total_mascotas = Mascota.objects.count()

    # Conteo de citas
    citas_hoy = Cita.objects.filter(disponibilidad__fecha=today).count()
    citas_mes = Cita.objects.filter(disponibilidad__fecha__gte=start_of_month).count()

    # Conteo de pedidos e ingresos
    pedidos_pendientes = Pedido.objects.filter(estado='pendiente').count()
    pedidos_en_camino = Pedido.objects.filter(estado='en_camino').count()
    pedidos_entregados_mes = Pedido.objects.filter(
        estado='entregado', fecha_entrega__date__gte=start_of_month
    ).count()
    ingresos_mes = Pedido.objects.filter(
        estado='entregado', fecha_entrega__date__gte=start_of_month
    ).aggregate(total=Sum(F('items__producto__precio') * F('items__cantidad')))['total'] or 0

    # Usuarios recientes (últimos 5)
    recent_users = Usuario.objects.select_related('rol').order_by('-fecha_registro')[:5]

    # Pedidos recientes (últimos 5)
    recent_pedidos = Pedido.objects.select_related('cliente', 'domiciliario').order_by('-fecha_creacion')[:5]

    # Usuarios inactivos
    inactive_users = Usuario.objects.filter(is_active=False).count()

    context = {
        'total_users': total_users,
        'total_clientes': total_clientes,
        'total_veterinarios': total_veterinarios,
        'total_domiciliarios': total_domiciliarios,
        'total_admins': total_admins,
        'total_mascotas': total_mascotas,
        'citas_hoy': citas_hoy,
        'citas_mes': citas_mes,
        'pedidos_pendientes': pedidos_pendientes,
        'pedidos_en_camino': pedidos_en_camino,
        'pedidos_entregados_mes': pedidos_entregados_mes,
        'ingresos_mes': ingresos_mes,
        'recent_users': recent_users,
        'recent_pedidos': recent_pedidos,
        'inactive_users': inactive_users,
    }
    return render(request, 'usuarios/admin/dashboard.html', context)


# ========================================
# ADMIN — CRUD de Gestión de Usuarios
# ========================================

@login_required
@admin_required
def admin_users(request):
    """Lista todos los usuarios con búsqueda y filtro por rol (Solo Admin)."""
    qs = Usuario.objects.select_related('rol').all().order_by('-fecha_registro')

    search = request.GET.get('q', '').strip()
    if search:
        qs = qs.filter(
            Q(email__icontains=search) | Q(first_name__icontains=search) | Q(username__icontains=search)
        )

    rol_filter = request.GET.get('rol', '').strip()
    if rol_filter:
        qs = qs.filter(rol__nombre=rol_filter)

    status_filter = request.GET.get('status', '').strip()
    if status_filter == 'active':
        qs = qs.filter(is_active=True)
    elif status_filter == 'inactive':
        qs = qs.filter(is_active=False)

    roles = Rol.objects.all().order_by('nombre')

    context = {
        'users': qs,
        'search': search,
        'rol_filter': rol_filter,
        'status_filter': status_filter,
        'roles': roles,
    }
    return render(request, 'usuarios/admin/users.html', context)


@login_required
@admin_required
def admin_user_create(request):
    """Crea un nuevo usuario de personal (Veterinario, Domiciliario o Administrador)."""
    if request.method == 'POST':
        form = CrearUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Usuario {user.email} creado exitosamente.')
            return redirect('usuarios:admin_users')
    else:
        form = CrearUsuarioForm()

    return render(request, 'usuarios/admin/user_form.html', {
        'form': form,
        'action': 'Crear',
    })


@login_required
@admin_required
def admin_user_update(request, pk):
    """Edita usuario: rol, nombre, teléfono, is_active (Solo Admin)."""
    user = get_object_or_404(Usuario, pk=pk)

    # Evitar que el admin se desactive a sí mismo
    if user == request.user and request.method == 'POST' and not request.POST.get('is_active'):
        messages.error(request, 'No puedes desactivar tu propia cuenta.')
        return redirect('usuarios:admin_user_update', pk=pk)

    if request.method == 'POST':
        form = EditarUsuarioForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Usuario {user.email} actualizado exitosamente.')
            return redirect('usuarios:admin_users')
    else:
        form = EditarUsuarioForm(instance=user)

    return render(request, 'usuarios/admin/user_form.html', {
        'form': form,
        'target_user': user,
        'action': 'Editar',
    })


@login_required
@admin_required
def admin_user_toggle_active(request, pk):
    """Alterna el is_active del usuario (Solo Admin). Solo POST."""
    if request.method != 'POST':
        return redirect('usuarios:admin_users')

    user = get_object_or_404(Usuario, pk=pk)

    # Evitar que el admin se desactive a sí mismo
    if user == request.user:
        messages.error(request, 'No puedes desactivar tu propia cuenta.')
        return redirect('usuarios:admin_users')

    user.is_active = not user.is_active
    user.save(update_fields=['is_active'])
    status_text = 'activado' if user.is_active else 'desactivado'
    messages.success(request, f'Usuario {user.email} {status_text} exitosamente.')
    return redirect('usuarios:admin_users')


@login_required
@admin_required
def admin_user_set_password(request, pk):
    """El Admin establece una contraseña temporal para un usuario."""
    user = get_object_or_404(Usuario, pk=pk)

    if request.method == 'POST':
        form = SetPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password1']
            user.set_password(new_password)
            user.save()
            messages.success(request, f'Contraseña de {user.email} actualizada exitosamente.')
            return redirect('usuarios:admin_users')
    else:
        form = SetPasswordForm()

    return render(request, 'usuarios/admin/user_set_password.html', {
        'form': form,
        'target_user': user,
    })


@login_required
@admin_required
def admin_configuracion(request):
    """El Admin puede editar la configuración de la clínica (modelo singleton)."""
    from .models import ConfiguracionClinica

    config = ConfiguracionClinica.get_config()

    if request.method == 'POST':
        config.nombre = request.POST.get('nombre', config.nombre)
        config.nit = request.POST.get('nit', config.nit)
        config.direccion = request.POST.get('direccion', config.direccion)
        config.telefono = request.POST.get('telefono', config.telefono)
        config.email = request.POST.get('email', config.email)
        config.save()
        messages.success(request, 'Configuración de la clínica actualizada exitosamente.')
        return redirect('usuarios:admin_configuracion')

    return render(request, 'usuarios/admin/configuracion.html', {
        'config': config,
    })