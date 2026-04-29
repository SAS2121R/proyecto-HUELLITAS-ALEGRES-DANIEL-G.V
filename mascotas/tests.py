from datetime import date

from django.test import TestCase
from django.db import IntegrityError
from django.urls import reverse, resolve
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model

from usuarios.models import Rol


# ========================================
# FASE 4: Tests de Vista de Creación (REQ-04)
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
        """R4.1: Veterinario crea mascota exitosamente"""
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
        """R4.2: Administrador crea mascota exitosamente"""
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

    def test_cliente_can_create_mascota(self):
        """R4.3: Cliente puede crear mascota (propietario forzado a request.user)"""
        self.client.force_login(self.cliente_user)
        from mascotas.models import Mascota
        resp = self.client.post(reverse('mascotas:nuevo'), data={
            'nombre': 'ClientDog',
            'especie': 'Canino',
            'sexo': 'Macho',
        })
        self.assertEqual(resp.status_code, 302)
        mascota = Mascota.objects.get(nombre='ClientDog')
        self.assertEqual(mascota.propietario, self.cliente_user)

    def test_unauthenticated_redirected_to_login(self):
        """R4.4: Usuario no autenticado redirigido a login"""
        resp = self.client.get(reverse('mascotas:nuevo'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/usuarios/login/', resp.url)

    def test_form_errors_render(self):
        """R4.5: Errores de formulario renderizan con mensajes"""
        self.client.force_login(self.vet_user)
        resp = self.client.post(reverse('mascotas:nuevo'), data={
            'nombre': '',  # Campo requerido faltante
            'especie': 'Canino',
            'sexo': 'Macho',
        })
        self.assertEqual(resp.status_code, 200)
        from mascotas.models import Mascota
        self.assertEqual(Mascota.objects.count(), 0)


# ========================================
# FASE 3: Tests de Vista de Lista (REQ-03)
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
        """R3.1: Veterinario ve todas las mascotas"""
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('mascotas:lista'))
        self.assertEqual(resp.status_code, 200)
        content = resp.content.decode()
        self.assertIn('Fido', content)
        self.assertIn('Mishi', content)

    def test_administrador_sees_all_mascotas(self):
        """R3.2: Administrador ve todas las mascotas"""
        self.client.force_login(self.admin_user)
        resp = self.client.get(reverse('mascotas:lista'))
        self.assertEqual(resp.status_code, 200)
        content = resp.content.decode()
        self.assertIn('Fido', content)
        self.assertIn('Mishi', content)

    def test_cliente_sees_only_own_mascotas(self):
        """R3.3: Cliente ve solo sus propias mascotas"""
        self.client.force_login(self.cliente_user)
        resp = self.client.get(reverse('mascotas:lista'))
        self.assertEqual(resp.status_code, 200)
        content = resp.content.decode()
        self.assertIn('Fido', content)
        self.assertNotIn('Mishi', content)

    def test_unauthenticated_redirected_to_login(self):
        """R3.4: Usuario no autenticado redirigido a login"""
        resp = self.client.get(reverse('mascotas:lista'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/usuarios/login/', resp.url)


# ========================================
# FASE 2: Tests de Capa de Formulario (REQ-02)
# ========================================

class MascotaFormTest(TestCase):
    """REQ-02: MascotaForm — 6 scenarios"""

    def test_valid_form_creates_mascota(self):
        """R2.1: Formulario válido es válido y guarda"""
        from mascotas.forms import MascotaForm
        form = MascotaForm(data={
            'nombre': 'Fido',
            'especie': 'Canino',
            'raza': 'Labrador',
            'sexo': 'Macho',
        })
        self.assertTrue(form.is_valid(), form.errors)

    def test_invalid_especie_rejected(self):
        """R2.2: Especie inválida es rechazada"""
        from mascotas.forms import MascotaForm
        form = MascotaForm(data={
            'nombre': 'Test',
            'especie': 'Dinosaurio',
            'sexo': 'Macho',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('especie', form.errors)

    def test_invalid_sexo_rejected(self):
        """R2.3: Sexo inválido es rechazado"""
        from mascotas.forms import MascotaForm
        form = MascotaForm(data={
            'nombre': 'Test',
            'especie': 'Canino',
            'sexo': 'Hermafrodita',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('sexo', form.errors)

    def test_blank_raza_accepted(self):
        """R2.4: Raza en blanco es aceptada"""
        from mascotas.forms import MascotaForm
        form = MascotaForm(data={
            'nombre': 'Test',
            'especie': 'Felino',
            'raza': '',
            'sexo': 'Hembra',
        })
        self.assertTrue(form.is_valid(), form.errors)

    def test_blank_fecha_nacimiento_accepted(self):
        """R2.5: Fecha_nacimiento en blanco es aceptada"""
        from mascotas.forms import MascotaForm
        form = MascotaForm(data={
            'nombre': 'Test',
            'especie': 'Ave',
            'sexo': 'Macho',
            'fecha_nacimiento': '',
        })
        self.assertTrue(form.is_valid(), form.errors)

    def test_future_fecha_nacimiento_rejected(self):
        """R2.6: Fecha_nacimiento futura es rechazada"""
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
# FASE 1: Tests de Modelo + Registro de App + URLs (REQ-01, REQ-08, REQ-09)
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
        """R1.1: Creación de Mascota con todos los campos poblados"""
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
        """R1.2: Creación de Mascota con raza y fecha_nacimiento omitidos"""
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
        """R1.3: __str__ devuelve 'nombre (especie)'"""
        from mascotas.models import Mascota
        m = Mascota.objects.create(
            nombre='Rex',
            especie='Canino',
            sexo='Macho',
            propietario=self.owner,
        )
        self.assertEqual(str(m), 'Rex (Canino)')

    def test_propietario_related_name_works(self):
        """R1.4: usuario.mascotas.all() devuelve mascotas para ese usuario"""
        from mascotas.models import Mascota
        Mascota.objects.create(nombre='Fido', especie='Canino', sexo='Macho', propietario=self.owner)
        Mascota.objects.create(nombre='Mishi', especie='Felino', sexo='Hembra', propietario=self.owner)
        mascotas = self.owner.mascotas.all()
        self.assertEqual(mascotas.count(), 2)

    def test_especie_choices_enforced(self):
        """R1.5: Especie inválida lanza ValidationError"""
        from mascotas.models import Mascota
        m = Mascota(nombre='Invalido', especie='Dinosaurio', sexo='Macho', propietario=self.owner)
        with self.assertRaisesMessage(Exception, 'is not a valid choice'):
            m.full_clean()

    def test_sexo_choices_enforced(self):
        """R1.6: Sexo inválido lanza ValidationError"""
        from mascotas.models import Mascota
        m = Mascota(nombre='Test', especie='Canino', sexo='Neutro', propietario=self.owner)
        with self.assertRaisesMessage(Exception, 'is not a valid choice'):
            m.full_clean()


class AppRegistrationTest(TestCase):
    """REQ-09: App is registered in INSTALLED_APPS"""

    def test_mascotas_app_registered(self):
        """R9.1: 'mascotas' está en INSTALLED_APPS"""
        self.assertIn('mascotas', settings.INSTALLED_APPS)


class URLConfigurationTest(TestCase):
    """REQ-08: URL configuration — all CRUD URLs resolve"""

    def test_lista_url_resolves(self):
        """R8.1: mascotas:lista resuelve a /mascotas/"""
        url = reverse('mascotas:lista')
        self.assertEqual(url, '/mascotas/')

    def test_nuevo_url_resolves(self):
        """R8.1: mascotas:nuevo resuelve a /mascotas/nuevo/"""
        url = reverse('mascotas:nuevo')
        self.assertEqual(url, '/mascotas/nuevo/')

    def test_editar_url_resolves(self):
        """R8.1: mascotas:editar con pk=1 resuelve a /mascotas/editar/1/"""
        url = reverse('mascotas:editar', kwargs={'pk': 1})
        self.assertEqual(url, '/mascotas/editar/1/')

    def test_eliminar_url_resolves(self):
        """R8.1: mascotas:eliminar con pk=1 resuelve a /mascotas/eliminar/1/"""
        url = reverse('mascotas:eliminar', kwargs={'pk': 1})
        self.assertEqual(url, '/mascotas/eliminar/1/')


# ========================================
# FASE 5: Tests de Vista de Edición (REQ-05)
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
        """R5.1: Veterinario edita cualquier mascota"""
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
        """R5.2: Administrador edita cualquier mascota"""
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
        """R5.3: Cliente edita su propia mascota"""
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
        """R5.4: Cliente no puede editar mascota de otro usuario (403)"""
        self.client.force_login(self.owner_user)
        resp = self.client.get(reverse('mascotas:editar', kwargs={'pk': self.other_mascota.pk}))
        self.assertEqual(resp.status_code, 403)

    def test_unauthenticated_redirected_to_login_edit(self):
        """R5.5: No autenticado redirigido a login"""
        resp = self.client.get(reverse('mascotas:editar', kwargs={'pk': self.own_mascota.pk}))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/usuarios/login/', resp.url)


# ========================================
# FASE 6: Tests de Vista de Eliminación (REQ-06)
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
        """R6.1: Veterinario elimina mascota — GET=confirmación, POST=eliminar"""
        self.client.force_login(self.vet_user)
        # GET muestra página de confirmación
        resp_get = self.client.get(reverse('mascotas:eliminar', kwargs={'pk': self.mascota.pk}))
        self.assertEqual(resp_get.status_code, 200)
        self.assertContains(resp_get, 'ToDelete')
        # POST elimina
        resp_post = self.client.post(reverse('mascotas:eliminar', kwargs={'pk': self.mascota.pk}))
        self.assertEqual(resp_post.status_code, 302)
        from mascotas.models import Mascota
        self.assertFalse(Mascota.objects.filter(pk=self.mascota.pk).exists())

    def test_administrador_deletes_mascota(self):
        """R6.2: Administrador elimina mascota"""
        self.client.force_login(self.admin_user)
        resp = self.client.post(reverse('mascotas:eliminar', kwargs={'pk': self.mascota.pk}))
        self.assertEqual(resp.status_code, 302)
        from mascotas.models import Mascota
        self.assertFalse(Mascota.objects.filter(pk=self.mascota.pk).exists())

    def test_cliente_cannot_delete_403(self):
        """R6.3: Cliente no puede eliminar (403)"""
        self.client.force_login(self.cliente_user)
        resp = self.client.get(reverse('mascotas:eliminar', kwargs={'pk': self.mascota.pk}))
        self.assertEqual(resp.status_code, 403)

    def test_unauthenticated_redirected_to_login_delete(self):
        """R6.4: No autenticado redirigido a login"""
        resp = self.client.get(reverse('mascotas:eliminar', kwargs={'pk': self.mascota.pk}))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/usuarios/login/', resp.url)


# ========================================
# FASE 7: Tests de Integración de Dashboard (REQ-07)
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
        """R7.1: Dashboard contiene link a mascotas:lista"""
        from django.test import Client
        client = Client()
        client.force_login(self.vet_user)
        resp = client.get(reverse('usuarios:vet_dashboard'))
        self.assertEqual(resp.status_code, 200)
        mascotas_url = reverse('mascotas:lista')
        self.assertContains(resp, mascotas_url)


# ========================================
# FASE 1 INFRA: Tests de Configuración de Media (T1.2, T1.3)
# ========================================

class MediaConfigTest(TestCase):
    """T1.2/T1.3: MEDIA_URL, MEDIA_ROOT, and debug media serving"""

    def test_media_url_configured(self):
        """MEDIA_URL está configurado a '/media/'"""
        self.assertEqual(settings.MEDIA_URL, '/media/')

    def test_media_root_configured(self):
        """MEDIA_ROOT está configurado y termina con 'media'"""
        self.assertTrue(hasattr(settings, 'MEDIA_ROOT'))
        self.assertTrue(str(settings.MEDIA_ROOT).endswith('media'))

    def test_media_serves_files_in_debug(self):
        """Cuando DEBUG=True, patrón URL /media/ existe en configuración de URLs"""
        from django.conf import settings as django_settings
        from huellitas_alegres.urls import urlpatterns
        if django_settings.DEBUG:
            # Verificar que al menos un patrón de URL empieza con 'media/'
            media_patterns = [p for p in urlpatterns if hasattr(p, 'pattern') and 'media' in str(p.pattern)]
            self.assertTrue(len(media_patterns) > 0, "No media URL pattern found when DEBUG=True")


# ========================================
# FASE 1 INFRA: Tests de Mejoras al Modelo Mascota (T1.4, T1.5)
# ========================================

class MascotaModelEnhancementTest(TestCase):
    """T1.4/T1.5: Nuevos campos en modelo Mascota — alergias, esterilizado, foto"""

    def setUp(self):
        self.cliente_rol = Rol.objects.get(nombre='Cliente')
        User = get_user_model()
        self.owner = User.objects.create_user(
            username='owner_enh', email='owner_enh@test.com',
            password='pass123', rol=self.cliente_rol,
        )

    # T1.4 — alergias field
    def test_alergias_field_exists(self):
        """Mascota puede ser creada con alergias='Penicilina'"""
        from mascotas.models import Mascota
        m = Mascota.objects.create(
            nombre='Fido', especie='Canino', sexo='Macho',
            propietario=self.owner, alergias='Penicilina',
        )
        self.assertEqual(m.alergias, 'Penicilina')

    def test_alergias_default_ninguna(self):
        """Mascota sin alergias por defecto es 'Ninguna'"""
        from mascotas.models import Mascota
        m = Mascota.objects.create(
            nombre='Mishi', especie='Felino', sexo='Hembra',
            propietario=self.owner,
        )
        self.assertEqual(m.alergias, 'Ninguna')

    # T1.4 — esterilizado field
    def test_esterilizado_field_exists(self):
        """Mascota puede ser creada con esterilizado=True"""
        from mascotas.models import Mascota
        m = Mascota.objects.create(
            nombre='Rex', especie='Canino', sexo='Macho',
            propietario=self.owner, esterilizado=True,
        )
        self.assertTrue(m.esterilizado)

    def test_esterilizado_default_false(self):
        """Mascota sin esterilizado por defecto es False"""
        from mascotas.models import Mascota
        m = Mascota.objects.create(
            nombre='Luna', especie='Felino', sexo='Hembra',
            propietario=self.owner,
        )
        self.assertFalse(m.esterilizado)

    # T1.5 — foto field
    def test_foto_field_blank_and_null(self):
        """Mascota puede ser creada sin foto (blank/null)"""
        from mascotas.models import Mascota
        m = Mascota.objects.create(
            nombre='Buddy', especie='Canino', sexo='Macho',
            propietario=self.owner,
        )
        self.assertFalse(m.foto)

    def test_foto_upload_to_mascotas(self):
        """Campo foto tiene upload_to='mascotas/'"""
        from mascotas.models import Mascota
        foto_field = Mascota._meta.get_field('foto')
        self.assertEqual(foto_field.upload_to, 'mascotas/')


# ========================================
# FASE 1 INFRA: Test de Cédula de Usuario (T1.6)
# ========================================

class UsuarioCedulaTest(TestCase):
    """T1.6: Campo Cédula en modelo Usuario"""

    def setUp(self):
        self.cliente_rol = Rol.objects.get(nombre='Cliente')

    def test_cedula_field_exists(self):
        """Usuario puede ser creado con cedula='12345678'"""
        User = get_user_model()
        u = User.objects.create_user(
            username='cedula_test', email='cedula@test.com',
            password='pass123', rol=self.cliente_rol,
            cedula='12345678',
        )
        self.assertEqual(u.cedula, '12345678')

    def test_cedula_default_empty(self):
        """Usuario sin cedula por defecto es string vacío"""
        User = get_user_model()
        u = User.objects.create_user(
            username='cedula_empty', email='cedula_empty@test.com',
            password='pass123', rol=self.cliente_rol,
        )
        self.assertEqual(u.cedula, '')

    def test_cedula_blank_allowed(self):
        """Usuario puede ser creado con cedula='' (blank permitido)"""
        User = get_user_model()
        u = User.objects.create_user(
            username='cedula_blank', email='cedula_blank@test.com',
            password='pass123', rol=self.cliente_rol,
            cedula='',
        )
        self.assertEqual(u.cedula, '')


# ========================================
# FASE 2: Lógica del Modelo — Tests de get_edad() (REQ-03)
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
        """Helper: calcular fecha de nacimiento N años y M meses atrás, seguro para cualquier día."""
        today = date.today()
        # Calcular año y mes
        total_months = today.year * 12 + today.month - (years * 12 + months)
        y = total_months // 12
        m = total_months % 12
        if m == 0:
            y -= 1
            m = 12
        # Usar mínimo de birth-day y 28 para evitar errores de InvalidDay
        d = min(today.day, 28)
        return date(y, m, d)

    def test_get_edad_years_and_months(self):
        """R3.1: Mascota nacida hace 2 años 3 meses devuelve '2 años, 3 meses'"""
        from mascotas.models import Mascota
        birth = self._birth_date(years=2, months=3)
        m = Mascota.objects.create(
            nombre='Fido', especie='Canino', sexo='Macho',
            propietario=self.owner, fecha_nacimiento=birth,
        )
        self.assertEqual(m.get_edad(), '2 años, 3 meses')

    def test_get_edad_single_year(self):
        """R3.2: Mascota nacida hace exactamente 1 año devuelve '1 año' (singular)"""
        from mascotas.models import Mascota
        birth = self._birth_date(years=1)
        m = Mascota.objects.create(
            nombre='Rex', especie='Canino', sexo='Macho',
            propietario=self.owner, fecha_nacimiento=birth,
        )
        self.assertEqual(m.get_edad(), '1 año')

    def test_get_edad_months_only(self):
        """R3.3: Mascota nacida hace 2 meses devuelve '2 meses'"""
        from mascotas.models import Mascota
        birth = self._birth_date(months=2)
        m = Mascota.objects.create(
            nombre='Cachorro', especie='Canino', sexo='Macho',
            propietario=self.owner, fecha_nacimiento=birth,
        )
        self.assertEqual(m.get_edad(), '2 meses')

    def test_get_edad_null_fecha_nacimiento(self):
        """R3.4: Mascota sin fecha_nacimiento devuelve 'Edad desconocida'"""
        from mascotas.models import Mascota
        m = Mascota.objects.create(
            nombre='SinFecha', especie='Felino', sexo='Hembra',
            propietario=self.owner,
        )
        self.assertEqual(m.get_edad(), 'Edad desconocida')

    def test_get_edad_today_born(self):
        """R3.5: Mascota nacida hoy devuelve 'Recién nacido'"""
        from mascotas.models import Mascota
        m = Mascota.objects.create(
            nombre='Bebe', especie='Canino', sexo='Macho',
            propietario=self.owner, fecha_nacimiento=date.today(),
        )
        self.assertEqual(m.get_edad(), 'Recién nacido')


# ========================================
# FASE 3: Tests de Búsqueda y Filtro (REQ-05, REQ-06, REQ-11, REQ-12)
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
        """R5.1: Búsqueda por nombre encuentra mascotas coincidentes"""
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('mascotas:lista'), {'q': 'Fido'})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Fido')
        self.assertNotContains(resp, 'Mishi')
        self.assertNotContains(resp, 'Piolin')

    def test_search_by_especie(self):
        """R5.2: Búsqueda por especie encuentra mascotas coincidentes"""
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('mascotas:lista'), {'q': 'Canino'})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Fido')
        self.assertNotContains(resp, 'Mishi')

    def test_search_by_cedula(self):
        """R5.3: Búsqueda por cédula del propietario encuentra mascotas coincidentes"""
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('mascotas:lista'), {'q': '12345678'})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Fido')
        self.assertContains(resp, 'Mishi')
        self.assertNotContains(resp, 'Piolin')

    def test_search_no_results(self):
        """R5.4: Búsqueda sin resultados coincidentes muestra vacío"""
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('mascotas:lista'), {'q': 'XYZ999'})
        self.assertEqual(resp.status_code, 200)
        self.assertNotContains(resp, 'Fido')
        self.assertNotContains(resp, 'Mishi')
        self.assertNotContains(resp, 'Piolin')

    def test_search_combined_with_especie_filter(self):
        """R5.5: Búsqueda combinada con filtro de especie"""
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('mascotas:lista'), {'q': '12345678', 'especie': 'Canino'})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Fido')
        self.assertNotContains(resp, 'Mishi')  # Felino, filtrado


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
        """R6.1: Filtrar por Canino muestra solo caninos"""
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('mascotas:lista'), {'especie': 'Canino'})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Fido')
        self.assertNotContains(resp, 'Mishi')
        self.assertNotContains(resp, 'Piolin')

    def test_filter_by_felino(self):
        """R6.2: Filtrar por Felino muestra solo felinos"""
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('mascotas:lista'), {'especie': 'Felino'})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Mishi')
        self.assertNotContains(resp, 'Fido')

    def test_filter_invalid_species_shows_all(self):
        """R6.3: Filtrar por especie inválida muestra todas las mascotas (ignora filtro inválido)"""
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('mascotas:lista'), {'especie': 'Dinosaurio'})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Fido')
        self.assertContains(resp, 'Mishi')
        self.assertContains(resp, 'Piolin')

    def test_filter_no_especie_shows_all(self):
        """R6.4: Sin filtro de especie muestra todas las mascotas"""
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('mascotas:lista'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Fido')
        self.assertContains(resp, 'Mishi')
        self.assertContains(resp, 'Piolin')


class MascotaFormEnhancementTest(TestCase):
    """REQ-11: MascotaForm includes new fields (alergias, esterilizado, foto)"""

    def test_form_includes_alergias(self):
        """R11.1: MascotaForm tiene campo alergias"""
        from mascotas.forms import MascotaForm
        form = MascotaForm()
        self.assertIn('alergias', form.fields)

    def test_form_includes_esterilizado(self):
        """R11.2: MascotaForm tiene campo esterilizado"""
        from mascotas.forms import MascotaForm
        form = MascotaForm()
        self.assertIn('esterilizado', form.fields)

    def test_form_includes_foto(self):
        """R11.3: MascotaForm tiene campo foto"""
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
        """Formulario de búsqueda con input q se renderiza en página de lista"""
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('mascotas:lista'))
        self.assertContains(resp, 'name="q"')

    def test_species_badges_present(self):
        """Badges de filtro de especie se renderizan en página de lista incluyendo Todos"""
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('mascotas:lista'))
        self.assertContains(resp, 'Canino')
        self.assertContains(resp, 'Felino')
        self.assertContains(resp, 'Todos')


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
        # Crear 15 mascotas para asegurar paginación
        for i in range(15):
            especie = 'Canino' if i % 2 == 0 else 'Felino'
            Mascota.objects.create(
                nombre=f'Mascota{i}', especie=especie, sexo='Macho',
                propietario=self.owner,
            )

    def test_pagination_preserves_search_query(self):
        """R12.1: Link de página 2 incluye parámetro ?q="""
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('mascotas:lista'), {'q': 'Mascota', 'page': 1})
        self.assertEqual(resp.status_code, 200)
        # Verificar que links de paginación preservan query de búsqueda
        content = resp.content.decode()
        self.assertIn('q=Mascota', content)

    def test_pagination_preserves_especie_filter(self):
        """R12.2: Links de página incluyen parámetro ?especie="""
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('mascotas:lista'), {'especie': 'Canino', 'page': 1})
        self.assertEqual(resp.status_code, 200)
        content = resp.content.decode()
        self.assertIn('especie=Canino', content)

    def test_pagination_preserves_combined_params(self):
        """R12.3: Links de página preservan ambos ?q= y ?especie="""
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('mascotas:lista'), {'q': 'Mascota', 'especie': 'Canino', 'page': 1})
        self.assertEqual(resp.status_code, 200)
        content = resp.content.decode()
        self.assertIn('q=Mascota', content)
        self.assertIn('especie=Canino', content)

    def test_pagination_no_params_works(self):
        """R12.4: Paginación funciona sin parámetros de búsqueda"""
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('mascotas:lista'), {'page': 1})
        self.assertEqual(resp.status_code, 200)


