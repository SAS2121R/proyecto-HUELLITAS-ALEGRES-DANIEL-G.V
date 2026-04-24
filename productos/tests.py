from datetime import date
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import ProtectedError

from .models import Producto, MovimientoInventario, CATEGORIAS, TIPO_MOVIMIENTO_CHOICES
from usuarios.models import Rol
from mascotas.models import Mascota
from historial.models import HistorialClinico

User = get_user_model()


# ========================================
# Helper
# ========================================

def create_user_with_role(rol_nombre, **kwargs):
    """Helper to create a user with the given role."""
    rol, _ = Rol.objects.get_or_create(nombre=rol_nombre)
    user = User.objects.create_user(
        username=kwargs.get('username', f'user_{rol_nombre.lower()}'),
        email=kwargs.get('email', f'{rol_nombre.lower()}@test.com'),
        password='testpass123',
        rol=rol,
    )
    return user


def create_producto(**kwargs):
    """Helper to create a product with sensible defaults."""
    defaults = {
        'nombre': 'Producto Test',
        'descripcion': 'Descripción de prueba',
        'precio': '10.00',
        'cantidad_stock': 50,
        'stock_minimo': 10,
        'categoria': 'otros',
    }
    defaults.update(kwargs)
    return Producto.all_objects.create(**defaults)


# ========================================
# R1: Producto Model — Extended Fields
# ========================================

class ProductoModelTest(TestCase):
    """Tests for extended Producto model fields and constraints."""

    def test_creacion_basica(self):
        """R1.1: Create Producto with all new fields"""
        p = create_producto(
            nombre='Vacuna Rabia',
            categoria='vacunas',
            stock_minimo=5,
            proveedor='LabVet',
            esta_activo=True,
        )
        self.assertEqual(p.categoria, 'vacunas')
        self.assertEqual(p.stock_minimo, 5)
        self.assertEqual(p.proveedor, 'LabVet')
        self.assertTrue(p.esta_activo)

    def test_nombre_unique(self):
        """R1.2: Producto nombre must be unique"""
        create_producto(nombre='Producto A')
        with self.assertRaises(Exception):
            create_producto(nombre='Producto A')

    def test_categorias_count(self):
        """R1.3: 7 categories exist in CATEGORIAS"""
        self.assertEqual(len(CATEGORIAS), 7)

    def test_stock_minimo_default(self):
        """R1.4: stock_minimo defaults to 10"""
        p = create_producto()
        self.assertEqual(p.stock_minimo, 10)

    def test_stock_minimo_negative_rejected(self):
        """R1.5: stock_minimo cannot be negative"""
        p = create_producto()
        p.stock_minimo = -1
        with self.assertRaises(ValidationError):
            p.full_clean()

    def test_proveedor_blank(self):
        """R1.6: proveedor can be blank"""
        p = create_producto(proveedor='')
        self.assertEqual(p.proveedor, '')

    def test_esta_activo_default_true(self):
        """R1.7: esta_activo defaults to True"""
        p = create_producto()
        self.assertTrue(p.esta_activo)

    def test_cantidad_stock_allows_negative(self):
        """R1.8: cantidad_stock CAN be negative (medical priority)"""
        p = create_producto(cantidad_stock=-5)
        p.full_clean()  # Should NOT raise
        self.assertEqual(p.cantidad_stock, -5)

    def test_fecha_creacion_is_datetime(self):
        """R1.9: fecha_creacion is DateTimeField (upgraded from DateField)"""
        p = create_producto()
        self.assertIsNotNone(p.fecha_creacion)
        self.assertTrue(hasattr(p.fecha_creacion, 'hour'))

    def test_str_returns_nombre(self):
        """R1.10: __str__ returns product nombre"""
        p = create_producto(nombre='Vacuna Triple')
        self.assertEqual(str(p), 'Vacuna Triple')


# ========================================
# R2: Producto estado_stock — Semáforo
# ========================================

