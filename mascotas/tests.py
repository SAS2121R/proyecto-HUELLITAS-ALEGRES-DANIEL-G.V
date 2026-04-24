from datetime import date

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


# ========================================
# PHASE 1 INFRA: Media Configuration Tests (T1.2, T1.3)
# ========================================

class MediaConfigTest(TestCase):
    """T1.2/T1.3: MEDIA_URL, MEDIA_ROOT, and debug media serving"""

    def test_media_url_configured(self):
        """MEDIA_URL is set to '/media/'"""
        self.assertEqual(settings.MEDIA_URL, '/media/')

    def test_media_root_configured(self):
        """MEDIA_ROOT is set and ends with 'media'"""
        self.assertTrue(hasattr(settings, 'MEDIA_ROOT'))
        self.assertTrue(str(settings.MEDIA_ROOT).endswith('media'))

    def test_media_serves_files_in_debug(self):
        """When DEBUG=True, /media/ URL pattern exists in URL conf"""
        from django.conf import settings as django_settings
        from huellitas_alegres.urls import urlpatterns
        if django_settings.DEBUG:
            # Check that at least one URL pattern starts with 'media/'
            media_patterns = [p for p in urlpatterns if hasattr(p, 'pattern') and 'media' in str(p.pattern)]
            self.assertTrue(len(media_patterns) > 0, "No media URL pattern found when DEBUG=True")


# ========================================
# PHASE 1 INFRA: Mascota Model Enhancement Tests (T1.4, T1.5)
# ========================================

class MascotaModelEnhancementTest(TestCase):
    """T1.4/T1.5: New fields on Mascota model — alergias, esterilizado, foto"""

    def setUp(self):
        self.cliente_rol = Rol.objects.get(nombre='Cliente')
        User = get_user_model()
        self.owner = User.objects.create_user(
            username='owner_enh', email='owner_enh@test.com',
            password='pass123', rol=self.cliente_rol,
        )

    # T1.4 — alergias field
    def test_alergias_field_exists(self):
        """Mascota can be created with alergias='Penicilina'"""
        from mascotas.models import Mascota
        m = Mascota.objects.create(
            nombre='Fido', especie='Canino', sexo='Macho',
            propietario=self.owner, alergias='Penicilina',
        )
        self.assertEqual(m.alergias, 'Penicilina')

    def test_alergias_default_ninguna(self):
        """Mascota without alergias defaults to 'Ninguna'"""
        from mascotas.models import Mascota
        m = Mascota.objects.create(
            nombre='Mishi', especie='Felino', sexo='Hembra',
            propietario=self.owner,
        )
        self.assertEqual(m.alergias, 'Ninguna')

    # T1.4 — esterilizado field
    def test_esterilizado_field_exists(self):
        """Mascota can be created with esterilizado=True"""
        from mascotas.models import Mascota
        m = Mascota.objects.create(
            nombre='Rex', especie='Canino', sexo='Macho',
            propietario=self.owner, esterilizado=True,
        )
        self.assertTrue(m.esterilizado)

    def test_esterilizado_default_false(self):
        """Mascota without esterilizado defaults to False"""
        from mascotas.models import Mascota
        m = Mascota.objects.create(
            nombre='Luna', especie='Felino', sexo='Hembra',
            propietario=self.owner,
        )
        self.assertFalse(m.esterilizado)

    # T1.5 — foto field
    def test_foto_field_blank_and_null(self):
        """Mascota can be created without foto (blank/null)"""
        from mascotas.models import Mascota
        m = Mascota.objects.create(
            nombre='Buddy', especie='Canino', sexo='Macho',
            propietario=self.owner,
        )
        self.assertFalse(m.foto)

    def test_foto_upload_to_mascotas(self):
        """Foto field has upload_to='mascotas/'"""
        from mascotas.models import Mascota
        foto_field = Mascota._meta.get_field('foto')
        self.assertEqual(foto_field.upload_to, 'mascotas/')


# ========================================
# PHASE 1 INFRA: Usuario Cédula Test (T1.6)
# ========================================