# ========================================
# FASE 4: Tests de Vista de Detalle (REQ-07, REQ-08, REQ-09)
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
        """R7.1: Usuario autenticado puede acceder a página de detalle"""
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('mascotas:detalle', kwargs={'pk': self.own_mascota.pk}))
        self.assertEqual(resp.status_code, 200)

    def test_owner_cliente_can_see_own_mascota(self):
        """R7.2: Cliente puede ver detalle de su propia mascota"""
        self.client.force_login(self.owner_user)
        resp = self.client.get(reverse('mascotas:detalle', kwargs={'pk': self.own_mascota.pk}))
        self.assertEqual(resp.status_code, 200)

    def test_other_cliente_gets_403(self):
        """R7.3: Cliente recibe 403 para mascota de otro usuario"""
        self.client.force_login(self.other_user)
        resp = self.client.get(reverse('mascotas:detalle', kwargs={'pk': self.own_mascota.pk}))
        self.assertEqual(resp.status_code, 403)

    def test_admin_can_see_any_mascota(self):
        """R7.4: Admin puede ver detalle de cualquier mascota"""
        self.client.force_login(self.admin_user)
        resp = self.client.get(reverse('mascotas:detalle', kwargs={'pk': self.own_mascota.pk}))
        self.assertEqual(resp.status_code, 200)

    def test_unauthenticated_redirected_to_login(self):
        """R7.5: Usuario no autenticado redirigido a login"""
        resp = self.client.get(reverse('mascotas:detalle', kwargs={'pk': self.own_mascota.pk}))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/usuarios/login/', resp.url)

    def test_detail_nonexistent_mascota_returns_404(self):
        """R7.6: Vista de detalle para mascota inexistente devuelve 404"""
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('mascotas:detalle', kwargs={'pk': 99999}))
        self.assertEqual(resp.status_code, 404)

    def test_agendar_cita_link_present(self):
        """Link de Agendar Cita está presente en página de detalle"""
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
        """R8.1: Mascota con alergias='Penicilina' muestra banner rojo"""
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
        """R8.2: Mascota con alergias='Ninguna' NO muestra banner"""
        from mascotas.models import Mascota
        m = Mascota.objects.create(
            nombre='Sano', especie='Canino', sexo='Macho',
            propietario=self.vet_user, alergias='Ninguna',
        )
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('mascotas:detalle', kwargs={'pk': m.pk}))
        self.assertNotContains(resp, 'ALERTA')

    def test_allergy_banner_hidden_when_empty_string(self):
        """R8.3: Mascota con alergias='' (string vacío) NO muestra banner"""
        from mascotas.models import Mascota
        m = Mascota.objects.create(
            nombre='Vacio', especie='Canino', sexo='Macho',
            propietario=self.vet_user, alergias='',
        )
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('mascotas:detalle', kwargs={'pk': m.pk}))
        self.assertNotContains(resp, 'ALERTA')

    def test_allergy_banner_content(self):
        """R8.3: Banner contiene el texto específico de alergia"""
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
        """R9.1: Mascota con Cita Atendida muestra fecha de visita"""
        from agenda.models import Cita
        Cita.objects.create(
            mascota=self.mascota, disponibilidad=self.disp,
            estado='Atendida',
        )
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('mascotas:detalle', kwargs={'pk': self.mascota.pk}))
        # Django renderiza fecha como formato "April 23, 2026"
        self.assertContains(resp, '2026')
        self.assertContains(resp, 'ltima visita')  # Coincide con "Última" y "ultima"

    def test_last_visit_shows_no_visits(self):
        """R9.2: Mascota sin citas muestra 'Sin visitas registradas'"""
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('mascotas:detalle', kwargs={'pk': self.mascota.pk}))
        self.assertContains(resp, 'Sin visitas registradas')

    def test_last_visit_ignores_cancelled(self):
        """R9.3: Citas Canceladas son ignoradas — muestra 'Sin visitas registradas'"""
        from agenda.models import Cita
        Cita.objects.create(
            mascota=self.mascota, disponibilidad=self.disp,
            estado='Cancelada', motivo_cancelacion='No asistió',
        )
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('mascotas:detalle', kwargs={'pk': self.mascota.pk}))
        self.assertContains(resp, 'Sin visitas registradas')

    def test_last_visit_ignores_programada(self):
        """R9.4: Citas Programadas son ignoradas para última visita"""
        from agenda.models import Cita
        Cita.objects.create(
            mascota=self.mascota, disponibilidad=self.disp,
            estado='Programada',
        )
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('mascotas:detalle', kwargs={'pk': self.mascota.pk}))
        self.assertContains(resp, 'Sin visitas registradas')

    def test_last_visit_shows_most_recent(self):
        """R9.5: Múltiples Citas Atendidas muestran la más reciente"""
        from agenda.models import Disponibilidad, Cita
        from datetime import timedelta
        # Crear una disponibilidad más antigua
        old_date = date.today() - timedelta(days=30)
        disp_old = Disponibilidad.objects.create(
            fecha=old_date, hora_inicio='09:00', hora_fin='10:00',
            veterinario=self.vet_user,
        )
        Cita.objects.create(
            mascota=self.mascota, disponibilidad=disp_old,
            estado='Atendida',
        )
        # El self.disp existente es hoy (más reciente)
        Cita.objects.create(
            mascota=self.mascota, disponibilidad=self.disp,
            estado='Atendida',
        )
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('mascotas:detalle', kwargs={'pk': self.mascota.pk}))
        # Debe mostrar fecha de hoy (más reciente), no hace 30 días
        self.assertContains(resp, str(date.today().year))


