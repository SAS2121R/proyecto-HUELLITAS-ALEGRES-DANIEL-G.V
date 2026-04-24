from datetime import date, timedelta

from django.test import TestCase, Client
from django.conf import settings
from django.urls import reverse
from django.core.exceptions import PermissionDenied, ValidationError
from django.contrib.auth import get_user_model
from django.db.models import ProtectedError

from usuarios.models import Rol
from mascotas.models import Mascota
from agenda.models import Cita, Disponibilidad
from historial.models import HistorialClinico

User = get_user_model()


def create_user_with_role(rol_nombre, **kwargs):
    """Helper to create a Usuario with the given role."""
    rol, _ = Rol.objects.get_or_create(nombre=rol_nombre)
    user = User.objects.create_user(
        username=kwargs.get('username', f'user_{rol_nombre.lower()}'),
        email=kwargs.get('email', f'{rol_nombre.lower()}@test.com'),
        password='testpass123',
        rol=rol,
        **{k: v for k, v in kwargs.items() if k not in ('username', 'email', 'password', 'rol')}
    )
    return user


# ========================================
# PHASE 1: Model Tests (REQ-01 through REQ-07)
# ========================================

class HistorialClinicoModelTest(TestCase):
    """REQ-01: HistorialClinico model — basic creation, str, ordering, nullable cita"""

    def setUp(self):
        self.vet = create_user_with_role('Veterinario', username='vet_hist', email='vet_hist@test.com')
        self.cliente = create_user_with_role('Cliente', username='cliente_hist', email='cliente_hist@test.com')
        self.mascota = Mascota.objects.create(
            nombre='Firulais', especie='Canino', sexo='Macho',
            propietario=self.cliente,
        )

    def test_creacion_basica(self):
        """R1.1: Create HistorialClinico with all required fields, fecha_consulta auto-populated"""
        from historial.models import HistorialClinico
        hc = HistorialClinico.objects.create(
            mascota=self.mascota,
            veterinario=self.vet,
            tipo_consulta='consulta',
            motivo_consulta='Revisión general',
            diagnostico='Animal sano',
        )
        self.assertEqual(hc.mascota, self.mascota)
        self.assertEqual(hc.veterinario, self.vet)
        self.assertEqual(hc.tipo_consulta, 'consulta')
        self.assertEqual(hc.motivo_consulta, 'Revisión general')
        self.assertEqual(hc.diagnostico, 'Animal sano')
        self.assertIsNotNone(hc.pk)
        self.assertIsNotNone(hc.fecha_consulta)

    def test_cita_nullable(self):
        """R1.2: HistorialClinico without cita is valid"""
        from historial.models import HistorialClinico
        hc = HistorialClinico(
            mascota=self.mascota,
            veterinario=self.vet,
            tipo_consulta='consulta',
            motivo_consulta='Revisión',
            diagnostico='OK',
        )
        hc.full_clean()  # Should NOT raise
        hc.save()
        self.assertIsNone(hc.cita)

    def test_str_format(self):
        """R1.3: __str__ returns 'mascota - tipo_consulta (dd/mm/yyyy)'"""
        from historial.models import HistorialClinico
        hc = HistorialClinico.objects.create(
            mascota=self.mascota,
            veterinario=self.vet,
            tipo_consulta='consulta',
            motivo_consulta='Revisión',
            diagnostico='OK',
        )
        fecha_str = hc.fecha_consulta.strftime('%d/%m/%Y')
        expected = f"{self.mascota} - Consulta general ({fecha_str})"
        self.assertEqual(str(hc), expected)

    def test_ordering_newest_first(self):
        """R1.4: Results ordered by -fecha_consulta (newest first)"""
        from historial.models import HistorialClinico
        import time
        hc1 = HistorialClinico.objects.create(
            mascota=self.mascota,
            veterinario=self.vet,
            tipo_consulta='consulta',
            motivo_consulta='Primero',
            diagnostico='OK',
        )
        time.sleep(0.05)  # Ensure different timestamps
        hc2 = HistorialClinico.objects.create(
            mascota=self.mascota,
            veterinario=self.vet,
            tipo_consulta='vacunacion',
            motivo_consulta='Segundo',
            diagnostico='OK',
        )
        results = list(HistorialClinico.objects.all())
        self.assertEqual(results[0].pk, hc2.pk)
        self.assertEqual(results[1].pk, hc1.pk)


