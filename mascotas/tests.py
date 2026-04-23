from django.test import TestCase
from django.db import IntegrityError
from django.urls import reverse, resolve
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model

from usuarios.models import Rol


# ========================================
# PHASE 4: Create View Tests (REQ-04)
# ========================================

class MascotaCreateViewTest(TestCase):
    """REQ-04: Mascota create view — 5 scenarios"""

    def setUp(self):
        User = get_user_model()
        self.vet_rol = Rol.objects.get(nombre='Veterinario')
        self.admin_rol = Rol.objects.get(nombre='Administrador')
        self.cliente_rol = Rol.objects.get(nombre='Cliente')
        self.vet_user = User.objects.create_user(
            username='vet_create', email='vet_c@test.com',
            password='pass123', rol=self.vet_rol,
        )
        self.admin_user = User.objects.create_user(
            username='admin_create', email='admin_c@test.com',
            password='pass123', rol=self.admin_rol,
        )
        self.cliente_user = User.objects.create_user(
            username='cliente_create', email='cliente_c@test.com',
            password='pass123', rol=self.cliente_rol,
        )

    def test_veterinario_creates_mascota(self):
        """R4.1: Veterinario creates mascota successfully"""
        self.client.force_login(self.vet_user)
        from mascotas.models import Mascota
        count_before = Mascota.objects.count()
        resp = self.client.post(reverse('mascotas:nuevo'), data={
            'nombre': 'Fido',
            'especie': 'Canino',
            'raza': 'Labrador',
            'sexo': 'Macho',
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Mascota.objects.count(), count_before + 1)
        mascota = Mascota.objects.get(nombre='Fido')
        self.assertEqual(mascota.propietario, self.vet_user)

    def test_administrador_creates_mascota(self):
        """R4.2: Administrador creates mascota successfully"""
        self.client.force_login(self.admin_user)
        from mascotas.models import Mascota
        count_before = Mascota.objects.count()
        resp = self.client.post(reverse('mascotas:nuevo'), data={
            'nombre': 'Mishi',
            'especie': 'Felino',
            'sexo': 'Hembra',
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Mascota.objects.count(), count_before + 1)

    def test_cliente_cannot_create_403(self):
        """R4.3: Cliente gets 403 Forbidden"""
        self.client.force_login(self.cliente_user)
        resp = self.client.get(reverse('mascotas:nuevo'))
        self.assertEqual(resp.status_code, 403)

    def test_unauthenticated_redirected_to_login(self):
        """R4.4: Unauthenticated user redirected to login"""
        resp = self.client.get(reverse('mascotas:nuevo'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/usuarios/login/', resp.url)

    def test_form_errors_render(self):
        """R4.5: Form errors render with messages"""
        self.client.force_login(self.vet_user)
        resp = self.client.post(reverse('mascotas:nuevo'), data={
            'nombre': '',  # Missing required field
            'especie': 'Canino',
            'sexo': 'Macho',
        })
        self.assertEqual(resp.status_code, 200)
        from mascotas.models import Mascota
        self.assertEqual(Mascota.objects.count(), 0)


# ========================================
# PHASE 3: List View Tests (REQ-03)
# ========================================

class MascotaListViewTest(TestCase):
    """REQ-03: Mascota list view — 4 scenarios"""

    def setUp(self):
        User = get_user_model()
        self.vet_rol = Rol.objects.get(nombre='Veterinario')
        self.admin_rol = Rol.objects.get(nombre='Administrador')
        self.cliente_rol = Rol.objects.get(nombre='Cliente')
        self.vet_user = User.objects.create_user(
            username='vet_list', email='vet@test.com',
            password='pass123', rol=self.vet_rol,
        )
        self.admin_user = User.objects.create_user(
            username='admin_list', email='admin@test.com',
            password='pass123', rol=self.admin_rol,
        )
        self.cliente_user = User.objects.create_user(
            username='cliente_list', email='cliente@test.com',
            password='pass123', rol=self.cliente_rol,
        )
        self.other_user = User.objects.create_user(
            username='other_list', email='other@test.com',
            password='pass123', rol=self.cliente_rol,
        )
        from mascotas.models import Mascota
        Mascota.objects.create(nombre='Fido', especie='Canino', sexo='Macho', propietario=self.cliente_user)
        Mascota.objects.create(nombre='Mishi', especie='Felino', sexo='Hembra', propietario=self.other_user)

    def test_veterinario_sees_all_mascotas(self):
        """R3.1: Veterinario sees all mascotas"""
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('mascotas:lista'))
        self.assertEqual(resp.status_code, 200)
        content = resp.content.decode()
        self.assertIn('Fido', content)
        self.assertIn('Mishi', content)

    def test_administrador_sees_all_mascotas(self):
        """R3.2: Administrador sees all mascotas"""
        self.client.force_login(self.admin_user)
        resp = self.client.get(reverse('mascotas:lista'))
        self.assertEqual(resp.status_code, 200)
        content = resp.content.decode()
        self.assertIn('Fido', content)
        self.assertIn('Mishi', content)

    def test_cliente_sees_only_own_mascotas(self):
        """R3.3: Cliente sees only own mascotas"""
        self.client.force_login(self.cliente_user)
        resp = self.client.get(reverse('mascotas:lista'))
        self.assertEqual(resp.status_code, 200)
        content = resp.content.decode()
        self.assertIn('Fido', content)
        self.assertNotIn('Mishi', content)

    def test_unauthenticated_redirected_to_login(self):
        """R3.4: Unauthenticated user redirected to login"""
        resp = self.client.get(reverse('mascotas:lista'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/usuarios/login/', resp.url)


# ========================================
# PHASE 2: Form Layer Tests (REQ-02)
# ========================================

class MascotaFormTest(TestCase):
    """REQ-02: MascotaForm — 6 scenarios"""

    def test_valid_form_creates_mascota(self):
        """R2.1: Valid form is valid and saves"""
        from mascotas.forms import MascotaForm
        form = MascotaForm(data={
            'nombre': 'Fido',
            'especie': 'Canino',
            'raza': 'Labrador',
            'sexo': 'Macho',
        })
        self.assertTrue(form.is_valid(), form.errors)

    def test_invalid_especie_rejected(self):
        """R2.2: Invalid especie is rejected"""
        from mascotas.forms import MascotaForm
        form = MascotaForm(data={
            'nombre': 'Test',
            'especie': 'Dinosaurio',
            'sexo': 'Macho',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('especie', form.errors)

    def test_invalid_sexo_rejected(self):
        """R2.3: Invalid sexo is rejected"""
        from mascotas.forms import MascotaForm
        form = MascotaForm(data={
            'nombre': 'Test',
            'especie': 'Canino',
            'sexo': 'Hermafrodita',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('sexo', form.errors)

    def test_blank_raza_accepted(self):
        """R2.4: Blank raza is accepted"""
        from mascotas.forms import MascotaForm
        form = MascotaForm(data={
            'nombre': 'Test',
            'especie': 'Felino',
            'raza': '',
            'sexo': 'Hembra',
        })
        self.assertTrue(form.is_valid(), form.errors)

    def test_blank_fecha_nacimiento_accepted(self):
        """R2.5: Blank fecha_nacimiento is accepted"""
        from mascotas.forms import MascotaForm
        form = MascotaForm(data={
            'nombre': 'Test',
            'especie': 'Ave',
            'sexo': 'Macho',
            'fecha_nacimiento': '',
        })
        self.assertTrue(form.is_valid(), form.errors)

    def test_future_fecha_nacimiento_rejected(self):
        """R2.6: Future fecha_nacimiento is rejected"""
        from mascotas.forms import MascotaForm
        form = MascotaForm(data={
            'nombre': 'Test',
            'especie': 'Canino',
            'sexo': 'Macho',
            'fecha_nacimiento': '2099-12-31',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('fecha_nacimiento', form.errors)


# ========================================
# PHASE 1: Model + App Registration + URL Tests (REQ-01, REQ-08, REQ-09)
# ========================================

class MascotaModelTest(TestCase):
    """REQ-01: Mascota model — 6 scenarios"""

    def setUp(self):
        self.cliente_rol = Rol.objects.get(nombre='Cliente')
        User = get_user_model()
        self.owner = User.objects.create_user(
            username='owner1', email='owner@test.com',
            password='pass123', rol=self.cliente_rol,
        )

    def test_mascota_creation_all_fields(self):
        """R1.1: Mascota creation with all fields populated"""
        from mascotas.models import Mascota
        m = Mascota.objects.create(
            nombre='Fido',
            especie='Canino',
            raza='Labrador',
            sexo='Macho',
            fecha_nacimiento='2020-01-15',
            propietario=self.owner,
        )
        self.assertEqual(m.nombre, 'Fido')
        self.assertEqual(m.especie, 'Canino')
        self.assertEqual(m.raza, 'Labrador')
        self.assertEqual(m.sexo, 'Macho')
        self.assertEqual(str(m.fecha_nacimiento), '2020-01-15')
        self.assertEqual(m.propietario, self.owner)

    def test_mascota_creation_optional_fields_blank(self):
        """R1.2: Mascota creation with raza and fecha_nacimiento omitted"""
        from mascotas.models import Mascota
        m = Mascota.objects.create(
            nombre='Mishi',
            especie='Felino',
            sexo='Hembra',
            propietario=self.owner,
        )
        self.assertEqual(m.raza, '')
        self.assertIsNone(m.fecha_nacimiento)

    def test_mascota_str_returns_nombre_especie(self):
        """R1.3: __str__ returns 'nombre (especie)'"""
        from mascotas.models import Mascota
        m = Mascota.objects.create(
            nombre='Rex',
            especie='Canino',
            sexo='Macho',
            propietario=self.owner,
        )
        self.assertEqual(str(m), 'Rex (Canino)')

    def test_propietario_related_name_works(self):
        """R1.4: usuario.mascotas.all() returns mascotas for that user"""
        from mascotas.models import Mascota
        Mascota.objects.create(nombre='Fido', especie='Canino', sexo='Macho', propietario=self.owner)
        Mascota.objects.create(nombre='Mishi', especie='Felino', sexo='Hembra', propietario=self.owner)
        mascotas = self.owner.mascotas.all()
        self.assertEqual(mascotas.count(), 2)

    def test_especie_choices_enforced(self):
        """R1.5: Invalid especie raises ValidationError"""
        from mascotas.models import Mascota
        m = Mascota(nombre='Invalido', especie='Dinosaurio', sexo='Macho', propietario=self.owner)
        with self.assertRaisesMessage(Exception, 'is not a valid choice'):
            m.full_clean()

    def test_sexo_choices_enforced(self):
        """R1.6: Invalid sexo raises ValidationError"""
        from mascotas.models import Mascota
        m = Mascota(nombre='Test', especie='Canino', sexo='Neutro', propietario=self.owner)
        with self.assertRaisesMessage(Exception, 'is not a valid choice'):
            m.full_clean()


class AppRegistrationTest(TestCase):
    """REQ-09: App is registered in INSTALLED_APPS"""

    def test_mascotas_app_registered(self):
        """R9.1: 'mascotas' is in INSTALLED_APPS"""
        self.assertIn('mascotas', settings.INSTALLED_APPS)


class URLConfigurationTest(TestCase):
    """REQ-08: URL configuration — all CRUD URLs resolve"""

    def test_lista_url_resolves(self):
        """R8.1: mascotas:lista resolves to /mascotas/"""
        url = reverse('mascotas:lista')
        self.assertEqual(url, '/mascotas/')

    def test_nuevo_url_resolves(self):
        """R8.1: mascotas:nuevo resolves to /mascotas/nuevo/"""
        url = reverse('mascotas:nuevo')
        self.assertEqual(url, '/mascotas/nuevo/')

    def test_editar_url_resolves(self):
        """R8.1: mascotas:editar with pk=1 resolves to /mascotas/editar/1/"""
        url = reverse('mascotas:editar', kwargs={'pk': 1})
        self.assertEqual(url, '/mascotas/editar/1/')

    def test_eliminar_url_resolves(self):
        """R8.1: mascotas:eliminar with pk=1 resolves to /mascotas/eliminar/1/"""
        url = reverse('mascotas:eliminar', kwargs={'pk': 1})
        self.assertEqual(url, '/mascotas/eliminar/1/')


# ========================================
# PHASE 5: Edit View Tests (REQ-05)
# ========================================

class MascotaEditViewTest(TestCase):
    """REQ-05: Mascota edit view — 5 scenarios"""

    def setUp(self):
        from mascotas.models import Mascota
        self.vet_rol = Rol.objects.get(nombre='Veterinario')
        self.admin_rol = Rol.objects.get(nombre='Administrador')
        self.cliente_rol = Rol.objects.get(nombre='Cliente')
        User = get_user_model()

        self.vet_user = User.objects.create_user(
            username='vet_r5', email='vet_r5@test.com',
            password='pass123', rol=self.vet_rol,
        )
        self.admin_user = User.objects.create_user(
            username='admin_r5', email='admin_r5@test.com',
            password='pass123', rol=self.admin_rol,
        )
        self.owner_user = User.objects.create_user(
            username='owner_r5', email='owner_r5@test.com',
            password='pass123', rol=self.cliente_rol,
        )
        self.other_user = User.objects.create_user(
            username='other_r5', email='other_r5@test.com',
            password='pass123', rol=self.cliente_rol,
        )
        self.own_mascota = Mascota.objects.create(
            nombre='Firulais', especie='Canino', sexo='Macho',
            propietario=self.owner_user,
        )
        self.other_mascota = Mascota.objects.create(
            nombre='Mishi', especie='Felino', sexo='Hembra',
            propietario=self.other_user,
        )

    def test_veterinario_edits_any_mascota(self):
        """R5.1: Veterinario edits any mascota"""
        self.client.force_login(self.vet_user)
        resp = self.client.post(reverse('mascotas:editar', kwargs={'pk': self.other_mascota.pk}), {
            'nombre': 'Mishi Actualizada',
            'especie': 'Felino',
            'sexo': 'Hembra',
        })
        self.assertEqual(resp.status_code, 302)
        self.other_mascota.refresh_from_db()
        self.assertEqual(self.other_mascota.nombre, 'Mishi Actualizada')

    def test_administrador_edits_any_mascota(self):
        """R5.2: Administrador edits any mascota"""
        self.client.force_login(self.admin_user)
        resp = self.client.post(reverse('mascotas:editar', kwargs={'pk': self.other_mascota.pk}), {
            'nombre': 'Mishi Admin Edit',
            'especie': 'Felino',
            'sexo': 'Hembra',
        })
        self.assertEqual(resp.status_code, 302)
        self.other_mascota.refresh_from_db()
        self.assertEqual(self.other_mascota.nombre, 'Mishi Admin Edit')

    def test_cliente_edits_own_mascota(self):
        """R5.3: Cliente edits own mascota"""
        self.client.force_login(self.owner_user)
        resp = self.client.post(reverse('mascotas:editar', kwargs={'pk': self.own_mascota.pk}), {
            'nombre': 'Firulais Editado',
            'especie': 'Canino',
            'sexo': 'Macho',
        })
        self.assertEqual(resp.status_code, 302)
        self.own_mascota.refresh_from_db()
        self.assertEqual(self.own_mascota.nombre, 'Firulais Editado')

    def test_cliente_cannot_edit_others_mascota(self):
        """R5.4: Cliente cannot edit another user's mascota (403)"""
        self.client.force_login(self.owner_user)
        resp = self.client.get(reverse('mascotas:editar', kwargs={'pk': self.other_mascota.pk}))
        self.assertEqual(resp.status_code, 403)

    def test_unauthenticated_redirected_to_login_edit(self):
        """R5.5: Unauthenticated redirected to login"""
        resp = self.client.get(reverse('mascotas:editar', kwargs={'pk': self.own_mascota.pk}))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/usuarios/login/', resp.url)


# ========================================
# PHASE 6: Delete View Tests (REQ-06)
# ========================================

class MascotaDeleteViewTest(TestCase):
    """REQ-06: Mascota delete view — 4 scenarios"""

    def setUp(self):
        from mascotas.models import Mascota
        self.vet_rol = Rol.objects.get(nombre='Veterinario')
        self.admin_rol = Rol.objects.get(nombre='Administrador')
        self.cliente_rol = Rol.objects.get(nombre='Cliente')
        User = get_user_model()

        self.vet_user = User.objects.create_user(
            username='vet_r6', email='vet_r6@test.com',
            password='pass123', rol=self.vet_rol,
        )
        self.admin_user = User.objects.create_user(
            username='admin_r6', email='admin_r6@test.com',
            password='pass123', rol=self.admin_rol,
        )
        self.cliente_user = User.objects.create_user(
            username='cliente_r6', email='cliente_r6@test.com',
            password='pass123', rol=self.cliente_rol,
        )
        self.mascota = Mascota.objects.create(
            nombre='ToDelete', especie='Canino', sexo='Macho',
            propietario=self.cliente_user,
        )

    def test_veterinario_deletes_with_confirmation(self):
        """R6.1: Veterinario deletes mascota — GET=confirmation, POST=delete"""
        self.client.force_login(self.vet_user)
        # GET shows confirmation page
        resp_get = self.client.get(reverse('mascotas:eliminar', kwargs={'pk': self.mascota.pk}))
        self.assertEqual(resp_get.status_code, 200)
        self.assertContains(resp_get, 'ToDelete')
        # POST deletes
        resp_post = self.client.post(reverse('mascotas:eliminar', kwargs={'pk': self.mascota.pk}))
        self.assertEqual(resp_post.status_code, 302)
        from mascotas.models import Mascota
        self.assertFalse(Mascota.objects.filter(pk=self.mascota.pk).exists())

    def test_administrador_deletes_mascota(self):
        """R6.2: Administrador deletes mascota"""
        self.client.force_login(self.admin_user)
        resp = self.client.post(reverse('mascotas:eliminar', kwargs={'pk': self.mascota.pk}))
        self.assertEqual(resp.status_code, 302)
        from mascotas.models import Mascota
        self.assertFalse(Mascota.objects.filter(pk=self.mascota.pk).exists())

    def test_cliente_cannot_delete_403(self):
        """R6.3: Cliente cannot delete (403)"""
        self.client.force_login(self.cliente_user)
        resp = self.client.get(reverse('mascotas:eliminar', kwargs={'pk': self.mascota.pk}))
        self.assertEqual(resp.status_code, 403)

    def test_unauthenticated_redirected_to_login_delete(self):
        """R6.4: Unauthenticated redirected to login"""
        resp = self.client.get(reverse('mascotas:eliminar', kwargs={'pk': self.mascota.pk}))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/usuarios/login/', resp.url)


# ========================================
# PHASE 7: Dashboard Integration Tests (REQ-07)
# ========================================

class DashboardIntegrationTest(TestCase):
    """REQ-07: Dashboard integration — Pacientes link points to mascotas:lista"""

    def setUp(self):
        self.vet_rol = Rol.objects.get(nombre='Veterinario')
        User = get_user_model()
        self.vet_user = User.objects.create_user(
            username='vet_r7', email='vet_r7@test.com',
            password='pass123', rol=self.vet_rol, first_name='Dr. García',
        )

    def test_dashboard_contains_mascotas_link(self):
        """R7.1: Dashboard contains link to mascotas:lista"""
        from django.test import Client
        client = Client()
        client.force_login(self.vet_user)
        resp = client.get(reverse('usuarios:vet_dashboard'))
        self.assertEqual(resp.status_code, 200)
        mascotas_url = reverse('mascotas:lista')
        self.assertContains(resp, mascotas_url)
