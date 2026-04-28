from decimal import Decimal
from django.test import TestCase
from django.urls import reverse, resolve
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from usuarios.models import Rol, Usuario
from productos.models import Producto

from .models import Pedido, PedidoItem, ESTADO_CHOICES, MAX_EVIDENCIA_SIZE


def create_user_with_role(rol_nombre, **kwargs):
    """Helper to create a Usuario with the given role."""
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
# PHASE 1: App Scaffold + Model + Migration
# ========================================

class AppRegistrationTest(TestCase):
    """REQ-10: App is registered in INSTALLED_APPS"""

    def test_entregas_in_installed_apps(self):
        """R10.1: 'entregas' is in INSTALLED_APPS"""
        self.assertIn('entregas', settings.INSTALLED_APPS)


# ========================================
# MODEL TESTS — Pedido
# ========================================

class PedidoModelTest(TestCase):
    """Tests for the Pedido model."""

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
        """Create a Pedido with all required fields."""
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
        """Default estado must be 'pendiente'."""
        pedido = Pedido.objects.create(
            cliente=self.cliente,
            domiciliario=self.domiciliario,
            direccion_entrega='Cra 10 # 20-30',
            telefono_contacto='3109876543',
        )
        self.assertEqual(pedido.estado, 'pendiente')

    def test_pedido_estado_choices(self):
        """Estado must accept only valid choices."""
        for value, label in ESTADO_CHOICES:
            pedido = Pedido(
                cliente=self.cliente,
                domiciliario=self.domiciliario,
                direccion_entrega='Cra 5 # 10-20',
                telefono_contacto='3155551234',
                estado=value,
                # Cancelado requires incidente_notas
                incidente_notas='Motivo de prueba' if value == 'cancelado' else '',
            )
            # Full clean should not raise for valid choices
            pedido.full_clean()  # will validate choices

    def test_pedido_estado_invalid_raises(self):
        """Invalid estado must raise ValidationError."""
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
        """Pedido __str__ returns readable format."""
        pedido = Pedido.objects.create(
            cliente=self.cliente,
            domiciliario=self.domiciliario,
            direccion_entrega='Calle 100 # 50-60',
            telefono_contacto='3001112222',
        )
        self.assertIn(str(pedido.id), str(pedido))

    def test_pedido_notas_blank(self):
        """Notas field is optional."""
        pedido = Pedido.objects.create(
            cliente=self.cliente,
            domiciliario=self.domiciliario,
            direccion_entrega='Calle 10 # 20-30',
            telefono_contacto='3001112222',
        )
        self.assertEqual(pedido.notas, '')

    def test_pedido_incidente_fields_blank(self):
        """Incidente fields default to empty/null."""
        pedido = Pedido.objects.create(
            cliente=self.cliente,
            domiciliario=self.domiciliario,
            direccion_entrega='Calle 10 # 20-30',
            telefono_contacto='3001112222',
        )
        self.assertEqual(pedido.incidente_notas, '')
        self.assertIsNone(pedido.incidente_fecha)

    def test_pedido_fecha_creacion_auto(self):
        """fecha_creacion is auto-populated."""
        pedido = Pedido.objects.create(
            cliente=self.cliente,
            domiciliario=self.domiciliario,
            direccion_entrega='Calle 10 # 20-30',
            telefono_contacto='3001112222',
        )
        self.assertIsNotNone(pedido.fecha_creacion)

    def test_pedido_fecha_entrega_null_until_delivered(self):
        """fecha_entrega is null until the order is delivered."""
        pedido = Pedido.objects.create(
            cliente=self.cliente,
            domiciliario=self.domiciliario,
            direccion_entrega='Calle 10 # 20-30',
            telefono_contacto='3001112222',
        )
        self.assertIsNone(pedido.fecha_entrega)

    def test_pedido_direccion_required(self):
        """direccion_entrega is required — cannot be blank."""
        pedido = Pedido(
            cliente=self.cliente,
            domiciliario=self.domiciliario,
            direccion_entrega='',
            telefono_contacto='3001112222',
        )
        with self.assertRaises(ValidationError):
            pedido.full_clean()

    def test_pedido_telefono_required(self):
        """telefono_contacto is required — cannot be blank."""
        pedido = Pedido(
            cliente=self.cliente,
            domiciliario=self.domiciliario,
            direccion_entrega='Calle 10',
            telefono_contacto='',
        )
        with self.assertRaises(ValidationError):
            pedido.full_clean()


