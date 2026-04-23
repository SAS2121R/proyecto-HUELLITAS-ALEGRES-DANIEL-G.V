from django.test import TestCase
from django.urls import reverse, resolve
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import ProtectedError
from django.contrib import admin
from datetime import date, time, datetime

from usuarios.models import Rol, Usuario
from mascotas.models import Mascota
from .models import Cita, Disponibilidad


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
# PHASE 1: App Scaffold + Model + Migration + URL Config
# ========================================

class AppRegistrationTest(TestCase):
    """REQ-10: App is registered in INSTALLED_APPS"""

    def test_agenda_in_installed_apps(self):
        """R10.1: 'agenda' is in INSTALLED_APPS"""
        self.assertIn('agenda', settings.INSTALLED_APPS)


class DisponibilidadModelTest(TestCase):
    """REQ-01: Disponibilidad model — 5 scenarios"""

    def setUp(self):
        self.vet = create_user_with_role('Veterinario', username='vet_model', email='vet_model@test.com')

    def test_creacion_basica(self):
        """R1.1: Create Disponibilidad with all fields, assert persistence"""
        from agenda.models import Disponibilidad
        d = Disponibilidad.objects.create(
            veterinario=self.vet,
            fecha=date(2026, 5, 1),
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
            activa=True,
        )
        self.assertEqual(d.veterinario, self.vet)
        self.assertEqual(d.fecha, date(2026, 5, 1))
        self.assertEqual(d.hora_inicio, time(8, 0))
        self.assertEqual(d.hora_fin, time(10, 0))
        self.assertTrue(d.activa)
        self.assertIsNotNone(d.pk)

    def test_str_format(self):
        """R1.2: __str__ returns 'vet — date start-end'"""
        from agenda.models import Disponibilidad
        d = Disponibilidad.objects.create(
            veterinario=self.vet,
            fecha=date(2026, 4, 22),
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
        )
        expected = f"{self.vet} — 2026-04-22 08:00-10:00"
        self.assertEqual(str(d), expected)

    def test_activa_default_true(self):
        """R1.5: activa defaults to True"""
        from agenda.models import Disponibilidad
        d = Disponibilidad(
            veterinario=self.vet,
            fecha=date(2026, 5, 1),
            hora_inicio=time(9, 0),
            hora_fin=time(11, 0),
        )
        self.assertTrue(d.activa)

    def test_limit_choices_to_veterinario(self):
        """R1.3: FK has limit_choices_to for Veterinario role"""
        from agenda.models import Disponibilidad
        field = Disponibilidad._meta.get_field('veterinario')
        self.assertEqual(field.remote_field.limit_choices_to, {'rol__nombre': 'Veterinario'})

    def test_meta_ordering(self):
        """R1.4: Results ordered by fecha, hora_inicio"""
        from agenda.models import Disponibilidad
        Disponibilidad.objects.create(
            veterinario=self.vet,
            fecha=date(2026, 5, 2),
            hora_inicio=time(10, 0),
            hora_fin=time(12, 0),
        )
        Disponibilidad.objects.create(
            veterinario=self.vet,
            fecha=date(2026, 5, 1),
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
        )
        Disponibilidad.objects.create(
            veterinario=self.vet,
            fecha=date(2026, 5, 1),
            hora_inicio=time(14, 0),
            hora_fin=time(16, 0),
        )
        results = list(Disponibilidad.objects.all())
        self.assertEqual(results[0].fecha, date(2026, 5, 1))
        self.assertEqual(results[0].hora_inicio, time(8, 0))
        self.assertEqual(results[1].hora_inicio, time(14, 0))
        self.assertEqual(results[2].fecha, date(2026, 5, 2))


class URLConfigurationTest(TestCase):
    """REQ-09: All URL patterns resolve under agenda: namespace"""

    def test_url_patterns_resolve(self):
        """R9.1: All 4 URL names reverse correctly"""
        url_lista = reverse('agenda:lista_disponibilidad')
        self.assertEqual(url_lista, '/agenda/disponibilidades/')

        url_crear = reverse('agenda:crear_disponibilidad')
        self.assertEqual(url_crear, '/agenda/disponibilidades/nuevo/')

        url_editar = reverse('agenda:editar_disponibilidad', kwargs={'pk': 5})
        self.assertEqual(url_editar, '/agenda/disponibilidades/editar/5/')

        url_eliminar = reverse('agenda:eliminar_disponibilidad', kwargs={'pk': 5})
        self.assertEqual(url_eliminar, '/agenda/disponibilidades/eliminar/5/')


# ========================================
# PHASE 2: Model Validation — Overlap + Date/Time
# ========================================

class OverlapValidationTest(TestCase):
    """REQ-02: Overlap validation in clean() — 5 scenarios"""

    def setUp(self):
        self.vet = create_user_with_role('Veterinario', username='vet_overlap', email='vet_overlap@test.com')
        self.vet2 = create_user_with_role('Veterinario', username='vet_overlap2', email='vet_overlap2@test.com')

    def test_mismo_veterinario_rechaza(self):
        """R2.1: Overlapping same vet same date raises ValidationError"""
        from agenda.models import Disponibilidad
        Disponibilidad.objects.create(
            veterinario=self.vet,
            fecha=date(2026, 5, 1),
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
        )
        overlapping = Disponibilidad(
            veterinario=self.vet,
            fecha=date(2026, 5, 1),
            hora_inicio=time(9, 0),
            hora_fin=time(11, 0),
        )
        with self.assertRaises(ValidationError):
            overlapping.full_clean()

    def test_borde_adyacente_permite(self):
        """R2.2: Boundary-touching (08-10, 10-12) passes"""
        from agenda.models import Disponibilidad
        Disponibilidad.objects.create(
            veterinario=self.vet,
            fecha=date(2026, 5, 1),
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
        )
        adjacent = Disponibilidad(
            veterinario=self.vet,
            fecha=date(2026, 5, 1),
            hora_inicio=time(10, 0),
            hora_fin=time(12, 0),
        )
        # Should NOT raise
        adjacent.full_clean()

    def test_identicos_rechaza(self):
        """R2.3: Identical block raises ValidationError"""
        from agenda.models import Disponibilidad
        Disponibilidad.objects.create(
            veterinario=self.vet,
            fecha=date(2026, 5, 1),
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
        )
        identical = Disponibilidad(
            veterinario=self.vet,
            fecha=date(2026, 5, 1),
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
        )
        with self.assertRaises(ValidationError):
            identical.full_clean()

    def test_diferente_veterinario_permite(self):
        """R2.4: Same time different vet passes"""
        from agenda.models import Disponibilidad
        Disponibilidad.objects.create(
            veterinario=self.vet,
            fecha=date(2026, 5, 1),
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
        )
        different_vet = Disponibilidad(
            veterinario=self.vet2,
            fecha=date(2026, 5, 1),
            hora_inicio=time(9, 0),
            hora_fin=time(11, 0),
        )
        # Should NOT raise
        different_vet.full_clean()

    def test_exclusion_self_update(self):
        """R2.5: Editing self without changes passes"""
        from agenda.models import Disponibilidad
        d = Disponibilidad.objects.create(
            veterinario=self.vet,
            fecha=date(2026, 5, 1),
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
        )
        # Editing self — should NOT raise false positive
        d.full_clean()


class DateTimeValidationTest(TestCase):
    """REQ-03: Date/Time validation in clean() — 2 scenarios"""

    def setUp(self):
        self.vet = create_user_with_role('Veterinario', username='vet_dt', email='vet_dt@test.com')

    def test_hora_inicio_mayor_rechaza(self):
        """R3.1: hora_inicio >= hora_fin raises ValidationError"""
        from agenda.models import Disponibilidad
        d = Disponibilidad(
            veterinario=self.vet,
            fecha=date(2026, 5, 1),
            hora_inicio=time(10, 0),
            hora_fin=time(8, 0),
        )
        with self.assertRaises(ValidationError):
            d.full_clean()

    def test_fecha_pasada_rechaza(self):
        """R3.2: Past date raises ValidationError"""
        from agenda.models import Disponibilidad
        d = Disponibilidad(
            veterinario=self.vet,
            fecha=date(2020, 1, 1),
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
        )
        with self.assertRaises(ValidationError):
            d.full_clean()


# ========================================
# PHASE 3: Form Layer Tests (REQ-04)
# ========================================

