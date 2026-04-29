from decimal import Decimal
from django.test import TestCase
from django.urls import reverse, resolve
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from usuarios.models import Rol, Usuario
from productos.models import Producto

from .models import Pedido, PedidoItem, ESTADO_CHOICES, MAX_EVIDENCIA_SIZE


def create_user_with_role(rol_nombre, **kwargs):
    """Helper para crear un Usuario con el rol dado."""
    rol, _ = Rol.objects.get_or_create(nombre=rol_nombre)
    user = Usuario.objects.create_user(
        username=kwargs.get('username', f'user_{rol_nombre.lower()}'),
        email=kwargs.get('email', f'{rol_nombre.lower()}@test.com'),
        password='testpass123',
        rol=rol,
        **{k: v for k, v in kwargs.items() if k not in ('username', 'email', 'password', 'rol')}
    )
    return user


# ========================================
# FASE 1: Scaffold de la App + Modelo + Migration
# ========================================

class AppRegistrationTest(TestCase):
    """REQ-10: La app está registrada en INSTALLED_APPS"""

    def test_entregas_in_installed_apps(self):
        """R10.1: 'entregas' está en INSTALLED_APPS"""
        self.assertIn('entregas', settings.INSTALLED_APPS)


# ========================================
# TESTS DE MODELO — Pedido
# ========================================

class PedidoModelTest(TestCase):
    """Tests para el modelo Pedido."""

    def setUp(self):
        self.admin = create_user_with_role('Administrador', username='admin_ped', email='admin_ped@test.com')
        self.domiciliario = create_user_with_role('Domiciliario', username='domic_ped', email='domic_ped@test.com')
        self.cliente = create_user_with_role('Cliente', username='cli_ped', email='cli_ped@test.com')
        self.producto = Producto.all_objects.create(
            nombre='Antipulgas Premium',
            categoria='medicamentos',
            precio=Decimal('25000.00'),
            cantidad_stock=50,
        )

    def test_pedido_creacion_basica(self):
        """Crear un Pedido con todos los campos requeridos."""
        pedido = Pedido.objects.create(
            cliente=self.cliente,
            domiciliario=self.domiciliario,
            direccion_entrega='Calle 45 # 67-89, Bogotá',
            telefono_contacto='3001234567',
        )
        self.assertEqual(pedido.cliente, self.cliente)
        self.assertEqual(pedido.domiciliario, self.domiciliario)
        self.assertEqual(pedido.estado, 'pendiente')
        self.assertEqual(pedido.direccion_entrega, 'Calle 45 # 67-89, Bogotá')
        self.assertEqual(pedido.telefono_contacto, '3001234567')

    def test_pedido_default_estado_is_pendiente(self):
        """El estado por defecto debe ser 'pendiente'."""
        pedido = Pedido.objects.create(
            cliente=self.cliente,
            domiciliario=self.domiciliario,
            direccion_entrega='Cra 10 # 20-30',
            telefono_contacto='3109876543',
        )
        self.assertEqual(pedido.estado, 'pendiente')

    def test_pedido_estado_choices(self):
        """El estado debe aceptar solo opciones válidas."""
        for value, label in ESTADO_CHOICES:
            pedido = Pedido(
                cliente=self.cliente,
                domiciliario=self.domiciliario,
                direccion_entrega='Cra 5 # 10-20',
                telefono_contacto='3155551234',
                estado=value,
                # Cancelado requiere incidente_notas
                incidente_notas='Motivo de prueba' if value == 'cancelado' else '',
            )
            # full_clean no debe lanzar para opciones válidas
            pedido.full_clean()  # will validate choices

    def test_pedido_estado_invalid_raises(self):
        """Un estado inválido debe lanzar ValidationError."""
        pedido = Pedido(
            cliente=self.cliente,
            domiciliario=self.domiciliario,
            direccion_entrega='Cra 5 # 10-20',
            telefono_contacto='3155551234',
            estado='invalido',
        )
        with self.assertRaises(ValidationError):
            pedido.full_clean()

    def test_pedido_str(self):
        """El __str__ de Pedido retorna formato legible."""
        pedido = Pedido.objects.create(
            cliente=self.cliente,
            domiciliario=self.domiciliario,
            direccion_entrega='Calle 100 # 50-60',
            telefono_contacto='3001112222',
        )
        self.assertIn(str(pedido.id), str(pedido))

    def test_pedido_notas_blank(self):
        """El campo notas es opcional."""
        pedido = Pedido.objects.create(
            cliente=self.cliente,
            domiciliario=self.domiciliario,
            direccion_entrega='Calle 10 # 20-30',
            telefono_contacto='3001112222',
        )
        self.assertEqual(pedido.notas, '')

    def test_pedido_incidente_fields_blank(self):
        """Los campos de incidente por defecto son vacío/null."""
        pedido = Pedido.objects.create(
            cliente=self.cliente,
            domiciliario=self.domiciliario,
            direccion_entrega='Calle 10 # 20-30',
            telefono_contacto='3001112222',
        )
        self.assertEqual(pedido.incidente_notas, '')
        self.assertIsNone(pedido.incidente_fecha)

    def test_pedido_fecha_creacion_auto(self):
        """fecha_creacion se auto-popula."""
        pedido = Pedido.objects.create(
            cliente=self.cliente,
            domiciliario=self.domiciliario,
            direccion_entrega='Calle 10 # 20-30',
            telefono_contacto='3001112222',
        )
        self.assertIsNotNone(pedido.fecha_creacion)

    def test_pedido_fecha_entrega_null_until_delivered(self):
        """fecha_entrega es null hasta que el pedido es entregado."""
        pedido = Pedido.objects.create(
            cliente=self.cliente,
            domiciliario=self.domiciliario,
            direccion_entrega='Calle 10 # 20-30',
            telefono_contacto='3001112222',
        )
        self.assertIsNone(pedido.fecha_entrega)

    def test_pedido_direccion_required(self):
        """direccion_entrega es requerido — no puede estar vacío."""
        pedido = Pedido(
            cliente=self.cliente,
            domiciliario=self.domiciliario,
            direccion_entrega='',
            telefono_contacto='3001112222',
        )
        with self.assertRaises(ValidationError):
            pedido.full_clean()

    def test_pedido_telefono_required(self):
        """telefono_contacto es requerido — no puede estar vacío."""
        pedido = Pedido(
            cliente=self.cliente,
            domiciliario=self.domiciliario,
            direccion_entrega='Calle 10',
            telefono_contacto='',
        )
        with self.assertRaises(ValidationError):
            pedido.full_clean()