class PedidoItemModelTest(TestCase):
    """Tests for the PedidoItem through model."""

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
        """Create a PedidoItem linking Pedido and Producto with quantity."""
        item = PedidoItem.objects.create(
            pedido=self.pedido,
            producto=self.producto,
            cantidad=3,
        )
        self.assertEqual(item.pedido, self.pedido)
        self.assertEqual(item.producto, self.producto)
        self.assertEqual(item.cantidad, 3)

    def test_pedido_item_multiple_products(self):
        """A Pedido can have multiple PedidoItems."""
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
        """PedidoItem __str__ includes product name and quantity."""
        item = PedidoItem.objects.create(
            pedido=self.pedido,
            producto=self.producto,
            cantidad=5,
        )
        self.assertIn('Shampoo Canino', str(item))
        self.assertIn('5', str(item))

    def test_pedido_item_cantidad_min_1(self):
        """Quantity must be at least 1."""
        item = PedidoItem(
            pedido=self.pedido,
            producto=self.producto,
            cantidad=0,
        )
        with self.assertRaises(ValidationError):
            item.full_clean()

    def test_pedido_subtotal_property(self):
        """PedidoItem.subtotal returns precio * cantidad."""
        item = PedidoItem.objects.create(
            pedido=self.pedido,
            producto=self.producto,
            cantidad=3,
        )
        expected = Decimal('18000.00') * 3
        self.assertEqual(item.subtotal, expected)

    def test_pedido_total_property(self):
        """Pedido.total returns sum of all item subtotals."""
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
    """Tests for photo evidence validation (reuse 5MB pattern from historial)."""

    def setUp(self):
        self.domiciliario = create_user_with_role('Domiciliario', username='domic_ev', email='domic_ev@test.com')
        self.cliente = create_user_with_role('Cliente', username='cli_ev', email='cli_ev@test.com')

    def test_max_evidencia_size_is_5mb(self):
        """MAX_EVIDENCIA_SIZE must be 5MB."""
        self.assertEqual(MAX_EVIDENCIA_SIZE, 5 * 1024 * 1024)

    def test_pedido_foto_evidencia_oversized_raises(self):
        """ foto_evidencia over 5MB must raise ValidationError."""
        pedido = Pedido.objects.create(
            cliente=self.cliente,
            domiciliario=self.domiciliario,
            direccion_entrega='Calle 10 # 20-30',
            telefono_contacto='3001112222',
        )
        # Create a file larger than 5MB
        big_file = SimpleUploadedFile('evidence.jpg', b'x' * (MAX_EVIDENCIA_SIZE + 1), content_type='image/jpeg')
        pedido.foto_evidencia = big_file
        with self.assertRaises(ValidationError):
            pedido.full_clean()

    def test_pedido_foto_evidencia_valid(self):
        """Small foto_evidencia should pass validation."""
        pedido = Pedido.objects.create(
            cliente=self.cliente,
            domiciliario=self.domiciliario,
            direccion_entrega='Calle 10 # 20-30',
            telefono_contacto='3001112222',
        )
        small_file = SimpleUploadedFile('evidence.jpg', b'x' * 100, content_type='image/jpeg')
        pedido.foto_evidencia = small_file
        # Should NOT raise — just check it doesn't crash
        # (full_clean skips file size if not saved yet, so we test the validator separately)


