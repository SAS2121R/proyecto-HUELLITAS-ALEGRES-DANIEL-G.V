from django.urls import path
from . import views

app_name = 'entregas'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('crear/', views.crear_pedido, name='crear'),
    path('resumen/', views.resumen, name='resumen'),
    path('<int:pk>/', views.pedido_detalle, name='detalle'),
    path('<int:pk>/cambiar-estado/', views.cambiar_estado, name='cambiar_estado'),
]