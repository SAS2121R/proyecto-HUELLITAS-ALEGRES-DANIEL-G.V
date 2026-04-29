from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from agenda.models import Cita
from historial.models import HistorialClinico
from productos.models import Producto
from servicios.models import Servicio
from entregas.models import Pedido, PedidoItem
from mascotas.models import Mascota
from usuarios.models import Rol

Usuario = get_user_model()


def create_user_with_role(rol_nombre, **kwargs):
    """Función auxiliar para crear un Usuario con el rol dado."""
    rol, _ = Rol.objects.get_or_create(nombre=rol_nombre)
    user = Usuario.objects.create_user(
        username=kwargs.get('username', f'user_{rol_nombre.lower()}'),
        email=kwargs.get('email', f'{rol_nombre.lower()}@test.com'),
        password='testpass123',
        rol=rol,
        **{k: v for k, v in kwargs.items() if k not in ('username', 'email', 'password', 'rol')}
    )
    return user


def add_permission(user, permission_codename, model_class):
    """Función auxiliar para agregar un permiso específico a un usuario."""
    ct = ContentType.objects.get_for_model(model_class)
    perm = Permission.objects.get(content_type=ct, codename=permission_codename)
    user.user_permissions.add(perm)


class ReporteURLTests(TestCase):
    """Pruebas de que todas las URLs de reportes se resuelven correctamente."""

    def setUp(self):
        self.client = Client()

    def test_reporte_citas_url_resolves(self):
        url = reverse('reportes:citas')
        self.assertEqual(url, '/reportes/citas/')

    def test_reporte_historial_url_resolves(self):
        url = reverse('reportes:historial', kwargs={'mascota_pk': 1})
        self.assertEqual(url, '/reportes/historial/1/')

    def test_reporte_inventario_url_resolves(self):
        url = reverse('reportes:inventario')
        self.assertEqual(url, '/reportes/inventario/')

    def test_reporte_servicios_url_resolves(self):
        url = reverse('reportes:servicios')
        self.assertEqual(url, '/reportes/servicios/')