class ProductoEstadoStockTest(TestCase):
    """Tests for estado_stock property returning semáforo color."""

    def test_verde(self):
        """R2.1: Stock > stock_minimo * 1.5 returns verde"""
        p = create_producto(cantidad_stock=50, stock_minimo=10)
        self.assertEqual(p.estado_stock, 'verde')

    def test_amarillo(self):
        """R2.2: 0 < stock <= stock_minimo * 1.5 returns amarillo"""
        p = create_producto(cantidad_stock=8, stock_minimo=10)
        self.assertEqual(p.estado_stock, 'amarillo')

    def test_amarillo_at_threshold(self):
        """R2.3: stock == stock_minimo * 1.5 exactly returns amarillo"""
        p = create_producto(cantidad_stock=15, stock_minimo=10)
        self.assertEqual(p.estado_stock, 'amarillo')

    def test_rojo_zero(self):
        """R2.4: Stock == 0 returns rojo"""
        p = create_producto(cantidad_stock=0, stock_minimo=10)
        self.assertEqual(p.estado_stock, 'rojo')

    def test_rojo_negative(self):
        """R2.5: Stock < 0 returns rojo"""
        p = create_producto(cantidad_stock=-3, stock_minimo=10)
        self.assertEqual(p.estado_stock, 'rojo')

    def test_rojo_one_with_min_one(self):
        """R2.6: Stock=1, stock_minimo=1 returns amarillo (1 > 0 and 1 <= 1.5)"""
        p = create_producto(cantidad_stock=1, stock_minimo=1)
        self.assertEqual(p.estado_stock, 'amarillo')


# ========================================
# R3: ProductoManager — Soft Delete
# ========================================

class ProductoManagerTest(TestCase):
    """Tests for ProductoManager filtering esta_activo=True by default."""

    def test_default_queryset_filters_active(self):
        """R3.1: Producto.objects filters esta_activo=True"""
        create_producto(nombre='Activo', esta_activo=True)
        create_producto(nombre='Inactivo', esta_activo=False)
        self.assertEqual(Producto.objects.count(), 1)
        self.assertEqual(Producto.objects.first().nombre, 'Activo')

    def test_all_objects_includes_inactive(self):
        """R3.2: Producto.all_objects includes inactive products"""
        create_producto(nombre='Activo', esta_activo=True)
        create_producto(nombre='Inactivo', esta_activo=False)
        self.assertEqual(Producto.all_objects.count(), 2)

    def test_soft_delete_does_not_remove(self):
        """R3.3: Setting esta_activo=False hides from default queryset but keeps row"""
        p = create_producto(nombre='ToDelete')
        p.esta_activo = False
        p.save()
        self.assertEqual(Producto.objects.count(), 0)
        self.assertEqual(Producto.all_objects.count(), 1)


# ========================================
# R4: MovimientoInventario Model
# ========================================

class MovimientoInventarioModelTest(TestCase):
    """Tests for MovimientoInventario model and constraints."""

    def setUp(self):
        self.producto = create_producto(nombre='Vacuna Rabia', categoria='vacunas')
        self.vet = create_user_with_role('Veterinario', username='vet_mov', email='vet_mov@test.com')

    def test_create_entrada(self):
        """R4.1: Create entrada movement"""
        mov = MovimientoInventario.objects.create(
            producto=self.producto,
            tipo_movimiento='entrada',
            cantidad=10,
            usuario=self.vet,
            motivo='Compra inicial',
        )
        self.assertEqual(mov.tipo_movimiento, 'entrada')
        self.assertEqual(mov.cantidad, 10)
        self.assertIsNotNone(mov.fecha)

    def test_create_salida(self):
        """R4.2: Create salida movement"""
        mov = MovimientoInventario.objects.create(
            producto=self.producto,
            tipo_movimiento='salida',
            cantidad=1,
            usuario=self.vet,
            motivo='Uso en consulta',
        )
        self.assertEqual(mov.tipo_movimiento, 'salida')

    def test_create_ajuste(self):
        """R4.3: Create ajuste movement"""
        mov = MovimientoInventario.objects.create(
            producto=self.producto,
            tipo_movimiento='ajuste',
            cantidad=5,
            usuario=self.vet,
            motivo='Ajuste por inventario',
        )
        self.assertEqual(mov.tipo_movimiento, 'ajuste')

    def test_producto_protect(self):
        """R4.4: Cannot delete Producto with MovimientoInventario records"""
        MovimientoInventario.objects.create(
            producto=self.producto,
            tipo_movimiento='entrada',
            cantidad=10,
            usuario=self.vet,
        )
        with self.assertRaises(ProtectedError):
            self.producto.delete()

    def test_movimiento_ordering(self):
        """R4.5: Movimientos ordered by fecha descending (newest first)"""
        mov1 = MovimientoInventario.objects.create(
            producto=self.producto, tipo_movimiento='entrada', cantidad=10, usuario=self.vet,
        )
        mov2 = MovimientoInventario.objects.create(
            producto=self.producto, tipo_movimiento='salida', cantidad=1, usuario=self.vet,
        )
        movs = list(MovimientoInventario.objects.all())
        # Both may have same timestamp; verify ordering Meta is set correctly
        self.assertEqual(MovimientoInventario._meta.ordering, ['-fecha'])
        self.assertEqual(len(movs), 2)

    def test_cantidad_min_validator(self):
        """R4.6: cantidad must be >= 1"""
        mov = MovimientoInventario(
            producto=self.producto,
            tipo_movimiento='entrada',
            cantidad=0,
            usuario=self.vet,
        )
        with self.assertRaises(ValidationError):
            mov.full_clean()

    def test_historial_clinico_nullable(self):
        """R4.7: historial_clinico can be null (manual movements)"""
        mov = MovimientoInventario.objects.create(
            producto=self.producto,
            tipo_movimiento='entrada',
            cantidad=10,
            usuario=self.vet,
        )
        self.assertIsNone(mov.historial_clinico)

    def test_motivo_blank(self):
        """R4.8: motivo can be blank"""
        mov = MovimientoInventario.objects.create(
            producto=self.producto,
            tipo_movimiento='entrada',
            cantidad=10,
            usuario=self.vet,
            motivo='',
        )
        self.assertEqual(mov.motivo, '')

    def test_tipo_movimiento_choices(self):
        """R4.9: TIPO_MOVIMIENTO_CHOICES has entrada, salida, ajuste"""
        tipos = [t[0] for t in TIPO_MOVIMIENTO_CHOICES]
        self.assertIn('entrada', tipos)
        self.assertIn('salida', tipos)
        self.assertIn('ajuste', tipos)


