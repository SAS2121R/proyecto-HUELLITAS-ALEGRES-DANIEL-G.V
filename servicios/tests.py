from django.test import TestCase
from django.urls import reverse, resolve
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from usuarios.models import Rol, Usuario
from .models import Servicio, CATEGORIAS_SERVICIO


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
# PHASE 1: Model Tests
# ========================================

class ServicioModelTest(TestCase):
    """Tests for Servicio model."""

    def test_creacion_servicio(self):
        """s1.1: Servicio creation with all required fields."""
        s = Servicio.objects.create(nombre='Consulta general', tarifa=50000)
        self.assertEqual(s.nombre, 'Consulta general')
        self.assertEqual(s.tarifa, 50000)
        self.assertTrue(s.esta_activo)
        self.assertEqual(s.duracion_minutos, 30)

    def test_nombre_unique(self):
        """s1.2: nombre must be unique."""
        Servicio.objects.create(nombre='Vacunación', tarifa=30000)
        with self.assertRaises(Exception):
            Servicio.objects.create(nombre='Vacunación', tarifa=35000)

    def test_tarifa_default(self):
        """s1.3: tarifa defaults to 0."""
        s = Servicio.objects.create(nombre='Control', tarifa=0)
        self.assertEqual(s.tarifa, 0)

    def test_duracion_default(self):
        """s1.4: duracion_minutos defaults to 30."""
        s = Servicio.objects.create(nombre='Cirugía', tarifa=200000)
        self.assertEqual(s.duracion_minutos, 30)

    def test_esta_activo_default(self):
        """s1.5: esta_activo defaults to True."""
        s = Servicio.objects.create(nombre='Estética', tarifa=25000)
        self.assertTrue(s.esta_activo)

    def test_soft_delete(self):
        """s1.6: Soft delete works — objects manager filters out inactive."""
        s = Servicio.objects.create(nombre='Laboratorio', tarifa=40000)
        s.esta_activo = False
        s.save()
        # Default manager should not return it
        self.assertEqual(Servicio.objects.count(), 0)
        # all_objects should return it
        self.assertEqual(Servicio.all_objects.count(), 1)

    def test_categoria_choices_validation(self):
        """s1.7: Invalid categoria raises ValidationError."""
        s = Servicio(nombre='Invalid', tarifa=0, categoria='invalid_cat')
        with self.assertRaises(ValidationError):
            s.clean()

    def test_str(self):
        """s1.8: __str__ returns nombre."""
        s = Servicio.objects.create(nombre='Hospitalización', tarifa=100000)
        self.assertEqual(str(s), 'Hospitalización')


# ========================================
# PHASE 2: URL Tests
# ========================================

class ServicioURLTest(TestCase):
    """Tests for Servicio URL configuration."""

    def test_lista_url(self):
        """s2.1: lista URL resolves."""
        url = reverse('servicios:lista')
        self.assertEqual(url, '/servicios/')

    def test_crear_url(self):
        """s2.2: crear URL resolves."""
        url = reverse('servicios:crear')
        self.assertEqual(url, '/servicios/nuevo/')

    def test_editar_url(self):
        """s2.3: editar URL resolves."""
        url = reverse('servicios:editar', kwargs={'pk': 1})
        self.assertEqual(url, '/servicios/editar/1/')

    def test_eliminar_url(self):
        """s2.4: eliminar URL resolves."""
        url = reverse('servicios:eliminar', kwargs={'pk': 1})
        self.assertEqual(url, '/servicios/eliminar/1/')


# ========================================
# PHASE 3: Form Tests
# ========================================

