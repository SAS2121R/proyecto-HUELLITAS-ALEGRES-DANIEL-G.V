from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import Proveedor
from .forms import ProveedorForm
from usuarios.models import Rol

Usuario = get_user_model()


class ProveedorModelTest(TestCase):
    """Pruebas del modelo Proveedor."""

    def test_proveedor_creation(self):
        """Se puede crear un Proveedor con los campos obligatorios."""
        prov = Proveedor.objects.create(nombre='LabVet Colombia')
        self.assertEqual(prov.nombre, 'LabVet Colombia')
        self.assertTrue(prov.esta_activo)
        self.assertEqual(str(prov), 'LabVet Colombia')

    def test_proveedor_unique_nombre(self):
        """El nombre del proveedor debe ser único."""
        Proveedor.objects.create(nombre='LabVet Colombia')
        with self.assertRaises(Exception):
            Proveedor.objects.create(nombre='LabVet Colombia')

    def test_proveedor_optional_fields(self):
        """Los campos opcionales tienen valor por defecto vacío."""
        prov = Proveedor.objects.create(nombre='Test Prov')
        self.assertEqual(prov.nit, '')
        self.assertEqual(prov.telefono, '')
        self.assertEqual(prov.email, '')
        self.assertEqual(prov.direccion, '')
        self.assertEqual(prov.contacto, '')

    def test_proveedor_with_all_fields(self):
        """Se puede crear un Proveedor con todos los campos completos."""
        prov = Proveedor.objects.create(
            nombre='VetSupply',
            nit='901.234.567-9',
            telefono='601-555-9999',
            email='info@vetsupply.com',
            direccion='Calle 50 # 10-20',
            contacto='Juan Pérez',
        )
        self.assertEqual(prov.nit, '901.234.567-9')
        self.assertEqual(prov.telefono, '601-555-9999')
        self.assertEqual(prov.email, 'info@vetsupply.com')


class ProveedorCRUDTest(TestCase):
    """Pruebas de las vistas CRUD de Proveedor — solo Administrador."""

    def setUp(self):
        self.client = Client()
        admin_rol = Rol.objects.get(nombre='Administrador')
        cliente_rol = Rol.objects.get(nombre='Cliente')
        self.admin = Usuario.objects.create_user(
            username='prov_admin', email='prov_admin@test.com',
            password='adminpass123', rol=admin_rol,
        )
        self.cliente = Usuario.objects.create_user(
            username='prov_cli', email='prov_cli@test.com',
            password='clipass123', rol=cliente_rol,
        )
        self.proveedor = Proveedor.objects.create(
            nombre='LabVet', nit='900.111.222-3', telefono='3001112222',
        )

    def test_lista_proveedores_admin(self):
        """El Administrador puede ver la lista de proveedores."""
        self.client.force_login(self.admin)
        resp = self.client.get(reverse('proveedores:lista'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'LabVet')

    def test_lista_proveedores_non_admin_403(self):
        """Un usuario que no es Administrador recibe error 403."""
        self.client.force_login(self.cliente)
        resp = self.client.get(reverse('proveedores:lista'))
        self.assertEqual(resp.status_code, 403)

    def test_crear_proveedor(self):
        """El Administrador puede crear un nuevo proveedor."""
        self.client.force_login(self.admin)
        resp = self.client.post(reverse('proveedores:crear'), {
            'nombre': 'VetSupply',
            'nit': '901.234.567-9',
            'telefono': '601-555-0000',
        })
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Proveedor.objects.filter(nombre='VetSupply').exists())

    def test_editar_proveedor(self):
        """El Administrador puede actualizar los datos de un proveedor."""
        self.client.force_login(self.admin)
        resp = self.client.post(reverse('proveedores:editar', kwargs={'pk': self.proveedor.pk}), {
            'nombre': 'LabVet Updated',
            'nit': '900.111.222-3',
            'telefono': '3001112222',
        })
        self.assertEqual(resp.status_code, 302)
        self.proveedor.refresh_from_db()
        self.assertEqual(self.proveedor.nombre, 'LabVet Updated')

    def test_toggle_proveedor(self):
        """El Administrador puede activar o desactivar un proveedor."""
        self.client.force_login(self.admin)
        self.assertTrue(self.proveedor.esta_activo)
        resp = self.client.post(reverse('proveedores:toggle', kwargs={'pk': self.proveedor.pk}))
        self.assertEqual(resp.status_code, 302)
        self.proveedor.refresh_from_db()
        self.assertFalse(self.proveedor.esta_activo)

    def test_crear_proveedor_duplicate_nombre(self):
        """No se puede crear un proveedor con un nombre duplicado."""
        self.client.force_login(self.admin)
        resp = self.client.post(reverse('proveedores:crear'), {
            'nombre': 'LabVet',  # ya existe
        })
        self.assertEqual(resp.status_code, 200)  # Error de formulario, permanece en la página
        self.assertEqual(Proveedor.objects.filter(nombre='LabVet').count(), 1)


class ProveedorFormTest(TestCase):
    """Pruebas de validación del formulario ProveedorForm."""

    def test_form_valid(self):
        """El formulario acepta datos válidos."""
        form = ProveedorForm(data={'nombre': 'New Prov', 'esta_activo': True})
        self.assertTrue(form.is_valid())

    def test_form_missing_nombre(self):
        """El formulario rechaza datos sin el nombre obligatorio."""
        form = ProveedorForm(data={'esta_activo': True})
        self.assertFalse(form.is_valid())
        self.assertIn('nombre', form.errors)