class HistorialClinicoValidationTest(TestCase):
    """REQ-02: Model field validators — peso, temperatura, frecuencia, tipo_consulta"""

    def setUp(self):
        self.vet = create_user_with_role('Veterinario', username='vet_val', email='vet_val@test.com')
        self.cliente = create_user_with_role('Cliente', username='cliente_val', email='cliente_val@test.com')
        self.mascota = Mascota.objects.create(
            nombre='Firulais', especie='Canino', sexo='Macho',
            propietario=self.cliente,
        )

    def _make_hc(self, **kwargs):
        """Helper to create HistorialClinico instance without saving."""
        from historial.models import HistorialClinico
        defaults = {
            'mascota': self.mascota,
            'veterinario': self.vet,
            'tipo_consulta': 'consulta',
            'motivo_consulta': 'Test',
            'diagnostico': 'Test',
        }
        defaults.update(kwargs)
        return HistorialClinico(**defaults)

    def test_peso_min_validator(self):
        """R2.1: peso=0.00 raises ValidationError"""
        hc = self._make_hc(peso=0.00)
        with self.assertRaises(ValidationError):
            hc.full_clean()

    def test_peso_max_validator(self):
        """R2.2: peso=1000.00 raises ValidationError"""
        hc = self._make_hc(peso=1000.00)
        with self.assertRaises(ValidationError):
            hc.full_clean()

    def test_temperatura_min_validator(self):
        """R2.3: temperatura=33.9 raises ValidationError"""
        hc = self._make_hc(temperatura=33.9)
        with self.assertRaises(ValidationError):
            hc.full_clean()

    def test_temperatura_max_validator(self):
        """R2.4: temperatura=43.1 raises ValidationError"""
        hc = self._make_hc(temperatura=43.1)
        with self.assertRaises(ValidationError):
            hc.full_clean()

    def test_fc_min_validator(self):
        """R2.5: frecuencia_cardiaca=39 raises ValidationError"""
        hc = self._make_hc(frecuencia_cardiaca=39)
        with self.assertRaises(ValidationError):
            hc.full_clean()

    def test_fc_max_validator(self):
        """R2.6: frecuencia_cardiaca=301 raises ValidationError"""
        hc = self._make_hc(frecuencia_cardiaca=301)
        with self.assertRaises(ValidationError):
            hc.full_clean()

    def test_fr_min_validator(self):
        """R2.7: frecuencia_respiratoria=4 raises ValidationError"""
        hc = self._make_hc(frecuencia_respiratoria=4)
        with self.assertRaises(ValidationError):
            hc.full_clean()

    def test_fr_max_validator(self):
        """R2.8: frecuencia_respiratoria=61 raises ValidationError"""
        hc = self._make_hc(frecuencia_respiratoria=61)
        with self.assertRaises(ValidationError):
            hc.full_clean()

    def test_tipo_consulta_invalid(self):
        """R2.9: Invalid tipo_consulta raises ValidationError"""
        hc = self._make_hc(tipo_consulta='invalido')
        with self.assertRaises(Exception):  # ValueError for invalid choice
            hc.full_clean()

    def test_valid_values_pass(self):
        """R2.10: Valid peso, temperatura, fc, fr pass validation"""
        hc = self._make_hc(
            peso=5.50,
            temperatura=38.5,
            frecuencia_cardiaca=120,
            frecuencia_respiratoria=30,
        )
        hc.full_clean()  # Should NOT raise


class HistorialClinicoFKTest(TestCase):
    """REQ-03: FK behavior — PROTECT, SET_NULL, related_name"""

    def setUp(self):
        self.vet = create_user_with_role('Veterinario', username='vet_fk', email='vet_fk@test.com')
        self.cliente = create_user_with_role('Cliente', username='cliente_fk', email='cliente_fk@test.com')
        self.mascota = Mascota.objects.create(
            nombre='Firulais', especie='Canino', sexo='Macho',
            propietario=self.cliente,
        )

    def test_mascota_protection(self):
        """R3.1: Deleting mascota with historial raises ProtectedError"""
        from historial.models import HistorialClinico
        HistorialClinico.objects.create(
            mascota=self.mascota,
            veterinario=self.vet,
            tipo_consulta='consulta',
            motivo_consulta='Test',
            diagnostico='Test',
        )
        with self.assertRaises(ProtectedError):
            self.mascota.delete()

    def test_veterinario_protection(self):
        """R3.2: Deleting vet with historial raises ProtectedError"""
        from historial.models import HistorialClinico
        HistorialClinico.objects.create(
            mascota=self.mascota,
            veterinario=self.vet,
            tipo_consulta='consulta',
            motivo_consulta='Test',
            diagnostico='Test',
        )
        with self.assertRaises(ProtectedError):
            self.vet.delete()

    def test_mascota_related_name(self):
        """R3.3: mascota.historiales.all() returns related historiales"""
        from historial.models import HistorialClinico
        HistorialClinico.objects.create(
            mascota=self.mascota,
            veterinario=self.vet,
            tipo_consulta='consulta',
            motivo_consulta='Test 1',
            diagnostico='Test',
        )
        HistorialClinico.objects.create(
            mascota=self.mascota,
            veterinario=self.vet,
            tipo_consulta='vacunacion',
            motivo_consulta='Test 2',
            diagnostico='Test',
        )
        historiales = self.mascota.historiales.all()
        self.assertEqual(historiales.count(), 2)

    def test_historial_without_cita(self):
        """R3.4: HistorialClinico without cita field is valid"""
        from historial.models import HistorialClinico
        hc = HistorialClinico.objects.create(
            mascota=self.mascota,
            veterinario=self.vet,
            tipo_consulta='consulta',
            motivo_consulta='Test',
            diagnostico='Test',
        )
        self.assertIsNone(hc.cita)


class CitaMotivoTest(TestCase):
    """REQ-04: Cita.motivo field exists with default empty string"""

    def setUp(self):
        self.vet = create_user_with_role('Veterinario', username='vet_motivo', email='vet_motivo@test.com')
        self.cliente = create_user_with_role('Cliente', username='cliente_motivo', email='cliente_motivo@test.com')
        self.mascota = Mascota.objects.create(
            nombre='Firulais', especie='Canino', sexo='Macho',
            propietario=self.cliente,
        )

    def test_cita_motivo_field_exists(self):
        """R4.1: Cita has motivo attribute"""
        from agenda.models import Cita, Disponibilidad
        disp = Disponibilidad.objects.create(
            veterinario=self.vet, fecha=date(2026, 5, 1),
            hora_inicio='09:00', hora_fin='10:00',
        )
        cita = Cita.objects.create(mascota=self.mascota, disponibilidad=disp)
        self.assertTrue(hasattr(cita, 'motivo'))

    def test_cita_motivo_default_empty(self):
        """R4.2: New Cita has motivo=''"""
        from agenda.models import Cita, Disponibilidad
        disp = Disponibilidad.objects.create(
            veterinario=self.vet, fecha=date(2026, 5, 1),
            hora_inicio='09:00', hora_fin='10:00',
        )
        cita = Cita(mascota=self.mascota, disponibilidad=disp)
        self.assertEqual(cita.motivo, '')


class HistorialAppRegistrationTest(TestCase):
    """REQ-05: App is registered in INSTALLED_APPS"""

    def test_historial_in_installed_apps(self):
        """R5.1: 'historial' is in INSTALLED_APPS"""
        self.assertIn('historial', settings.INSTALLED_APPS)