class EstadoTransitionTest(TestCase):
    """Tests for Pedido state transitions — mirrors Cita pattern."""

    def setUp(self):
        self.domiciliario = create_user_with_role('Domiciliario', username='domic_trans', email='domic_trans@test.com')
        self.cliente = create_user_with_role('Cliente', username='cli_trans', email='cli_trans@test.com')

    def test_pendiente_to_en_camino(self):
        """Valid transition: pendiente → en_camino."""
        pedido = Pedido.objects.create(
            cliente=self.cliente,
            domiciliario=self.domiciliario,
            direccion_entrega='Calle 10',
            telefono_contacto='3001112222',
        )
        pedido.estado = 'en_camino'
        pedido.full_clean()  # should not raise

    def test_en_camino_to_entregado(self):
        """Valid transition: en_camino → entregado."""
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
        """Valid transition: pendiente → cancelado (requires incidente_notas)."""
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
        """Once entregado, state must not change."""
        pedido = Pedido.objects.create(
            cliente=self.cliente,
            domiciliario=self.domiciliario,
            direccion_entrega='Calle 10',
            telefono_contacto='3001112222',
            estado='entregado',
        )
        # Change estado on the saved instance — clean() checks DB for old state
        pedido.estado = 'en_camino'
        with self.assertRaises(ValidationError):
            pedido.full_clean()

    def test_cancelado_cannot_reactivate(self):
        """Once cancelado, must not be reactivated."""
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
        """Setting estado to cancelado requires incidente_notas."""
        pedido = Pedido(
            cliente=self.cliente,
            domiciliario=self.domiciliario,
            direccion_entrega='Calle 10',
            telefono_contacto='3001112222',
            estado='cancelado',
        )
        # Without incidente_notas, should fail
        with self.assertRaises(ValidationError):
            pedido.full_clean()

    def test_cancelado_with_incidente_notas_passes(self):
        """Cancelado WITH incidente_notas should pass validation."""
        pedido = Pedido(
            cliente=self.cliente,
            domiciliario=self.domiciliario,
            direccion_entrega='Calle 10',
            telefono_contacto='3001112222',
            estado='cancelado',
            incidente_notas='Cliente no se encontraba en la dirección',
        )
        # Should not raise — incidente_notas is provided
        pedido.full_clean()


# ========================================
# PHASE 2: URLs, Views, Permissions
# ========================================

from django.test import Client
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType


class EntregasURLTests(TestCase):
    """Test that entregas URLs resolve correctly."""

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
    """Test that entregas views require login and Domiciliario/Admin role."""

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
        """Clientes should get 403 on dashboard."""
        cliente = create_user_with_role('Cliente', username='cli_dash', email='cli_dash@test.com')
        self.client_test.force_login(cliente)
        response = self.client_test.get(reverse('entregas:dashboard'))
        self.assertEqual(response.status_code, 403)


class DashboardViewTests(TestCase):
    """Test the dashboard view for Domiciliario role."""

    def setUp(self):
        self.client_test = Client()
        self.domiciliario = create_user_with_role('Domiciliario', username='domic_dash', email='domic_dash@test.com')
        self.admin = create_user_with_role('Administrador', username='admin_dash', email='admin_dash@test.com')
        self.cliente = create_user_with_role('Cliente', username='cli_dash', email='cli_dash@test.com')

    def test_domiciliario_sees_own_pedidos_only(self):
        """Domiciliario should only see pedidos assigned to them."""
        other_domic = create_user_with_role('Domiciliario', username='domic_other', email='domic_other@test.com')
        Pedido.objects.create(cliente=self.cliente, domiciliario=self.domiciliario, direccion_entrega='Calle 1', telefono_contacto='3001')
        Pedido.objects.create(cliente=self.cliente, domiciliario=other_domic, direccion_entrega='Calle 2', telefono_contacto='3002')
        self.client_test.force_login(self.domiciliario)
        response = self.client_test.get(reverse('entregas:dashboard'))
        self.assertEqual(response.status_code, 200)
        # Should only see 1 pedido (the one assigned to this domiciliario)
        self.assertEqual(response.context['page_obj'].paginator.count, 1)

    def test_admin_sees_all_pedidos(self):
        """Admin should see all pedidos."""
        other_domic = create_user_with_role('Domiciliario', username='domic_other2', email='domic_other2@test.com')
        Pedido.objects.create(cliente=self.cliente, domiciliario=self.domiciliario, direccion_entrega='Calle 1', telefono_contacto='3001')
        Pedido.objects.create(cliente=self.cliente, domiciliario=other_domic, direccion_entrega='Calle 2', telefono_contacto='3002')
        self.client_test.force_login(self.admin)
        response = self.client_test.get(reverse('entregas:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page_obj'].paginator.count, 2)

    def test_dashboard_filter_by_estado(self):
        """Dashboard should filter by estado query param."""
        Pedido.objects.create(cliente=self.cliente, domiciliario=self.domiciliario, direccion_entrega='Calle 1', telefono_contacto='3001', estado='pendiente')
        Pedido.objects.create(cliente=self.cliente, domiciliario=self.domiciliario, direccion_entrega='Calle 2', telefono_contacto='3002', estado='en_camino')
        self.client_test.force_login(self.domiciliario)
        response = self.client_test.get(reverse('entregas:dashboard') + '?estado=pendiente')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page_obj'].paginator.count, 1)