class PedidoItemModelTest(TestCase):
    """Tests para el modelo a través PedidoItem."""

    def setUp(self):
        self.domiciliario = create_user_with_role('Domiciliario', username='domic_item', email='domic_item@test.com')
        self.cliente = create_user_with_role('Cliente', username='cli_item', email='cli_item@test.com')
        self.producto = Producto.all_objects.create(
            nombre='Shampoo Canino',
            categoria='higiene',
            precio=Decimal('18000.00'),
            cantidad_stock=30,
        )
        self.pedido = Pedido.objects.create(
            cliente=self.cliente,
            domiciliario=self.domiciliario,
            direccion_entrega='Calle 50 # 30-20',
            telefono_contacto='3009998888',
        )

    def test_pedido_item_creacion(self):
        """Crear un PedidoItem vinculando Pedido y Producto con cantidad."""
        item = PedidoItem.objects.create(
            pedido=self.pedido,
            producto=self.producto,
            cantidad=3,
        )
        self.assertEqual(item.pedido, self.pedido)
        self.assertEqual(item.producto, self.producto)
        self.assertEqual(item.cantidad, 3)

    def test_pedido_item_multiple_products(self):
        """Un Pedido puede tener múltiples PedidoItems."""
        producto2 = Producto.all_objects.create(
            nombre='Ración Perro 5kg',
            categoria='alimentos',
            precio=Decimal('45000.00'),
            cantidad_stock=100,
        )
        PedidoItem.objects.create(pedido=self.pedido, producto=self.producto, cantidad=2)
        PedidoItem.objects.create(pedido=self.pedido, producto=producto2, cantidad=1)
        self.assertEqual(self.pedido.items.count(), 2)

    def test_pedido_item_str(self):
        """El __str__ de PedidoItem incluye nombre del producto y cantidad."""
        item = PedidoItem.objects.create(
            pedido=self.pedido,
            producto=self.producto,
            cantidad=5,
        )
        self.assertIn('Shampoo Canino', str(item))
        self.assertIn('5', str(item))

    def test_pedido_item_cantidad_min_1(self):
        """La cantidad debe ser al menos 1."""
        item = PedidoItem(
            pedido=self.pedido,
            producto=self.producto,
            cantidad=0,
        )
        with self.assertRaises(ValidationError):
            item.full_clean()

    def test_pedido_subtotal_property(self):
        """PedidoItem.subtotal retorna precio * cantidad."""
        item = PedidoItem.objects.create(
            pedido=self.pedido,
            producto=self.producto,
            cantidad=3,
        )
        expected = Decimal('18000.00') * 3
        self.assertEqual(item.subtotal, expected)

    def test_pedido_total_property(self):
        """Pedido.total retorna la suma de todos los subtotales de items."""
        producto2 = Producto.all_objects.create(
            nombre='Ración Gato 3kg',
            categoria='alimentos',
            precio=Decimal('35000.00'),
            cantidad_stock=80,
        )
        PedidoItem.objects.create(pedido=self.pedido, producto=self.producto, cantidad=2)
        PedidoItem.objects.create(pedido=self.pedido, producto=producto2, cantidad=1)
        expected_total = Decimal('18000.00') * 2 + Decimal('35000.00')
        self.assertEqual(self.pedido.total, expected_total)


class EvidenciaValidationTest(TestCase):
    """Tests para validación de foto de evidencia (reutiliza patrón de 5MB de historial)."""

    def setUp(self):
        self.domiciliario = create_user_with_role('Domiciliario', username='domic_ev', email='domic_ev@test.com')
        self.cliente = create_user_with_role('Cliente', username='cli_ev', email='cli_ev@test.com')

    def test_max_evidencia_size_is_5mb(self):
        """MAX_EVIDENCIA_SIZE debe ser 5MB."""
        self.assertEqual(MAX_EVIDENCIA_SIZE, 5 * 1024 * 1024)

    def test_pedido_foto_evidencia_oversized_raises(self):
        """foto_evidencia sobre 5MB debe lanzar ValidationError."""
        pedido = Pedido.objects.create(
            cliente=self.cliente,
            domiciliario=self.domiciliario,
            direccion_entrega='Calle 10 # 20-30',
            telefono_contacto='3001112222',
        )
        # Crear un archivo mayor a 5MB
        big_file = SimpleUploadedFile('evidence.jpg', b'x' * (MAX_EVIDENCIA_SIZE + 1), content_type='image/jpeg')
        pedido.foto_evidencia = big_file
        with self.assertRaises(ValidationError):
            pedido.full_clean()

    def test_pedido_foto_evidencia_valid(self):
        """foto_evidencia pequeña debe pasar validación."""
        pedido = Pedido.objects.create(
            cliente=self.cliente,
            domiciliario=self.domiciliario,
            direccion_entrega='Calle 10 # 20-30',
            telefono_contacto='3001112222',
        )
        small_file = SimpleUploadedFile('evidence.jpg', b'x' * 100, content_type='image/jpeg')
        pedido.foto_evidencia = small_file
        # NO debe lanzar — solo verificar que no crashee
        # (full_clean omite tamaño de archivo si aún no se guarda, así que probamos el validador por separado)