# ========================================
# R5: Signal — Auto stock deduction on HistorialClinico
# ========================================

class HistorialSignalTest(TestCase):
    """Tests for post_save signal on HistorialClinico auto-deducting stock."""

    def setUp(self):
        self.vet = create_user_with_role('Veterinario', username='vet_signal', email='vet_signal@test.com')
        self.cliente = create_user_with_role('Cliente', username='cliente_signal', email='cliente_signal@test.com')
        self.mascota = Mascota.objects.create(
            nombre='Firulais', especie='Canino', sexo='Macho',
            propietario=self.cliente,
        )
        self.producto = create_producto(nombre='Vacuna Rabia', categoria='vacunas', cantidad_stock=10)

    def _create_historial(self, producto_aplicado=None):
        """Helper to create a HistorialClinico instance."""
        return HistorialClinico.objects.create(
            mascota=self.mascota,
            veterinario=self.vet,
            tipo_consulta='vacunacion',
            motivo_consulta='Vacunación anual',
            diagnostico='Vacuna aplicada',
            producto_aplicado=producto_aplicado,
        )

    def test_signal_deducts_stock_on_historial_create(self):
        """R5.1: Creating HistorialClinico with producto_aplicado deducts 1 from stock"""
        initial_stock = self.producto.cantidad_stock
        self._create_historial(producto_aplicado=self.producto)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.cantidad_stock, initial_stock - 1)

    def test_signal_creates_movimiento_salida(self):
        """R5.2: Creating HistorialClinico with producto_aplicado creates MovimientoInventario(tipo='salida')"""
        self._create_historial(producto_aplicado=self.producto)
        mov = MovimientoInventario.objects.filter(producto=self.producto, tipo_movimiento='salida').first()
        self.assertIsNotNone(mov)
        self.assertEqual(mov.cantidad, 1)
        self.assertEqual(mov.usuario, self.vet)

    def test_signal_no_deduct_for_servicios(self):
        """R5.3: Categoria 'servicios' does NOT deduct stock"""
        servicio = create_producto(nombre='Consulta General', categoria='servicios', cantidad_stock=5)
        initial_stock = servicio.cantidad_stock
        self._create_historial(producto_aplicado=servicio)
        servicio.refresh_from_db()
        self.assertEqual(servicio.cantidad_stock, initial_stock)

    def test_signal_no_deduct_without_producto(self):
        """R5.4: HistorialClinico without producto_aplicado does NOT deduct stock"""
        initial_stock = self.producto.cantidad_stock
        self._create_historial(producto_aplicado=None)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.cantidad_stock, initial_stock)

    def test_signal_allows_negative_stock(self):
        """R5.5: Stock can go negative — never block clinical record creation"""
        producto_low = create_producto(nombre='Antipulgas', categoria='medicamentos', cantidad_stock=0)
        h = self._create_historial(producto_aplicado=producto_low)
        producto_low.refresh_from_db()
        self.assertEqual(producto_low.cantidad_stock, -1)
        # No exception raised — medical priority

    def test_signal_does_not_fire_on_update(self):
        """R5.6: Signal should only fire on create, not on update"""
        initial_stock = self.producto.cantidad_stock
        h = self._create_historial(producto_aplicado=self.producto)
        self.producto.refresh_from_db()
        stock_after_create = self.producto.cantidad_stock
        self.assertEqual(stock_after_create, initial_stock - 1)

        # Update the historial — stock should NOT change again
        h.diagnostico = 'Vacuna exitosa'
        h.save()
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.cantidad_stock, stock_after_create)

    def test_signal_movimiento_linked_to_historial(self):
        """R5.7: MovimientoInventario is linked to the HistorialClinico record"""
        h = self._create_historial(producto_aplicado=self.producto)
        mov = MovimientoInventario.objects.filter(producto=self.producto).first()
        self.assertIsNotNone(mov)
        self.assertEqual(mov.historial_clinico_id, h.pk)