class DisponibilidadFormTest(TestCase):
    """REQ-04: DisponibilidadForm — 4 scenarios"""

    def setUp(self):
        self.vet = create_user_with_role('Veterinario', username='vet_form', email='vet_form@test.com')
        self.vet2 = create_user_with_role('Veterinario', username='vet_form2', email='vet_form2@test.com')

    def test_guardado_valido(self):
        """R4.1: Valid form data creates Disponibilidad successfully"""
        from agenda.forms import DisponibilidadForm
        from agenda.models import Disponibilidad
        form = DisponibilidadForm(data={
            'fecha': '2026-06-01',
            'hora_inicio': '09:00',
            'hora_fin': '11:00',
            'activa': True,
        })
        # Set veterinario on instance (excluded from form, set in view layer)
        form.instance.veterinario = self.vet
        self.assertTrue(form.is_valid(), form.errors)
        count_before = Disponibilidad.objects.count()
        instance = form.save()
        self.assertEqual(Disponibilidad.objects.count(), count_before + 1)
        self.assertEqual(instance.veterinario, self.vet)
        self.assertEqual(instance.fecha, date(2026, 6, 1))
        self.assertEqual(instance.hora_inicio, time(9, 0))
        self.assertEqual(instance.hora_fin, time(11, 0))
        self.assertTrue(instance.activa)

    def test_excluye_veterinario(self):
        """R4.2: Form Meta excludes veterinario field"""
        from agenda.forms import DisponibilidadForm
        form = DisponibilidadForm()
        self.assertNotIn('veterinario', form.fields)

    def test_widgets_html5(self):
        """R4.3: fecha uses DateInput type=date, hora uses TimeInput type=time"""
        from agenda.forms import DisponibilidadForm
        form = DisponibilidadForm()
        self.assertEqual(form.fields['fecha'].widget.input_type, 'date')
        self.assertEqual(form.fields['hora_inicio'].widget.input_type, 'time')
        self.assertEqual(form.fields['hora_fin'].widget.input_type, 'time')

    def test_hereda_validacion_modelo(self):
        """R4.4: Form inherits model clean() validation (overlap, past date, invalid times)"""
        from agenda.forms import DisponibilidadForm
        # Create an existing block
        from agenda.models import Disponibilidad
        Disponibilidad.objects.create(
            veterinario=self.vet,
            fecha=date(2026, 6, 1),
            hora_inicio=time(9, 0),
            hora_fin=time(11, 0),
        )
        # Test overlap validation
        form = DisponibilidadForm(data={
            'fecha': '2026-06-01',
            'hora_inicio': '10:00',
            'hora_fin': '12:00',
            'activa': True,
        })
        form.instance.veterinario = self.vet
        self.assertFalse(form.is_valid())
        self.assertIn('hora_inicio', form.errors)

        # Test past date validation
        form2 = DisponibilidadForm(data={
            'fecha': '2020-01-01',
            'hora_inicio': '09:00',
            'hora_fin': '11:00',
            'activa': True,
        })
        form2.instance.veterinario = self.vet
        self.assertFalse(form2.is_valid())
        self.assertIn('fecha', form2.errors)

        # Test hora_inicio >= hora_fin validation
        form3 = DisponibilidadForm(data={
            'fecha': '2026-06-01',
            'hora_inicio': '14:00',
            'hora_fin': '10:00',
            'activa': True,
        })
        form3.instance.veterinario = self.vet
        self.assertFalse(form3.is_valid())
        self.assertIn('hora_fin', form3.errors)


# ========================================
# PHASE 4: List View Tests (REQ-05)
# ========================================