class ReportePermissionTests(TestCase):
    """Pruebas de que todas las vistas de reportes requieren inicio de sesión y permisos."""

    def setUp(self):
        self.client = Client()

    def test_citas_requires_login(self):
        response = self.client.get(reverse('reportes:citas'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/usuarios/login/', response.url)

    def test_inventario_requires_login(self):
        response = self.client.get(reverse('reportes:inventario'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/usuarios/login/', response.url)

    def test_servicios_requires_login(self):
        response = self.client.get(reverse('reportes:servicios'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/usuarios/login/', response.url)

    def test_historial_requires_login(self):
        response = self.client.get(reverse('reportes:historial', kwargs={'mascota_pk': 1}))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/usuarios/login/', response.url)


class CitasPDFTests(TestCase):
    """Pruebas de generación de reporte de citas."""

    def setUp(self):
        self.client = Client()
        self.vet = create_user_with_role('Veterinario', username='vet_citas', email='vet_citas@test.com')
        add_permission(self.vet, 'view_cita', Cita)

    def test_citas_pdf_with_vet(self):
        self.client.force_login(self.vet)
        response = self.client.get(reverse('reportes:citas'))
        self.assertEqual(response.status_code, 200)

    def test_citas_pdf_content_type(self):
        self.client.force_login(self.vet)
        response = self.client.get(reverse('reportes:citas'))
        self.assertIn('pdf', response['Content-Type'].lower())

    def test_citas_pdf_filter_by_estado(self):
        self.client.force_login(self.vet)
        response = self.client.get(reverse('reportes:citas') + '?estado=confirmada')
        self.assertEqual(response.status_code, 200)


class HistorialPDFTests(TestCase):
    """Pruebas de generación de reporte de historial clínico."""

    def setUp(self):
        self.client = Client()
        self.vet = create_user_with_role('Veterinario', username='vet_hist', email='vet_hist@test.com')
        add_permission(self.vet, 'view_historialclinico', HistorialClinico)

    def test_historial_pdf_nonexistent_mascota(self):
        self.client.force_login(self.vet)
        response = self.client.get(reverse('reportes:historial', kwargs={'mascota_pk': 999}))
        self.assertEqual(response.status_code, 404)


class InventarioPDFTests(TestCase):
    """Pruebas de generación de reporte de inventario."""

    def setUp(self):
        self.client = Client()
        self.admin = create_user_with_role('Administrador', username='admin_inv', email='admin_inv@test.com')
        add_permission(self.admin, 'view_producto', Producto)

    def test_inventario_pdf_with_admin(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('reportes:inventario'))
        self.assertEqual(response.status_code, 200)

    def test_inventario_excel_with_admin(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('reportes:inventario') + '?format=excel')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    def test_inventario_pdf_filter_stock_bajo(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('reportes:inventario') + '?stock_bajo=1')
        self.assertEqual(response.status_code, 200)


class ServiciosPDFTests(TestCase):
    """Pruebas de generación de reporte de servicios."""

    def setUp(self):
        self.client = Client()
        self.admin = create_user_with_role('Administrador', username='admin_srv', email='admin_srv@test.com')
        add_permission(self.admin, 'view_servicio', Servicio)

    def test_servicios_pdf_with_admin(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('reportes:servicios'))
        self.assertEqual(response.status_code, 200)

def test_servicios_pdf_filter_by_categoria(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('reportes:servicios') + '?categoria=consulta')
        self.assertEqual(response.status_code, 200)


# ========================================
# ADMIN: Súper Reportes — Metricas
# ========================================


class AdminMetricasTest(TestCase):
    """Pruebas del panel de métricas del Administrador: Top Productos, Productividad de Staff, Tasa de Cumplimiento."""

    def setUp(self):
        from decimal import Decimal
        from django.utils import timezone
        from entregas.models import Pedido, PedidoItem

        User = get_user_model()
        self.admin_rol = Rol.objects.get(nombre='Administrador')
        self.cliente_rol = Rol.objects.get(nombre='Cliente')
        self.vet_rol = Rol.objects.get(nombre='Veterinario')
        self.dom_rol = Rol.objects.get(nombre='Domiciliario')

        self.admin = User.objects.create_user(
            username='met_admin', email='met_admin@test.com',
            password='adminpass123', rol=self.admin_rol,
        )
        self.cliente = User.objects.create_user(
            username='met_cli', email='met_cli@test.com',
            password='clipass123', rol=self.cliente_rol,
        )
        self.vet = User.objects.create_user(
            username='met_vet', email='met_vet@test.com',
            password='vetpass123', rol=self.vet_rol, first_name='Dr. Perez',
        )
        self.dom = User.objects.create_user(
            username='met_dom', email='met_dom@test.com',
            password='dompass123', rol=self.dom_rol, first_name='Carlos',
        )

        # Crear productos de prueba
        self.prod1 = Producto.objects.create(nombre='Dog Chow', precio=Decimal('45000'), cantidad_stock=50, categoria='alimentos')
        self.prod2 = Producto.objects.create(nombre='Cat Vibes', precio=Decimal('30000'), cantidad_stock=30, categoria='alimentos')

        # Crear un pedido entregado (datos para top productos)
        self.pedido = Pedido.objects.create(
            cliente=self.cliente, domiciliario=self.dom,
            direccion_entrega='Calle 10', telefono_contacto='3001112222',
            estado='entregado', fecha_entrega=timezone.now(),
        )
        PedidoItem.objects.create(pedido=self.pedido, producto=self.prod1, cantidad=5)
        PedidoItem.objects.create(pedido=self.pedido, producto=self.prod2, cantidad=2)

        self.c = Client()

    def test_admin_metricas_access(self):
        """El Administrador puede acceder a la página de métricas."""
        self.c.force_login(self.admin)
        resp = self.c.get(reverse('reportes:admin_metricas'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Métricas de Negocio')

    def test_admin_metricas_shows_top_products(self):
        """La página de métricas muestra la sección de Top Productos."""
        self.c.force_login(self.admin)
        resp = self.c.get(reverse('reportes:admin_metricas'))
        self.assertContains(resp, 'Top 5 Productos')
        self.assertIn('top_productos', resp.context)

    def test_admin_metricas_shows_staff_productivity(self):
        """La página de métricas muestra la sección de Productividad de Staff."""
        self.c.force_login(self.admin)
        resp = self.c.get(reverse('reportes:admin_metricas'))
        self.assertContains(resp, 'Productividad de Staff')
        self.assertIn('vet_productividad', resp.context)

    def test_admin_metricas_shows_compliance_rate(self):
        """La página de métricas muestra la tasa de cumplimiento."""
        self.c.force_login(self.admin)
        resp = self.c.get(reverse('reportes:admin_metricas'))
        self.assertIn('tasa_cumplimiento', resp.context)

    def test_admin_metricas_non_admin_403(self):
        """Un usuario que no es Administrador recibe error 403 en la página de métricas."""
        self.c.force_login(self.cliente)
        resp = self.c.get(reverse('reportes:admin_metricas'))
        self.assertEqual(resp.status_code, 403)

    def test_admin_metricas_config_in_context(self):
        """La página de métricas incluye los datos de configuración de la clínica."""
        self.c.force_login(self.admin)
        resp = self.c.get(reverse('reportes:admin_metricas'))
        self.assertIn('config', resp.context)
