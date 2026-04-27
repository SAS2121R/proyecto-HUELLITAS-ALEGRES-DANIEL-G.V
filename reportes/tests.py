from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from agenda.models import Cita
from historial.models import HistorialClinico
from productos.models import Producto
from servicios.models import Servicio
from mascotas.models import Mascota
from usuarios.models import Rol

Usuario = get_user_model()


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


def add_permission(user, permission_codename, model_class):
    """Helper to add a specific permission to a user."""
    ct = ContentType.objects.get_for_model(model_class)
    perm = Permission.objects.get(content_type=ct, codename=permission_codename)
    user.user_permissions.add(perm)


class ReporteURLTests(TestCase):
    """Test that all report URLs resolve correctly."""

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
    """Test that all report views require login and permissions."""

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
    """Test cita report generation."""

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
    """Test historial report generation."""

    def setUp(self):
        self.client = Client()
        self.vet = create_user_with_role('Veterinario', username='vet_hist', email='vet_hist@test.com')
        add_permission(self.vet, 'view_historialclinico', HistorialClinico)

    def test_historial_pdf_nonexistent_mascota(self):
        self.client.force_login(self.vet)
        response = self.client.get(reverse('reportes:historial', kwargs={'mascota_pk': 999}))
        self.assertEqual(response.status_code, 404)


class InventarioPDFTests(TestCase):
    """Test inventario report generation."""

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
    """Test servicios report generation."""

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