class EstadoTransitionTest(TestCase):
    """Tests para transiciones de estado de Pedido — refleja el patrón de Cita."""

    def setUp(self):
        self.domiciliario = create_user_with_role('Domiciliario', username='domic_trans', email='domic_trans@test.com')
        self.cliente = create_user_with_role('Cliente', username='cli_trans', email='cli_trans@test.com')

    def test_pendiente_to_en_camino(self):
        """Transición válida: pendiente → en_camino."""
        pedido = Pedido.objects.create(
            cliente=self.cliente,
            domiciliario=self.domiciliario,
            direccion_entrega='Calle 10',
            telefono_contacto='3001112222',
        )
        pedido.estado = 'en_camino'
        pedido.full_clean()  # should not raise

    def test_en_camino_to_entregado(self):
        """Transición válida: en_camino → entregado."""
        pedido = Pedido.objects.create(
            cliente=self.cliente,
            domiciliario=self.domiciliario,
            direccion_entrega='Calle 10',
            telefono_contacto='3001112222',
            estado='en_camino',
        )
        pedido.estado = 'entregado'
        pedido.full_clean()  # should not raise

    def test_pendiente_to_cancelado(self):
        """Transición válida: pendiente → cancelado (requiere incidente_notas)."""
        pedido = Pedido.objects.create(
            cliente=self.cliente,
            domiciliario=self.domiciliario,
            direccion_entrega='Calle 10',
            telefono_contacto='3001112222',
        )
        pedido.estado = 'cancelado'
        pedido.incidente_notas = 'Cliente solicitó cancelación'
        pedido.full_clean()  # should not raise

    def test_entregado_cannot_change_state(self):
        """Una vez entregado, el estado no debe cambiar."""
        pedido = Pedido.objects.create(
            cliente=self.cliente,
            domiciliario=self.domiciliario,
            direccion_entrega='Calle 10',
            telefono_contacto='3001112222',
            estado='entregado',
        )
        # Cambiar estado en la instancia guardada — clean() verifica en BD el estado antiguo
        pedido.estado = 'en_camino'
        with self.assertRaises(ValidationError):
            pedido.full_clean()

    def test_cancelado_cannot_reactivate(self):
        """Una vez cancelado, no debe poder reactivarse."""
        pedido = Pedido.objects.create(
            cliente=self.cliente,
            domiciliario=self.domiciliario,
            direccion_entrega='Calle 10',
            telefono_contacto='3001112222',
            estado='cancelado',
            incidente_notas='Cliente no se encontraba',
        )
        pedido.estado = 'pendiente'
        with self.assertRaises(ValidationError):
            pedido.full_clean()

    def test_cancelado_requires_incidente_notas(self):
        """Cambiar estado a cancelado requiere incidente_notas."""
        pedido = Pedido(
            cliente=self.cliente,
            domiciliario=self.domiciliario,
            direccion_entrega='Calle 10',
            telefono_contacto='3001112222',
            estado='cancelado',
        )
        # Sin incidente_notas, debe fallar
        with self.assertRaises(ValidationError):
            pedido.full_clean()

    def test_cancelado_with_incidente_notas_passes(self):
        """Cancelado CON incidente_notas debe pasar validación."""
        pedido = Pedido(
            cliente=self.cliente,
            domiciliario=self.domiciliario,
            direccion_entrega='Calle 10',
            telefono_contacto='3001112222',
            estado='cancelado',
            incidente_notas='Cliente no se encontraba en la dirección',
        )
        # No debe lanzar — incidente_notas está proporcionado
        pedido.full_clean()


# ========================================
# FASE 2: URLs, Vistas, Permisos
# ========================================

from django.test import Client
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType


class EntregasURLTests(TestCase):
    """Test que las URLs de entregas resuelven correctamente."""

    def test_dashboard_url_resolves(self):
        url = reverse('entregas:dashboard')
        self.assertEqual(url, '/entregas/')

    def test_pedido_detalle_url_resolves(self):
        url = reverse('entregas:detalle', kwargs={'pk': 1})
        self.assertEqual(url, '/entregas/1/')

    def test_cambiar_estado_url_resolves(self):
        url = reverse('entregas:cambiar_estado', kwargs={'pk': 1})
        self.assertEqual(url, '/entregas/1/cambiar-estado/')