class UsuarioCedulaTest(TestCase):
    """T1.6: Cédula field on Usuario model"""

    def setUp(self):
        self.cliente_rol = Rol.objects.get(nombre='Cliente')

    def test_cedula_field_exists(self):
        """Usuario can be created with cedula='12345678'"""
        User = get_user_model()
        u = User.objects.create_user(
            username='cedula_test', email='cedula@test.com',
            password='pass123', rol=self.cliente_rol,
            cedula='12345678',
        )
        self.assertEqual(u.cedula, '12345678')

    def test_cedula_default_empty(self):
        """Usuario without cedula defaults to empty string"""
        User = get_user_model()
        u = User.objects.create_user(
            username='cedula_empty', email='cedula_empty@test.com',
            password='pass123', rol=self.cliente_rol,
        )
        self.assertEqual(u.cedula, '')

    def test_cedula_blank_allowed(self):
        """Usuario can be created with cedula='' (blank allowed)"""
        User = get_user_model()
        u = User.objects.create_user(
            username='cedula_blank', email='cedula_blank@test.com',
            password='pass123', rol=self.cliente_rol,
            cedula='',
        )
        self.assertEqual(u.cedula, '')


# ========================================
# PHASE 2: Model Logic — get_edad() Tests (REQ-03)
# ========================================

class MascotaEdadTest(TestCase):
    """REQ-03: get_edad() method — dynamic age calculation in Spanish"""

    def setUp(self):
        self.cliente_rol = Rol.objects.get(nombre='Cliente')
        User = get_user_model()
        self.owner = User.objects.create_user(
            username='owner_edad', email='owner_edad@test.com',
            password='pass123', rol=self.cliente_rol,
        )

    @staticmethod
    def _birth_date(years=0, months=0):
        """Helper: calculate a birth date N years and M months ago, safe for any day."""
        today = date.today()
        # Compute year and month
        total_months = today.year * 12 + today.month - (years * 12 + months)
        y = total_months // 12
        m = total_months % 12
        if m == 0:
            y -= 1
            m = 12
        # Use minimum of birth-day and 28 to avoid InvalidDay errors
        d = min(today.day, 28)
        return date(y, m, d)

    def test_get_edad_years_and_months(self):
        """R3.1: Mascota born 2 years 3 months ago returns '2 años, 3 meses'"""
        from mascotas.models import Mascota
        birth = self._birth_date(years=2, months=3)
        m = Mascota.objects.create(
            nombre='Fido', especie='Canino', sexo='Macho',
            propietario=self.owner, fecha_nacimiento=birth,
        )
        self.assertEqual(m.get_edad(), '2 años, 3 meses')

    def test_get_edad_single_year(self):
        """R3.2: Mascota born exactly 1 year ago returns '1 año' (singular)"""
        from mascotas.models import Mascota
        birth = self._birth_date(years=1)
        m = Mascota.objects.create(
            nombre='Rex', especie='Canino', sexo='Macho',
            propietario=self.owner, fecha_nacimiento=birth,
        )
        self.assertEqual(m.get_edad(), '1 año')

    def test_get_edad_months_only(self):
        """R3.3: Mascota born 2 months ago returns '2 meses'"""
        from mascotas.models import Mascota
        birth = self._birth_date(months=2)
        m = Mascota.objects.create(
            nombre='Cachorro', especie='Canino', sexo='Macho',
            propietario=self.owner, fecha_nacimiento=birth,
        )
        self.assertEqual(m.get_edad(), '2 meses')

    def test_get_edad_null_fecha_nacimiento(self):
        """R3.4: Mascota with no fecha_nacimiento returns 'Edad desconocida'"""
        from mascotas.models import Mascota
        m = Mascota.objects.create(
            nombre='SinFecha', especie='Felino', sexo='Hembra',
            propietario=self.owner,
        )
        self.assertEqual(m.get_edad(), 'Edad desconocida')

    def test_get_edad_today_born(self):
        """R3.5: Mascota born today returns 'Recién nacido'"""
        from mascotas.models import Mascota
        m = Mascota.objects.create(
            nombre='Bebe', especie='Canino', sexo='Macho',
            propietario=self.owner, fecha_nacimiento=date.today(),
        )
        self.assertEqual(m.get_edad(), 'Recién nacido')


# ========================================
# PHASE 3: Search & Filter Tests (REQ-05, REQ-06, REQ-11, REQ-12)
# ========================================

