from django.urls import path
from . import views

app_name = 'entregas'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('crear/', views.crear_pedido, name='crear'),
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
    path('resumen/', views.resumen, name='resumen'),
    path('torre-control/', views.torre_control, name='torre_control'),
    path('<int:pk>/', views.pedido_detalle, name='detalle'),
    path('<int:pk>/cambiar-estado/', views.cambiar_estado, name='cambiar_estado'),
    path('<int:pk>/editar/', views.editar_pedido, name='editar'),
    path('<int:pk>/comprobante/', views.comprobante_pdf, name='comprobante_pdf'),
]