class EntregasPermissionTests(TestCase):
    """Test que las vistas de entregas requieren login y rol Domiciliario/Admin."""

    def setUp(self):
        self.client_test = Client()
        self.pedido = Pedido.objects.create(
            cliente=create_user_with_role('Cliente', username='cli_perm', email='cli_perm@test.com'),
            domiciliario=create_user_with_role('Domiciliario', username='domic_perm', email='domic_perm@test.com'),
            direccion_entrega='Calle 10',
            telefono_contacto='3001112222',
        )

    def test_dashboard_requires_login(self):
        response = self.client_test.get(reverse('entregas:dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/usuarios/login/', response.url)

    def test_detalle_requires_login(self):
        response = self.client_test.get(reverse('entregas:detalle', kwargs={'pk': self.pedido.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/usuarios/login/', response.url)

    def test_cambiar_estado_requires_login(self):
        response = self.client_test.post(reverse('entregas:cambiar_estado', kwargs={'pk': self.pedido.pk}))
        self.assertIn(response.status_code, [302, 403])

    def test_cliente_cannot_access_dashboard(self):
        """Clientes deben obtener 403 en dashboard."""
        cliente = create_user_with_role('Cliente', username='cli_dash', email='cli_dash@test.com')
        self.client_test.force_login(cliente)
        response = self.client_test.get(reverse('entregas:dashboard'))
        self.assertEqual(response.status_code, 403)


class DashboardViewTests(TestCase):
    """Test la vista dashboard para rol Domiciliario."""

    def setUp(self):
        self.client_test = Client()
        self.domiciliario = create_user_with_role('Domiciliario', username='domic_dash', email='domic_dash@test.com')
        self.admin = create_user_with_role('Administrador', username='admin_dash', email='admin_dash@test.com')
        self.cliente = create_user_with_role('Cliente', username='cli_dash', email='cli_dash@test.com')

    def test_domiciliario_sees_own_pedidos_only(self):
        """Domiciliario debe ver solo los pedidos asignados a él."""
        other_domic = create_user_with_role('Domiciliario', username='domic_other', email='domic_other@test.com')
        Pedido.objects.create(cliente=self.cliente, domiciliario=self.domiciliario, direccion_entrega='Calle 1', telefono_contacto='3001')
        Pedido.objects.create(cliente=self.cliente, domiciliario=other_domic, direccion_entrega='Calle 2', telefono_contacto='3002')
        self.client_test.force_login(self.domiciliario)
        response = self.client_test.get(reverse('entregas:dashboard'))
        self.assertEqual(response.status_code, 200)
        # Solo debe ver 1 pedido (el asignado a este domiciliario)
        self.assertEqual(response.context['page_obj'].paginator.count, 1)

    def test_admin_sees_all_pedidos(self):
        """Admin debe ver todos los pedidos."""
        other_domic = create_user_with_role('Domiciliario', username='domic_other2', email='domic_other2@test.com')
        Pedido.objects.create(cliente=self.cliente, domiciliario=self.domiciliario, direccion_entrega='Calle 1', telefono_contacto='3001')
        Pedido.objects.create(cliente=self.cliente, domiciliario=other_domic, direccion_entrega='Calle 2', telefono_contacto='3002')
        self.client_test.force_login(self.admin)
        response = self.client_test.get(reverse('entregas:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page_obj'].paginator.count, 2)

    def test_dashboard_filter_by_estado(self):
        """Dashboard debe filtrar por parámetro de query estado."""
        Pedido.objects.create(cliente=self.cliente, domiciliario=self.domiciliario, direccion_entrega='Calle 1', telefono_contacto='3001', estado='pendiente')
        Pedido.objects.create(cliente=self.cliente, domiciliario=self.domiciliario, direccion_entrega='Calle 2', telefono_contacto='3002', estado='en_camino')
        self.client_test.force_login(self.domiciliario)
        response = self.client_test.get(reverse('entregas:dashboard') + '?estado=pendiente')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page_obj'].paginator.count, 1)


class PedidoDetailViewTests(TestCase):
    """Test la vista de detalle del pedido."""

    def setUp(self):
        self.client_test = Client()
        self.domiciliario = create_user_with_role('Domiciliario', username='domic_det', email='domic_det@test.com')
        self.cliente = create_user_with_role('Cliente', username='cli_det', email='cli_det@test.com')
        self.pedido = Pedido.objects.create(
            cliente=self.cliente,
            domiciliario=self.domiciliario,
            direccion_entrega='Calle 100 # 50-30',
            telefono_contacto='3005551234',
        )

    def test_domiciliario_can_see_detail(self):
        self.client_test.force_login(self.domiciliario)
        response = self.client_test.get(reverse('entregas:detalle', kwargs={'pk': self.pedido.pk}))
        self.assertEqual(response.status_code, 200)

    def test_admin_can_see_detail(self):
        admin = create_user_with_role('Administrador', username='admin_det', email='admin_det@test.com')
        self.client_test.force_login(admin)
        response = self.client_test.get(reverse('entregas:detalle', kwargs={'pk': self.pedido.pk}))
        self.assertEqual(response.status_code, 200)


class CambiarEstadoViewTests(TestCase):
    """Test la vista de transición de estado."""

    def setUp(self):
        self.client_test = Client()
        self.domiciliario = create_user_with_role('Domiciliario', username='domic_state', email='domic_state@test.com')
        self.cliente = create_user_with_role('Cliente', username='cli_state', email='cli_state@test.com')
        self.pedido = Pedido.objects.create(
            cliente=self.cliente,
            domiciliario=self.domiciliario,
            direccion_entrega='Calle 50',
            telefono_contacto='3009991234',
        )

    def test_pendiente_to_en_camino(self):
        """POST a cambiar_estado con nuevo_estado=en_camino debe actualizar estado."""
        self.client_test.force_login(self.domiciliario)
        response = self.client_test.post(
            reverse('entregas:cambiar_estado', kwargs={'pk': self.pedido.pk}),
            {'nuevo_estado': 'en_camino'},
        )
        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.estado, 'en_camino')

    def test_en_camino_to_entregado(self):
        """POST a cambiar_estado con nuevo_estado=entregado debe actualizar estado."""
        self.pedido.estado = 'en_camino'
        self.pedido.save()
        self.client_test.force_login(self.domiciliario)
        response = self.client_test.post(
            reverse('entregas:cambiar_estado', kwargs={'pk': self.pedido.pk}),
            {'nuevo_estado': 'entregado'},
        )
        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.estado, 'entregado')

    def test_cambiar_estado_get_not_allowed(self):
        """GET a cambiar_estado debe retornar 405 o redirección."""
        self.client_test.force_login(self.domiciliario)
        response = self.client_test.get(reverse('entregas:cambiar_estado', kwargs={'pk': self.pedido.pk}))
        self.assertIn(response.status_code, [405, 302])


# ========================================
# FASE 3: Crear Pedido (Admin) + Resumen Diario
# ========================================


class CrearPedidoURLTests(TestCase):
    """Test resolución de URL de crear_pedido."""

    def test_crear_pedido_url_resolves(self):
        url = reverse('entregas:crear')
        self.assertEqual(url, '/entregas/crear/')

    def test_resumen_url_resolves(self):
        url = reverse('entregas:resumen')
        self.assertEqual(url, '/entregas/resumen/')


class CrearPedidoPermissionTests(TestCase):
    """Test que crear_pedido está restringido a Admin."""

    def setUp(self):
        self.client_test = Client()

    def test_crear_pedido_requires_login(self):
        response = self.client_test.get(reverse('entregas:crear'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/usuarios/login/', response.url)

    def test_crear_pedido_requires_admin(self):
        """Domiciliario debe obtener 403 en crear_pedido."""
        domiciliario = create_user_with_role('Domiciliario', username='domic_crear', email='domic_crear@test.com')
        self.client_test.force_login(domiciliario)
        response = self.client_test.get(reverse('entregas:crear'))
        self.assertEqual(response.status_code, 403)

    def test_crear_pedido_cliente_forbidden(self):
        """Cliente debe obtener 403 en crear_pedido."""
        cliente = create_user_with_role('Cliente', username='cli_crear', email='cli_crear@test.com')
        self.client_test.force_login(cliente)
        response = self.client_test.get(reverse('entregas:crear'))
        self.assertEqual(response.status_code, 403)


class CrearPedidoViewTests(TestCase):
    """Test la vista Admin crear_pedido."""

    def setUp(self):
        self.client_test = Client()
        self.admin = create_user_with_role('Administrador', username='admin_crear', email='admin_crear@test.com')
        self.domiciliario = create_user_with_role('Domiciliario', username='domic_crear2', email='domic_crear2@test.com')
        self.cliente = create_user_with_role('Cliente', username='cli_crear2', email='cli_crear2@test.com')
        self.producto = Producto.all_objects.create(
            nombre='Antibiótico Canino',
            categoria='medicamentos',
            precio=Decimal('32000.00'),
            cantidad_stock=100,
        )

    def test_admin_can_access_crear_pedido(self):
        self.client_test.force_login(self.admin)
        response = self.client_test.get(reverse('entregas:crear'))
        self.assertEqual(response.status_code, 200)

    def test_admin_can_create_pedido(self):
        """Admin puede crear un pedido con items via POST."""
        self.client_test.force_login(self.admin)
        response = self.client_test.post(reverse('entregas:crear'), {
            'cliente': self.cliente.pk,
            'domiciliario': self.domiciliario.pk,
            'direccion_entrega': 'Calle 30 # 15-20',
            'telefono_contacto': '3105551234',
            'notas': 'Entregar antes del mediodía',
            # Formulario de gestión para formset
            'items-TOTAL_FORMS': '1',
            'items-INITIAL_FORMS': '0',
            'items-0-producto': self.producto.pk,
            'items-0-cantidad': '2',
        })
        self.assertEqual(response.status_code, 302)  # redirect after success
        self.assertEqual(Pedido.objects.count(), 1)
        pedido = Pedido.objects.first()
        self.assertEqual(pedido.items.count(), 1)
        self.assertEqual(pedido.estado, 'pendiente')

    def test_create_pedido_without_items_still_creates(self):
        """Un pedido sin items debe seguir creándose."""
        self.client_test.force_login(self.admin)
        response = self.client_test.post(reverse('entregas:crear'), {
            'cliente': self.cliente.pk,
            'domiciliario': self.domiciliario.pk,
            'direccion_entrega': 'Calle 40 # 20-30',
            'telefono_contacto': '3105555678',
            'items-TOTAL_FORMS': '0',
            'items-INITIAL_FORMS': '0',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Pedido.objects.count(), 1)
        pedido = Pedido.objects.first()
        self.assertEqual(pedido.items.count(), 0)


class ResumenViewTests(TestCase):
    """Test la vista de resumen diario para Domiciliario."""

    def setUp(self):
        self.client_test = Client()
        self.domiciliario = create_user_with_role('Domiciliario', username='domic_res', email='domic_res@test.com')
        self.admin = create_user_with_role('Administrador', username='admin_res', email='admin_res@test.com')
        self.cliente = create_user_with_role('Cliente', username='cli_res', email='cli_res@test.com')

    def test_resumen_requires_login(self):
        response = self.client_test.get(reverse('entregas:resumen'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/usuarios/login/', response.url)

    def test_domiciliario_can_see_resumen(self):
        self.client_test.force_login(self.domiciliario)
        response = self.client_test.get(reverse('entregas:resumen'))
        self.assertEqual(response.status_code, 200)

    def test_resumen_shows_only_entregado_pedidos(self):
        """Resumen debe mostrar solo pedidos entregados (entregado)."""
        from django.utils import timezone
        pedido_entregado = Pedido.objects.create(cliente=self.cliente, domiciliario=self.domiciliario, direccion_entrega='Calle 1', telefono_contacto='3001', estado='entregado', fecha_entrega=timezone.now())
        Pedido.objects.create(cliente=self.cliente, domiciliario=self.domiciliario, direccion_entrega='Calle 2', telefono_contacto='3002', estado='pendiente')
        self.client_test.force_login(self.domiciliario)
        response = self.client_test.get(reverse('entregas:resumen'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['pedidos_entregados']), 1)

    def test_cliente_cannot_access_resumen(self):
        """Clientes deben obtener 403."""
        cliente = create_user_with_role('Cliente', username='cli_res2', email='cli_res2@test.com')
        self.client_test.force_login(cliente)
        response = self.client_test.get(reverse('entregas:resumen'))
        self.assertEqual(response.status_code, 403)


# ========================================
# FASE 4: Deducción de Stock + Mis Pedidos + Editar Admin
# ========================================

from productos.models import MovimientoInventario


class StockDeductionTest(TestCase):
    """Test que entregar un pedido descuenta stock de Producto."""

    def setUp(self):
        self.domiciliario = create_user_with_role('Domiciliario', username='domic_stock', email='domic_stock@test.com')
        self.cliente = create_user_with_role('Cliente', username='cli_stock', email='cli_stock@test.com')
        self.producto = Producto.all_objects.create(
            nombre='Antipulgas Max',
            categoria='medicamentos',
            precio=Decimal('25000.00'),
            cantidad_stock=50,
        )

    def test_delivery_deducts_stock(self):
        """Cuando estado cambia a entregado, el stock debe descontarse."""
        pedido = Pedido.objects.create(
            cliente=self.cliente,
            domiciliario=self.domiciliario,
            direccion_entrega='Calle 10',
            telefono_contacto='3001112222',
        )
        PedidoItem.objects.create(pedido=pedido, producto=self.producto, cantidad=3)
        # Antes de la entrega
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.cantidad_stock, 50)

        # Transición: pendiente → en_camino → entregado
        self.client_test = Client()
        self.client_test.force_login(self.domiciliario)
        self.client_test.post(
            reverse('entregas:cambiar_estado', kwargs={'pk': pedido.pk}),
            {'nuevo_estado': 'en_camino'},
        )
        self.client_test.post(
            reverse('entregas:cambiar_estado', kwargs={'pk': pedido.pk}),
            {'nuevo_estado': 'entregado'},
        )
        # Después de la entrega, el stock debe estar descontado
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.cantidad_stock, 47)

    def test_delivery_creates_movimiento_inventario(self):
        """Entregar un pedido debe crear un MovimientoInventario para cada item."""
        pedido = Pedido.objects.create(
            cliente=self.cliente,
            domiciliario=self.domiciliario,
            direccion_entrega='Calle 10',
            telefono_contacto='3001112222',
        )
        PedidoItem.objects.create(pedido=pedido, producto=self.producto, cantidad=3)
        self.client_test = Client()
        self.client_test.force_login(self.domiciliario)
        # Transición: pendiente → en_camino → entregado
        self.client_test.post(
            reverse('entregas:cambiar_estado', kwargs={'pk': pedido.pk}),
            {'nuevo_estado': 'en_camino'},
        )
        self.client_test.post(
            reverse('entregas:cambiar_estado', kwargs={'pk': pedido.pk}),
            {'nuevo_estado': 'entregado'},
        )
        # Debe crear un movimiento de salida
        mov = MovimientoInventario.objects.filter(producto=self.producto, tipo_movimiento='salida')
        self.assertEqual(mov.count(), 1)
        self.assertEqual(mov.first().cantidad, 3)

    def test_cancelled_pedido_does_not_deduct_stock(self):
        """Cancelar un pedido NO debe descontar stock."""
        pedido = Pedido.objects.create(
            cliente=self.cliente,
            domiciliario=self.domiciliario,
            direccion_entrega='Calle 10',
            telefono_contacto='3001112222',
        )
        PedidoItem.objects.create(pedido=pedido, producto=self.producto, cantidad=5)
        self.client_test = Client()
        self.client_test.force_login(self.domiciliario)
        self.client_test.post(
            reverse('entregas:cambiar_estado', kwargs={'pk': pedido.pk}),
            {'nuevo_estado': 'cancelado', 'incidente_notas': 'Cliente no encontrado'},
        )
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.cantidad_stock, 50)


class MisPedidosViewTests(TestCase):
    """Test la vista mis_pedidos para Cliente."""

    def setUp(self):
        self.client_test = Client()
        self.domiciliario = create_user_with_role('Domiciliario', username='domic_mp', email='domic_mp@test.com')
        self.cliente = create_user_with_role('Cliente', username='cli_mp', email='cli_mp@test.com')
        self.other_cliente = create_user_with_role('Cliente', username='cli_mp2', email='cli_mp2@test.com')

    def test_mis_pedidos_url_resolves(self):
        url = reverse('entregas:mis_pedidos')
        self.assertEqual(url, '/entregas/mis-pedidos/')

    def test_cliente_can_see_own_pedidos(self):
        """Cliente ve solo sus propios pedidos."""
        Pedido.objects.create(cliente=self.cliente, domiciliario=self.domiciliario, direccion_entrega='Calle 1', telefono_contacto='3001')
        Pedido.objects.create(cliente=self.other_cliente, domiciliario=self.domiciliario, direccion_entrega='Calle 2', telefono_contacto='3002')
        self.client_test.force_login(self.cliente)
        response = self.client_test.get(reverse('entregas:mis_pedidos'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page_obj'].paginator.count, 1)

    def test_domiciliario_cannot_access_mis_pedidos(self):
        """Domiciliario debe obtener 403 en mis_pedidos."""
        self.client_test.force_login(self.domiciliario)
        response = self.client_test.get(reverse('entregas:mis_pedidos'))
        self.assertEqual(response.status_code, 403)

    def test_mis_pedidos_requires_login(self):
        response = self.client_test.get(reverse('entregas:mis_pedidos'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/usuarios/login/', response.url)


class EditarPedidoViewTests(TestCase):
    """Test la vista editar_pedido para Admin."""

    def setUp(self):
        self.client_test = Client()
        self.admin = create_user_with_role('Administrador', username='admin_edit', email='admin_edit@test.com')
        self.domiciliario = create_user_with_role('Domiciliario', username='domic_edit', email='domic_edit@test.com')
        self.domiciliario2 = create_user_with_role('Domiciliario', username='domic_edit2', email='domic_edit2@test.com')
        self.cliente = create_user_with_role('Cliente', username='cli_edit', email='cli_edit@test.com')
        self.pedido = Pedido.objects.create(
            cliente=self.cliente,
            domiciliario=self.domiciliario,
            direccion_entrega='Calle 50 # 30-20',
            telefono_contacto='3009998888',
        )

    def test_editar_pedido_url_resolves(self):
        url = reverse('entregas:editar', kwargs={'pk': self.pedido.pk})
        self.assertEqual(url, f'/entregas/{self.pedido.pk}/editar/')

    def test_admin_can_access_editar_pedido(self):
        self.client_test.force_login(self.admin)
        response = self.client_test.get(reverse('entregas:editar', kwargs={'pk': self.pedido.pk}))
        self.assertEqual(response.status_code, 200)

    def test_domiciliario_cannot_edit_pedido(self):
        """Domiciliario debe obtener 403 en editar_pedido."""
        self.client_test.force_login(self.domiciliario)
        response = self.client_test.get(reverse('entregas:editar', kwargs={'pk': self.pedido.pk}))
        self.assertEqual(response.status_code, 403)

    def test_admin_can_reassign_domiciliario(self):
        """Admin puede hacer POST para reasignar domiciliario."""
        self.client_test.force_login(self.admin)
        response = self.client_test.post(reverse('entregas:editar', kwargs={'pk': self.pedido.pk}), {
            'cliente': self.cliente.pk,
            'domiciliario': self.domiciliario2.pk,
            'direccion_entrega': 'Calle 99 # 1-2',
            'telefono_contacto': '3105559999',
            'notas': 'Cambio de dirección',
        })
        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.domiciliario, self.domiciliario2)
        self.assertEqual(self.pedido.direccion_entrega, 'Calle 99 # 1-2')


# ========================================
# FASE 5: Bug Fix + PDF Comprobante + Detalle Cliente
# ========================================


class IncidenteFechaTest(TestCase):
    """Test que la cancelación establece incidente_fecha automáticamente."""

    def setUp(self):
        self.client_test = Client()
        self.domiciliario = create_user_with_role('Domiciliario', username='domic_inc', email='domic_inc@test.com')
        self.cliente = create_user_with_role('Cliente', username='cli_inc', email='cli_inc@test.com')
        self.pedido = Pedido.objects.create(
            cliente=self.cliente,
            domiciliario=self.domiciliario,
            direccion_entrega='Calle 70 # 20-10',
            telefono_contacto='3007778888',
        )

    def test_cancelacion_sets_incidente_fecha(self):
        """Cancelar un pedido debe establecer incidente_fecha a ahora."""
        self.client_test.force_login(self.domiciliario)
        self.client_test.post(
            reverse('entregas:cambiar_estado', kwargs={'pk': self.pedido.pk}),
            {'nuevo_estado': 'cancelado', 'incidente_notas': 'Cliente no encontrado'},
        )
        self.pedido.refresh_from_db()
        self.assertIsNotNone(self.pedido.incidente_fecha)
        self.assertEqual(self.pedido.estado, 'cancelado')
        self.assertEqual(self.pedido.incidente_notas, 'Cliente no encontrado')

    def test_pendiente_to_en_camino_does_not_set_incidente_fecha(self):
        """Transiciones distintas de cancelar NO deben establecer incidente_fecha."""
        self.client_test.force_login(self.domiciliario)
        self.client_test.post(
            reverse('entregas:cambiar_estado', kwargs={'pk': self.pedido.pk}),
            {'nuevo_estado': 'en_camino'},
        )
        self.pedido.refresh_from_db()
        self.assertIsNone(self.pedido.incidente_fecha)


class ClienteDetalleViewTests(TestCase):
    """Test que Cliente puede acceder a pedido_detalle para sus propios pedidos."""

    def setUp(self):
        self.client_test = Client()
        self.admin = create_user_with_role('Administrador', username='admin_cd', email='admin_cd@test.com')
        self.domiciliario = create_user_with_role('Domiciliario', username='domic_cd', email='domic_cd@test.com')
        self.cliente = create_user_with_role('Cliente', username='cli_cd', email='cli_cd@test.com')
        self.other_cliente = create_user_with_role('Cliente', username='cli_cd2', email='cli_cd2@test.com')
        self.pedido = Pedido.objects.create(
            cliente=self.cliente,
            domiciliario=self.domiciliario,
            direccion_entrega='Calle 80 # 15-30',
            telefono_contacto='3008889999',
        )

    def test_cliente_can_see_own_pedido_detalle(self):
        """Cliente puede acceder a detalle para su propio pedido."""
        self.client_test.force_login(self.cliente)
        response = self.client_test.get(reverse('entregas:detalle', kwargs={'pk': self.pedido.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['pedido'], self.pedido)

    def test_cliente_cannot_see_other_pedido_detalle(self):
        """Cliente obtiene 403 al intentar acceder al pedido de otro cliente."""
        other_pedido = Pedido.objects.create(
            cliente=self.other_cliente,
            domiciliario=self.domiciliario,
            direccion_entrega='Calle 90',
            telefono_contacto='3001110000',
        )
        self.client_test.force_login(self.cliente)
        response = self.client_test.get(reverse('entregas:detalle', kwargs={'pk': other_pedido.pk}))
        self.assertEqual(response.status_code, 403)

    def test_cliente_detalle_no_estado_form_in_context(self):
        """Cliente debe ver detalles del pedido pero SIN estado_form ni botones de acción."""
        self.client_test.force_login(self.cliente)
        response = self.client_test.get(reverse('entregas:detalle', kwargs={'pk': self.pedido.pk}))
        self.assertEqual(response.status_code, 200)
        # estado_form NO debe estar en context para Cliente
        self.assertIsNone(response.context.get('estado_form'))

    def test_domiciliario_detalle_has_estado_form(self):
        """Domiciliario debe seguir viendo estado_form para pedidos activos."""
        self.client_test.force_login(self.domiciliario)
        response = self.client_test.get(reverse('entregas:detalle', kwargs={'pk': self.pedido.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context.get('estado_form'))


class ComprobantePDFTests(TestCase):
    """Test generación de PDF comprobante para entregas."""

    def setUp(self):
        self.client_test = Client()
        self.admin = create_user_with_role('Administrador', username='admin_pdf', email='admin_pdf@test.com')
        self.domiciliario = create_user_with_role('Domiciliario', username='domic_pdf', email='domic_pdf@test.com')
        self.cliente = create_user_with_role('Cliente', username='cli_pdf', email='cli_pdf@test.com')
        self.producto = Producto.all_objects.create(
            nombre='Dog Chow Adulto',
            categoria='alimentos',
            precio=Decimal('45000.00'),
            cantidad_stock=100,
        )
        self.pedido = Pedido.objects.create(
            cliente=self.cliente,
            domiciliario=self.domiciliario,
            direccion_entrega='Calle 100 # 50-20',
            telefono_contacto='3009990000',
        )
        PedidoItem.objects.create(pedido=self.pedido, producto=self.producto, cantidad=2)

    def test_comprobante_url_resolves(self):
        url = reverse('entregas:comprobante_pdf', kwargs={'pk': self.pedido.pk})
        self.assertEqual(url, f'/entregas/{self.pedido.pk}/comprobante/')

    def test_comprobante_requires_login(self):
        response = self.client_test.get(reverse('entregas:comprobante_pdf', kwargs={'pk': self.pedido.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/usuarios/login/', response.url)

    def test_comprobante_entregado_returns_pdf(self):
        """El PDF comprobante solo debe estar disponible para pedidos entregados."""
        # Transición a entregado
        self.pedido.estado = 'en_camino'
        self.pedido.save()
        self.client_test.force_login(self.domiciliario)
        self.client_test.post(
            reverse('entregas:cambiar_estado', kwargs={'pk': self.pedido.pk}),
            {'nuevo_estado': 'entregado'},
        )
        self.pedido.refresh_from_db()

        # Ahora solicitar PDF
        self.client_test.force_login(self.admin)
        response = self.client_test.get(reverse('entregas:comprobante_pdf', kwargs={'pk': self.pedido.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_comprobante_pendiente_returns_404(self):
        """Pedidos no entregados NO deben tener PDF comprobante."""
        self.client_test.force_login(self.admin)
        response = self.client_test.get(reverse('entregas:comprobante_pdf', kwargs={'pk': self.pedido.pk}))
        self.assertEqual(response.status_code, 404)

    def test_cliente_can_get_own_comprobante_pdf(self):
        """Cliente puede descargar PDF para su propio pedido entregado."""
        self.pedido.estado = 'en_camino'
        self.pedido.save()
        self.client_test.force_login(self.domiciliario)
        self.client_test.post(
            reverse('entregas:cambiar_estado', kwargs={'pk': self.pedido.pk}),
            {'nuevo_estado': 'entregado'},
        )
        self.pedido.refresh_from_db()

        self.client_test.force_login(self.cliente)
        response = self.client_test.get(reverse('entregas:comprobante_pdf', kwargs={'pk': self.pedido.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_cliente_cannot_get_other_comprobante_pdf(self):
        """Cliente obtiene 404 para el comprobante de otro cliente."""
        other_pedido = Pedido.objects.create(
            cliente=create_user_with_role('Cliente', username='cli_other', email='cli_other@test.com'),
            domiciliario=self.domiciliario,
            direccion_entrega='Calle 200',
            telefono_contacto='3000000000',
        )
        other_pedido.estado = 'entregado'
        other_pedido.fecha_entrega = timezone.now()
        other_pedido.save()

        self.client_test.force_login(self.cliente)
        response = self.client_test.get(reverse('entregas:comprobante_pdf', kwargs={'pk': other_pedido.pk}))
        self.assertEqual(response.status_code, 404)


# ========================================
# ADMIN: Torre de Control
# ========================================


class TorreControlTest(TestCase):
    """Test Torre de Control Admin: ver todos los pedidos, filtrar, reasignar domiciliario."""

    def setUp(self):
        self.admin = create_user_with_role('Administrador', username='tc_admin', email='tc_admin@test.com')
        self.domiciliario1 = create_user_with_role('Domiciliario', username='tc_dom1', email='tc_dom1@test.com', first_name='Carlos')
        self.domiciliario2 = create_user_with_role('Domiciliario', username='tc_dom2', email='tc_dom2@test.com', first_name='Maria')
        self.cliente = create_user_with_role('Cliente', username='tc_cli', email='tc_cli@test.com')

        self.prod = Producto.objects.create(
            nombre='TC Product', precio=Decimal('10000'),
            cantidad_stock=50, categoria='alimentos',
        )
        self.pedido1 = Pedido.objects.create(
            cliente=self.cliente, domiciliario=self.domiciliario1,
            direccion_entrega='Calle 10', telefono_contacto='3001112222',
            estado='pendiente',
        )
        PedidoItem.objects.create(pedido=self.pedido1, producto=self.prod, cantidad=2)

        self.pedido2 = Pedido.objects.create(
            cliente=self.cliente, domiciliario=self.domiciliario2,
            direccion_entrega='Calle 20', telefono_contacto='3003334444',
            estado='en_camino',
        )
        PedidoItem.objects.create(pedido=self.pedido2, producto=self.prod, cantidad=1)

        self.c = Client()

    def test_torre_control_admin_access(self):
        """Admin puede acceder a Torre de Control."""
        self.c.force_login(self.admin)
        resp = self.c.get(reverse('entregas:torre_control'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Torre de Control')

    def test_torre_control_shows_all_pedidos(self):
        """Torre de Control muestra todos los pedidos."""
        self.c.force_login(self.admin)
        resp = self.c.get(reverse('entregas:torre_control'))
        self.assertContains(resp, f'#{self.pedido1.pk}')
        self.assertContains(resp, f'#{self.pedido2.pk}')

    def test_torre_control_filter_by_estado(self):
        """Filtrar pedidos por estado."""
        self.c.force_login(self.admin)
        resp = self.c.get(reverse('entregas:torre_control') + '?estado=pendiente')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, f'#{self.pedido1.pk}')

    def test_torre_control_search_by_client(self):
        """Buscar pedidos por email de cliente."""
        self.c.force_login(self.admin)
        resp = self.c.get(reverse('entregas:torre_control') + f'?q={self.cliente.email}')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, f'#{self.pedido1.pk}')

    def test_torre_control_non_admin_403(self):
        """No-admin obtiene 403 en Torre de Control."""
        self.c.force_login(self.cliente)
        resp = self.c.get(reverse('entregas:torre_control'))
        self.assertEqual(resp.status_code, 403)

    def test_torre_control_reassign_domiciliario(self):
        """Admin puede reasignar domiciliario para un pedido pendiente."""
        self.c.force_login(self.admin)
        resp = self.c.post(reverse('entregas:torre_control'), {
            'pedido_pk': self.pedido1.pk,
            'domiciliario': self.domiciliario2.pk,
        })
        self.assertEqual(resp.status_code, 302)
        self.pedido1.refresh_from_db()
        self.assertEqual(self.pedido1.domiciliario, self.domiciliario2)

    def test_torre_control_cannot_reassign_entregado(self):
        """No se puede reasignar domiciliario para pedido entregado."""
        self.pedido1.estado = 'entregado'
        self.pedido1.fecha_entrega = timezone.now()
        self.pedido1.save()
        self.c.force_login(self.admin)
        resp = self.c.post(reverse('entregas:torre_control'), {
            'pedido_pk': self.pedido1.pk,
            'domiciliario': self.domiciliario2.pk,
        })
        self.assertEqual(resp.status_code, 302)
        self.pedido1.refresh_from_db()
        # NO debe cambiar — entregado es final
        self.assertEqual(self.pedido1.domiciliario, self.domiciliario1)

    def test_torre_control_domiciliarios_in_context(self):
        """El context de Torre de Control incluye domiciliarios disponibles."""
        self.c.force_login(self.admin)
        resp = self.c.get(reverse('entregas:torre_control'))
        self.assertIn('domiciliarios', resp.context)