class MascotaSearchTest(TestCase):
    """REQ-05: Q-object search — nombre, especie, cédula"""

    def setUp(self):
        self.vet_rol = Rol.objects.get(nombre='Veterinario')
        self.cliente_rol = Rol.objects.get(nombre='Cliente')
        User = get_user_model()
        self.vet_user = User.objects.create_user(
            username='vet_search', email='vet_search@test.com',
            password='pass123', rol=self.vet_rol,
        )
        # Cliente con cédula
        self.owner1 = User.objects.create_user(
            username='owner_search1', email='owner1@test.com',
            password='pass123', rol=self.cliente_rol, cedula='12345678',
        )
        # Cliente sin cédula
        self.owner2 = User.objects.create_user(
            username='owner_search2', email='owner2@test.com',
            password='pass123', rol=self.cliente_rol,
        )
        from mascotas.models import Mascota
        self.fido = Mascota.objects.create(
            nombre='Fido', especie='Canino', raza='Labrador',
            sexo='Macho', propietario=self.owner1,
        )
        self.mishi = Mascota.objects.create(
            nombre='Mishi', especie='Felino', raza='Siames',
            sexo='Hembra', propietario=self.owner1,
        )
        self.loro = Mascota.objects.create(
            nombre='Piolin', especie='Ave', sexo='Macho',
            propietario=self.owner2,
        )

    def test_search_by_nombre(self):
        """R5.1: Search by nombre finds matching mascotas"""
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('mascotas:lista'), {'q': 'Fido'})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Fido')
        self.assertNotContains(resp, 'Mishi')
        self.assertNotContains(resp, 'Piolin')

    def test_search_by_especie(self):
        """R5.2: Search by especie finds matching mascotas"""
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('mascotas:lista'), {'q': 'Canino'})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Fido')
        self.assertNotContains(resp, 'Mishi')

    def test_search_by_cedula(self):
        """R5.3: Search by propietario cedula finds matching mascotas"""
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('mascotas:lista'), {'q': '12345678'})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Fido')
        self.assertContains(resp, 'Mishi')
        self.assertNotContains(resp, 'Piolin')

    def test_search_no_results(self):
        """R5.4: Search with no matching results shows empty"""
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('mascotas:lista'), {'q': 'XYZ999'})
        self.assertEqual(resp.status_code, 200)
        self.assertNotContains(resp, 'Fido')
        self.assertNotContains(resp, 'Mishi')
        self.assertNotContains(resp, 'Piolin')

    def test_search_combined_with_especie_filter(self):
        """R5.5: Search combined with especie filter"""
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('mascotas:lista'), {'q': '12345678', 'especie': 'Canino'})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Fido')
        self.assertNotContains(resp, 'Mishi')  # Felino, filtered out


class MascotaSpeciesFilterTest(TestCase):
    """REQ-06: Species filter via ?especie= parameter"""

    def setUp(self):
        self.vet_rol = Rol.objects.get(nombre='Veterinario')
        self.cliente_rol = Rol.objects.get(nombre='Cliente')
        User = get_user_model()
        self.vet_user = User.objects.create_user(
            username='vet_filter', email='vet_filter@test.com',
            password='pass123', rol=self.vet_rol,
        )
        self.owner = User.objects.create_user(
            username='owner_filter', email='owner_filter@test.com',
            password='pass123', rol=self.cliente_rol,
        )
        from mascotas.models import Mascota
        Mascota.objects.create(nombre='Fido', especie='Canino', sexo='Macho', propietario=self.owner)
        Mascota.objects.create(nombre='Mishi', especie='Felino', sexo='Hembra', propietario=self.owner)
        Mascota.objects.create(nombre='Piolin', especie='Ave', sexo='Macho', propietario=self.owner)

    def test_filter_by_canino(self):
        """R6.1: Filter by Canino shows only caninos"""
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('mascotas:lista'), {'especie': 'Canino'})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Fido')
        self.assertNotContains(resp, 'Mishi')
        self.assertNotContains(resp, 'Piolin')

    def test_filter_by_felino(self):
        """R6.2: Filter by Felino shows only felinos"""
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('mascotas:lista'), {'especie': 'Felino'})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Mishi')
        self.assertNotContains(resp, 'Fido')

    def test_filter_invalid_species_shows_empty(self):
        """R6.3: Filter by invalid species shows empty (strict filter)"""
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('mascotas:lista'), {'especie': 'Dinosaurio'})
        self.assertEqual(resp.status_code, 200)
        self.assertNotContains(resp, 'Fido')
        self.assertNotContains(resp, 'Mishi')

    def test_filter_no_especie_shows_all(self):
        """R6.4: No especie filter shows all mascotas"""
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('mascotas:lista'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Fido')
        self.assertContains(resp, 'Mishi')
        self.assertContains(resp, 'Piolin')


class MascotaFormEnhancementTest(TestCase):
    """REQ-11: MascotaForm includes new fields (alergias, esterilizado, foto)"""

    def test_form_includes_alergias(self):
        """R11.1: MascotaForm has alergias field"""
        from mascotas.forms import MascotaForm
        form = MascotaForm()
        self.assertIn('alergias', form.fields)

    def test_form_includes_esterilizado(self):
        """R11.2: MascotaForm has esterilizado field"""
        from mascotas.forms import MascotaForm
        form = MascotaForm()
        self.assertIn('esterilizado', form.fields)

    def test_form_includes_foto(self):
        """R11.3: MascotaForm has foto field"""
        from mascotas.forms import MascotaForm
        form = MascotaForm()
        self.assertIn('foto', form.fields)


class MascotaSearchUITest(TestCase):
    """REQ-05/06: Search bar and species badges render in list template"""

    def setUp(self):
        self.vet_rol = Rol.objects.get(nombre='Veterinario')
        User = get_user_model()
        self.vet_user = User.objects.create_user(
            username='vet_ui', email='vet_ui@test.com',
            password='pass123', rol=self.vet_rol,
        )

    def test_search_bar_present(self):
        """Search form with q input renders in list page"""
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('mascotas:lista'))
        self.assertContains(resp, 'name="q"')

    def test_species_badges_present(self):
        """Species filter badges render in list page"""
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('mascotas:lista'))
        self.assertContains(resp, 'Canino')
        self.assertContains(resp, 'Felino')


