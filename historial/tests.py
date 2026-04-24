from datetime import date, timedelta, datetime

from django.test import TestCase
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import ProtectedError
from django.contrib.auth import get_user_model

from usuarios.models import Rol, Usuario
from mascotas.models import Mascota
from agenda.models import Cita, Disponibilidad


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
# PHASE 1: Historial Clinico Model + Migration + Admin + URLs
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
# PHASE 2: Form Layer
# ========================================

class HistorialClinicoFormTest(TestCase):
    """REQ-HC03: HistorialClinicoForm — validation and fields"""

    def setUp(self):
        self.vet_rol = Rol.objects.get(nombre='Veterinario')
        self.cliente_rol = Rol.objects.get(nombre='Cliente')
        User = get_user_model()
        self.vet = User.objects.create_user(
            username='vet_form', email='vet_form@test.com',
            password='pass123', rol=self.vet_rol,
        )
        self.cliente = User.objects.create_user(
            username='cliente_form', email='cliente_form@test.com',
            password='pass123', rol=self.cliente_rol,
        )
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
            # missing motivo_consulta and diagnostico
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
        self.vet_rol = Rol.objects.get(nombre='Veterinario')
        self.cliente_rol = Rol.objects.get(nombre='Cliente')
        User = get_user_model()
        self.vet = User.objects.create_user(
            username='vet_atender', email='vet_atender@test.com',
            password='pass123', rol=self.vet_rol,
        )
        self.cliente = User.objects.create_user(
            username='cliente_atender', email='cliente_atender@test.com',
            password='pass123', rol=self.cliente_rol,
        )
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

        # Test lowercase accented
        cita_lower = self._create_cita(motivo='vacunación anual')
        form_lower = AtenderCitaForm(cita=cita_lower)
        self.assertEqual(form_lower.fields['tipo_consulta'].initial, 'vacunacion')