# ========================================
# R6: ProductoForm
# ========================================

class ProductoFormTest(TestCase):
    """Tests for ProductoForm with extended fields."""

    def test_form_includes_new_fields(self):
        """R6.1: ProductoForm includes categoria, stock_minimo, proveedor fields"""
        from .forms import ProductoForm
        form = ProductoForm()
        self.assertIn('categoria', form.fields)
        self.assertIn('stock_minimo', form.fields)
        self.assertIn('proveedor', form.fields)

    def test_form_valid_data(self):
        """R6.2: ProductoForm valid data passes"""
        from .forms import ProductoForm
        form = ProductoForm(data={
            'nombre': 'Test Product',
            'descripcion': 'Test desc',
            'precio': '10.00',
            'cantidad_stock': 50,
            'categoria': 'otros',
            'stock_minimo': 10,
            'proveedor': 'TestProv',
        })
        self.assertTrue(form.is_valid(), form.errors)

    def test_form_rejects_negative_stock_minimo(self):
        """R6.3: ProductoForm rejects negative stock_minimo"""
        from .forms import ProductoForm
        form = ProductoForm(data={
            'nombre': 'Test Product',
            'descripcion': 'Test desc',
            'precio': '10.00',
            'cantidad_stock': 50,
            'categoria': 'otros',
            'stock_minimo': -5,
            'proveedor': '',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('stock_minimo', form.errors)

    def test_form_excludes_esta_activo(self):
        """R6.4: ProductoForm does NOT include esta_activo field"""
        from .forms import ProductoForm
        form = ProductoForm()
        self.assertNotIn('esta_activo', form.fields)


# ========================================
# R7: MovimientoInventarioForm
# ========================================

class MovimientoInventarioFormTest(TestCase):
    """Tests for MovimientoInventarioForm."""

    def test_form_excludes_usuario_and_historial(self):
        """R7.1: Form excludes usuario and historial_clinico fields"""
        from .forms import MovimientoInventarioForm
        form = MovimientoInventarioForm()
        self.assertNotIn('usuario', form.fields)
        self.assertNotIn('historial_clinico', form.fields)

    def test_form_valid_data(self):
        """R7.2: Form valid with product, tipo, cantidad, motivo"""
        from .forms import MovimientoInventarioForm
        p = create_producto(nombre='FormTest Product')
        form = MovimientoInventarioForm(data={
            'producto': p.pk,
            'tipo_movimiento': 'entrada',
            'cantidad': 10,
            'motivo': 'Reposición',
        })
        self.assertTrue(form.is_valid(), form.errors)

    def test_form_rejects_cantidad_zero(self):
        """R7.3: Form rejects cantidad < 1"""
        from .forms import MovimientoInventarioForm
        p = create_producto(nombre='FormTest Product2')
        form = MovimientoInventarioForm(data={
            'producto': p.pk,
            'tipo_movimiento': 'entrada',
            'cantidad': 0,
            'motivo': 'Test',
        })
        self.assertFalse(form.is_valid())


# ========================================
# R8: Producto View Tests
# ========================================

class ProductoViewTest(TestCase):
    """Tests for Producto views — listing, search, filter, soft delete."""

    def setUp(self):
        self.vet = create_user_with_role('Veterinario', username='vet_pv', email='vet_pv@test.com')
        self.admin = create_user_with_role('Administrador', username='admin_pv', email='admin_pv@test.com')
        self.cliente = create_user_with_role('Cliente', username='cli_pv', email='cli_pv@test.com')
        self.p1 = create_producto(nombre='Vacuna Rabia', categoria='vacunas', cantidad_stock=5)
        self.p2 = create_producto(nombre='Antipulgas', categoria='medicamentos', cantidad_stock=20)
        self.p3 = create_producto(nombre='Consulta General', categoria='servicios', cantidad_stock=100)

    def test_lista_shows_active_products(self):
        """R8.1: lista_productos shows active products only"""
        self.p2.esta_activo = False
        self.p2.save()
        self.client.force_login(self.admin)
        resp = self.client.get(reverse('productos:lista'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Vacuna Rabia')
        self.assertNotContains(resp, 'Antipulgas')

    def test_lista_search_by_name(self):
        """R8.2: lista_productos search filters by name"""
        self.client.force_login(self.admin)
        resp = self.client.get(reverse('productos:lista'), {'q': 'Vacuna'})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Vacuna Rabia')
        self.assertNotContains(resp, 'Antipulgas')

    def test_lista_category_filter(self):
        """R8.3: lista_productos category filter"""
        self.client.force_login(self.admin)
        resp = self.client.get(reverse('productos:lista'), {'categoria': 'vacunas'})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Vacuna Rabia')
        self.assertNotContains(resp, 'Antipulgas')

    def test_soft_delete(self):
        """R8.4: delete_product soft-deletes (sets esta_activo=False)"""
        self.client.force_login(self.vet)
        resp = self.client.post(reverse('productos:eliminar', kwargs={'pk': self.p1.pk}))
        self.assertEqual(resp.status_code, 302)
        # Use all_objects because default manager filters out inactive
        self.p1 = Producto.all_objects.get(pk=self.p1.pk)
        self.assertFalse(self.p1.esta_activo)
        # Hard count unchanged
        self.assertEqual(Producto.all_objects.filter(pk=self.p1.pk).count(), 1)

    def test_create_requires_vet_or_admin(self):
        """R8.5: create_product requires Vet/Admin role"""
        self.client.force_login(self.cliente)
        resp = self.client.get(reverse('productos:nuevo'))
        self.assertEqual(resp.status_code, 403)

    def test_edit_requires_vet_or_admin(self):
        """R8.6: edit_product requires Vet/Admin role"""
        self.client.force_login(self.cliente)
        resp = self.client.get(reverse('productos:editar', kwargs={'pk': self.p1.pk}))
        self.assertEqual(resp.status_code, 403)


# ========================================
# R9: Kardex View
# ========================================

class KardexViewTest(TestCase):
    """Tests for Kardex (product movement history) view."""

    def setUp(self):
        self.vet = create_user_with_role('Veterinario', username='vet_kx', email='vet_kx@test.com')
        self.cliente = create_user_with_role('Cliente', username='cli_kx', email='cli_kx@test.com')
        self.producto = create_producto(nombre='Vacuna Rabia', categoria='vacunas', cantidad_stock=10)

    def test_kardex_shows_movimientos(self):
        """R9.1: kardex shows MovimientoInventario for a product"""
        MovimientoInventario.objects.create(
            producto=self.producto, tipo_movimiento='entrada', cantidad=10,
            usuario=self.vet, motivo='Initial stock',
        )
        self.client.force_login(self.vet)
        resp = self.client.get(reverse('productos:kardex', kwargs={'pk': self.producto.pk}))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Entrada')

    def test_kardex_requires_login(self):
        """R9.2: kardex requires login"""
        resp = self.client.get(reverse('productos:kardex', kwargs={'pk': self.producto.pk}))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/usuarios/login/', resp.url)


# ========================================
# R10: Alertas Stock View
# ========================================

class AlertasViewTest(TestCase):
    """Tests for alertas_stock view — shows low-stock products."""

    def setUp(self):
        self.vet = create_user_with_role('Veterinario', username='vet_al', email='vet_al@test.com')
        self.admin = create_user_with_role('Administrador', username='admin_al', email='admin_al@test.com')
        self.p_verde = create_producto(nombre='Stock OK', cantidad_stock=100, stock_minimo=10)
        self.p_amarillo = create_producto(nombre='Stock Bajo', cantidad_stock=12, stock_minimo=10)
        self.p_rojo = create_producto(nombre='Stock Critico', cantidad_stock=0, stock_minimo=10)

    def test_alertas_shows_non_verde_products(self):
        """R10.1: alertas shows products with estado_stock != 'verde'"""
        self.client.force_login(self.admin)
        resp = self.client.get(reverse('productos:alertas'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Stock Bajo')
        self.assertContains(resp, 'Stock Critico')
        self.assertNotContains(resp, 'Stock OK')

    def test_alertas_requires_login(self):
        """R10.2: alertas requires login"""
        resp = self.client.get(reverse('productos:alertas'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/usuarios/login/', resp.url)