class PaginationPreservationTest(TestCase):
    """REQ-12: Pagination preserves ?q= and ?especie= parameters"""

    def setUp(self):
        self.vet_rol = Rol.objects.get(nombre='Veterinario')
        self.cliente_rol = Rol.objects.get(nombre='Cliente')
        User = get_user_model()
        self.vet_user = User.objects.create_user(
            username='vet_pag', email='vet_pag@test.com',
            password='pass123', rol=self.vet_rol,
        )
        self.owner = User.objects.create_user(
            username='owner_pag', email='owner_pag@test.com',
            password='pass123', rol=self.cliente_rol,
        )
        from mascotas.models import Mascota
        # Create 15 mascotas to ensure pagination
        for i in range(15):
            especie = 'Canino' if i % 2 == 0 else 'Felino'
            Mascota.objects.create(
                nombre=f'Mascota{i}', especie=especie, sexo='Macho',
                propietario=self.owner,
            )

    def test_pagination_preserves_search_query(self):
        """R12.1: Page 2 link includes ?q= parameter"""
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('mascotas:lista'), {'q': 'Mascota', 'page': 1})
        self.assertEqual(resp.status_code, 200)
        # Verify pagination links preserve search query
        content = resp.content.decode()
        self.assertIn('q=Mascota', content)

    def test_pagination_preserves_especie_filter(self):
        """R12.2: Page links include ?especie= parameter"""
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('mascotas:lista'), {'especie': 'Canino', 'page': 1})
        self.assertEqual(resp.status_code, 200)
        content = resp.content.decode()
        self.assertIn('especie=Canino', content)

    def test_pagination_preserves_combined_params(self):
        """R12.3: Page links preserve both ?q= and ?especie="""
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('mascotas:lista'), {'q': 'Mascota', 'especie': 'Canino', 'page': 1})
        self.assertEqual(resp.status_code, 200)
        content = resp.content.decode()
        self.assertIn('q=Mascota', content)
        self.assertIn('especie=Canino', content)

    def test_pagination_no_params_works(self):
        """R12.4: Pagination works without any search params"""
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('mascotas:lista'), {'page': 1})
        self.assertEqual(resp.status_code, 200)


# ========================================
# PHASE 4: Detail View Tests (REQ-07, REQ-08, REQ-09)
# ========================================