# ========================================
# FASE 5: Tests de Integración y Pulido
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
        """Nombre de mascota en lista linkea a vista de detalle"""
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('mascotas:lista'))
        detail_url = reverse('mascotas:detalle', kwargs={'pk': self.mascota.pk})
        self.assertContains(resp, detail_url)


class MascotaAdminEnhancementTest(TestCase):
    """REQ-01/04: Admin updates for alergias, esterilizado, cedula"""

    def test_cedula_in_admin_list_display(self):
        """Cédula aparece en list_display del admin de Usuario"""
        from usuarios.admin import UsuarioAdmin
        self.assertIn('cedula', UsuarioAdmin.list_display)

    def test_cedula_in_admin_search(self):
        """Cédula aparece en search_fields del admin de Usuario"""
        from usuarios.admin import UsuarioAdmin
        self.assertIn('cedula', UsuarioAdmin.search_fields)

    def test_alergias_in_mascota_admin(self):
        """Alergias y esterilizado en admin de Mascota"""
        from mascotas.admin import MascotaAdmin
        self.assertIn('alergias', MascotaAdmin.list_display)
        self.assertIn('esterilizado', MascotaAdmin.list_filter)


# ========================================
# CLIENTE ROLE: Phase 1 — Dashboard + CRUD Mascotas
# ========================================