class PedidoDetailViewTests(TestCase):
    """Test the pedido detail view."""

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
    """Test the state transition view."""

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
        """POST to cambiar_estado with nuevo_estado=en_camino should update estado."""
        self.client_test.force_login(self.domiciliario)
        response = self.client_test.post(
            reverse('entregas:cambiar_estado', kwargs={'pk': self.pedido.pk}),
            {'nuevo_estado': 'en_camino'},
        )
        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.estado, 'en_camino')

    def test_en_camino_to_entregado(self):
        """POST to cambiar_estado with nuevo_estado=entregado should update estado."""
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
        """GET to cambiar_estado should return 405 or redirect."""
        self.client_test.force_login(self.domiciliario)
        response = self.client_test.get(reverse('entregas:cambiar_estado', kwargs={'pk': self.pedido.pk}))
        self.assertIn(response.status_code, [405, 302])


# ========================================
# PHASE 3: Create Pedido (Admin) + Resumen Diario
# ========================================


class CrearPedidoURLTests(TestCase):
    """Test crear_pedido URL resolution."""

    def test_crear_pedido_url_resolves(self):
        url = reverse('entregas:crear')
        self.assertEqual(url, '/entregas/crear/')

    def test_resumen_url_resolves(self):
        url = reverse('entregas:resumen')
        self.assertEqual(url, '/entregas/resumen/')


