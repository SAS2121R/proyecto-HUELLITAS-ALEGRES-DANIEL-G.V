from django.test import TestCase
from django.urls import reverse
from django.conf import settings
from django.core.exceptions import ValidationError
from datetime import date, time, datetime

from usuarios.models import Rol, Usuario


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