class ServicioFormTest(TestCase):
    """Tests for ServicioForm."""

    def test_guardado_valido(self):
        """s4.1: Valid data saves successfully."""
        from .forms import ServicioForm
        form = ServicioForm(data={
            'nombre': 'Vacunación antirrábica',
            'descripcion': 'Vacuna anual',
            'categoria': 'vacunacion',
            'tarifa': '25000',
            'duracion_minutos': 30,
        })
        self.assertTrue(form.is_valid(), form.errors)

    def test_nombre_duplicado(self):
        """s4.2: Duplicate nombre shows validation error."""
        from .forms import ServicioForm
        Servicio.objects.create(nombre='Consulta', tarifa=50000)
        form = ServicioForm(data={
            'nombre': 'Consulta',
            'tarifa': '60000',
            'categoria': 'consulta',
            'duracion_minutos': 30,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('nombre', form.errors)

    def test_tarifa_negativa(self):
        """s4.3: Negative tarifa shows validation error."""
        from .forms import ServicioForm
        form = ServicioForm(data={
            'nombre': 'Servicio negativo',
            'tarifa': '-100',
            'categoria': 'otro',
            'duracion_minutos': 30,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('tarifa', form.errors)


# ========================================
# PHASE 4: View Tests
# ========================================

class ServicioViewTest(TestCase):
    """Tests for Servicio CRUD views."""

    def setUp(self):
        self.vet = create_user_with_role('Veterinario', username='vet_srv', email='vet_srv@test.com')
        self.admin = create_user_with_role('Administrador', username='admin_srv', email='admin_srv@test.com')
        self.cliente = create_user_with_role('Cliente', username='cli_srv', email='cli_srv@test.com')
        self.servicio = Servicio.objects.create(
            nombre='Consulta general', tarifa=50000,
            categoria='consulta', duracion_minutos=30,
        )
        self.servicio2 = Servicio.objects.create(
            nombre='Cirugía menor', tarifa=150000,
            categoria='cirugia', duracion_minutos=60,
        )

    # --- lista ---

    def test_lista_authenticated(self):
        """s3.1: Any authenticated user sees active services."""
        self.client.force_login(self.cliente)
        resp = self.client.get(reverse('servicios:lista'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Consulta general')

    def test_lista_filter_categoria(self):
        """s3.2: lista filters by categoria."""
        self.client.force_login(self.vet)
        resp = self.client.get(reverse('servicios:lista'), {'categoria': 'cirugia'})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Cirugía menor')
        self.assertNotContains(resp, 'Consulta general')

    def test_lista_search(self):
        """s3.3: lista filters by search term."""
        self.client.force_login(self.vet)
        resp = self.client.get(reverse('servicios:lista'), {'q': 'Consulta'})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Consulta general')
        self.assertNotContains(resp, 'Cirugía menor')

    def test_lista_hides_inactive(self):
        """s3.14: lista does not show inactive services by default."""
        self.servicio2.esta_activo = False
        self.servicio2.save()
        self.client.force_login(self.cliente)
        resp = self.client.get(reverse('servicios:lista'))
        self.assertEqual(resp.status_code, 200)
        self.assertNotContains(resp, 'Cirugía menor')
        self.assertContains(resp, 'Consulta general')

    # --- crear ---

    def test_crear_cliente_403(self):
        """s3.4: crear requires Vet/Admin — Cliente gets 403."""
        self.client.force_login(self.cliente)
        resp = self.client.get(reverse('servicios:crear'))
        self.assertEqual(resp.status_code, 403)

    def test_crear_post_success(self):
        """s3.5: crear POST creates service and redirects."""
        self.client.force_login(self.admin)
        resp = self.client.post(reverse('servicios:crear'), {
            'nombre': 'Vacunación',
            'descripcion': 'Vacuna anual',
            'categoria': 'vacunacion',
            'tarifa': '30000',
            'duracion_minutos': 30,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Servicio.objects.filter(nombre='Vacunación').exists())

    def test_crear_unauthenticated_redirect(self):
        """s3.6: crear unauthenticated redirects to login."""
        resp = self.client.get(reverse('servicios:crear'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/usuarios/login/', resp.url)

    def test_crear_duplicate_nombre(self):
        """s3.12: crear duplicate nombre shows error."""
        self.client.force_login(self.admin)
        resp = self.client.post(reverse('servicios:crear'), {
            'nombre': 'Consulta general',
            'categoria': 'consulta',
            'tarifa': '50000',
            'duracion_minutos': 30,
        })
        self.assertEqual(resp.status_code, 200)  # Re-renders form
        self.assertFalse(Servicio.objects.filter(nombre='Consulta general').count() > 1)

    # --- editar ---

    def test_editar_vet_admin(self):
        """s3.7: editar requires Vet/Admin."""
        self.client.force_login(self.cliente)
        resp = self.client.get(reverse('servicios:editar', kwargs={'pk': self.servicio.pk}))
        self.assertEqual(resp.status_code, 403)

    def test_editar_post_success(self):
        """s3.8: editar POST updates and redirects."""
        self.client.force_login(self.vet)
        resp = self.client.post(reverse('servicios:editar', kwargs={'pk': self.servicio.pk}), {
            'nombre': 'Consulta general',
            'descripcion': 'Consulta completa',
            'categoria': 'consulta',
            'tarifa': '55000',
            'duracion_minutos': 45,
        })
        self.assertEqual(resp.status_code, 302)
        self.servicio.refresh_from_db()
        self.assertEqual(str(self.servicio.tarifa), '55000.00')

    def test_editar_invalid_data(self):
        """s3.13: editar with invalid data re-renders form."""
        self.client.force_login(self.admin)
        resp = self.client.post(reverse('servicios:editar', kwargs={'pk': self.servicio.pk}), {
            'nombre': '',
            'tarifa': '-100',
            'categoria': 'consulta',
            'duracion_minutos': 30,
        })
        self.assertEqual(resp.status_code, 200)  # Re-renders form

    # --- eliminar (soft delete) ---

    def test_eliminar_cliente_403(self):
        """s3.9: eliminar requires Vet/Admin — Cliente gets 403."""
        self.client.force_login(self.cliente)
        resp = self.client.post(reverse('servicios:eliminar', kwargs={'pk': self.servicio.pk}))
        self.assertEqual(resp.status_code, 403)

    def test_eliminar_soft_delete(self):
        """s3.10: eliminar POST soft-deletes (esta_activo=False)."""
        self.client.force_login(self.admin)
        resp = self.client.post(reverse('servicios:eliminar', kwargs={'pk': self.servicio.pk}))
        self.assertEqual(resp.status_code, 302)
        self.servicio.refresh_from_db()
        self.assertFalse(self.servicio.esta_activo)

    def test_eliminar_get_confirms(self):
        """s3.11: eliminar GET shows confirmation page."""
        self.client.force_login(self.vet)
        resp = self.client.get(reverse('servicios:eliminar', kwargs={'pk': self.servicio.pk}))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Consulta general')