class HistorialURLTest(TestCase):
    """REQ-06: URL configuration — all patterns resolve under historial: namespace"""

    def test_url_patterns_resolve(self):
        """R6.1: All URL names reverse correctly"""
        from django.urls import reverse
        url_lista = reverse('historial:lista')
        self.assertEqual(url_lista, '/historial/')

        url_crear = reverse('historial:crear')
        self.assertEqual(url_crear, '/historial/nuevo/')

        url_detalle = reverse('historial:detalle', kwargs={'pk': 5})
        self.assertEqual(url_detalle, '/historial/5/')

        url_editar = reverse('historial:editar', kwargs={'pk': 5})
        self.assertEqual(url_editar, '/historial/5/editar/')

        url_por_mascota = reverse('historial:por_mascota', kwargs={'mascota_pk': 3})
        self.assertEqual(url_por_mascota, '/historial/mascota/3/')

        url_atender = reverse('historial:atender_cita', kwargs={'cita_pk': 7})
        self.assertEqual(url_atender, '/historial/atender/7/')


class HistorialAdminTest(TestCase):
    """REQ-07: Admin registration"""

    def test_historial_admin_registered(self):
        """R7.1: HistorialClinico model is in admin.site._registry"""
        from django.contrib import admin
        from historial.models import HistorialClinico
        self.assertIn(HistorialClinico, admin.site._registry)


# ========================================
# PHASE 2: Form Layer Tests
# ========================================

