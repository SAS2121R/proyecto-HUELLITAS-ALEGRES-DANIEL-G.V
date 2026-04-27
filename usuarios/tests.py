from django.test import TestCase
from django.db import IntegrityError
from django.db.models import ProtectedError
from django.urls import path, reverse
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.core.exceptions import ValidationError
import json

from .models import Rol


class RolModelTest(TestCase):
    """R1: Rol model — nombre (unique), descripcion (blank)"""

    def test_rol_creation_with_nombre_and_descripcion(self):
        """R1 scenario 1: Rol creation with nombre and descripcion"""
        # Use unique names not in seed data to avoid UNIQUE conflict
        rol, _ = Rol.objects.get_or_create(nombre="Supervisor", defaults={"descripcion": "Supervisor staff"})
        self.assertEqual(rol.nombre, "Supervisor")
        self.assertEqual(rol.descripcion, "Supervisor staff")

    def test_rol_nombre_must_be_unique(self):
        """R1 scenario 2: Duplicate nombre raises IntegrityError"""
        # 'Cliente' already exists from seed data
        with self.assertRaises(IntegrityError):
            Rol.objects.create(nombre="Cliente", descripcion="Duplicate")

    def test_rol_descripcion_can_be_blank(self):
        """R1 scenario 3: Blank descripcion is valid"""
        rol, _ = Rol.objects.get_or_create(nombre="Gerente", defaults={"descripcion": ""})
        self.assertEqual(rol.descripcion, "")

    def test_rol_str_returns_nombre(self):
        """Rol __str__ returns nombre"""
        rol = Rol.objects.get(nombre='Cliente')
        self.assertEqual(str(rol), "Cliente")


class MigrationSeedTest(TestCase):
    """R2: Role seeding migration; R3: Existing users get Cliente role"""

    def test_four_roles_exist_after_migration(self):
        """R2 scenario 1: Exactly 4 roles exist after migrations"""
        roles = Rol.objects.all()
        self.assertEqual(roles.count(), 4)
        role_names = set(roles.values_list('nombre', flat=True))
        self.assertEqual(role_names, {'Cliente', 'Veterinario', 'Domiciliario', 'Administrador'})

    def test_migration_is_idempotent(self):
        """R2 scenario 2: Seeding with get_or_create is idempotent"""
        # Roles already exist from migration; calling get_or_create again should not duplicate
        Rol.objects.get_or_create(nombre='Cliente', defaults={'descripcion': 'Dueño de mascota'})
        Rol.objects.get_or_create(nombre='Veterinario', defaults={'descripcion': 'Veterinario'})
        Rol.objects.get_or_create(nombre='Domiciliario', defaults={'descripcion': 'Domiciliario'})
        Rol.objects.get_or_create(nombre='Administrador', defaults={'descripcion': 'Administrador'})
        self.assertEqual(Rol.objects.count(), 4)

    def test_existing_users_get_cliente_role(self):
        """R3 scenario 1: Existing users assigned Cliente role"""
        User = get_user_model()
        cliente_rol = Rol.objects.get(nombre='Cliente')
        user = User.objects.create_user(
            username='existinguser', email='existing@test.com',
            password='pass123', rol=cliente_rol
        )
        user.refresh_from_db()
        self.assertEqual(user.rol, cliente_rol)


class UsuarioRolTest(TestCase):
    """R4: Usuario rol FK and telefono field"""

    def setUp(self):
        self.cliente_rol = Rol.objects.get(nombre='Cliente')

    def test_user_cannot_save_without_rol(self):
        """R4 scenario 1: User without rol raises IntegrityError"""
        User = get_user_model()
        user = User(username='norol_user', email='norol@test.com')
        user.set_password('testpass123')
        with self.assertRaises(IntegrityError):
            user.save()

    def test_cannot_delete_rol_with_assigned_users(self):
        """R4 scenario 2: Deleting a Rol with users raises ProtectedError"""
        User = get_user_model()
        User.objects.create_user(
            username='protecteduser', email='protected@test.com',
            password='testpass123', rol=self.cliente_rol
        )
        with self.assertRaises(ProtectedError):
            self.cliente_rol.delete()

    def test_telefono_field_exists_and_accepts_values(self):
        """telefono field accepts values up to 15 chars"""
        User = get_user_model()
        user = User.objects.create_user(
            username='phoneuser', email='phone@test.com',
            password='testpass123', rol=self.cliente_rol,
            telefono='3001234567'
        )
        user.refresh_from_db()
        self.assertEqual(user.telefono, '3001234567')

    def test_telefono_can_be_blank(self):
        """telefono can be blank/empty"""
        User = get_user_model()
        user = User.objects.create_user(
            username='blankphone', email='blank@test.com',
            password='testpass123', rol=self.cliente_rol,
            telefono=''
        )
        user.refresh_from_db()
        self.assertEqual(user.telefono, '')