class MascotaDetailViewTest(TestCase):
    """REQ-07: Detail view — authenticated access, ownership, role-based"""

    def setUp(self):
        self.vet_rol = Rol.objects.get(nombre='Veterinario')
        self.admin_rol = Rol.objects.get(nombre='Administrador')
        self.cliente_rol = Rol.objects.get(nombre='Cliente')
        User = get_user_model()
        self.vet_user = User.objects.create_user(
            username='vet_detail', email='vet_detail@test.com',
            password='pass123', rol=self.vet_rol,
        )
        self.admin_user = User.objects.create_user(
            username='admin_detail', email='admin_detail@test.com',
            password='pass123', rol=self.admin_rol,
        )
        self.owner_user = User.objects.create_user(
            username='owner_detail', email='owner_detail@test.com',
            password='pass123', rol=self.cliente_rol,
        )
        self.other_user = User.objects.create_user(
            username='other_detail', email='other_detail@test.com',
            password='pass123', rol=self.cliente_rol,
        )
        from mascotas.models import Mascota
        self.own_mascota = Mascota.objects.create(
            nombre='Firulais', especie='Canino', sexo='Macho',
            propietario=self.owner_user,
        )

    def test_authenticated_user_can_access_detail(self):
        """R7.1: Authenticated user can access detail page"""
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('mascotas:detalle', kwargs={'pk': self.own_mascota.pk}))
        self.assertEqual(resp.status_code, 200)

    def test_owner_cliente_can_see_own_mascota(self):
        """R7.2: Cliente can see detail of own mascota"""
        self.client.force_login(self.owner_user)
        resp = self.client.get(reverse('mascotas:detalle', kwargs={'pk': self.own_mascota.pk}))
        self.assertEqual(resp.status_code, 200)

    def test_other_cliente_gets_403(self):
        """R7.3: Cliente gets 403 for another user's mascota"""
        self.client.force_login(self.other_user)
        resp = self.client.get(reverse('mascotas:detalle', kwargs={'pk': self.own_mascota.pk}))
        self.assertEqual(resp.status_code, 403)

    def test_admin_can_see_any_mascota(self):
        """R7.4: Admin can see any mascota detail"""
        self.client.force_login(self.admin_user)
        resp = self.client.get(reverse('mascotas:detalle', kwargs={'pk': self.own_mascota.pk}))
        self.assertEqual(resp.status_code, 200)

    def test_unauthenticated_redirected_to_login(self):
        """R7.5: Unauthenticated user redirected to login"""
        resp = self.client.get(reverse('mascotas:detalle', kwargs={'pk': self.own_mascota.pk}))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/usuarios/login/', resp.url)

    def test_agendar_cita_link_present(self):
        """Agendar Cita link is present on detail page"""
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('mascotas:detalle', kwargs={'pk': self.own_mascota.pk}))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, reverse('agenda:crear_cita'))


class AllergyBannerTest(TestCase):
    """REQ-08: Allergy banner — red alert when alergias != 'Ninguna'"""

    def setUp(self):
        self.vet_rol = Rol.objects.get(nombre='Veterinario')
        User = get_user_model()
        self.vet_user = User.objects.create_user(
            username='vet_allergy', email='vet_allergy@test.com',
            password='pass123', rol=self.vet_rol,
        )

    def test_allergy_banner_shows_when_alergias(self):
        """R8.1: Mascota with alergias='Penicilina' shows red banner"""
        from mascotas.models import Mascota
        m = Mascota.objects.create(
            nombre='Alergico', especie='Canino', sexo='Macho',
            propietario=self.vet_user, alergias='Penicilina',
        )
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('mascotas:detalle', kwargs={'pk': m.pk}))
        self.assertContains(resp, 'ALERTA')
        self.assertContains(resp, 'Penicilina')

    def test_allergy_banner_hidden_when_ninguna(self):
        """R8.2: Mascota with alergias='Ninguna' does NOT show banner"""
        from mascotas.models import Mascota
        m = Mascota.objects.create(
            nombre='Sano', especie='Canino', sexo='Macho',
            propietario=self.vet_user, alergias='Ninguna',
        )
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('mascotas:detalle', kwargs={'pk': m.pk}))
        self.assertNotContains(resp, 'ALERTA')

    def test_allergy_banner_content(self):
        """R8.3: Banner contains the specific allergy text"""
        from mascotas.models import Mascota
        m = Mascota.objects.create(
            nombre='GatoAlergico', especie='Felino', sexo='Hembra',
            propietario=self.vet_user, alergias='Lactosa, Penicilina',
        )
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('mascotas:detalle', kwargs={'pk': m.pk}))
        self.assertContains(resp, 'Lactosa, Penicilina')
        self.assertContains(resp, 'alert-danger')


