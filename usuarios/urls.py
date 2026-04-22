from django.urls import path
from . import views

# Namespace para las URLs de usuarios
app_name = 'usuarios'

urlpatterns = [
    # Vista principal de autenticación (registro/login)
    path('', views.login_view, name='login'),
    path('auth/', views.auth_view, name='auth'),
    
    # Nuevas vistas para formularios HTML
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    
    # APIs para registro y login (mantener compatibilidad)
    path('api/registro/', views.registro_usuario, name='api_registro'),
    path('api/login/', views.login_usuario, name='api_login'),
    path('logout/', views.logout_usuario, name='logout'),
    
    # Vistas de administración (solo Administrador)
    path('admin/usuarios/', views.admin_user_list, name='admin_user_list'),
    path('admin/usuarios/<int:pk>/editar/', views.admin_user_edit, name='admin_user_edit'),
    
    # Vistas de veterinario (solo Veterinario)
    path('dashboard/', views.vet_dashboard, name='vet_dashboard'),
]