class RegistroFormTest(TestCase):
    """R7-R11: Registration form validation tests"""

    def setUp(self):
        self.cliente_rol = Rol.objects.get(nombre='Cliente')

    # R7: telefono field
    def test_valid_form_saves_telefono(self):
        """R7 scenario 1: Phone is saved during registration"""
        from .forms import RegistroForm
        form = RegistroForm(data={
            'first_name': 'Juan',
            'email': 'juan@test.com',
            'telefono': '3001234567',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
        })
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertEqual(user.telefono, '3001234567')

    def test_blank_telefono_accepted(self):
        """R7 scenario 2: Phone can be blank"""
        from .forms import RegistroForm
        form = RegistroForm(data={
            'first_name': 'Maria',
            'email': 'maria@test.com',
            'telefono': '',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
        })
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['telefono'], '')

    def test_telefono_max_length_enforced(self):
        """R7 scenario 3: Phone exceeding 15 chars is rejected"""
        from .forms import RegistroForm
        form = RegistroForm(data={
            'first_name': 'Pedro',
            'email': 'pedro@test.com',
            'telefono': '1234567890123456',  # 16 chars
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('telefono', form.errors)

    # R8: nombre maps to first_name
    def test_nombre_maps_to_first_name(self):
        """R8 scenario 1: nombre maps to first_name"""
        from .forms import RegistroForm
        form = RegistroForm(data={
            'first_name': 'Carlos',
            'email': 'carlos@test.com',
            'telefono': '3001111111',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
        })
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertEqual(user.first_name, 'Carlos')

    def test_empty_nombre_rejected(self):
        """R8 scenario 2: Empty nombre fails validation"""
        from .forms import RegistroForm
        form = RegistroForm(data={
            'first_name': '',
            'email': 'nome@test.com',
            'telefono': '',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('first_name', form.errors)

    # R9: form validation
    def test_valid_form_creates_user(self):
        """R9 scenario 1: Valid form creates user and assigns Cliente role"""
        from .forms import RegistroForm
        form = RegistroForm(data={
            'first_name': 'Ana',
            'email': 'ana@test.com',
            'telefono': '3002222222',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
        })
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertEqual(user.email, 'ana@test.com')
        self.assertEqual(user.rol, self.cliente_rol)

    def test_duplicate_email_rejected(self):
        """R9 scenario 2: Duplicate email shows error"""
        from .forms import RegistroForm
        User = get_user_model()
        User.objects.create_user(username='existing', email='dup@test.com', password='pass123', rol=self.cliente_rol)
        form = RegistroForm(data={
            'first_name': 'Nuevo',
            'email': 'dup@test.com',
            'telefono': '',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
        })
        self.assertFalse(form.is_valid())

    def test_password_mismatch_error(self):
        """R9 scenario 3: Password confirmation mismatch"""
        from .forms import RegistroForm
        form = RegistroForm(data={
            'first_name': 'Test',
            'email': 'mismatch@test.com',
            'telefono': '',
            'password1': 'TestPass123!',
            'password2': 'DifferentPass456!',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    # R10: nombre required
    def test_missing_nombre_fails_validation(self):
        """R10 scenario 1: Missing nombre fails validation"""
        from .forms import RegistroForm
        form = RegistroForm(data={
            'first_name': '',
            'email': 'noname@test.com',
            'telefono': '',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('first_name', form.errors)

    def test_whitespace_only_nombre_rejected(self):
        """R10 scenario 2: Whitespace-only nombre rejected"""
        from .forms import RegistroForm
        form = RegistroForm(data={
            'first_name': '   ',
            'email': 'ws@test.com',
            'telefono': '',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('first_name', form.errors)

    # R11: phone format validation
    def test_valid_phone_format_accepted(self):
        """R11 scenario 1: Valid phone format accepted"""
        from .forms import RegistroForm
        form = RegistroForm(data={
            'first_name': 'Luis',
            'email': 'luis@test.com',
            'telefono': '+57 300 123',  # 11 chars, valid format
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
        })
        self.assertTrue(form.is_valid(), form.errors)

    def test_phone_with_letters_rejected(self):
        """R11 scenario 2: Phone with letters rejected"""
        from .forms import RegistroForm
        form = RegistroForm(data={
            'first_name': 'Marta',
            'email': 'marta@test.com',
            'telefono': '300abc4567',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('telefono', form.errors)

    # R5: default role assignment (tested via form)
    def test_new_user_defaults_to_cliente_role(self):
        """R5 scenario 1: New user defaults to Cliente role"""
        from .forms import RegistroForm
        form = RegistroForm(data={
            'first_name': 'Nuevo',
            'email': 'nuevo@test.com',
            'telefono': '',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
        })
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertEqual(user.rol, self.cliente_rol)


class RegistroViewTest(TestCase):
    """R5, R9: Registration view tests — register_view uses RegistroForm"""

    def setUp(self):
        self.cliente_rol = Rol.objects.get(nombre='Cliente')

    def test_register_valid_data_creates_user_with_cliente_role(self):
        """R5 scenario 1: New user defaults to Cliente role via view"""
        User = get_user_model()
        resp = self.client.post(reverse('usuarios:register'), data={
            'first_name': 'Ana',
            'email': 'ana@test.com',
            'telefono': '3001111111',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
        })
        # Should redirect after successful registration
        self.assertIn(resp.status_code, [200, 302])
        user = User.objects.get(email='ana@test.com')
        self.assertEqual(user.rol, self.cliente_rol)
        self.assertEqual(user.first_name, 'Ana')

    def test_register_valid_form_redirects(self):
        """R9 scenario 1: Valid form creates user and redirects"""
        User = get_user_model()
        resp = self.client.post(reverse('usuarios:register'), data={
            'first_name': 'Carlos',
            'email': 'carlos@test.com',
            'telefono': '',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
        })
        # Successful registration should redirect or render success
        self.assertIn(resp.status_code, [200, 302])
        self.assertTrue(User.objects.filter(email='carlos@test.com').exists())

    def test_register_duplicate_email_shows_error(self):
        """R9 scenario 2: Duplicate email shows error"""
        User = get_user_model()
        User.objects.create_user(
            username='dup', email='dup@test.com',
            password='pass123', rol=self.cliente_rol
        )
        resp = self.client.post(reverse('usuarios:register'), data={
            'first_name': 'Dup',
            'email': 'dup@test.com',
            'telefono': '',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
        })
        # Should NOT create another user and should show error
        self.assertEqual(User.objects.filter(email='dup@test.com').count(), 1)
        # Should render the page again with errors (not redirect to success)
        self.assertEqual(resp.status_code, 200)

    def test_register_password_mismatch_shows_error(self):
        """R9 scenario 3: Password mismatch shows error"""
        User = get_user_model()
        resp = self.client.post(reverse('usuarios:register'), data={
            'first_name': 'Mismatch',
            'email': 'mismatch@test.com',
            'telefono': '',
            'password1': 'TestPass123!',
            'password2': 'DifferentPass456!',
        })
        # Should NOT create the user
        self.assertFalse(User.objects.filter(email='mismatch@test.com').exists())
        self.assertEqual(resp.status_code, 200)


class AdminViewTest(TestCase):
    """R6: Admin views and decorator tests"""

    def setUp(self):
        User = get_user_model()
        self.admin_rol = Rol.objects.get(nombre='Administrador')
        self.cliente_rol = Rol.objects.get(nombre='Cliente')
        self.admin_user = User.objects.create_user(
            username='adminuser', email='admin@test.com',
            password='adminpass123', rol=self.admin_rol,
            first_name='Admin',
        )
        self.regular_user = User.objects.create_user(
            username='regularuser', email='regular@test.com',
            password='regularpass123', rol=self.cliente_rol,
            first_name='Regular',
        )

    def test_admin_can_access_user_list(self):
        """R6 scenario 1: Admin can change user role — access user list"""
        self.client.force_login(self.admin_user)
        resp = self.client.get(reverse('usuarios:admin_user_list'))
        self.assertEqual(resp.status_code, 200)

    def test_admin_can_change_user_role(self):
        """R6 scenario 1: Admin can change user role"""
        veterinario_rol = Rol.objects.get(nombre='Veterinario')
        self.client.force_login(self.admin_user)
        resp = self.client.post(
            reverse('usuarios:admin_user_edit', args=[self.regular_user.pk]),
            data={'rol': veterinario_rol.pk}
        )
        # Should redirect after successful edit
        self.assertIn(resp.status_code, [200, 302])
        self.regular_user.refresh_from_db()
        self.assertEqual(self.regular_user.rol, veterinario_rol)

    def test_non_admin_gets_403_on_admin_views(self):
        """R6 scenario 2: Non-admin gets 403 on admin views"""
        self.client.force_login(self.regular_user)
        resp = self.client.get(reverse('usuarios:admin_user_list'))
        self.assertEqual(resp.status_code, 403)

    def test_non_admin_gets_403_on_role_change(self):
        """R6 scenario 2: Non-admin cannot change roles"""
        self.client.force_login(self.regular_user)
        resp = self.client.post(
            reverse('usuarios:admin_user_edit', args=[self.admin_user.pk]),
            data={'rol': self.cliente_rol.pk}
        )
        self.assertEqual(resp.status_code, 403)


class UsuariosViewsTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.cliente_rol = Rol.objects.get(nombre='Cliente')
        self.password = "testpass123"
        self.user = User.objects.create_user(
            username="tester",
            email="tester@example.com",
            password=self.password,
            rol=self.cliente_rol,
        )

    def test_auth_page_renders(self):
        resp = self.client.get(reverse("usuarios:auth"))
        self.assertEqual(resp.status_code, 200)

    def test_login_page_renders(self):
        resp = self.client.get(reverse("usuarios:login"))
        self.assertEqual(resp.status_code, 200)

    def test_register_page_renders(self):
        resp = self.client.get(reverse("usuarios:register"), follow=True)
        self.assertEqual(resp.status_code, 200)
        # La vista de registro usa la misma plantilla de login
        self.assertTemplateUsed(resp, "usuarios/login.html")

    def test_products_redirects_when_not_authenticated(self):
        # Acceso a lista de productos requiere login y redirige a /usuarios/
        resp = self.client.get(reverse("productos:lista"))
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith("/usuarios/"))

    def test_products_access_when_authenticated(self):
        # Autenticar sesión directamente usando el usuario personalizado
        self.client.force_login(self.user)
        resp = self.client.get(reverse("productos:lista"))
        self.assertEqual(resp.status_code, 200)


# ========================================
# PHASE 1: Decorator Tests (REQ-01, REQ-02, REQ-03)
# ========================================

# Test views for decorator testing
from .decorators import role_required, veterinario_required, admin_required

@role_required('Veterinario')
def _vet_only_view(request):
    return HttpResponse('OK')

@role_required('Administrador', 'Veterinario')
def _multi_role_view(request):
    return HttpResponse('OK')

@veterinario_required
def _vet_alias_view(request):
    return HttpResponse('OK')

@admin_required
def _admin_alias_view(request):
    return HttpResponse('OK')

# Register test URLs
urlpatterns = [
    path('test/vet-only/', _vet_only_view, name='test_vet_only'),
    path('test/multi-role/', _multi_role_view, name='test_multi_role'),
    path('test/vet-alias/', _vet_alias_view, name='test_vet_alias'),
    path('test/admin-alias/', _admin_alias_view, name='test_admin_alias'),
]

# Inject test URLs into usuarios app
from . import urls as usuarios_urls
usuarios_urls.urlpatterns += urlpatterns


class RoleRequiredDecoratorTest(TestCase):
    """REQ-01: role_required decorator — 4 scenarios"""

    def setUp(self):
        User = get_user_model()
        self.vet_rol = Rol.objects.get(nombre='Veterinario')
        self.cliente_rol = Rol.objects.get(nombre='Cliente')
        self.admin_rol = Rol.objects.get(nombre='Administrador')
        self.vet_user = User.objects.create_user(
            username='vetuser', email='vet@test.com',
            password='vetpass123', rol=self.vet_rol,
        )
        self.cliente_user = User.objects.create_user(
            username='clienteuser', email='cliente@test.com',
            password='clientepass123', rol=self.cliente_rol,
        )
        self.admin_user = User.objects.create_user(
            username='adminuser2', email='admin2@test.com',
            password='adminpass123', rol=self.admin_rol,
        )

    def test_authenticated_vet_accesses_vet_only_view(self):
        """R1 scenario 1: Authenticated user with correct role gets access (200)"""
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('usuarios:test_vet_only'))
        self.assertEqual(resp.status_code, 200)

    def test_authenticated_cliente_gets_403(self):
        """R1 scenario 2: Authenticated user with wrong role gets 403"""
        self.client.force_login(self.cliente_user)
        resp = self.client.get(reverse('usuarios:test_vet_only'))
        self.assertEqual(resp.status_code, 403)

    def test_unauthenticated_gets_redirect(self):
        """R1 scenario 3: Unauthenticated user gets redirected to login (302)"""
        resp = self.client.get(reverse('usuarios:test_vet_only'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse('usuarios:login'), resp.url)

    def test_multi_role_accepts_admin(self):
        """R1 scenario 4: Multiple roles accepted — Admin accesses multi-role view (200)"""
        self.client.force_login(self.admin_user)
        resp = self.client.get(reverse('usuarios:test_multi_role'))
        self.assertEqual(resp.status_code, 200)


class VeterinarioRequiredDecoratorTest(TestCase):
    """REQ-02: veterinario_required alias — 2 scenarios"""

    def setUp(self):
        User = get_user_model()
        self.vet_rol = Rol.objects.get(nombre='Veterinario')
        self.cliente_rol = Rol.objects.get(nombre='Cliente')
        self.vet_user = User.objects.create_user(
            username='vetuser2', email='vet2@test.com',
            password='vetpass123', rol=self.vet_rol,
        )
        self.cliente_user = User.objects.create_user(
            username='clienteuser2', email='cliente2@test.com',
            password='clientepass123', rol=self.cliente_rol,
        )

    def test_vet_user_passes_through_alias(self):
        """R2 scenario 1: Veterinario user passes through (200)"""
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('usuarios:test_vet_alias'))
        self.assertEqual(resp.status_code, 200)

    def test_non_vet_gets_403(self):
        """R2 scenario 2: Non-Veterinario user gets 403"""
        self.client.force_login(self.cliente_user)
        resp = self.client.get(reverse('usuarios:test_vet_alias'))
        self.assertEqual(resp.status_code, 403)


class AdminRequiredBackwardCompatTest(TestCase):
    """REQ-03: admin_required backward compatibility — 3 scenarios"""

    def setUp(self):
        User = get_user_model()
        self.admin_rol = Rol.objects.get(nombre='Administrador')
        self.cliente_rol = Rol.objects.get(nombre='Cliente')
        self.admin_user = User.objects.create_user(
            username='adminuser3', email='admin3@test.com',
            password='adminpass123', rol=self.admin_rol,
            first_name='Admin',
        )
        self.cliente_user = User.objects.create_user(
            username='clienteuser3', email='cliente3@test.com',
            password='clientepass123', rol=self.cliente_rol,
        )

    def test_existing_admin_view_test_still_passes(self):
        """R3 scenario 1: Existing AdminViewTest tests still pass — admin accesses admin_user_list (200)"""
        self.client.force_login(self.admin_user)
        resp = self.client.get(reverse('usuarios:admin_user_list'))
        self.assertEqual(resp.status_code, 200)

    def test_admin_user_accesses_admin_alias_view(self):
        """R3 scenario 2: Admin user can still access admin-required view (200)"""
        self.client.force_login(self.admin_user)
        resp = self.client.get(reverse('usuarios:test_admin_alias'))
        self.assertEqual(resp.status_code, 200)

    def test_non_admin_still_gets_403(self):
        """R3 scenario 3: Non-admin still gets 403"""
        self.client.force_login(self.cliente_user)
        resp = self.client.get(reverse('usuarios:test_admin_alias'))
        self.assertEqual(resp.status_code, 403)


# ========================================
# PHASE 2: Redirect Helper Tests (REQ-08)
# ========================================

class GetRedirectUrlHelperTest(TestCase):
    """REQ-08: get_redirect_url helper — 5 scenarios"""

    def setUp(self):
        User = get_user_model()
        self.admin_rol = Rol.objects.get(nombre='Administrador')
        self.vet_rol = Rol.objects.get(nombre='Veterinario')
        self.cliente_rol = Rol.objects.get(nombre='Cliente')
        self.domiciliario_rol = Rol.objects.get(nombre='Domiciliario')
        self.admin_user = User.objects.create_user(
            username='admin_r8', email='admin_r8@test.com',
            password='pass123', rol=self.admin_rol,
        )
        self.vet_user = User.objects.create_user(
            username='vet_r8', email='vet_r8@test.com',
            password='pass123', rol=self.vet_rol,
        )
        self.cliente_user = User.objects.create_user(
            username='cliente_r8', email='cliente_r8@test.com',
            password='pass123', rol=self.cliente_rol,
        )
        self.domiciliario_user = User.objects.create_user(
            username='domi_r8', email='domi_r8@test.com',
            password='pass123', rol=self.domiciliario_rol,
        )

    def test_returns_admin_url_for_administrador(self):
        """R8 scenario 1: Returns admin URL for Administrador"""
        from .views import get_redirect_url
        url = get_redirect_url(self.admin_user)
        self.assertEqual(url, reverse('usuarios:admin_user_list'))

    def test_returns_vet_dashboard_url_for_veterinario(self):
        """R8 scenario 2: Returns vet dashboard URL for Veterinario"""
        from .views import get_redirect_url
        url = get_redirect_url(self.vet_user)
        self.assertEqual(url, reverse('usuarios:vet_dashboard'))

    def test_returns_mascotas_url_for_cliente(self):
        """R8 scenario 3: Returns mascotas URL for Cliente"""
        from .views import get_redirect_url
        url = get_redirect_url(self.cliente_user)
        self.assertEqual(url, reverse('mascotas:lista'))

    def test_returns_productos_url_for_domiciliario(self):
        """R8 scenario 4: Returns productos URL for Domiciliario"""
        from .views import get_redirect_url
        url = get_redirect_url(self.domiciliario_user)
        self.assertEqual(url, reverse('productos:lista'))

    def test_returns_productos_url_for_unknown_role(self):
        """R8 scenario 5: Handles unexpected role with default (productos:lista)"""
        from .views import get_redirect_url
        # Create a mock user-like object with an unrecognized role
        class MockUser:
            class MockRol:
                nombre = 'Guest'
            rol = MockRol()
        url = get_redirect_url(MockUser())
        self.assertEqual(url, reverse('productos:lista'))


# ========================================
# PHASE 3: Vet Dashboard View Tests (REQ-04)
# ========================================

class VetDashboardViewTest(TestCase):
    """REQ-04: Vet dashboard view — 4 scenarios"""

    def setUp(self):
        User = get_user_model()
        self.vet_rol = Rol.objects.get(nombre='Veterinario')
        self.cliente_rol = Rol.objects.get(nombre='Cliente')
        self.domiciliario_rol = Rol.objects.get(nombre='Domiciliario')
        self.vet_user = User.objects.create_user(
            username='vet_r4', email='vet_r4@test.com',
            password='pass123', rol=self.vet_rol,
            first_name='Dr. García',
        )
        self.cliente_user = User.objects.create_user(
            username='cliente_r4', email='cliente_r4@test.com',
            password='pass123', rol=self.cliente_rol,
        )
        self.domiciliario_user = User.objects.create_user(
            username='domi_r4', email='domi_r4@test.com',
            password='pass123', rol=self.domiciliario_rol,
        )

    def test_vet_accesses_dashboard(self):
        """R4 scenario 1: Veterinario accesses dashboard (200)"""
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('usuarios:vet_dashboard'))
        self.assertEqual(resp.status_code, 200)

    def test_cliente_gets_403(self):
        """R4 scenario 2: Cliente gets 403 Forbidden"""
        self.client.force_login(self.cliente_user)
        resp = self.client.get(reverse('usuarios:vet_dashboard'))
        self.assertEqual(resp.status_code, 403)

    def test_domiciliario_gets_403(self):
        """R4 scenario 3: Domiciliario gets 403 Forbidden"""
        self.client.force_login(self.domiciliario_user)
        resp = self.client.get(reverse('usuarios:vet_dashboard'))
        self.assertEqual(resp.status_code, 403)

    def test_unauthenticated_gets_redirect(self):
        """R4 scenario 4: Unauthenticated gets redirect to login (302)"""
        resp = self.client.get(reverse('usuarios:vet_dashboard'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/usuarios/login/', resp.url)


class VetDashboardTemplateTest(TestCase):
    """REQ-05: Dashboard template — 3 scenarios"""

    def setUp(self):
        User = get_user_model()
        self.vet_rol = Rol.objects.get(nombre='Veterinario')
        self.vet_user = User.objects.create_user(
            username='vet_r5', email='vet_r5@test.com',
            password='pass123', rol=self.vet_rol,
            first_name='Dr. García',
        )

    def test_template_extends_base_and_renders(self):
        """R5 scenario 1: Template renders with 200 status and extends base.html"""
        from django.test import RequestFactory
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('usuarios:vet_dashboard'))
        self.assertEqual(resp.status_code, 200)

    def test_template_contains_navigation_items(self):
        """R5 scenario 2: Template contains nav placeholders for Agenda, Pacientes, Historial Clínico, Servicios"""
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('usuarios:vet_dashboard'))
        content = resp.content.decode()
        self.assertIn('Agenda', content)
        self.assertIn('Pacientes', content)
        self.assertIn('Historial', content)
        self.assertIn('Servicios', content)

    def test_template_shows_vet_welcome(self):
        """R5 scenario 3: Template shows vet-specific welcome message"""
        self.client.force_login(self.vet_user)
        resp = self.client.get(reverse('usuarios:vet_dashboard'))
        content = resp.content.decode()
        self.assertIn('Dr. García', content)
        self.assertIn('Veterinario', content)


class LoginRedirectHtmlTest(TestCase):
    """REQ-06: Role-based login redirect (HTML) — 3 scenarios"""

    def setUp(self):
        User = get_user_model()
        self.vet_rol = Rol.objects.get(nombre='Veterinario')
        self.admin_rol = Rol.objects.get(nombre='Administrador')
        self.cliente_rol = Rol.objects.get(nombre='Cliente')
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

    def test_vet_redirected_to_dashboard(self):
        """R6 scenario 1: Vet user redirected to vet dashboard after login"""
        resp = self.client.post(reverse('usuarios:login'), {
            'email': 'vet_r6@test.com',
            'password': 'pass123',
        })
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse('usuarios:vet_dashboard'), resp.url)

    def test_admin_redirected_to_admin_panel(self):
        """R6 scenario 2: Admin user redirected to admin panel after login"""
        resp = self.client.post(reverse('usuarios:login'), {
            'email': 'admin_r6@test.com',
            'password': 'pass123',
        })
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse('usuarios:admin_user_list'), resp.url)

    def test_client_redirected_to_mascotas(self):
        """R6 scenario 3: Client user redirected to mascotas after login"""
        resp = self.client.post(reverse('usuarios:login'), {
            'email': 'cliente_r6@test.com',
            'password': 'pass123',
        })
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse('mascotas:lista'), resp.url)


class LoginRedirectApiTest(TestCase):
    """REQ-07: Role-based login redirect (API) — 3 scenarios"""

    def setUp(self):
        User = get_user_model()
        self.vet_rol = Rol.objects.get(nombre='Veterinario')
        self.admin_rol = Rol.objects.get(nombre='Administrador')
        self.cliente_rol = Rol.objects.get(nombre='Cliente')
        self.vet_user = User.objects.create_user(
            username='vet_r7', email='vet_r7@test.com',
            password='pass123', rol=self.vet_rol,
        )
        self.admin_user = User.objects.create_user(
            username='admin_r7', email='admin_r7@test.com',
            password='pass123', rol=self.admin_rol,
        )
        self.cliente_user = User.objects.create_user(
            username='cliente_r7', email='cliente_r7@test.com',
            password='pass123', rol=self.cliente_rol,
        )

    def test_vet_api_login_returns_vet_url(self):
        """R7 scenario 1: Vet login API returns vet dashboard redirect_url"""
        from .models import Usuario
        resp = self.client.post(
            reverse('usuarios:api_login'),
            data=json.dumps({'email': 'vet_r7@test.com', 'password': 'pass123'}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertTrue(data['success'])
        self.assertIn(reverse('usuarios:vet_dashboard'), data['redirect_url'])

    def test_admin_api_login_returns_admin_url(self):
        """R7 scenario 2: Admin login API returns admin redirect_url"""
        resp = self.client.post(
            reverse('usuarios:api_login'),
            data=json.dumps({'email': 'admin_r7@test.com', 'password': 'pass123'}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertTrue(data['success'])
        self.assertIn(reverse('usuarios:admin_user_list'), data['redirect_url'])

    def test_client_api_login_returns_mascotas_url(self):
        """R7 scenario 3: Client login API returns mascotas redirect_url"""
        resp = self.client.post(
            reverse('usuarios:api_login'),
            data=json.dumps({'email': 'cliente_r7@test.com', 'password': 'pass123'}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertTrue(data['success'])
        self.assertIn(reverse('mascotas:lista'), data['redirect_url'])


# ========================================
# Perfil Model Tests (Fase E)
# ========================================

class PerfilModelTest(TestCase):
    """Tests for Perfil model — 4 tests (p1.1 - p1.4)"""

    def test_p1_1_creacion_perfil_linked_to_usuario(self):
        """p1.1: Perfil creation linked to Usuario"""
        User = get_user_model()
        cliente_rol = Rol.objects.get(nombre='Cliente')
        user = User.objects.create_user(
            username='perfil_user', email='perfil@test.com',
            password='testpass123', rol=cliente_rol,
        )
        from .models import Perfil
        perfil = Perfil.objects.create(usuario=user, bio='Test bio')
        self.assertEqual(perfil.usuario, user)
        self.assertEqual(perfil.bio, 'Test bio')
        self.assertEqual(str(perfil), f'Perfil de {user.email}')

    def test_p1_2_perfil_foto_exceeds_5mb_validation_error(self):
        """p1.2: Perfil foto exceeds 5MB raises ValidationError"""
        from .models import Perfil, MAX_PERFIL_FOTO_SIZE
        from django.core.files.uploadedfile import SimpleUploadedFile

        User = get_user_model()
        cliente_rol = Rol.objects.get(nombre='Cliente')
        user = User.objects.create_user(
            username='foto_user', email='foto@test.com',
            password='testpass123', rol=cliente_rol,
        )

        large_file = SimpleUploadedFile(
            'test.jpg', b'x' * (MAX_PERFIL_FOTO_SIZE + 1024),
            content_type='image/jpeg'
        )

        perfil = Perfil(usuario=user, bio='Test')
        perfil.foto = large_file
        with self.assertRaises(ValidationError):
            perfil.full_clean()

    def test_p1_3_perfil_str_returns_user_email(self):
        """p1.3: Perfil __str__ returns user email"""
        from .models import Perfil
        User = get_user_model()
        cliente_rol = Rol.objects.get(nombre='Cliente')
        user = User.objects.create_user(
            username='str_user', email='str@test.com',
            password='testpass123', rol=cliente_rol,
        )
        perfil = Perfil.objects.create(usuario=user)
        self.assertEqual(str(perfil), 'Perfil de str@test.com')

    def test_p1_4_delete_user_cascades_to_perfil(self):
        """p1.4: Deleting user cascades to perfil"""
        from .models import Perfil
        User = get_user_model()
        cliente_rol = Rol.objects.get(nombre='Cliente')
        user = User.objects.create_user(
            username='cascade_user', email='cascade@test.com',
            password='testpass123', rol=cliente_rol,
        )
        perfil = Perfil.objects.create(usuario=user, bio='Cascade test')
        user_id = user.pk
        user.delete()
        self.assertFalse(Perfil.objects.filter(usuario_id=user_id).exists())


# ========================================
# Perfil View Tests (Fase E)
# ========================================

class PerfilViewTest(TestCase):
    """Tests for Perfil views — 5 tests (p2.1 - p2.5)"""

    def setUp(self):
        User = get_user_model()
        self.cliente_rol = Rol.objects.get(nombre='Cliente')
        self.admin_rol = Rol.objects.get(nombre='Administrador')
        self.cliente = User.objects.create_user(
            username='perfil_cli', email='perfil_cli@test.com',
            password='testpass123', rol=self.cliente_rol,
        )
        self.admin = User.objects.create_user(
            username='perfil_admin', email='perfil_admin@test.com',
            password='testpass123', rol=self.admin_rol,
        )

    def test_p2_1_mi_perfil_shows_current_user_profile(self):
        """p2.1: mi_perfil shows current user's profile"""
        from .models import Perfil
        Perfil.objects.create(usuario=self.cliente, bio='Mi bio')
        self.client.force_login(self.cliente)
        resp = self.client.get(reverse('usuarios:mi_perfil'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Mi bio')

    def test_p2_2_mi_perfil_post_updates_bio(self):
        """p2.2: mi_perfil POST updates bio"""
        from .models import Perfil
        Perfil.objects.create(usuario=self.cliente, bio='Vieja bio')
        self.client.force_login(self.cliente)
        resp = self.client.post(reverse('usuarios:mi_perfil'), {'bio': 'Nueva bio actualizada'})
        self.assertEqual(resp.status_code, 302)
        perfil = Perfil.objects.get(usuario=self.cliente)
        self.assertEqual(perfil.bio, 'Nueva bio actualizada')

    def test_p2_3_mi_perfil_requires_login(self):
        """p2.3: mi_perfil requires login (302 redirect)"""
        resp = self.client.get(reverse('usuarios:mi_perfil'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/usuarios/login/', resp.url)

    def test_p2_4_lista_usuarios_admin_can_see_all(self):
        """p2.4: lista_usuarios Admin can see all users"""
        self.client.force_login(self.admin)
        resp = self.client.get(reverse('usuarios:lista_usuarios'))
        self.assertEqual(resp.status_code, 200)

    def test_p2_5_lista_usuarios_cliente_gets_403(self):
        """p2.5: lista_usuarios Cliente gets 403"""
        self.client.force_login(self.cliente)
        resp = self.client.get(reverse('usuarios:lista_usuarios'))
        self.assertEqual(resp.status_code, 403)