class ClienteMascotaCRUDTest(TestCase):
    """Test that Cliente can create, list, edit, and view their own mascotas."""

    def setUp(self):
        User = get_user_model()
        self.cliente_rol = Rol.objects.get(nombre='Cliente')
        self.vet_rol = Rol.objects.get(nombre='Veterinario')
        self.cliente = User.objects.create_user(
            username='cli_masc', email='cli_masc@test.com',
            password='testpass123', rol=self.cliente_rol,
            first_name='Carlos',
        )
        self.other_cliente = User.objects.create_user(
            username='cli_masc2', email='cli_masc2@test.com',
            password='testpass123', rol=self.cliente_rol,
            first_name='Maria',
        )

    def test_cliente_can_access_crear_mascota(self):
        """Cliente debe poder hacer GET a crear_mascota."""
        self.client.force_login(self.cliente)
        response = self.client.get(reverse('mascotas:nuevo'))
        self.assertEqual(response.status_code, 200)

    def test_cliente_can_create_mascota(self):
        """Cliente puede hacer POST para crear mascota — propietario forzado a request.user."""
        from mascotas.models import Mascota
        self.client.force_login(self.cliente)
        response = self.client.post(reverse('mascotas:nuevo'), data={
            'nombre': 'Firulais',
            'especie': 'Canino',
            'raza': 'Bulldog',
            'sexo': 'Macho',
        })
        self.assertEqual(response.status_code, 302)
        mascota = Mascota.objects.get(nombre='Firulais')
        self.assertEqual(mascota.propietario, self.cliente)

    def test_cliente_create_mascota_forces_propietario(self):
        """Incluso si un Cliente malicioso intenta setear propietario, debe ser forzado a request.user."""
        from mascotas.models import Mascota
        self.client.force_login(self.cliente)
        response = self.client.post(reverse('mascotas:nuevo'), data={
            'nombre': 'Boby',
            'especie': 'Canino',
            'sexo': 'Hembra',
            # Note: propietario is excluded from the form (exclude=['propietario'])
            # so this can't be forged via the form anyway
        })
        self.assertEqual(response.status_code, 302)
        mascota = Mascota.objects.get(nombre='Boby')
        self.assertEqual(mascota.propietario, self.cliente)

    def test_cliente_sees_only_own_mascotas(self):
        """Lista de Cliente muestra solo sus propias mascotas."""
        from mascotas.models import Mascota
        Mascota.objects.create(nombre='Rex', especie='Canino', sexo='Macho', propietario=self.cliente)
        Mascota.objects.create(nombre='Luna', especie='Felino', sexo='Hembra', propietario=self.other_cliente)
        self.client.force_login(self.cliente)
        response = self.client.get(reverse('mascotas:lista'))
        self.assertEqual(response.status_code, 200)
        mascotas = response.context['mascotas']
        self.assertEqual(mascotas.paginator.count, 1)
        self.assertEqual(mascotas[0].nombre, 'Rex')

    def test_cliente_can_edit_own_mascota(self):
        """Cliente puede editar su propia mascota."""
        from mascotas.models import Mascota
        mascota = Mascota.objects.create(
            nombre='Rex', especie='Canino', sexo='Macho',
            propietario=self.cliente, raza='Pastor',
        )
        self.client.force_login(self.cliente)
        response = self.client.post(reverse('mascotas:editar', kwargs={'pk': mascota.pk}), data={
            'nombre': 'Rex Updated',
            'especie': 'Canino',
            'sexo': 'Macho',
            'raza': 'Pastor Alemán',
        })
        self.assertEqual(response.status_code, 302)
        mascota.refresh_from_db()
        self.assertEqual(mascota.nombre, 'Rex Updated')

    def test_cliente_cannot_edit_other_mascota(self):
        """Cliente recibe 403 al intentar editar mascota de otro cliente."""
        from mascotas.models import Mascota
        mascota = Mascota.objects.create(
            nombre='Luna', especie='Felino', sexo='Hembra',
            propietario=self.other_cliente,
        )
        self.client.force_login(self.cliente)
        response = self.client.get(reverse('mascotas:editar', kwargs={'pk': mascota.pk}))
        self.assertEqual(response.status_code, 403)

    def test_cliente_cannot_delete_mascota(self):
        """Cliente NO debe poder eliminar una mascota (solo Vet/Admin)."""
        from mascotas.models import Mascota
        mascota = Mascota.objects.create(
            nombre='Rex', especie='Canino', sexo='Macho',
            propietario=self.cliente,
        )
        self.client.force_login(self.cliente)
        response = self.client.get(reverse('mascotas:eliminar', kwargs={'pk': mascota.pk}))
        self.assertIn(response.status_code, [403, 302])

    def test_cliente_redirect_after_login(self):
        """Después del login, Cliente debe ser redirigido a mascotas:lista."""
        from usuarios.views import get_redirect_url
        url = get_redirect_url(self.cliente)
        self.assertEqual(url, reverse('mascotas:lista'))
