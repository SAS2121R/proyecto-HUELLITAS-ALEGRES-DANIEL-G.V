from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('', views.login_view, name='login'),
    path('auth/', views.auth_view, name='auth'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('api/registro/', views.registro_usuario, name='api_registro'),
    path('api/login/', views.login_usuario, name='api_login'),
    path('logout/', views.logout_usuario, name='logout'),

    # Admin
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/usuarios/', views.admin_users, name='admin_users'),
    path('admin/usuarios/crear/', views.admin_user_create, name='admin_user_create'),
    path('admin/usuarios/<int:pk>/editar/', views.admin_user_update, name='admin_user_update'),
    path('admin/usuarios/<int:pk>/toggle-active/', views.admin_user_toggle_active, name='admin_user_toggle_active'),
    path('admin/usuarios/<int:pk>/set-password/', views.admin_user_set_password, name='admin_user_set_password'),
    path('admin/configuracion/', views.admin_configuracion, name='admin_configuracion'),

    # Vet & General
    path('dashboard/', views.vet_dashboard, name='vet_dashboard'),
    path('perfil/', views.mi_perfil, name='mi_perfil'),
    path('perfil/cambiar-password/', views.cambiar_password, name='cambiar_password'),
    path('usuarios/lista/', views.lista_usuarios, name='lista_usuarios'),
    path('admin/old/', views.admin_user_list, name='admin_user_list'),
    path('admin/old/<int:pk>/editar/', views.admin_user_edit, name='admin_user_edit'),
]