class DisponibilidadListViewTest(TestCase):
    """REQ-05: List view with role-based filtering — 4 scenarios"""

    def setUp(self):
        from django.test import Client
        from agenda.models import Disponibilidad
        self.client = Client()
        self.vet_rol = Rol.objects.get(nombre='Veterinario')
        self.admin_rol = Rol.objects.get(nombre='Administrador')
        self.cliente_rol = Rol.objects.get(nombre='Cliente')
        self.vet_user = Usuario.objects.create_user(
            username='vet_list', email='vet_list@test.com',
            password='pass123', rol=self.vet_rol,
        )
        self.vet2_user = Usuario.objects.create_user(
            username='vet_list2', email='vet_list2@test.com',
            password='pass123', rol=self.vet_rol,
        )
        self.admin_user = Usuario.objects.create_user(
            username='admin_list', email='admin_list@test.com',
            password='pass123', rol=self.admin_rol,
        )
        self.cliente_user = Usuario.objects.create_user(
            username='cliente_list', email='cliente_list@test.com',
            password='pass123', rol=self.cliente_rol,
        )
        # Vet 1 owns 3 slots
        Disponibilidad.objects.create(
            veterinario=self.vet_user, fecha=date(2026, 6, 1),
            hora_inicio=time(8, 0), hora_fin=time(10, 0),
        )
        Disponibilidad.objects.create(
            veterinario=self.vet_user, fecha=date(2026, 6, 2),
            hora_inicio=time(10, 0), hora_fin=time(12, 0),
        )
        Disponibilidad.objects.create(
            veterinario=self.vet_user, fecha=date(2026, 6, 3),
            hora_inicio=time(14, 0), hora_fin=time(16, 0),
        )
        # Vet 2 owns 2 slots
        Disponibilidad.objects.create(
            veterinario=self.vet2_user, fecha=date(2026, 6, 1),
            hora_inicio=time(9, 0), hora_fin=time(11, 0),
        )
        Disponibilidad.objects.create(
            veterinario=self.vet2_user, fecha=date(2026, 6, 2),
            hora_inicio=time(13, 0), hora_fin=time(15, 0),
        )

    def test_veterinario_ve_solo_sus_disponibilidades(self):
        """R5.1: Veterinario sees only own disponibilidades"""
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('agenda:lista_disponibilidad'))
        self.assertEqual(resp.status_code, 200)
        content = resp.content.decode()
        # Should see own slots (3 slots from vet_user)
        self.assertIn('08:00', content)  # vet's own slot 1
        self.assertIn('10:00', content)  # vet's own slot 2
        self.assertIn('14:00', content)  # vet's own slot 3
        # Should NOT see vet2's exclusive time slots (09:00 and 13:00)
        self.assertNotIn('09:00', content)  # vet2's slot on 2026-06-01
        self.assertNotIn('13:00', content)  # vet2's slot on 2026-06-02

    def test_admin_ve_todas(self):
        """R5.2: Administrador sees all disponibilidades"""
        self.client.force_login(self.admin_user)
        resp = self.client.get(reverse('agenda:lista_disponibilidad'))
        self.assertEqual(resp.status_code, 200)
        content = resp.content.decode()
        # Should see both vets' slots
        self.assertIn('08:00', content)  # vet1
        self.assertIn('09:00', content)  # vet2
        self.assertIn('14:00', content)  # vet1
        self.assertIn('13:00', content)  # vet2

    def test_cliente_recibe_403(self):
        """R5.3: Cliente gets HTTP 403 Forbidden"""
        self.client.force_login(self.cliente_user)
        resp = self.client.get(reverse('agenda:lista_disponibilidad'))
        self.assertEqual(resp.status_code, 403)

    def test_no_autenticado_redirige(self):
        """R5.4: Unauthenticated user gets 302 redirect to login"""
        resp = self.client.get(reverse('agenda:lista_disponibilidad'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/usuarios/login/', resp.url)


# ========================================
# PHASE 5: Create View Tests (REQ-06)
# ========================================

class DisponibilidadCreateViewTest(TestCase):
    """REQ-06: Create view with role-based vet assignment — 5 scenarios"""

    def setUp(self):
        from django.test import Client
        self.client = Client()
        self.vet_rol = Rol.objects.get(nombre='Veterinario')
        self.admin_rol = Rol.objects.get(nombre='Administrador')
        self.cliente_rol = Rol.objects.get(nombre='Cliente')
        self.vet_user = Usuario.objects.create_user(
            username='vet_create', email='vet_create@test.com',
            password='pass123', rol=self.vet_rol,
        )
        self.admin_user = Usuario.objects.create_user(
            username='admin_create', email='admin_create@test.com',
            password='pass123', rol=self.admin_rol,
        )
        self.cliente_user = Usuario.objects.create_user(
            username='cliente_create', email='cliente_create@test.com',
            password='pass123', rol=self.cliente_rol,
        )

    def test_veterinario_crea_propia(self):
        """R6.1: Veterinario creates disponibilidad with vet=request.user, redirects to lista"""
        self.client.force_login(self.vet_user)
        resp = self.client.post(reverse('agenda:crear_disponibilidad'), {
            'fecha': '2026-06-01',
            'hora_inicio': '09:00',
            'hora_fin': '11:00',
            'activa': True,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse('agenda:lista_disponibilidad'))
        from agenda.models import Disponibilidad
        self.assertEqual(Disponibilidad.objects.count(), 1)
        d = Disponibilidad.objects.first()
        self.assertEqual(d.veterinario, self.vet_user)
        self.assertEqual(d.fecha, date(2026, 6, 1))
        self.assertEqual(d.hora_inicio, time(9, 0))
        self.assertEqual(d.hora_fin, time(11, 0))

    def test_admin_crea_cualquiera(self):
        """R6.2: Administrador can access create view and create disponibilidad"""
        self.client.force_login(self.admin_user)
        resp = self.client.post(reverse('agenda:crear_disponibilidad'), {
            'fecha': '2026-06-01',
            'hora_inicio': '09:00',
            'hora_fin': '11:00',
            'activa': True,
        })
        self.assertEqual(resp.status_code, 302)
        from agenda.models import Disponibilidad
        self.assertEqual(Disponibilidad.objects.count(), 1)

    def test_cliente_recibe_403(self):
        """R6.3: Cliente gets 403 Forbidden on GET and POST"""
        self.client.force_login(self.cliente_user)
        resp = self.client.get(reverse('agenda:crear_disponibilidad'))
        self.assertEqual(resp.status_code, 403)
        resp = self.client.post(reverse('agenda:crear_disponibilidad'), {})
        self.assertEqual(resp.status_code, 403)

    def test_no_autenticado_redirige(self):
        """R6.4: Unauthenticated user redirected to login"""
        resp = self.client.get(reverse('agenda:crear_disponibilidad'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/usuarios/login/', resp.url)

    def test_formulario_con_errores(self):
        """R6.5: Invalid data (past date) re-renders form with errors"""
        self.client.force_login(self.vet_user)
        resp = self.client.post(reverse('agenda:crear_disponibilidad'), {
            'fecha': '2020-01-01',
            'hora_inicio': '09:00',
            'hora_fin': '11:00',
            'activa': True,
        })
        self.assertEqual(resp.status_code, 200)
        self.assertIn('fecha', resp.context['form'].errors)


# ========================================
# PHASE 6: Edit View Tests (REQ-07)
# ========================================

class DisponibilidadEditViewTest(TestCase):
    """REQ-07: Edit view with object-level permissions — 5 scenarios"""

    def setUp(self):
        from django.test import Client
        from agenda.models import Disponibilidad
        self.client = Client()
        self.vet_rol = Rol.objects.get(nombre='Veterinario')
        self.admin_rol = Rol.objects.get(nombre='Administrador')
        self.cliente_rol = Rol.objects.get(nombre='Cliente')
        self.vet_user = Usuario.objects.create_user(
            username='vet_edit', email='vet_edit@test.com',
            password='pass123', rol=self.vet_rol,
        )
        self.vet2_user = Usuario.objects.create_user(
            username='vet_edit2', email='vet_edit2@test.com',
            password='pass123', rol=self.vet_rol,
        )
        self.admin_user = Usuario.objects.create_user(
            username='admin_edit', email='admin_edit@test.com',
            password='pass123', rol=self.admin_rol,
        )
        self.cliente_user = Usuario.objects.create_user(
            username='cliente_edit', email='cliente_edit@test.com',
            password='pass123', rol=self.cliente_rol,
        )
        # Vet 1 owns this disponibilidad
        self.disp = Disponibilidad.objects.create(
            veterinario=self.vet_user, fecha=date(2026, 6, 1),
            hora_inicio=time(9, 0), hora_fin=time(11, 0),
        )
        # Vet 2 owns this disponibilidad
        self.disp2 = Disponibilidad.objects.create(
            veterinario=self.vet2_user, fecha=date(2026, 6, 2),
            hora_inicio=time(10, 0), hora_fin=time(12, 0),
        )

    def test_veterinario_edita_propia(self):
        """R7.1: Veterinario edits own disponibilidad, data updated, redirects"""
        self.client.force_login(self.vet_user)
        resp = self.client.post(reverse('agenda:editar_disponibilidad', kwargs={'pk': self.disp.pk}), {
            'fecha': '2026-06-15',
            'hora_inicio': '09:00',
            'hora_fin': '12:00',
            'activa': True,
        })
        self.assertEqual(resp.status_code, 302)
        self.disp.refresh_from_db()
        self.assertEqual(self.disp.fecha, date(2026, 6, 15))
        self.assertEqual(self.disp.hora_fin, time(12, 0))

    def test_admin_edita_cualquiera(self):
        """R7.2: Administrador edits any disponibilidad, data updated"""
        self.client.force_login(self.admin_user)
        resp = self.client.post(reverse('agenda:editar_disponibilidad', kwargs={'pk': self.disp2.pk}), {
            'fecha': '2026-07-01',
            'hora_inicio': '08:00',
            'hora_fin': '10:00',
            'activa': True,
        })
        self.assertEqual(resp.status_code, 302)
        self.disp2.refresh_from_db()
        self.assertEqual(self.disp2.fecha, date(2026, 7, 1))

    def test_veterinario_cruzado_403(self):
        """R7.3: Veterinario cannot edit another vet's disponibilidad — 403"""
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('agenda:editar_disponibilidad', kwargs={'pk': self.disp2.pk}))
        self.assertEqual(resp.status_code, 403)
        # Also POST
        resp = self.client.post(reverse('agenda:editar_disponibilidad', kwargs={'pk': self.disp2.pk}), {
            'fecha': '2026-07-01',
            'hora_inicio': '08:00',
            'hora_fin': '10:00',
            'activa': True,
        })
        self.assertEqual(resp.status_code, 403)

    def test_cliente_recibe_403(self):
        """R7.4: Cliente gets 403 Forbidden"""
        self.client.force_login(self.cliente_user)
        resp = self.client.get(reverse('agenda:editar_disponibilidad', kwargs={'pk': self.disp.pk}))
        self.assertEqual(resp.status_code, 403)

    def test_no_autenticado_redirige(self):
        """R7.5: Unauthenticated redirected to login"""
        resp = self.client.get(reverse('agenda:editar_disponibilidad', kwargs={'pk': self.disp.pk}))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/usuarios/login/', resp.url)


# ========================================
# PHASE 7: Delete View Tests (REQ-08)
# ========================================

class DisponibilidadDeleteViewTest(TestCase):
    """REQ-08: Delete view with confirmation and role-based permissions — 6 scenarios"""

    def setUp(self):
        from django.test import Client
        from agenda.models import Disponibilidad
        self.client = Client()
        self.vet_rol = Rol.objects.get(nombre='Veterinario')
        self.admin_rol = Rol.objects.get(nombre='Administrador')
        self.cliente_rol = Rol.objects.get(nombre='Cliente')
        self.vet_user = Usuario.objects.create_user(
            username='vet_delete', email='vet_delete@test.com',
            password='pass123', rol=self.vet_rol,
        )
        self.vet2_user = Usuario.objects.create_user(
            username='vet_delete2', email='vet_delete2@test.com',
            password='pass123', rol=self.vet_rol,
        )
        self.admin_user = Usuario.objects.create_user(
            username='admin_delete', email='admin_delete@test.com',
            password='pass123', rol=self.admin_rol,
        )
        self.cliente_user = Usuario.objects.create_user(
            username='cliente_delete', email='cliente_delete@test.com',
            password='pass123', rol=self.cliente_rol,
        )
        # Vet 1 owns this disponibilidad
        self.disp = Disponibilidad.objects.create(
            veterinario=self.vet_user, fecha=date(2026, 6, 1),
            hora_inicio=time(9, 0), hora_fin=time(11, 0),
        )
        # Vet 2 owns this disponibilidad
        self.disp2 = Disponibilidad.objects.create(
            veterinario=self.vet2_user, fecha=date(2026, 6, 2),
            hora_inicio=time(10, 0), hora_fin=time(12, 0),
        )

    def test_veterinario_elimina_propia_get(self):
        """R8.1 GET: Veterinario sees delete confirmation page (200)"""
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('agenda:eliminar_disponibilidad', kwargs={'pk': self.disp.pk}))
        self.assertEqual(resp.status_code, 200)

    def test_veterinario_elimina_propia_post(self):
        """R8.1 POST: Veterinario deletes own disponibilidad, object deleted, redirects"""
        self.client.force_login(self.vet_user)
        pk = self.disp.pk
        resp = self.client.post(reverse('agenda:eliminar_disponibilidad', kwargs={'pk': pk}))
        self.assertEqual(resp.status_code, 302)
        from agenda.models import Disponibilidad
        self.assertFalse(Disponibilidad.objects.filter(pk=pk).exists())

    def test_admin_elimina_cualquiera(self):
        """R8.2: Administrador deletes any disponibilidad"""
        self.client.force_login(self.admin_user)
        pk = self.disp2.pk
        resp = self.client.post(reverse('agenda:eliminar_disponibilidad', kwargs={'pk': pk}))
        self.assertEqual(resp.status_code, 302)
        from agenda.models import Disponibilidad
        self.assertFalse(Disponibilidad.objects.filter(pk=pk).exists())

    def test_veterinario_cruzado_403(self):
        """R8.3: Veterinario cannot delete another vet's disponibilidad — 403"""
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('agenda:eliminar_disponibilidad', kwargs={'pk': self.disp2.pk}))
        self.assertEqual(resp.status_code, 403)
        # Also POST
        resp = self.client.post(reverse('agenda:eliminar_disponibilidad', kwargs={'pk': self.disp2.pk}))
        self.assertEqual(resp.status_code, 403)

    def test_cliente_recibe_403(self):
        """R8.4: Cliente gets 403 Forbidden"""
        self.client.force_login(self.cliente_user)
        resp = self.client.get(reverse('agenda:eliminar_disponibilidad', kwargs={'pk': self.disp.pk}))
        self.assertEqual(resp.status_code, 403)

    def test_no_autenticado_redirige(self):
        """R8.5: Unauthenticated redirected to login"""
        resp = self.client.get(reverse('agenda:eliminar_disponibilidad', kwargs={'pk': self.disp.pk}))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/usuarios/login/', resp.url)


# ========================================
# CITAS FASE B — Block 1: Model + Validations + esta_ocupada + URLs + Admin
# ========================================

class CitaModelTest(TestCase):
    """REQ-01: Cita model structure — 8 scenarios"""

    def setUp(self):
        self.rol_vet = Rol.objects.get_or_create(nombre='Veterinario')[0]
        self.rol_admin = Rol.objects.get_or_create(nombre='Administrador')[0]
        self.rol_cliente = Rol.objects.get_or_create(nombre='Cliente')[0]
        self.vet = Usuario.objects.create_user(
            username='vet_cita', email='vet_cita@test.com',
            password='testpass123', rol=self.rol_vet,
        )
        self.cliente = Usuario.objects.create_user(
            username='cliente_cita', email='cliente_cita@test.com',
            password='testpass123', rol=self.rol_cliente,
        )
        self.mascota = Mascota.objects.create(
            nombre='Firulais', especie='Canino', sexo='Macho',
            propietario=self.cliente,
        )
        self.disp = Disponibilidad.objects.create(
            veterinario=self.vet, fecha=date(2026, 5, 1),
            hora_inicio=time(9, 0), hora_fin=time(10, 0),
        )

    def test_creacion_basica(self):
        """R1.1: Create Cita with mascota, disponibilidad, estado='Programada'"""
        cita = Cita.objects.create(
            mascota=self.mascota, disponibilidad=self.disp,
        )
        self.assertEqual(cita.mascota, self.mascota)
        self.assertEqual(cita.disponibilidad, self.disp)
        self.assertEqual(cita.estado, 'Programada')
        self.assertIsNotNone(cita.pk)

    def test_str_format(self):
        """R1.2: __str__ returns 'Cita: {mascota} — {disponibilidad} [Programada]'"""
        cita = Cita.objects.create(
            mascota=self.mascota, disponibilidad=self.disp,
        )
        expected = f"Cita: {self.mascota} — {self.disp} [Programada]"
        self.assertEqual(str(cita), expected)

    def test_estado_default_programada(self):
        """R1.3: Default estado is 'Programada'"""
        cita = Cita(mascota=self.mascota, disponibilidad=self.disp)
        self.assertEqual(cita.estado, 'Programada')

    def test_motivo_cancelacion_default_empty(self):
        """R1.4: Default motivo_cancelacion is ''"""
        cita = Cita(mascota=self.mascota, disponibilidad=self.disp)
        self.assertEqual(cita.motivo_cancelacion, '')

    def test_protect_on_mascota_delete(self):
        """R1.5: Deleting Mascota linked to Cita raises ProtectedError"""
        Cita.objects.create(mascota=self.mascota, disponibilidad=self.disp)
        with self.assertRaises(ProtectedError):
            self.mascota.delete()

    def test_protect_on_disponibilidad_delete(self):
        """R1.6: Deleting Disponibilidad linked to Cita raises ProtectedError"""
        Cita.objects.create(mascota=self.mascota, disponibilidad=self.disp)
        with self.assertRaises(ProtectedError):
            self.disp.delete()

    def test_veterinario_property(self):
        """R1.7: cita.veterinario returns cita.disponibilidad.veterinario"""
        cita = Cita.objects.create(mascota=self.mascota, disponibilidad=self.disp)
        self.assertEqual(cita.veterinario, self.vet)

    def test_meta_ordering(self):
        """R1.8: Citas ordered by disponibilidad__fecha, disponibilidad__hora_inicio"""
        disp2 = Disponibilidad.objects.create(
            veterinario=self.vet, fecha=date(2026, 5, 2),
            hora_inicio=time(10, 0), hora_fin=time(11, 0),
        )
        Cita.objects.create(mascota=self.mascota, disponibilidad=disp2)
        Cita.objects.create(mascota=self.mascota, disponibilidad=self.disp)
        results = list(Cita.objects.all())
        self.assertEqual(results[0].disponibilidad.fecha, date(2026, 5, 1))
        self.assertEqual(results[1].disponibilidad.fecha, date(2026, 5, 2))


class DoubleBookingTest(TestCase):
    """REQ-02: Double-booking prevention — 5 scenarios"""

    def setUp(self):
        self.rol_vet = Rol.objects.get_or_create(nombre='Veterinario')[0]
        self.rol_cliente = Rol.objects.get_or_create(nombre='Cliente')[0]
        self.vet = Usuario.objects.create_user(
            username='vet_db', email='vet_db@test.com',
            password='testpass123', rol=self.rol_vet,
        )
        self.cliente = Usuario.objects.create_user(
            username='cliente_db', email='cliente_db@test.com',
            password='testpass123', rol=self.rol_cliente,
        )
        self.mascota = Mascota.objects.create(
            nombre='Firulais', especie='Canino', sexo='Macho',
            propietario=self.cliente,
        )
        self.disp = Disponibilidad.objects.create(
            veterinario=self.vet, fecha=date(2026, 5, 1),
            hora_inicio=time(9, 0), hora_fin=time(10, 0),
        )

    def test_programada_over_programada_blocked(self):
        """R2.1: Programada over Programada raises ValidationError"""
        Cita.objects.create(mascota=self.mascota, disponibilidad=self.disp, estado='Programada')
        cita2 = Cita(
            mascota=self.mascota, disponibilidad=self.disp, estado='Programada',
        )
        with self.assertRaises(ValidationError):
            cita2.full_clean()

    def test_programada_over_atendida_blocked(self):
        """R2.2: Programada over Atendida raises ValidationError"""
        c1 = Cita.objects.create(mascota=self.mascota, disponibilidad=self.disp, estado='Programada')
        Cita.objects.filter(pk=c1.pk).update(estado='Atendida')
        cita2 = Cita(
            mascota=self.mascota, disponibilidad=self.disp, estado='Programada',
        )
        with self.assertRaises(ValidationError):
            cita2.full_clean()

    def test_new_cita_over_cancelada_allowed(self):
        """R2.3: New Programada over Cancelada is allowed (Auto-Libre)"""
        Cita.objects.create(mascota=self.mascota, disponibilidad=self.disp, estado='Cancelada', motivo_cancelacion='Test')
        cita2 = Cita(mascota=self.mascota, disponibilidad=self.disp, estado='Programada')
        cita2.full_clean()  # Should NOT raise
        cita2.save()
        self.assertEqual(Cita.objects.filter(disponibilidad=self.disp).count(), 2)

    def test_multiple_canceladas_allowed(self):
        """R2.4: Multiple Canceladas on same Disponibilidad allowed (historical)"""
        c1 = Cita.objects.create(
            mascota=self.mascota, disponibilidad=self.disp,
            estado='Cancelada', motivo_cancelacion='Reason 1',
        )
        c2 = Cita(
            mascota=self.mascota, disponibilidad=self.disp,
            estado='Cancelada', motivo_cancelacion='Reason 2',
        )
        c2.full_clean()  # Should NOT raise
        c2.save()
        self.assertEqual(Cita.objects.filter(disponibilidad=self.disp, estado='Cancelada').count(), 2)

    def test_self_exclusion_on_edit(self):
        """R2.5: Editing same Cita without changing disponibilidad — no ValidationError"""
        cita = Cita.objects.create(mascota=self.mascota, disponibilidad=self.disp, estado='Programada')
        # Fetch from DB to ensure pk is set, then modify estado and re-validate
        cita = Cita.objects.get(pk=cita.pk)
        cita.estado = 'Atendida'
        cita.motivo_cancelacion = ''  # not required for Atendida
        # This MUST NOT raise — the existing cita on this disponibilidad is ITSELF
        cita.full_clean()


class StateTransitionTest(TestCase):
    """REQ-03: State transitions — 6 scenarios"""

    def setUp(self):
        self.rol_vet = Rol.objects.get_or_create(nombre='Veterinario')[0]
        self.rol_cliente = Rol.objects.get_or_create(nombre='Cliente')[0]
        self.vet = Usuario.objects.create_user(
            username='vet_st', email='vet_st@test.com',
            password='testpass123', rol=self.rol_vet,
        )
        self.cliente = Usuario.objects.create_user(
            username='cliente_st', email='cliente_st@test.com',
            password='testpass123', rol=self.rol_cliente,
        )
        self.mascota = Mascota.objects.create(
            nombre='Firulais', especie='Canino', sexo='Macho',
            propietario=self.cliente,
        )
        self.disp = Disponibilidad.objects.create(
            veterinario=self.vet, fecha=date(2026, 5, 1),
            hora_inicio=time(9, 0), hora_fin=time(10, 0),
        )

    def test_programada_to_atendida(self):
        """R3.1: Programada → Atendida is valid"""
        cita = Cita.objects.create(mascota=self.mascota, disponibilidad=self.disp, estado='Programada')
        cita.estado = 'Atendida'
        cita.full_clean()  # Should NOT raise

    def test_programada_to_cancelada_with_motivo(self):
        """R3.2: Programada → Cancelada with motivo is valid"""
        cita = Cita.objects.create(mascota=self.mascota, disponibilidad=self.disp, estado='Programada')
        cita.estado = 'Cancelada'
        cita.motivo_cancelacion = 'Urgencia familiar'
        cita.full_clean()  # Should NOT raise

    def test_atendida_to_programada_blocked(self):
        """R3.3: Atendida → Programada raises ValidationError (terminal state)"""
        c1 = Cita.objects.create(mascota=self.mascota, disponibilidad=self.disp, estado='Programada')
        Cita.objects.filter(pk=c1.pk).update(estado='Atendida')
        cita = Cita.objects.get(pk=c1.pk)
        cita.estado = 'Programada'
        with self.assertRaises(ValidationError):
            cita.full_clean()

    def test_atendida_to_cancelada_blocked(self):
        """R3.4: Atendida → Cancelada raises ValidationError (terminal state)"""
        c1 = Cita.objects.create(mascota=self.mascota, disponibilidad=self.disp, estado='Programada')
        Cita.objects.filter(pk=c1.pk).update(estado='Atendida')
        cita = Cita.objects.get(pk=c1.pk)
        cita.estado = 'Cancelada'
        cita.motivo_cancelacion = 'Test'
        with self.assertRaises(ValidationError):
            cita.full_clean()

    def test_cancelada_to_programada_blocked(self):
        """R3.5: Cancelada → Programada raises ValidationError (no reactivation)"""
        c1 = Cita.objects.create(
            mascota=self.mascota, disponibilidad=self.disp,
            estado='Cancelada', motivo_cancelacion='Test',
        )
        cita = Cita.objects.get(pk=c1.pk)
        cita.estado = 'Programada'
        with self.assertRaises(ValidationError):
            cita.full_clean()

    def test_cancelada_to_atendida_blocked(self):
        """R3.6: Cancelada → Atendida raises ValidationError (no reactivation)"""
        c1 = Cita.objects.create(
            mascota=self.mascota, disponibilidad=self.disp,
            estado='Cancelada', motivo_cancelacion='Test',
        )
        cita = Cita.objects.get(pk=c1.pk)
        cita.estado = 'Atendida'
        with self.assertRaises(ValidationError):
            cita.full_clean()


class MotivoCancelacionTest(TestCase):
    """REQ-04: Motivo cancelación validation — 3 scenarios"""

    def setUp(self):
        self.rol_vet = Rol.objects.get_or_create(nombre='Veterinario')[0]
        self.rol_cliente = Rol.objects.get_or_create(nombre='Cliente')[0]
        self.vet = Usuario.objects.create_user(
            username='vet_mc', email='vet_mc@test.com',
            password='testpass123', rol=self.rol_vet,
        )
        self.cliente = Usuario.objects.create_user(
            username='cliente_mc', email='cliente_mc@test.com',
            password='testpass123', rol=self.rol_cliente,
        )
        self.mascota = Mascota.objects.create(
            nombre='Firulais', especie='Canino', sexo='Macho',
            propietario=self.cliente,
        )
        self.disp = Disponibilidad.objects.create(
            veterinario=self.vet, fecha=date(2026, 5, 1),
            hora_inicio=time(9, 0), hora_fin=time(10, 0),
        )

    def test_cancel_without_motivo_raises_error(self):
        """R4.1: Cancel without motivo_cancelacion raises ValidationError"""
        cita = Cita(mascota=self.mascota, disponibilidad=self.disp, estado='Cancelada')
        with self.assertRaises(ValidationError):
            cita.full_clean()

    def test_cancel_with_motivo_valid(self):
        """R4.2: Cancel with motivo is valid"""
        cita = Cita(
            mascota=self.mascota, disponibilidad=self.disp,
            estado='Cancelada', motivo_cancelacion='Urgencia familiar',
        )
        cita.full_clean()  # Should NOT raise

    def test_programada_with_empty_motivo_valid(self):
        """R4.3: Programada with empty motivo is valid"""
        cita = Cita(
            mascota=self.mascota, disponibilidad=self.disp,
            estado='Programada', motivo_cancelacion='',
        )
        cita.full_clean()  # Should NOT raise


class EstaOcupadaTest(TestCase):
    """REQ-05: Disponibilidad.esta_ocupada property — 4 scenarios"""

    def setUp(self):
        self.rol_vet = Rol.objects.get_or_create(nombre='Veterinario')[0]
        self.rol_cliente = Rol.objects.get_or_create(nombre='Cliente')[0]
        self.vet = Usuario.objects.create_user(
            username='vet_eo', email='vet_eo@test.com',
            password='testpass123', rol=self.rol_vet,
        )
        self.cliente = Usuario.objects.create_user(
            username='cliente_eo', email='cliente_eo@test.com',
            password='testpass123', rol=self.rol_cliente,
        )
        self.mascota = Mascota.objects.create(
            nombre='Firulais', especie='Canino', sexo='Macho',
            propietario=self.cliente,
        )
        self.disp = Disponibilidad.objects.create(
            veterinario=self.vet, fecha=date(2026, 5, 1),
            hora_inicio=time(9, 0), hora_fin=time(10, 0),
        )

    def test_true_with_programada(self):
        """R5.1: Disponibilidad with Cita(Programada) → esta_ocupada=True"""
        Cita.objects.create(mascota=self.mascota, disponibilidad=self.disp, estado='Programada')
        self.assertTrue(self.disp.esta_ocupada)

    def test_true_with_atendida(self):
        """R5.2: Disponibilidad with Cita(Atendida) → esta_ocupada=True"""
        c1 = Cita.objects.create(mascota=self.mascota, disponibilidad=self.disp, estado='Programada')
        Cita.objects.filter(pk=c1.pk).update(estado='Atendida')
        self.disp.refresh_from_db()
        self.assertTrue(self.disp.esta_ocupada)

    def test_false_with_only_canceladas(self):
        """R5.3: Disponibilidad with only Cancelada Citas → esta_ocupada=False"""
        Cita.objects.create(
            mascota=self.mascota, disponibilidad=self.disp,
            estado='Cancelada', motivo_cancelacion='Test',
        )
        self.disp.refresh_from_db()
        self.assertFalse(self.disp.esta_ocupada)

    def test_false_with_no_citas(self):
        """R5.4: Disponibilidad with no Citas → esta_ocupada=False"""
        self.assertFalse(self.disp.esta_ocupada)


class CitaURLTest(TestCase):
    """REQ-11: URL configuration — 1 scenario"""

    def test_url_patterns_resolve(self):
        """R11.1: All 4 cita URL patterns resolve correctly under agenda: namespace"""
        url_lista = reverse('agenda:lista_citas')
        self.assertEqual(url_lista, '/agenda/citas/')

        url_crear = reverse('agenda:crear_cita')
        self.assertEqual(url_crear, '/agenda/citas/nueva/')

        url_editar = reverse('agenda:editar_cita', kwargs={'pk': 5})
        self.assertEqual(url_editar, '/agenda/citas/editar/5/')

        url_eliminar = reverse('agenda:eliminar_cita', kwargs={'pk': 5})
        self.assertEqual(url_eliminar, '/agenda/citas/eliminar/5')


class CitaAdminTest(TestCase):
    """REQ-12: Admin registration — 1 scenario"""

    def test_cita_admin_registered(self):
        """R12.1: Cita model is in admin.site._registry"""
        self.assertIn(Cita, admin.site._registry)


class ColoredEstadoTest(TestCase):
    """REQ-13: Colored estado in admin — 2 scenarios"""

    def setUp(self):
        self.rol_vet = Rol.objects.get_or_create(nombre='Veterinario')[0]
        self.rol_cliente = Rol.objects.get_or_create(nombre='Cliente')[0]
        self.vet = Usuario.objects.create_user(
            username='vet_ce', email='vet_ce@test.com',
            password='testpass123', rol=self.rol_vet,
        )
        self.cliente = Usuario.objects.create_user(
            username='cliente_ce', email='cliente_ce@test.com',
            password='testpass123', rol=self.rol_cliente,
        )
        self.mascota = Mascota.objects.create(
            nombre='Firulais', especie='Canino', sexo='Macho',
            propietario=self.cliente,
        )
        self.disp = Disponibilidad.objects.create(
            veterinario=self.vet, fecha=date(2026, 5, 1),
            hora_inicio=time(9, 0), hora_fin=time(10, 0),
        )

    def test_colored_estado_returns_html(self):
        """R13.1: CitaAdmin.colored_estado returns format_html with colored badges"""
        from agenda.admin import CitaAdmin
        admin_instance = CitaAdmin(Cita, admin.site)

        cita_prog = Cita.objects.create(mascota=self.mascota, disponibilidad=self.disp, estado='Programada')
        html = admin_instance.colored_estado(cita_prog)
        self.assertIn('orange', str(html))
        self.assertIn('Programada', str(html))

        c1 = Cita.objects.create(
            mascota=self.mascota, disponibilidad=self.disp,
            estado='Cancelada', motivo_cancelacion='Test',
        )
        Cita.objects.filter(pk=c1.pk).update(estado='Atendida')
        cita_atendida = Cita.objects.get(pk=c1.pk)
        html = admin_instance.colored_estado(cita_atendida)
        self.assertIn('green', str(html))
        self.assertIn('Atendida', str(html))

        c2 = Cita.objects.create(
            mascota=self.mascota, disponibilidad=self.disp,
            estado='Cancelada', motivo_cancelacion='Test 2',
        )
        html = admin_instance.colored_estado(c2)
        self.assertIn('red', str(html))
        self.assertIn('Cancelada', str(html))

    def test_colored_estado_admin_order_field(self):
        """R13.2: colored_estado has admin_order_field = 'estado'"""
        from agenda.admin import CitaAdmin
        admin_instance = CitaAdmin(Cita, admin.site)
        self.assertEqual(admin_instance.colored_estado.admin_order_field, 'estado')


# ========================================
# CITAS FASE B — Block 2: CitaForm (REQ-06)
# ========================================

class CitaFormTest(TestCase):
    """REQ-06: CitaForm — 6 scenarios"""

    def setUp(self):
        self.rol_vet = Rol.objects.get_or_create(nombre='Veterinario')[0]
        self.rol_cliente = Rol.objects.get_or_create(nombre='Cliente')[0]
        self.vet = Usuario.objects.create_user(
            username='vet_form_cita', email='vet_form_cita@test.com',
            password='testpass123', rol=self.rol_vet,
        )
        self.cliente = Usuario.objects.create_user(
            username='cliente_form_cita', email='cliente_form_cita@test.com',
            password='testpass123', rol=self.rol_cliente,
        )
        self.mascota = Mascota.objects.create(
            nombre='Firulais', especie='Canino', sexo='Macho',
            propietario=self.cliente,
        )
        self.disp = Disponibilidad.objects.create(
            veterinario=self.vet, fecha=date(2026, 5, 1),
            hora_inicio=time(9, 0), hora_fin=time(10, 0),
        )

    def test_valid_form_creates_cita(self):
        """R6.1: Valid form data with mascota and disponibilidad creates Cita successfully"""
        from agenda.forms import CitaForm
        form = CitaForm(data={
            'mascota': self.mascota.pk,
            'disponibilidad': self.disp.pk,
        })
        self.assertTrue(form.is_valid(), form.errors)
        count_before = Cita.objects.count()
        cita = form.save()
        self.assertEqual(Cita.objects.count(), count_before + 1)
        self.assertEqual(cita.mascota, self.mascota)
        self.assertEqual(cita.disponibilidad, self.disp)
        self.assertEqual(cita.estado, 'Programada')

    def test_excludes_estado_on_creation(self):
        """R6.2: Form for creation excludes estado field"""
        from agenda.forms import CitaForm
        form = CitaForm()
        self.assertNotIn('estado', form.fields)

    def test_shows_estado_on_edit(self):
        """R6.3: Form for edit includes estado field"""
        from agenda.forms import CitaForm
        cita = Cita.objects.create(mascota=self.mascota, disponibilidad=self.disp)
        form = CitaForm(instance=cita)
        self.assertIn('estado', form.fields)

    def test_motivo_cancelacion_field_visible(self):
        """R6.4: Form includes motivo_cancelacion field (always visible)"""
        from agenda.forms import CitaForm
        # On creation
        form_create = CitaForm()
        self.assertIn('motivo_cancelacion', form_create.fields)
        # On edit
        cita = Cita.objects.create(mascota=self.mascota, disponibilidad=self.disp)
        form_edit = CitaForm(instance=cita)
        self.assertIn('motivo_cancelacion', form_edit.fields)
        # Not required by default (model handles requirement on cancel)
        self.assertFalse(form_create.fields['motivo_cancelacion'].required)

    def test_disponibilidad_queryset_filters_available(self):
        """R6.5: disponibilidad queryset only includes active & unoccupied slots"""
        from agenda.forms import CitaForm
        # disp1: active, no cita → available
        disp1 = Disponibilidad.objects.create(
            veterinario=self.vet, fecha=date(2026, 5, 2),
            hora_inicio=time(10, 0), hora_fin=time(11, 0), activa=True,
        )
        # disp2: active, has Cita(Programada) → occupied
        disp2 = Disponibilidad.objects.create(
            veterinario=self.vet, fecha=date(2026, 5, 3),
            hora_inicio=time(11, 0), hora_fin=time(12, 0), activa=True,
        )
        Cita.objects.create(mascota=self.mascota, disponibilidad=disp2, estado='Programada')
        # disp3: inactive → not available
        disp3 = Disponibilidad.objects.create(
            veterinario=self.vet, fecha=date(2026, 5, 4),
            hora_inicio=time(13, 0), hora_fin=time(14, 0), activa=False,
        )

        form = CitaForm()
        qs_pks = list(form.fields['disponibilidad'].queryset.values_list('pk', flat=True))
        # Should include self.disp (active, no cita) and disp1 (active, no cita)
        self.assertIn(self.disp.pk, qs_pks)
        self.assertIn(disp1.pk, qs_pks)
        # Should NOT include disp2 (occupied) or disp3 (inactive)
        self.assertNotIn(disp2.pk, qs_pks)
        self.assertNotIn(disp3.pk, qs_pks)

        # When editing a Cita, its own disponibilidad should still be in queryset
        cita = Cita.objects.create(mascota=self.mascota, disponibilidad=disp2)
        form_edit = CitaForm(instance=cita)
        qs_pks_edit = list(form_edit.fields['disponibilidad'].queryset.values_list('pk', flat=True))
        self.assertIn(disp2.pk, qs_pks_edit)  # current disp included even if occupied

    def test_inherits_model_validation(self):
        """R6.6: Form with invalid data triggers model clean() errors in form.errors"""
        from agenda.forms import CitaForm
        # Test 1: Overlapping data triggers form error
        Cita.objects.create(mascota=self.mascota, disponibilidad=self.disp, estado='Programada')
        form_overlap = CitaForm(data={
            'mascota': self.mascota.pk,
            'disponibilidad': self.disp.pk,
        })
        self.assertFalse(form_overlap.is_valid())
        self.assertIn('disponibilidad', form_overlap.errors)

        # Test 2: Blocked state transition triggers form error
        cita = Cita.objects.create(
            mascota=self.mascota, disponibilidad=self.disp,
            estado='Cancelada', motivo_cancelacion='Test cancel',
        )
        form_transition = CitaForm(
            data={
                'mascota': self.mascota.pk,
                'disponibilidad': self.disp.pk,
                'estado': 'Programada',
                'motivo_cancelacion': '',
            },
            instance=cita,
        )
        self.assertFalse(form_transition.is_valid())
        self.assertIn('estado', form_transition.errors)

        # Test 3: Cancel without motivo triggers form error
        cita2 = Cita.objects.create(mascota=self.mascota, disponibilidad=self.disp)
        form_cancel = CitaForm(
            data={
                'mascota': self.mascota.pk,
                'disponibilidad': self.disp.pk,
                'estado': 'Cancelada',
                'motivo_cancelacion': '',
            },
            instance=cita2,
        )
        self.assertFalse(form_cancel.is_valid())
        self.assertIn('motivo_cancelacion', form_cancel.errors)


# ========================================
# CITAS FASE B — Block 3: List + Create Views (REQ-07, REQ-08)
# ========================================

class CitaListViewTest(TestCase):
    """REQ-07: List view permissions — 4 scenarios"""

    def setUp(self):
        from django.test import Client
        self.client = Client()
        self.rol_vet = Rol.objects.get_or_create(nombre='Veterinario')[0]
        self.rol_admin = Rol.objects.get_or_create(nombre='Administrador')[0]
        self.rol_cliente = Rol.objects.get_or_create(nombre='Cliente')[0]
        self.vet = Usuario.objects.create_user(
            username='vet_cl', email='vet_cl@test.com',
            password='testpass123', rol=self.rol_vet,
        )
        self.vet2 = Usuario.objects.create_user(
            username='vet_cl2', email='vet_cl2@test.com',
            password='testpass123', rol=self.rol_vet,
        )
        self.admin = Usuario.objects.create_user(
            username='admin_cl', email='admin_cl@test.com',
            password='testpass123', rol=self.rol_admin,
        )
        self.cliente = Usuario.objects.create_user(
            username='cliente_cl', email='cliente_cl@test.com',
            password='testpass123', rol=self.rol_cliente,
        )
        self.cliente2 = Usuario.objects.create_user(
            username='cliente_cl2', email='cliente_cl2@test.com',
            password='testpass123', rol=self.rol_cliente,
        )
        # Mascotas
        self.mascota1 = Mascota.objects.create(
            nombre='Rex', especie='Canino', sexo='Macho',
            propietario=self.cliente,
        )
        self.mascota2 = Mascota.objects.create(
            nombre='Mishi', especie='Felino', sexo='Hembra',
            propietario=self.cliente,
        )
        self.mascota3 = Mascota.objects.create(
            nombre='Loro', especie='Ave', sexo='Macho',
            propietario=self.cliente2,
        )
        # Disponibilidades
        self.disp1 = Disponibilidad.objects.create(
            veterinario=self.vet, fecha=date(2026, 5, 1),
            hora_inicio=time(9, 0), hora_fin=time(10, 0),
        )
        self.disp2 = Disponibilidad.objects.create(
            veterinario=self.vet, fecha=date(2026, 5, 2),
            hora_inicio=time(10, 0), hora_fin=time(11, 0),
        )
        self.disp3 = Disponibilidad.objects.create(
            veterinario=self.vet2, fecha=date(2026, 5, 3),
            hora_inicio=time(14, 0), hora_fin=time(15, 0),
        )
        # Citas: vet has 2 citas, vet2 has 1, cliente has 2 pets with citas
        self.cita_vet1 = Cita.objects.create(
            mascota=self.mascota1, disponibilidad=self.disp1, estado='Programada',
        )
        self.cita_vet2 = Cita.objects.create(
            mascota=self.mascota2, disponibilidad=self.disp2, estado='Programada',
        )
        self.cita_vet2_other = Cita.objects.create(
            mascota=self.mascota3, disponibilidad=self.disp3, estado='Programada',
        )

    def test_veterinario_ve_solo_sus_citas(self):
        """R7.1: Veterinario sees only citas where disponibilidad.veterinario == request.user"""
        self.client.force_login(self.vet)
        resp = self.client.get(reverse('agenda:lista_citas'))
        self.assertEqual(resp.status_code, 200)
        content = resp.content.decode()
        # Should see own citas (09:00 and 10:00)
        self.assertIn('09:00', content)
        self.assertIn('10:00', content)
        # Should NOT see vet2's exclusive time slot (14:00)
        self.assertNotIn('14:00', content)

    def test_admin_ve_todas(self):
        """R7.2: Administrador sees all citas"""
        self.client.force_login(self.admin)
        resp = self.client.get(reverse('agenda:lista_citas'))
        self.assertEqual(resp.status_code, 200)
        content = resp.content.decode()
        # Should see all time slots
        self.assertIn('09:00', content)
        self.assertIn('10:00', content)
        self.assertIn('14:00', content)

    def test_cliente_ve_citas_de_sus_mascotas(self):
        """R7.3: Cliente sees only citas where mascota.propietario == request.user"""
        self.client.force_login(self.cliente)
        resp = self.client.get(reverse('agenda:lista_citas'))
        self.assertEqual(resp.status_code, 200)
        content = resp.content.decode()
        # Should see own pets' citas (Rex at 09:00, Mishi at 10:00)
        self.assertIn('Rex', content)
        self.assertIn('Mishi', content)
        # Should NOT see other client's pet (Loro at 14:00)
        self.assertNotIn('Loro', content)

    def test_no_autenticado_redirige(self):
        """R7.4: Unauthenticated user gets 302 redirect to login"""
        resp = self.client.get(reverse('agenda:lista_citas'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/usuarios/login/', resp.url)


class CitaCreateViewTest(TestCase):
    """REQ-08: Create view permissions — 5 scenarios"""

    def setUp(self):
        from django.test import Client
        self.client = Client()
        self.rol_vet = Rol.objects.get_or_create(nombre='Veterinario')[0]
        self.rol_admin = Rol.objects.get_or_create(nombre='Administrador')[0]
        self.rol_cliente = Rol.objects.get_or_create(nombre='Cliente')[0]
        self.vet = Usuario.objects.create_user(
            username='vet_cr', email='vet_cr@test.com',
            password='testpass123', rol=self.rol_vet,
        )
        self.admin = Usuario.objects.create_user(
            username='admin_cr', email='admin_cr@test.com',
            password='testpass123', rol=self.rol_admin,
        )
        self.cliente = Usuario.objects.create_user(
            username='cliente_cr', email='cliente_cr@test.com',
            password='testpass123', rol=self.rol_cliente,
        )
        self.cliente_user = Usuario.objects.create_user(
            username='cliente_owner', email='cliente_owner@test.com',
            password='testpass123', rol=self.rol_cliente,
        )
        self.mascota = Mascota.objects.create(
            nombre='Rex', especie='Canino', sexo='Macho',
            propietario=self.cliente_user,
        )
        self.disp1 = Disponibilidad.objects.create(
            veterinario=self.vet, fecha=date(2026, 5, 1),
            hora_inicio=time(9, 0), hora_fin=time(10, 0),
        )
        self.disp2 = Disponibilidad.objects.create(
            veterinario=self.vet, fecha=date(2026, 5, 2),
            hora_inicio=time(10, 0), hora_fin=time(11, 0),
        )

    def test_veterinario_crea_cita(self):
        """R8.1: Veterinario POSTs valid data, Cita created, redirect to lista_citas"""
        self.client.force_login(self.vet)
        resp = self.client.post(reverse('agenda:crear_cita'), {
            'mascota': self.mascota.pk,
            'disponibilidad': self.disp1.pk,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse('agenda:lista_citas'))
        self.assertEqual(Cita.objects.count(), 1)
        cita = Cita.objects.first()
        self.assertEqual(cita.mascota, self.mascota)
        self.assertEqual(cita.disponibilidad, self.disp1)
        self.assertEqual(cita.estado, 'Programada')

    def test_admin_crea_cita(self):
        """R8.2: Administrador POSTs valid data, Cita created successfully"""
        self.client.force_login(self.admin)
        resp = self.client.post(reverse('agenda:crear_cita'), {
            'mascota': self.mascota.pk,
            'disponibilidad': self.disp1.pk,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Cita.objects.count(), 1)
        cita = Cita.objects.first()
        self.assertEqual(cita.mascota, self.mascota)
        self.assertEqual(cita.disponibilidad, self.disp1)

    def test_cliente_recibe_403(self):
        """R8.3: Cliente gets 403 on GET and POST"""
        self.client.force_login(self.cliente)
        resp = self.client.get(reverse('agenda:crear_cita'))
        self.assertEqual(resp.status_code, 403)
        resp = self.client.post(reverse('agenda:crear_cita'), {})
        self.assertEqual(resp.status_code, 403)

    def test_no_autenticado_redirige(self):
        """R8.4: Unauthenticated user gets 302 redirect to login"""
        resp = self.client.get(reverse('agenda:crear_cita'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/usuarios/login/', resp.url)

    def test_formulario_con_errores(self):
        """R8.5: POST with occupied disponibilidad re-renders form with errors"""
        # First, occupy disp2 with a Cita
        other_mascota = Mascota.objects.create(
            nombre='Mishi', especie='Felino', sexo='Hembra',
            propietario=self.cliente_user,
        )
        Cita.objects.create(mascota=other_mascota, disponibilidad=self.disp2, estado='Programada')
        # Now try to create another Cita for the same disp2
        self.client.force_login(self.vet)
        resp = self.client.post(reverse('agenda:crear_cita'), {
            'mascota': self.mascota.pk,
            'disponibilidad': self.disp2.pk,
        })
        # Should re-render form (200) with errors
        self.assertEqual(resp.status_code, 200)
        self.assertIn('form', resp.context)
        self.assertTrue(resp.context['form'].errors)
        # No new Cita should be created (only the original one)
        self.assertEqual(Cita.objects.count(), 1)


# ========================================
# CITAS FASE B — Block 4: Edit + Cancel Views (REQ-09, REQ-10)
# ========================================

class CitaEditViewTest(TestCase):
    """REQ-09: Edit view permissions and validation — 8 scenarios"""

    def setUp(self):
        from django.test import Client
        self.client = Client()
        self.rol_vet = Rol.objects.get_or_create(nombre='Veterinario')[0]
        self.rol_admin = Rol.objects.get_or_create(nombre='Administrador')[0]
        self.rol_cliente = Rol.objects.get_or_create(nombre='Cliente')[0]
        self.vet1 = Usuario.objects.create_user(
            username='vet1_ev', email='vet1_ev@test.com',
            password='testpass123', rol=self.rol_vet,
        )
        self.vet2 = Usuario.objects.create_user(
            username='vet2_ev', email='vet2_ev@test.com',
            password='testpass123', rol=self.rol_vet,
        )
        self.admin = Usuario.objects.create_user(
            username='admin_ev', email='admin_ev@test.com',
            password='testpass123', rol=self.rol_admin,
        )
        self.cliente = Usuario.objects.create_user(
            username='cliente_ev', email='cliente_ev@test.com',
            password='testpass123', rol=self.rol_cliente,
        )
        self.mascota = Mascota.objects.create(
            nombre='Rex', especie='Canino', sexo='Macho',
            propietario=self.cliente,
        )
        self.disp1 = Disponibilidad.objects.create(
            veterinario=self.vet1, fecha=date(2026, 5, 1),
            hora_inicio=time(9, 0), hora_fin=time(10, 0),
        )
        self.disp2 = Disponibilidad.objects.create(
            veterinario=self.vet2, fecha=date(2026, 5, 2),
            hora_inicio=time(10, 0), hora_fin=time(11, 0),
        )
        self.cita = Cita.objects.create(
            mascota=self.mascota, disponibilidad=self.disp1, estado='Programada',
        )

    def test_veterinario_edita_propia(self):
        """R9.1: Veterinario edits own cita (via disponibilidad__veterinario), changes estado to Atendida, redirects to lista_citas"""
        self.client.force_login(self.vet1)
        resp = self.client.post(reverse('agenda:editar_cita', kwargs={'pk': self.cita.pk}), {
            'mascota': self.mascota.pk,
            'disponibilidad': self.disp1.pk,
            'estado': 'Atendida',
            'motivo_cancelacion': '',
        })
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse('agenda:lista_citas'))
        self.cita.refresh_from_db()
        self.assertEqual(self.cita.estado, 'Atendida')

    def test_admin_edita_cualquiera(self):
        """R9.2: Administrador edits any cita successfully"""
        self.client.force_login(self.admin)
        resp = self.client.post(reverse('agenda:editar_cita', kwargs={'pk': self.cita.pk}), {
            'mascota': self.mascota.pk,
            'disponibilidad': self.disp1.pk,
            'estado': 'Atendida',
            'motivo_cancelacion': '',
        })
        self.assertEqual(resp.status_code, 302)
        self.cita.refresh_from_db()
        self.assertEqual(self.cita.estado, 'Atendida')

    def test_veterinario_cruzado_403(self):
        """R9.3: Veterinario tries to edit another vet's cita, gets 403 PermissionDenied"""
        self.client.force_login(self.vet2)
        resp = self.client.get(reverse('agenda:editar_cita', kwargs={'pk': self.cita.pk}))
        self.assertEqual(resp.status_code, 403)
        # Also POST
        resp = self.client.post(reverse('agenda:editar_cita', kwargs={'pk': self.cita.pk}), {
            'mascota': self.mascota.pk,
            'disponibilidad': self.disp1.pk,
            'estado': 'Atendida',
            'motivo_cancelacion': '',
        })
        self.assertEqual(resp.status_code, 403)

    def test_cliente_recibe_403(self):
        """R9.4: Cliente gets 403 on editar_cita"""
        self.client.force_login(self.cliente)
        resp = self.client.get(reverse('agenda:editar_cita', kwargs={'pk': self.cita.pk}))
        self.assertEqual(resp.status_code, 403)
        resp = self.client.post(reverse('agenda:editar_cita', kwargs={'pk': self.cita.pk}), {})
        self.assertEqual(resp.status_code, 403)

    def test_no_autenticado_redirige(self):
        """R9.5: Unauthenticated gets 302 redirect to login"""
        resp = self.client.get(reverse('agenda:editar_cita', kwargs={'pk': self.cita.pk}))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/usuarios/login/', resp.url)

    def test_cancel_sin_motivo_muestra_error(self):
        """R9.6: POST with estado='Cancelada' and empty motivo_cancelacion, form shows error"""
        self.client.force_login(self.vet1)
        resp = self.client.post(reverse('agenda:editar_cita', kwargs={'pk': self.cita.pk}), {
            'mascota': self.mascota.pk,
            'disponibilidad': self.disp1.pk,
            'estado': 'Cancelada',
            'motivo_cancelacion': '',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertIn('form', resp.context)
        self.assertIn('motivo_cancelacion', resp.context['form'].errors)

    def test_bloquear_transicion_desde_atendida(self):
        """R9.7: Attempt to change estado from Atendida to Programada, form/model shows error"""
        # Bypass clean() to set estado='Atendida'
        Cita.objects.filter(pk=self.cita.pk).update(estado='Atendida')
        self.cita.refresh_from_db()
        self.client.force_login(self.vet1)
        resp = self.client.post(reverse('agenda:editar_cita', kwargs={'pk': self.cita.pk}), {
            'mascota': self.mascota.pk,
            'disponibilidad': self.disp1.pk,
            'estado': 'Programada',
            'motivo_cancelacion': '',
        })
        # Should redirect with error message (edit blocked for terminal states)
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse('agenda:lista_citas'))

    def test_bloquear_transicion_desde_cancelada(self):
        """R9.8: Attempt to change estado from Cancelada to Programada, form/model shows error"""
        Cita.objects.filter(pk=self.cita.pk).update(estado='Cancelada', motivo_cancelacion='Test')
        self.cita.refresh_from_db()
        self.client.force_login(self.vet1)
        resp = self.client.post(reverse('agenda:editar_cita', kwargs={'pk': self.cita.pk}), {
            'mascota': self.mascota.pk,
            'disponibilidad': self.disp1.pk,
            'estado': 'Programada',
            'motivo_cancelacion': '',
        })
        # Should redirect with error message (edit blocked for terminal states)
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse('agenda:lista_citas'))


class CitaCancelViewTest(TestCase):
    """REQ-10: Delete (Cancel) view — soft cancel with motivo — 6 scenarios"""

    def setUp(self):
        from django.test import Client
        self.client = Client()
        self.rol_vet = Rol.objects.get_or_create(nombre='Veterinario')[0]
        self.rol_admin = Rol.objects.get_or_create(nombre='Administrador')[0]
        self.rol_cliente = Rol.objects.get_or_create(nombre='Cliente')[0]
        self.vet1 = Usuario.objects.create_user(
            username='vet1_cv', email='vet1_cv@test.com',
            password='testpass123', rol=self.rol_vet,
        )
        self.vet2 = Usuario.objects.create_user(
            username='vet2_cv', email='vet2_cv@test.com',
            password='testpass123', rol=self.rol_vet,
        )
        self.admin = Usuario.objects.create_user(
            username='admin_cv', email='admin_cv@test.com',
            password='testpass123', rol=self.rol_admin,
        )
        self.cliente = Usuario.objects.create_user(
            username='cliente_cv', email='cliente_cv@test.com',
            password='testpass123', rol=self.rol_cliente,
        )
        self.mascota = Mascota.objects.create(
            nombre='Rex', especie='Canino', sexo='Macho',
            propietario=self.cliente,
        )
        self.disp1 = Disponibilidad.objects.create(
            veterinario=self.vet1, fecha=date(2026, 5, 1),
            hora_inicio=time(9, 0), hora_fin=time(10, 0),
        )
        self.disp2 = Disponibilidad.objects.create(
            veterinario=self.vet2, fecha=date(2026, 5, 2),
            hora_inicio=time(10, 0), hora_fin=time(11, 0),
        )
        self.cita = Cita.objects.create(
            mascota=self.mascota, disponibilidad=self.disp1, estado='Programada',
        )

    def test_veterinario_cancela_propia_get(self):
        """R10.1: Vet GETs cancel page for own cita, sees confirmation form with motivo_cancelacion field (status 200)"""
        self.client.force_login(self.vet1)
        resp = self.client.get(reverse('agenda:eliminar_cita', kwargs={'pk': self.cita.pk}))
        self.assertEqual(resp.status_code, 200)
        content = resp.content.decode()
        self.assertIn('motivo_cancelacion', content)
        self.assertIn('Rex', content)

    def test_veterinario_cancela_propia_post(self):
        """R10.2: Vet POSTs cancel with motivo_cancelacion, cita.estado becomes 'Cancelada', redirect to lista"""
        self.client.force_login(self.vet1)
        resp = self.client.post(reverse('agenda:eliminar_cita', kwargs={'pk': self.cita.pk}), {
            'motivo_cancelacion': 'El cliente no pudo asistir',
        })
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse('agenda:lista_citas'))
        self.cita.refresh_from_db()
        self.assertEqual(self.cita.estado, 'Cancelada')
        self.assertEqual(self.cita.motivo_cancelacion, 'El cliente no pudo asistir')

    def test_admin_cancela_cualquiera(self):
        """R10.3: Admin can cancel any cita"""
        self.client.force_login(self.admin)
        resp = self.client.post(reverse('agenda:eliminar_cita', kwargs={'pk': self.cita.pk}), {
            'motivo_cancelacion': 'Cancelada por admin',
        })
        self.assertEqual(resp.status_code, 302)
        self.cita.refresh_from_db()
        self.assertEqual(self.cita.estado, 'Cancelada')

    def test_veterinario_cruzado_403(self):
        """R10.4: Vet tries to cancel another vet's cita, gets 403"""
        self.client.force_login(self.vet2)
        resp = self.client.get(reverse('agenda:eliminar_cita', kwargs={'pk': self.cita.pk}))
        self.assertEqual(resp.status_code, 403)
        # Also POST
        resp = self.client.post(reverse('agenda:eliminar_cita', kwargs={'pk': self.cita.pk}), {
            'motivo_cancelacion': 'Test',
        })
        self.assertEqual(resp.status_code, 403)

    def test_cliente_recibe_403(self):
        """R10.5: Cliente gets 403 on eliminar_cita"""
        self.client.force_login(self.cliente)
        resp = self.client.get(reverse('agenda:eliminar_cita', kwargs={'pk': self.cita.pk}))
        self.assertEqual(resp.status_code, 403)
        resp = self.client.post(reverse('agenda:eliminar_cita', kwargs={'pk': self.cita.pk}), {})
        self.assertEqual(resp.status_code, 403)

    def test_no_autenticado_redirige(self):
        """R10.6: Unauthenticated gets 302 redirect to login"""
        resp = self.client.get(reverse('agenda:eliminar_cita', kwargs={'pk': self.cita.pk}))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/usuarios/login/', resp.url)