class LastVisitTest(TestCase):
    """REQ-09: Last visit indicator from agenda app"""

    def setUp(self):
        self.vet_rol = Rol.objects.get(nombre='Veterinario')
        self.cliente_rol = Rol.objects.get(nombre='Cliente')
        User = get_user_model()
        self.vet_user = User.objects.create_user(
            username='vet_visit', email='vet_visit@test.com',
            password='pass123', rol=self.vet_rol,
        )
        self.owner = User.objects.create_user(
            username='owner_visit', email='owner_visit@test.com',
            password='pass123', rol=self.cliente_rol,
        )
        from mascotas.models import Mascota
        from agenda.models import Disponibilidad
        self.mascota = Mascota.objects.create(
            nombre='Visitado', especie='Canino', sexo='Macho',
            propietario=self.owner,
        )
        self.disp = Disponibilidad.objects.create(
            fecha=date.today(), hora_inicio='10:00', hora_fin='11:00', veterinario=self.vet_user,
        )

    def test_last_visit_shows_date(self):
        """R9.1: Mascota with Atendida Cita shows visit date"""
        from agenda.models import Cita
        Cita.objects.create(
            mascota=self.mascota, disponibilidad=self.disp,
            estado='Atendida',
        )
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('mascotas:detalle', kwargs={'pk': self.mascota.pk}))
        # Django renders date as "April 23, 2026" format
        self.assertContains(resp, '2026')
        self.assertContains(resp, 'ltima visita')  # Matches both "Última" and "ultima"

    def test_last_visit_shows_no_visits(self):
        """R9.2: Mascota with no citas shows 'Sin visitas registradas'"""
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('mascotas:detalle', kwargs={'pk': self.mascota.pk}))
        self.assertContains(resp, 'Sin visitas registradas')

    def test_last_visit_ignores_cancelled(self):
        """R9.3: Cancelled citas are ignored — shows 'Sin visitas registradas'"""
        from agenda.models import Cita
        Cita.objects.create(
            mascota=self.mascota, disponibilidad=self.disp,
            estado='Cancelada', motivo_cancelacion='No asistió',
        )
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('mascotas:detalle', kwargs={'pk': self.mascota.pk}))
        self.assertContains(resp, 'Sin visitas registradas')

    def test_last_visit_ignores_programada(self):
        """R9.4: Programada citas are ignored for last visit"""
        from agenda.models import Cita
        Cita.objects.create(
            mascota=self.mascota, disponibilidad=self.disp,
            estado='Programada',
        )
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('mascotas:detalle', kwargs={'pk': self.mascota.pk}))
        self.assertContains(resp, 'Sin visitas registradas')


# ========================================
# PHASE 5: Integration & Polish Tests
# ========================================

class MascotaDetailLinkTest(TestCase):
    """REQ-07: Detail link in list view"""

    def setUp(self):
        self.vet_rol = Rol.objects.get(nombre='Veterinario')
        User = get_user_model()
        self.vet_user = User.objects.create_user(
            username='vet_link', email='vet_link@test.com',
            password='pass123', rol=self.vet_rol,
        )
        from mascotas.models import Mascota
        self.mascota = Mascota.objects.create(
            nombre='LinkTest', especie='Canino', sexo='Macho',
            propietario=self.vet_user,
        )

    def test_mascota_name_links_to_detail(self):
        """Mascota name in list links to detail view"""
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('mascotas:lista'))
        detail_url = reverse('mascotas:detalle', kwargs={'pk': self.mascota.pk})
        self.assertContains(resp, detail_url)


class MascotaAdminEnhancementTest(TestCase):
    """REQ-01/04: Admin updates for alergias, esterilizado, cedula"""

    def test_cedula_in_admin_list_display(self):
        """Cedula appears in Usuario admin list_display"""
        from usuarios.admin import UsuarioAdmin
        self.assertIn('cedula', UsuarioAdmin.list_display)

    def test_cedula_in_admin_search(self):
        """Cedula appears in Usuario admin search_fields"""
        from usuarios.admin import UsuarioAdmin
        self.assertIn('cedula', UsuarioAdmin.search_fields)

    def test_alergias_in_mascota_admin(self):
        """Alergias and esterilizado in Mascota admin"""
        from mascotas.admin import MascotaAdmin
        self.assertIn('alergias', MascotaAdmin.list_display)
        self.assertIn('esterilizado', MascotaAdmin.list_filter)