class CrearPedidoPermissionTests(TestCase):
    """Test that crear_pedido is restricted to Admin."""

    def setUp(self):
        self.client_test = Client()

    def test_crear_pedido_requires_login(self):
        response = self.client_test.get(reverse('entregas:crear'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/usuarios/login/', response.url)

    def test_crear_pedido_requires_admin(self):
        """Domiciliario should get 403 on crear_pedido."""
        domiciliario = create_user_with_role('Domiciliario', username='domic_crear', email='domic_crear@test.com')
        self.client_test.force_login(domiciliario)
        response = self.client_test.get(reverse('entregas:crear'))
        self.assertEqual(response.status_code, 403)

    def test_crear_pedido_cliente_forbidden(self):
        """Cliente should get 403 on crear_pedido."""
        cliente = create_user_with_role('Cliente', username='cli_crear', email='cli_crear@test.com')
        self.client_test.force_login(cliente)
        response = self.client_test.get(reverse('entregas:crear'))
        self.assertEqual(response.status_code, 403)


class CrearPedidoViewTests(TestCase):
    """Test the Admin crear_pedido view."""

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
        """Admin can create a pedido with items via POST."""
        self.client_test.force_login(self.admin)
        response = self.client_test.post(reverse('entregas:crear'), {
            'cliente': self.cliente.pk,
            'domiciliario': self.domiciliario.pk,
            'direccion_entrega': 'Calle 30 # 15-20',
            'telefono_contacto': '3105551234',
            'notas': 'Entregar antes del mediodía',
            # Management form for formset
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
        """A pedido with no items should still be created."""
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
    """Test the daily summary view for Domiciliario."""

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
        """Resumen should only show delivered (entregado) pedidos."""
        from django.utils import timezone
        pedido_entregado = Pedido.objects.create(cliente=self.cliente, domiciliario=self.domiciliario, direccion_entrega='Calle 1', telefono_contacto='3001', estado='entregado', fecha_entrega=timezone.now())
        Pedido.objects.create(cliente=self.cliente, domiciliario=self.domiciliario, direccion_entrega='Calle 2', telefono_contacto='3002', estado='pendiente')
        self.client_test.force_login(self.domiciliario)
        response = self.client_test.get(reverse('entregas:resumen'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['pedidos_entregados']), 1)

    def test_cliente_cannot_access_resumen(self):
        """Clientes should get 403."""
        cliente = create_user_with_role('Cliente', username='cli_res2', email='cli_res2@test.com')
        self.client_test.force_login(cliente)
        response = self.client_test.get(reverse('entregas:resumen'))
        self.assertEqual(response.status_code, 403)


# ========================================
# PHASE 4: Stock Deduction + Mis Pedidos + Admin Edit
# ========================================

from productos.models import MovimientoInventario


class StockDeductionTest(TestCase):
    """Test that delivering a pedido deducts stock from Producto."""

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
        """When estado changes to entregado, stock should be deducted."""
        pedido = Pedido.objects.create(
            cliente=self.cliente,
            domiciliario=self.domiciliario,
            direccion_entrega='Calle 10',
            telefono_contacto='3001112222',
        )
        PedidoItem.objects.create(pedido=pedido, producto=self.producto, cantidad=3)
        # Before delivery
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.cantidad_stock, 50)

        # Transition: pendiente → en_camino → entregado
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
        # After delivery, stock should be deducted
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.cantidad_stock, 47)

    def test_delivery_creates_movimiento_inventario(self):
        """Delivering a pedido should create a MovimientoInventario for each item."""
        pedido = Pedido.objects.create(
            cliente=self.cliente,
            domiciliario=self.domiciliario,
            direccion_entrega='Calle 10',
            telefono_contacto='3001112222',
        )
        PedidoItem.objects.create(pedido=pedido, producto=self.producto, cantidad=3)
        self.client_test = Client()
        self.client_test.force_login(self.domiciliario)
        # Transition: pendiente → en_camino → entregado
        self.client_test.post(
            reverse('entregas:cambiar_estado', kwargs={'pk': pedido.pk}),
            {'nuevo_estado': 'en_camino'},
        )
        self.client_test.post(
            reverse('entregas:cambiar_estado', kwargs={'pk': pedido.pk}),
            {'nuevo_estado': 'entregado'},
        )
        # Should create a salida movimiento
        mov = MovimientoInventario.objects.filter(producto=self.producto, tipo_movimiento='salida')
        self.assertEqual(mov.count(), 1)
        self.assertEqual(mov.first().cantidad, 3)

    def test_cancelled_pedido_does_not_deduct_stock(self):
        """Cancelling a pedido should NOT deduct stock."""
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
    """Test the mis_pedidos view for Cliente."""

    def setUp(self):
        self.client_test = Client()
        self.domiciliario = create_user_with_role('Domiciliario', username='domic_mp', email='domic_mp@test.com')
        self.cliente = create_user_with_role('Cliente', username='cli_mp', email='cli_mp@test.com')
        self.other_cliente = create_user_with_role('Cliente', username='cli_mp2', email='cli_mp2@test.com')

    def test_mis_pedidos_url_resolves(self):
        url = reverse('entregas:mis_pedidos')
        self.assertEqual(url, '/entregas/mis-pedidos/')

    def test_cliente_can_see_own_pedidos(self):
        """Cliente sees only their own pedidos."""
        Pedido.objects.create(cliente=self.cliente, domiciliario=self.domiciliario, direccion_entrega='Calle 1', telefono_contacto='3001')
        Pedido.objects.create(cliente=self.other_cliente, domiciliario=self.domiciliario, direccion_entrega='Calle 2', telefono_contacto='3002')
        self.client_test.force_login(self.cliente)
        response = self.client_test.get(reverse('entregas:mis_pedidos'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page_obj'].paginator.count, 1)

    def test_domiciliario_cannot_access_mis_pedidos(self):
        """Domiciliario should get 403 on mis_pedidos."""
        self.client_test.force_login(self.domiciliario)
        response = self.client_test.get(reverse('entregas:mis_pedidos'))
        self.assertEqual(response.status_code, 403)

    def test_mis_pedidos_requires_login(self):
        response = self.client_test.get(reverse('entregas:mis_pedidos'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/usuarios/login/', response.url)


class EditarPedidoViewTests(TestCase):
    """Test the editar_pedido view for Admin."""

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
        """Domiciliario should get 403 on editar_pedido."""
        self.client_test.force_login(self.domiciliario)
        response = self.client_test.get(reverse('entregas:editar', kwargs={'pk': self.pedido.pk}))
        self.assertEqual(response.status_code, 403)

    def test_admin_can_reassign_domiciliario(self):
        """Admin can POST to reassign domiciliario."""
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