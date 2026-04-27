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
    path('admin/usuarios/', views.admin_user_list, name='admin_user_list'),
    path('admin/usuarios/<int:pk>/editar/', views.admin_user_edit, name='admin_user_edit'),
    path('dashboard/', views.vet_dashboard, name='vet_dashboard'),
    path('perfil/', views.mi_perfil, name='mi_perfil'),
    path('usuarios/lista/', views.lista_usuarios, name='lista_usuarios'),
]