class HistorialClinicoFormTest(TestCase):
    """REQ-HC03: HistorialClinicoForm — validation and fields"""

    def setUp(self):
        self.vet = create_user_with_role('Veterinario', username='vet_form', email='vet_form@test.com')
        self.cliente = create_user_with_role('Cliente', username='cliente_form', email='cliente_form@test.com')
        self.mascota = Mascota.objects.create(
            nombre='Firulais', especie='Canino', sexo='Macho',
            propietario=self.cliente,
        )

    def test_form_required_fields(self):
        """F2.1: Form requires motivo_consulta and diagnostico"""
        from historial.forms import HistorialClinicoForm
        form = HistorialClinicoForm(data={
            'mascota': self.mascota.pk,
            'veterinario': self.vet.pk,
            'tipo_consulta': 'consulta',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('motivo_consulta', form.errors)
        self.assertIn('diagnostico', form.errors)

    def test_form_valid_with_all_fields(self):
        """F2.2: Form is valid with all required fields"""
        from historial.forms import HistorialClinicoForm
        form = HistorialClinicoForm(data={
            'mascota': self.mascota.pk,
            'veterinario': self.vet.pk,
            'tipo_consulta': 'consulta',
            'motivo_consulta': 'Revisión general',
            'diagnostico': 'Animal sano',
            'peso': '25.50',
            'temperatura': '38.5',
            'frecuencia_cardiaca': '120',
            'frecuencia_respiratoria': '24',
        })
        self.assertTrue(form.is_valid(), form.errors)

    def test_form_peso_range_validation(self):
        """F2.3: Form rejects peso out of range"""
        from historial.forms import HistorialClinicoForm
        form = HistorialClinicoForm(data={
            'mascota': self.mascota.pk,
            'veterinario': self.vet.pk,
            'tipo_consulta': 'consulta',
            'motivo_consulta': 'Test',
            'diagnostico': 'Test',
            'peso': '0.00',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('peso', form.errors)

    def test_form_negative_peso_rejected(self):
        """F2.4: Form rejects negative peso"""
        from historial.forms import HistorialClinicoForm
        form = HistorialClinicoForm(data={
            'mascota': self.mascota.pk,
            'veterinario': self.vet.pk,
            'tipo_consulta': 'consulta',
            'motivo_consulta': 'Test',
            'diagnostico': 'Test',
            'peso': '-5.00',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('peso', form.errors)

    def test_form_valid_vital_signs_accepted(self):
        """F2.5: Form accepts valid vital signs"""
        from historial.forms import HistorialClinicoForm
        form = HistorialClinicoForm(data={
            'mascota': self.mascota.pk,
            'veterinario': self.vet.pk,
            'tipo_consulta': 'consulta',
            'motivo_consulta': 'Test',
            'diagnostico': 'Test',
            'peso': '25.50',
            'temperatura': '38.5',
            'frecuencia_cardiaca': '120',
            'frecuencia_respiratoria': '24',
        })
        self.assertTrue(form.is_valid(), form.errors)

    def test_form_past_proxima_vacunacion_rejected(self):
        """F2.6: Form rejects proxima_vacunacion in the past"""
        from historial.forms import HistorialClinicoForm
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        form = HistorialClinicoForm(data={
            'mascota': self.mascota.pk,
            'veterinario': self.vet.pk,
            'tipo_consulta': 'vacunacion',
            'motivo_consulta': 'Test',
            'diagnostico': 'Test',
            'proxima_vacunacion': yesterday,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('proxima_vacunacion', form.errors)

    def test_form_future_proxima_vacunacion_accepted(self):
        """F2.7: Form accepts proxima_vacunacion in the future"""
        from historial.forms import HistorialClinicoForm
        future = (date.today() + timedelta(days=30)).isoformat()
        form = HistorialClinicoForm(data={
            'mascota': self.mascota.pk,
            'veterinario': self.vet.pk,
            'tipo_consulta': 'vacunacion',
            'motivo_consulta': 'Test',
            'diagnostico': 'Test',
            'proxima_vacunacion': future,
        })
        self.assertTrue(form.is_valid(), form.errors)


class AtenderCitaFormTest(TestCase):
    """REQ-HC04: AtenderCitaForm — smart tipo_consulta inference and pre-fill"""

    def setUp(self):
        self.vet = create_user_with_role('Veterinario', username='vet_atender', email='vet_atender@test.com')
        self.cliente = create_user_with_role('Cliente', username='cliente_atender', email='cliente_atender@test.com')
        self.mascota = Mascota.objects.create(
            nombre='Firulais', especie='Canino', sexo='Macho',
            propietario=self.cliente,
        )
        self.disp = Disponibilidad.objects.create(
            veterinario=self.vet, fecha=date(2026, 5, 15),
            hora_inicio='10:00', hora_fin='11:00',
        )

    def _create_cita(self, motivo=''):
        return Cita.objects.create(
            mascota=self.mascota, disponibilidad=self.disp,
            estado='Programada', motivo=motivo,
        )

    def test_form_prefills_motivo_from_cita(self):
        """F3.1: AtenderCitaForm pre-fills motivo_consulta from cita.motivo"""
        from historial.forms import AtenderCitaForm
        cita = self._create_cita(motivo='Vacunación anual contra rabia')
        form = AtenderCitaForm(cita=cita)
        self.assertEqual(form.fields['motivo_consulta'].initial, 'Vacunación anual contra rabia')

    def test_form_infers_vacunacion(self):
        """F3.2: Motivo containing 'vacun' infers tipo_consulta='vacunacion'"""
        from historial.forms import AtenderCitaForm
        cita = self._create_cita(motivo='Vacunar perro')
        form = AtenderCitaForm(cita=cita)
        self.assertEqual(form.fields['tipo_consulta'].initial, 'vacunacion')

    def test_form_infers_cirugia(self):
        """F3.3: Motivo containing 'cirug' infers tipo_consulta='cirugia'"""
        from historial.forms import AtenderCitaForm
        cita = self._create_cita(motivo='Cirugía de esterilización')
        form = AtenderCitaForm(cita=cita)
        self.assertEqual(form.fields['tipo_consulta'].initial, 'cirugia')

    def test_form_infers_urgencia(self):
        """F3.4: Motivo containing 'urgencia' infers tipo_consulta='urgencia'"""
        from historial.forms import AtenderCitaForm
        cita = self._create_cita(motivo='Urgencia - vómitos')
        form = AtenderCitaForm(cita=cita)
        self.assertEqual(form.fields['tipo_consulta'].initial, 'urgencia')

    def test_form_infers_control(self):
        """F3.5: Motivo containing 'control' infers tipo_consulta='control'"""
        from historial.forms import AtenderCitaForm
        cita = self._create_cita(motivo='Control mensual')
        form = AtenderCitaForm(cita=cita)
        self.assertEqual(form.fields['tipo_consulta'].initial, 'control')

    def test_form_infers_laboratorio(self):
        """F3.6: Motivo containing 'laboratorio' infers tipo_consulta='laboratorio'"""
        from historial.forms import AtenderCitaForm
        cita = self._create_cita(motivo='Exámenes de laboratorio')
        form = AtenderCitaForm(cita=cita)
        self.assertEqual(form.fields['tipo_consulta'].initial, 'laboratorio')

    def test_form_defaults_consulta(self):
        """F3.7: Unknown motivo defaults to tipo_consulta='consulta'"""
        from historial.forms import AtenderCitaForm
        cita = self._create_cita(motivo='Revisión general')
        form = AtenderCitaForm(cita=cita)
        self.assertEqual(form.fields['tipo_consulta'].initial, 'consulta')

    def test_form_excludes_mascota(self):
        """F3.8: AtenderCitaForm does NOT include mascota field"""
        from historial.forms import AtenderCitaForm
        cita = self._create_cita(motivo='Test')
        form = AtenderCitaForm(cita=cita)
        self.assertNotIn('mascota', form.fields)

    def test_form_case_insensitive_inference(self):
        """F3.9: _infer_tipo_consulta is case-insensitive (CIRUGÍA, cirugia both match)"""
        from historial.forms import AtenderCitaForm
        cita_upper = self._create_cita(motivo='CIRUGÍA DE ESTERILIZACIÓN')
        form_upper = AtenderCitaForm(cita=cita_upper)
        self.assertEqual(form_upper.fields['tipo_consulta'].initial, 'cirugia')

        cita_lower = self._create_cita(motivo='vacunación anual')
        form_lower = AtenderCitaForm(cita=cita_lower)
        self.assertEqual(form_lower.fields['tipo_consulta'].initial, 'vacunacion')


# ========================================
# PHASE 3: View Tests
# ========================================

class ListaHistorialesViewTest(TestCase):
    """REQ-HC05: lista_historiales — role-based filtering, search, pagination"""

    def setUp(self):
        self.vet = create_user_with_role('Veterinario', username='vet_list', email='vet_list@test.com')
        self.admin = create_user_with_role('Administrador', username='admin_list', email='admin_list@test.com')
        self.cliente = create_user_with_role('Cliente', username='cliente_list', email='cliente_list@test.com')
        self.other_cliente = create_user_with_role('Cliente', username='other_list', email='other_list@test.com')
        self.mascota1 = Mascota.objects.create(
            nombre='Fido', especie='Canino', sexo='Macho', propietario=self.cliente,
        )
        self.mascota2 = Mascota.objects.create(
            nombre='Mishi', especie='Felino', sexo='Hembra', propietario=self.other_cliente,
        )
        from historial.models import HistorialClinico
        self.hc1 = HistorialClinico.objects.create(
            mascota=self.mascota1, veterinario=self.vet,
            tipo_consulta='consulta', motivo_consulta='Revisión', diagnostico='Sano',
        )
        self.hc2 = HistorialClinico.objects.create(
            mascota=self.mascota2, veterinario=self.vet,
            tipo_consulta='vacunacion', motivo_consulta='Vacunación', diagnostico='OK',
        )

    def test_vet_sees_own_historiales(self):
        """Vet sees only historiales where they are the vet"""
        self.client.force_login(self.vet)
        resp = self.client.get(reverse('historial:lista'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Revisión')
        self.assertContains(resp, 'Vacunación')

    def test_admin_sees_all_historiales(self):
        """Admin sees all historiales"""
        self.client.force_login(self.admin)
        resp = self.client.get(reverse('historial:lista'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Fido')
        self.assertContains(resp, 'Mishi')

    def test_cliente_sees_own_pets_historiales(self):
        """Cliente sees only historiales of own pets"""
        self.client.force_login(self.cliente)
        resp = self.client.get(reverse('historial:lista'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Fido')
        self.assertNotContains(resp, 'Mishi')

    def test_search_by_mascota_nombre(self):
        """Search filters by mascota nombre"""
        self.client.force_login(self.admin)
        resp = self.client.get(reverse('historial:lista'), {'q': 'Fido'})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Revisión')
        self.assertNotContains(resp, 'Vacunación')

    def test_search_by_diagnostico(self):
        """Search filters by diagnostico"""
        self.client.force_login(self.admin)
        resp = self.client.get(reverse('historial:lista'), {'q': 'Sano'})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Fido')
        self.assertNotContains(resp, 'Mishi')

    def test_anonymous_redirected_to_login(self):
        """Anonymous user redirected to login"""
        resp = self.client.get(reverse('historial:lista'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/usuarios/login/', resp.url)


class CrearHistorialViewTest(TestCase):
    """REQ-HC06: crear_historial — Vet/Admin can create, Cliente 403"""

    def setUp(self):
        self.vet = create_user_with_role('Veterinario', username='vet_crear', email='vet_crear@test.com')
        self.cliente = create_user_with_role('Cliente', username='cliente_crear', email='cliente_crear@test.com')
        self.mascota = Mascota.objects.create(
            nombre='Fido', especie='Canino', sexo='Macho', propietario=self.cliente,
        )

    def test_vet_creates_historial(self):
        """Vet creates historial directly"""
        self.client.force_login(self.vet)
        resp = self.client.post(reverse('historial:crear'), {
            'mascota': self.mascota.pk,
            'tipo_consulta': 'consulta',
            'motivo_consulta': 'Chequeo general',
            'diagnostico': 'Animal sano',
        })
        self.assertEqual(resp.status_code, 302)
        from historial.models import HistorialClinico
        hc = HistorialClinico.objects.get(motivo_consulta='Chequeo general')
        self.assertEqual(hc.veterinario, self.vet)

    def test_cliente_cannot_create_403(self):
        """Cliente gets 403 when trying to create historial"""
        self.client.force_login(self.cliente)
        resp = self.client.get(reverse('historial:crear'))
        self.assertEqual(resp.status_code, 403)


class DetalleHistorialViewTest(TestCase):
    """REQ-HC07: detalle_historial — object-level permissions"""

    def setUp(self):
        self.vet = create_user_with_role('Veterinario', username='vet_det', email='vet_det@test.com')
        self.admin = create_user_with_role('Administrador', username='admin_det', email='admin_det@test.com')
        self.cliente = create_user_with_role('Cliente', username='cliente_det', email='cliente_det@test.com')
        self.other_cliente = create_user_with_role('Cliente', username='other_det', email='other_det@test.com')
        self.mascota_own = Mascota.objects.create(
            nombre='Fido', especie='Canino', sexo='Macho', propietario=self.cliente,
        )
        self.mascota_other = Mascota.objects.create(
            nombre='Mishi', especie='Felino', sexo='Hembra', propietario=self.other_cliente,
        )
        from historial.models import HistorialClinico
        self.hc_own = HistorialClinico.objects.create(
            mascota=self.mascota_own, veterinario=self.vet,
            tipo_consulta='consulta', motivo_consulta='Test own', diagnostico='OK',
        )
        self.hc_other = HistorialClinico.objects.create(
            mascota=self.mascota_other, veterinario=self.vet,
            tipo_consulta='consulta', motivo_consulta='Test other', diagnostico='OK',
        )

    def test_vet_views_own_historial(self):
        """Vet can view own historial"""
        self.client.force_login(self.vet)
        resp = self.client.get(reverse('historial:detalle', kwargs={'pk': self.hc_own.pk}))
        self.assertEqual(resp.status_code, 200)

    def test_admin_views_any_historial(self):
        """Admin can view any historial"""
        self.client.force_login(self.admin)
        resp = self.client.get(reverse('historial:detalle', kwargs={'pk': self.hc_other.pk}))
        self.assertEqual(resp.status_code, 200)

    def test_cliente_views_own_pet_historial(self):
        """Cliente can view historial of own pet"""
        self.client.force_login(self.cliente)
        resp = self.client.get(reverse('historial:detalle', kwargs={'pk': self.hc_own.pk}))
        self.assertEqual(resp.status_code, 200)

    def test_cliente_cannot_view_other_pet_historial(self):
        """Cliente gets 403 for other pet's historial"""
        self.client.force_login(self.cliente)
        resp = self.client.get(reverse('historial:detalle', kwargs={'pk': self.hc_other.pk}))
        self.assertEqual(resp.status_code, 403)

    def test_nonexistent_historial_404(self):
        """Nonexistent historial returns 404"""
        self.client.force_login(self.vet)
        resp = self.client.get(reverse('historial:detalle', kwargs={'pk': 99999}))
        self.assertEqual(resp.status_code, 404)

    def test_anonymous_redirected_to_login(self):
        """Anonymous user redirected to login"""
        resp = self.client.get(reverse('historial:detalle', kwargs={'pk': self.hc_own.pk}))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/usuarios/login/', resp.url)


class EditarHistorialViewTest(TestCase):
    """REQ-HC08: editar_historial — ownership checks"""

    def setUp(self):
        self.vet1 = create_user_with_role('Veterinario', username='vet_edit1', email='vet_edit1@test.com')
        self.vet2 = create_user_with_role('Veterinario', username='vet_edit2', email='vet_edit2@test.com')
        self.admin = create_user_with_role('Administrador', username='admin_edit', email='admin_edit@test.com')
        self.cliente = create_user_with_role('Cliente', username='cliente_edit', email='cliente_edit@test.com')
        self.mascota = Mascota.objects.create(
            nombre='Fido', especie='Canino', sexo='Macho', propietario=self.cliente,
        )
        from historial.models import HistorialClinico
        self.hc = HistorialClinico.objects.create(
            mascota=self.mascota, veterinario=self.vet1,
            tipo_consulta='consulta', motivo_consulta='Original', diagnostico='Test',
        )

    def test_vet_edits_own_historial(self):
        """Vet can edit own historial"""
        self.client.force_login(self.vet1)
        resp = self.client.post(reverse('historial:editar', kwargs={'pk': self.hc.pk}), {
            'mascota': self.mascota.pk,
            'tipo_consulta': 'consulta',
            'motivo_consulta': 'Updated motivo',
            'diagnostico': 'Updated diag',
        })
        self.assertEqual(resp.status_code, 302)
        self.hc.refresh_from_db()
        self.assertEqual(self.hc.motivo_consulta, 'Updated motivo')

    def test_vet_cannot_edit_other_vet_historial(self):
        """Vet gets 403 for other vet's historial"""
        self.client.force_login(self.vet2)
        resp = self.client.get(reverse('historial:editar', kwargs={'pk': self.hc.pk}))
        self.assertEqual(resp.status_code, 403)

    def test_cliente_cannot_edit_historial(self):
        """Cliente always gets 403 for edit"""
        self.client.force_login(self.cliente)
        resp = self.client.get(reverse('historial:editar', kwargs={'pk': self.hc.pk}))
        self.assertEqual(resp.status_code, 403)

    def test_admin_edits_any_historial(self):
        """Admin can edit any historial"""
        self.client.force_login(self.admin)
        resp = self.client.post(reverse('historial:editar', kwargs={'pk': self.hc.pk}), {
            'mascota': self.mascota.pk,
            'tipo_consulta': 'consulta',
            'motivo_consulta': 'Admin edit',
            'diagnostico': 'Admin diag',
        })
        self.assertEqual(resp.status_code, 302)
        self.hc.refresh_from_db()
        self.assertEqual(self.hc.motivo_consulta, 'Admin edit')


class HistorialPorMascotaViewTest(TestCase):
    """REQ-HC09: historial_por_mascota — client isolation"""

    def setUp(self):
        self.vet = create_user_with_role('Veterinario', username='vet_masc', email='vet_masc@test.com')
        self.cliente = create_user_with_role('Cliente', username='cliente_masc', email='cliente_masc@test.com')
        self.other_cliente = create_user_with_role('Cliente', username='other_masc', email='other_masc@test.com')
        self.mascota_own = Mascota.objects.create(
            nombre='Fido', especie='Canino', sexo='Macho', propietario=self.cliente,
        )
        self.mascota_other = Mascota.objects.create(
            nombre='Mishi', especie='Felino', sexo='Hembra', propietario=self.other_cliente,
        )
        from historial.models import HistorialClinico
        HistorialClinico.objects.create(
            mascota=self.mascota_own, veterinario=self.vet,
            tipo_consulta='consulta', motivo_consulta='Test', diagnostico='OK',
        )

    def test_cliente_views_own_pet_history(self):
        """Cliente views own pet's full history"""
        self.client.force_login(self.cliente)
        resp = self.client.get(reverse('historial:por_mascota', kwargs={'mascota_pk': self.mascota_own.pk}))
        self.assertEqual(resp.status_code, 200)

    def test_cliente_cannot_view_other_pet_history(self):
        """Cliente gets 403 for other pet's history"""
        self.client.force_login(self.cliente)
        resp = self.client.get(reverse('historial:por_mascota', kwargs={'mascota_pk': self.mascota_other.pk}))
        self.assertEqual(resp.status_code, 403)

    def test_vet_views_any_pet_history(self):
        """Vet can view any pet's history"""
        self.client.force_login(self.vet)
        resp = self.client.get(reverse('historial:por_mascota', kwargs={'mascota_pk': self.mascota_own.pk}))
        self.assertEqual(resp.status_code, 200)


class AtenderCitaViewTest(TestCase):
    """REQ-HC10: atender_cita — atomic transaction, state validation, role access"""

    def setUp(self):
        self.vet = create_user_with_role('Veterinario', username='vet_at', email='vet_at@test.com')
        self.admin = create_user_with_role('Administrador', username='admin_at', email='admin_at@test.com')
        self.cliente = create_user_with_role('Cliente', username='cliente_at', email='cliente_at@test.com')
        self.mascota = Mascota.objects.create(
            nombre='Fido', especie='Canino', sexo='Macho', propietario=self.cliente,
        )
        self.disp = Disponibilidad.objects.create(
            veterinario=self.vet, fecha=date(2026, 6, 1),
            hora_inicio='10:00', hora_fin='11:00',
        )

    def _create_programada(self, motivo=''):
        return Cita.objects.create(
            mascota=self.mascota, disponibilidad=self.disp,
            estado='Programada', motivo=motivo,
        )

    def test_vet_attends_cita_successfully(self):
        """Vet attends scheduled cita — creates HistorialClinico + Cita becomes Atendida"""
        from historial.models import HistorialClinico
        cita = self._create_programada(motivo='Vacunación anual')
        self.client.force_login(self.vet)
        resp = self.client.post(reverse('historial:atender_cita', kwargs={'cita_pk': cita.pk}), {
            'tipo_consulta': 'vacunacion',
            'motivo_consulta': 'Vacunación anual',
            'diagnostico': 'Sano, vacuna aplicada',
        })
        self.assertEqual(resp.status_code, 302)
        cita.refresh_from_db()
        self.assertEqual(cita.estado, 'Atendida')
        hc = HistorialClinico.objects.get(cita=cita)
        self.assertEqual(hc.veterinario, self.vet)
        self.assertEqual(hc.mascota, self.mascota)

    def test_cannot_attend_already_atendida(self):
        """Cannot attend a cita that is already Atendida"""
        cita = self._create_programada(motivo='Test')
        cita.estado = 'Atendida'
        cita.save()
        self.client.force_login(self.vet)
        resp = self.client.get(reverse('historial:atender_cita', kwargs={'cita_pk': cita.pk}))
        self.assertEqual(resp.status_code, 302)

    def test_cannot_attend_cancelled_cita(self):
        """Cannot attend a cancelled cita"""
        cita = self._create_programada(motivo='Test')
        cita.estado = 'Cancelada'
        cita.motivo_cancelacion = 'No asistió'
        cita.save()
        self.client.force_login(self.vet)
        resp = self.client.get(reverse('historial:atender_cita', kwargs={'cita_pk': cita.pk}))
        self.assertEqual(resp.status_code, 302)

    def test_cliente_cannot_attend_cita(self):
        """Cliente gets 403 when trying to attend a cita"""
        cita = self._create_programada(motivo='Test')
        self.client.force_login(self.cliente)
        resp = self.client.get(reverse('historial:atender_cita', kwargs={'cita_pk': cita.pk}))
        self.assertEqual(resp.status_code, 403)

    def test_nonexistent_cita_404(self):
        """Nonexistent cita returns 404"""
        self.client.force_login(self.vet)
        resp = self.client.get(reverse('historial:atender_cita', kwargs={'cita_pk': 99999}))
        self.assertEqual(resp.status_code, 404)

    def test_attend_cita_pre_fills_form(self):
        """GET atender_cita shows form with pre-filled data from cita"""
        cita = self._create_programada(motivo='Vacunación contra rabia')
        self.client.force_login(self.vet)
        resp = self.client.get(reverse('historial:atender_cita', kwargs={'cita_pk': cita.pk}))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Vacunación contra rabia')


# ========================================
# PHASE 6: Adjunto Model & Upload Tests
# ========================================

import io
from django.core.files.uploadedfile import SimpleUploadedFile


def _create_test_file(content=b'test file content', name='test.pdf', content_type='application/pdf'):
    """Helper to create a SimpleUploadedFile for testing."""
    return SimpleUploadedFile(name, content, content_type=content_type)


class AdjuntoModelTest(TestCase):
    """Tests for Adjunto model — fields, constraints, file size validation."""

    def setUp(self):
        self.vet = create_user_with_role('Veterinario', username='vet_adj', email='vet_adj@test.com')
        self.cliente = create_user_with_role('Cliente', username='cli_adj', email='cli_adj@test.com')
        self.mascota = Mascota.objects.create(
            nombre='Firulais', especie='Canino', sexo='Macho', propietario=self.cliente,
        )
        self.hc = HistorialClinico.objects.create(
            mascota=self.mascota, veterinario=self.vet,
            tipo_consulta='consulta', motivo_consulta='Test', diagnostico='OK',
        )

    def test_adjunto_creation(self):
        """A6.1: Adjunto can be created with file and linked to HistorialClinico"""
        from historial.models import Adjunto
        adj = Adjunto.objects.create(
            historial_clinico=self.hc,
            archivo=_create_test_file(name='radiografia.png', content_type='image/png'),
            tipo='radiografia',
            descripcion='Radiografía torácica',
            subido_por=self.vet,
        )
        self.assertEqual(adj.historial_clinico, self.hc)
        self.assertEqual(adj.tipo, 'radiografia')
        self.assertEqual(adj.subido_por, self.vet)
        self.assertIsNotNone(adj.fecha_subida)

    def test_adjunto_tipos_choices(self):
        """A6.2: TIPO_ADJUNTO_CHOICES contains expected types"""
        from historial.models import TIPO_ADJUNTO_CHOICES
        tipos = [t[0] for t in TIPO_ADJUNTO_CHOICES]
        self.assertIn('radiografia', tipos)
        self.assertIn('laboratorio', tipos)
        self.assertIn('foto', tipos)
        self.assertIn('otro', tipos)

    def test_adjunto_fk_protect(self):
        """A6.3: Cannot delete HistorialClinico with Adjunto records"""
        from historial.models import Adjunto
        Adjunto.objects.create(
            historial_clinico=self.hc,
            archivo=_create_test_file(),
            tipo='otro',
            subido_por=self.vet,
        )
        with self.assertRaises(ProtectedError):
            self.hc.delete()

    def test_adjunto_file_size_limit(self):
        """A6.4: Adjunto file exceeding 5MB is rejected"""
        from historial.models import Adjunto, MAX_ADJUNTO_SIZE
        self.assertEqual(MAX_ADJUNTO_SIZE, 5 * 1024 * 1024)
        big_file = SimpleUploadedFile('big.pdf', b'x' * (5 * 1024 * 1024 + 1), content_type='application/pdf')
        adj = Adjunto(
            historial_clinico=self.hc,
            archivo=big_file,
            tipo='otro',
            subido_por=self.vet,
        )
        with self.assertRaises(ValidationError):
            adj.clean()

    def test_adjunto_file_size_within_limit(self):
        """A6.5: Adjunto file under 5MB passes validation"""
        from historial.models import Adjunto
        small_file = SimpleUploadedFile('small.pdf', b'x' * 1024, content_type='application/pdf')
        adj = Adjunto(
            historial_clinico=self.hc,
            archivo=small_file,
            tipo='otro',
            subido_por=self.vet,
        )
        # Should NOT raise
        adj.clean()

    def test_adjunto_multiple_per_historial(self):
        """A6.6: Multiple Adjuntos can be linked to same HistorialClinico (1:N)"""
        from historial.models import Adjunto
        Adjunto.objects.create(
            historial_clinico=self.hc,
            archivo=_create_test_file(name='file1.pdf'),
            tipo='radiografia',
            subido_por=self.vet,
        )
        Adjunto.objects.create(
            historial_clinico=self.hc,
            archivo=_create_test_file(name='file2.pdf'),
            tipo='laboratorio',
            subido_por=self.vet,
        )
        self.assertEqual(self.hc.adjuntos.count(), 2)

    def test_adjunto_descripcion_blank(self):
        """A6.7: descripcion can be blank"""
        from historial.models import Adjunto
        adj = Adjunto.objects.create(
            historial_clinico=self.hc,
            archivo=_create_test_file(),
            tipo='otro',
            descripcion='',
            subido_por=self.vet,
        )
        self.assertEqual(adj.descripcion, '')

    def test_adjunto_str_format(self):
        """A6.8: Adjunto __str__ returns readable format"""
        from historial.models import Adjunto
        adj = Adjunto.objects.create(
            historial_clinico=self.hc,
            archivo=_create_test_file(name='rx_torax.png'),
            tipo='radiografia',
            subido_por=self.vet,
        )
        self.assertIn('Radiograf', str(adj))


class AdjuntoViewTest(TestCase):
    """Tests for Adjunto upload/delete views — permissions, file validation."""

    def setUp(self):
        self.vet = create_user_with_role('Veterinario', username='vet_av', email='vet_av@test.com')
        self.admin = create_user_with_role('Administrador', username='admin_av', email='admin_av@test.com')
        self.cliente = create_user_with_role('Cliente', username='cli_av', email='cli_av@test.com')
        self.other_vet = create_user_with_role('Veterinario', username='vet_av2', email='vet_av2@test.com')
        self.mascota = Mascota.objects.create(
            nombre='Firulais', especie='Canino', sexo='Macho', propietario=self.cliente,
        )
        self.hc = HistorialClinico.objects.create(
            mascota=self.mascota, veterinario=self.vet,
            tipo_consulta='consulta', motivo_consulta='Test', diagnostico='OK',
        )

    def _upload_url(self):
        from django.urls import reverse
        return reverse('historial:subir_adjunto', kwargs={'pk': self.hc.pk})

    def test_vet_can_see_upload_form(self):
        """A7.1: Vet sees upload form on historial detail"""
        self.client.force_login(self.vet)
        resp = self.client.get(reverse('historial:detalle', kwargs={'pk': self.hc.pk}))
        self.assertEqual(resp.status_code, 200)

    def test_vet_can_upload_adjunto(self):
        """A7.2: Vet can upload an attachment to own historial"""
        from historial.models import Adjunto
        self.client.force_login(self.vet)
        upload_file = _create_test_file(name='radiografia.png', content_type='image/png')
        resp = self.client.post(self._upload_url(), {
            'archivo': upload_file,
            'tipo': 'radiografia',
            'descripcion': 'RX tórax',
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Adjunto.objects.count(), 1)

    def test_cliente_cannot_upload_adjunto(self):
        """A7.3: Cliente gets 403 when trying to upload"""
        self.client.force_login(self.cliente)
        upload_file = _create_test_file()
        resp = self.client.post(self._upload_url(), {
            'archivo': upload_file,
            'tipo': 'otro',
            'descripcion': 'Test',
        })
        self.assertEqual(resp.status_code, 403)

    def test_other_vet_cannot_upload_adjunto(self):
        """A7.4: Other vet gets 403 for historial they didn't create"""
        self.client.force_login(self.other_vet)
        upload_file = _create_test_file()
        resp = self.client.post(self._upload_url(), {
            'archivo': upload_file,
            'tipo': 'otro',
            'descripcion': 'Test',
        })
        self.assertEqual(resp.status_code, 403)

    def test_admin_can_upload_adjunto(self):
        """A7.5: Admin can upload attachment to any historial"""
        from historial.models import Adjunto
        self.client.force_login(self.admin)
        upload_file = _create_test_file(name='lab.pdf', content_type='application/pdf')
        resp = self.client.post(self._upload_url(), {
            'archivo': upload_file,
            'tipo': 'laboratorio',
            'descripcion': 'Hemograma',
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Adjunto.objects.count(), 1)

    def test_upload_file_too_large_rejected(self):
        """A7.6: Upload exceeding 5MB is rejected by the form"""
        from historial.models import MAX_ADJUNTO_SIZE
        self.client.force_login(self.vet)
        big_content = b'x' * (MAX_ADJUNTO_SIZE + 1)
        big_file = SimpleUploadedFile('big.pdf', big_content, content_type='application/pdf')
        resp = self.client.post(self._upload_url(), {
            'archivo': big_file,
            'tipo': 'otro',
            'descripcion': 'Big file',
        })
        self.assertEqual(resp.status_code, 200)  # Re-renders form with errors
        self.assertFalse(resp.context['form'].is_valid())

    def test_vet_can_delete_own_adjunto(self):
        """A7.7: Vet can delete their own attachment"""
        from historial.models import Adjunto
        adj = Adjunto.objects.create(
            historial_clinico=self.hc,
            archivo=_create_test_file(),
            tipo='otro',
            subido_por=self.vet,
        )
        self.client.force_login(self.vet)
        resp = self.client.post(reverse('historial:eliminar_adjunto', kwargs={'pk': adj.pk}))
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Adjunto.objects.count(), 0)

    def test_other_vet_cannot_delete_adjunto(self):
        """A7.8: Other vet gets 403 trying to delete attachment"""
        from historial.models import Adjunto
        adj = Adjunto.objects.create(
            historial_clinico=self.hc,
            archivo=_create_test_file(),
            tipo='otro',
            subido_por=self.vet,
        )
        self.client.force_login(self.other_vet)
        resp = self.client.post(reverse('historial:eliminar_adjunto', kwargs={'pk': adj.pk}))
        self.assertEqual(resp.status_code, 403)

    def test_admin_can_delete_any_adjunto(self):
        """A7.9: Admin can delete any attachment"""
        from historial.models import Adjunto
        adj = Adjunto.objects.create(
            historial_clinico=self.hc,
            archivo=_create_test_file(),
            tipo='otro',
            subido_por=self.vet,
        )
        self.client.force_login(self.admin)
        resp = self.client.post(reverse('historial:eliminar_adjunto', kwargs={'pk': adj.pk}))
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Adjunto.objects.count(), 0)