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
from proveedores.models import Proveedor

User = get_user_model()


# ========================================
# Auxiliar
# ========================================

def create_user_with_role(rol_nombre, **kwargs):
    """Auxiliar para crear un usuario con el rol especificado."""
    rol, _ = Rol.objects.get_or_create(nombre=rol_nombre)
    user = User.objects.create_user(
        username=kwargs.get('username', f'user_{rol_nombre.lower()}'),
        email=kwargs.get('email', f'{rol_nombre.lower()}@test.com'),
        password='testpass123',
        rol=rol,
    )
    return user


def create_producto(**kwargs):
    """Auxiliar para crear un producto con valores predeterminados razonables."""
    defaults = {
        'nombre': 'Producto Test',
        'descripcion': 'Descripción de prueba',
        'precio': '10.00',
        'cantidad_stock': 50,
        'stock_minimo': 10,
        'categoria': 'otros',
    }
    # Manejar proveedor: acepta instancia de Proveedor, None, o string (crea Proveedor)
    proveedor_val = kwargs.pop('proveedor', None)
    if isinstance(proveedor_val, str) and proveedor_val:
        proveedor_val, _ = Proveedor.objects.get_or_create(nombre=proveedor_val)
    elif proveedor_val is not None and not isinstance(proveedor_val, Proveedor):
        proveedor_val = None
    defaults['proveedor'] = proveedor_val
    defaults.update(kwargs)
    return Producto.all_objects.create(**defaults)


# ========================================
# R1: Modelo Producto — Campos Extendidos
# ========================================

class ProductoModelTest(TestCase):
    """Pruebas para campos y restricciones del modelo Producto extendido."""

    def test_creacion_basica(self):
        """R1.1: Crear Producto con todos los campos nuevos"""
        p = create_producto(
            nombre='Vacuna Rabia',
            categoria='vacunas',
            stock_minimo=5,
            proveedor='LabVet',
            esta_activo=True,
        )
        self.assertEqual(p.categoria, 'vacunas')
        self.assertEqual(p.stock_minimo, 5)
        self.assertEqual(p.proveedor.nombre, 'LabVet')
        self.assertTrue(p.esta_activo)

    def test_nombre_unique(self):
        """R1.2: El nombre de Producto debe ser único"""
        create_producto(nombre='Producto A')
        with self.assertRaises(Exception):
            create_producto(nombre='Producto A')

    def test_categorias_count(self):
        """R1.3: Existen 7 categorías en CATEGORIAS"""
        self.assertEqual(len(CATEGORIAS), 7)

    def test_stock_minimo_default(self):
        """R1.4: stock_minimo tiene valor predeterminado de 10"""
        p = create_producto()
        self.assertEqual(p.stock_minimo, 10)

    def test_stock_minimo_negative_rejected(self):
        """R1.5: stock_minimo no puede ser negativo"""
        p = create_producto()
        p.stock_minimo = -1
        with self.assertRaises(ValidationError):
            p.full_clean()

    def test_proveedor_blank(self):
        """R1.6: proveedor puede ser nulo (sin proveedor asignado)"""
        p = create_producto(proveedor=None)
        self.assertIsNone(p.proveedor)

    def test_esta_activo_default_true(self):
        """R1.7: esta_activo tiene valor predeterminado de True"""
        p = create_producto()
        self.assertTrue(p.esta_activo)

    def test_cantidad_stock_allows_negative(self):
        """R1.8: cantidad_stock PUEDE ser negativo (prioridad médica)"""
        p = create_producto(cantidad_stock=-5)
        p.full_clean()  # NO debe lanzar
        self.assertEqual(p.cantidad_stock, -5)

    def test_fecha_creacion_is_datetime(self):
        """R1.9: fecha_creacion es DateTimeField (actualizado desde DateField)"""
        p = create_producto()
        self.assertIsNotNone(p.fecha_creacion)
        self.assertTrue(hasattr(p.fecha_creacion, 'hour'))

    def test_str_returns_nombre(self):
        """R1.10: __str__ retorna el nombre del producto"""
        p = create_producto(nombre='Vacuna Triple')
        self.assertEqual(str(p), 'Vacuna Triple')


# ========================================
# R2: estado_stock de Producto — Semáforo
# ========================================

class ProductoEstadoStockTest(TestCase):
    """Pruebas para propiedad estado_stock retornando color de semáforo."""

    def test_verde(self):
        """R2.1: Stock > stock_minimo * 1.5 retorna verde"""
        p = create_producto(cantidad_stock=50, stock_minimo=10)
        self.assertEqual(p.estado_stock, 'verde')

    def test_amarillo(self):
        """R2.2: 0 < stock <= stock_minimo * 1.5 retorna amarillo"""
        p = create_producto(cantidad_stock=8, stock_minimo=10)
        self.assertEqual(p.estado_stock, 'amarillo')

    def test_amarillo_at_threshold(self):
        """R2.3: stock == stock_minimo * 1.5 exactamente retorna amarillo"""
        p = create_producto(cantidad_stock=15, stock_minimo=10)
        self.assertEqual(p.estado_stock, 'amarillo')

    def test_rojo_zero(self):
        """R2.4: Stock == 0 retorna rojo"""
        p = create_producto(cantidad_stock=0, stock_minimo=10)
        self.assertEqual(p.estado_stock, 'rojo')

    def test_rojo_negative(self):
        """R2.5: Stock < 0 retorna rojo"""
        p = create_producto(cantidad_stock=-3, stock_minimo=10)
        self.assertEqual(p.estado_stock, 'rojo')

    def test_rojo_one_with_min_one(self):
        """R2.6: Stock=1, stock_minimo=1 retorna amarillo (1 > 0 y 1 <= 1.5)"""
        p = create_producto(cantidad_stock=1, stock_minimo=1)
        self.assertEqual(p.estado_stock, 'amarillo')


# ========================================
# R3: ProductoManager — Eliminación Suave
# ========================================

class ProductoManagerTest(TestCase):
    """Pruebas para ProductoManager filtrando esta_activo=True por defecto."""

    def test_default_queryset_filters_active(self):
        """R3.1: Producto.objects filtra esta_activo=True"""
        create_producto(nombre='Activo', esta_activo=True)
        create_producto(nombre='Inactivo', esta_activo=False)
        self.assertEqual(Producto.objects.count(), 1)
        self.assertEqual(Producto.objects.first().nombre, 'Activo')

    def test_all_objects_includes_inactive(self):
        """R3.2: Producto.all_objects incluye productos inactivos"""
        create_producto(nombre='Activo', esta_activo=True)
        create_producto(nombre='Inactivo', esta_activo=False)
        self.assertEqual(Producto.all_objects.count(), 2)

    def test_soft_delete_does_not_remove(self):
        """R3.3: Establecer esta_activo=False oculta del queryset por defecto pero mantiene la fila"""
        p = create_producto(nombre='ToDelete')
        p.esta_activo = False
        p.save()
        self.assertEqual(Producto.objects.count(), 0)
        self.assertEqual(Producto.all_objects.count(), 1)


# ========================================
# R4: Modelo MovimientoInventario
# ========================================

class MovimientoInventarioModelTest(TestCase):
    """Pruebas para modelo y restricciones de MovimientoInventario."""

    def setUp(self):
        self.producto = create_producto(nombre='Vacuna Rabia', categoria='vacunas')
        self.vet = create_user_with_role('Veterinario', username='vet_mov', email='vet_mov@test.com')

    def test_create_entrada(self):
        """R4.1: Crear movimiento de entrada"""
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
        """R4.2: Crear movimiento de salida"""
        mov = MovimientoInventario.objects.create(
            producto=self.producto,
            tipo_movimiento='salida',
            cantidad=1,
            usuario=self.vet,
            motivo='Uso en consulta',
        )
        self.assertEqual(mov.tipo_movimiento, 'salida')

    def test_create_ajuste(self):
        """R4.3: Crear movimiento de ajuste"""
        mov = MovimientoInventario.objects.create(
            producto=self.producto,
            tipo_movimiento='ajuste',
            cantidad=5,
            usuario=self.vet,
            motivo='Ajuste por inventario',
        )
        self.assertEqual(mov.tipo_movimiento, 'ajuste')

    def test_producto_protect(self):
        """R4.4: No se puede eliminar Producto con registros de MovimientoInventario"""
        MovimientoInventario.objects.create(
            producto=self.producto,
            tipo_movimiento='entrada',
            cantidad=10,
            usuario=self.vet,
        )
        with self.assertRaises(ProtectedError):
            self.producto.delete()

    def test_movimiento_ordering(self):
        """R4.5: Movimientos ordenados por fecha descendente (más reciente primero)"""
        mov1 = MovimientoInventario.objects.create(
            producto=self.producto, tipo_movimiento='entrada', cantidad=10, usuario=self.vet,
        )
        mov2 = MovimientoInventario.objects.create(
            producto=self.producto, tipo_movimiento='salida', cantidad=1, usuario=self.vet,
        )
        movs = list(MovimientoInventario.objects.all())
        # Ambos pueden tener la misma marca de tiempo; verificar que Meta ordering está configurado correctamente
        self.assertEqual(MovimientoInventario._meta.ordering, ['-fecha'])
        self.assertEqual(len(movs), 2)

    def test_cantidad_min_validator(self):
        """R4.6: cantidad debe ser >= 1"""
        mov = MovimientoInventario(
            producto=self.producto,
            tipo_movimiento='entrada',
            cantidad=0,
            usuario=self.vet,
        )
        with self.assertRaises(ValidationError):
            mov.full_clean()

    def test_historial_clinico_nullable(self):
        """R4.7: historial_clinico puede ser nulo (movimientos manuales)"""
        mov = MovimientoInventario.objects.create(
            producto=self.producto,
            tipo_movimiento='entrada',
            cantidad=10,
            usuario=self.vet,
        )
        self.assertIsNone(mov.historial_clinico)

    def test_motivo_blank(self):
        """R4.8: motivo puede estar en blanco"""
        mov = MovimientoInventario.objects.create(
            producto=self.producto,
            tipo_movimiento='entrada',
            cantidad=10,
            usuario=self.vet,
            motivo='',
        )
        self.assertEqual(mov.motivo, '')

    def test_tipo_movimiento_choices(self):
        """R4.9: TIPO_MOVIMIENTO_CHOICES tiene entrada, salida, ajuste"""
        tipos = [t[0] for t in TIPO_MOVIMIENTO_CHOICES]
        self.assertIn('entrada', tipos)
        self.assertIn('salida', tipos)
        self.assertIn('ajuste', tipos)


# ========================================
# R5: Señal — Deducción Automática de Stock en HistorialClinico
# ========================================

class HistorialSignalTest(TestCase):
    """Pruebas para señal post_save en HistorialClinico que deduce stock automáticamente."""

    def setUp(self):
        self.vet = create_user_with_role('Veterinario', username='vet_signal', email='vet_signal@test.com')
        self.cliente = create_user_with_role('Cliente', username='cliente_signal', email='cliente_signal@test.com')
        self.mascota = Mascota.objects.create(
            nombre='Firulais', especie='Canino', sexo='Macho',
            propietario=self.cliente,
        )
        self.producto = create_producto(nombre='Vacuna Rabia', categoria='vacunas', cantidad_stock=10)

    def _create_historial(self, producto_aplicado=None):
        """Auxiliar para crear una instancia de HistorialClinico."""
        return HistorialClinico.objects.create(
            mascota=self.mascota,
            veterinario=self.vet,
            tipo_consulta='vacunacion',
            motivo_consulta='Vacunación anual',
            diagnostico='Vacuna aplicada',
            producto_aplicado=producto_aplicado,
        )

    def test_signal_deducts_stock_on_historial_create(self):
        """R5.1: Crear HistorialClinico con producto_aplicado deduce 1 del stock"""
        initial_stock = self.producto.cantidad_stock
        self._create_historial(producto_aplicado=self.producto)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.cantidad_stock, initial_stock - 1)

    def test_signal_creates_movimiento_salida(self):
        """R5.2: Crear HistorialClinico con producto_aplicado crea MovimientoInventario(tipo='salida')"""
        self._create_historial(producto_aplicado=self.producto)
        mov = MovimientoInventario.objects.filter(producto=self.producto, tipo_movimiento='salida').first()
        self.assertIsNotNone(mov)
        self.assertEqual(mov.cantidad, 1)
        self.assertEqual(mov.usuario, self.vet)

    def test_signal_no_deduct_for_servicios(self):
        """R5.3: Categoría 'servicios' NO deduce stock"""
        servicio = create_producto(nombre='Consulta General', categoria='servicios', cantidad_stock=5)
        initial_stock = servicio.cantidad_stock
        self._create_historial(producto_aplicado=servicio)
        servicio.refresh_from_db()
        self.assertEqual(servicio.cantidad_stock, initial_stock)

    def test_signal_no_deduct_without_producto(self):
        """R5.4: HistorialClinico sin producto_aplicado NO deduce stock"""
        initial_stock = self.producto.cantidad_stock
        self._create_historial(producto_aplicado=None)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.cantidad_stock, initial_stock)

    def test_signal_allows_negative_stock(self):
        """R5.5: El stock puede ser negativo — nunca bloquear la creación del registro clínico"""
        producto_low = create_producto(nombre='Antipulgas', categoria='medicamentos', cantidad_stock=0)
        h = self._create_historial(producto_aplicado=producto_low)
        producto_low.refresh_from_db()
        self.assertEqual(producto_low.cantidad_stock, -1)
        # Sin excepción lanzada — prioridad médica

    def test_signal_does_not_fire_on_update(self):
        """R5.6: La señal solo debe ejecutarse en creación, no en actualización"""
        initial_stock = self.producto.cantidad_stock
        h = self._create_historial(producto_aplicado=self.producto)
        self.producto.refresh_from_db()
        stock_after_create = self.producto.cantidad_stock
        self.assertEqual(stock_after_create, initial_stock - 1)

        # Actualizar el historial — el stock NO debe cambiar de nuevo
        h.diagnostico = 'Vacuna exitosa'
        h.save()
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.cantidad_stock, stock_after_create)

    def test_signal_movimiento_linked_to_historial(self):
        """R5.7: MovimientoInventario está vinculado al registro HistorialClinico"""
        h = self._create_historial(producto_aplicado=self.producto)
        mov = MovimientoInventario.objects.filter(producto=self.producto).first()
        self.assertIsNotNone(mov)
        self.assertEqual(mov.historial_clinico_id, h.pk)


# ========================================
# R6: Pruebas de ProductoForm
# ========================================

class ProductoFormTest(TestCase):
    """Pruebas para ProductoForm con campos extendidos."""

    def test_form_includes_new_fields(self):
        """R6.1: ProductoForm incluye campos categoria, stock_minimo, proveedor"""
        from .forms import ProductoForm
        form = ProductoForm()
        self.assertIn('categoria', form.fields)
        self.assertIn('stock_minimo', form.fields)
        self.assertIn('proveedor', form.fields)

    def test_form_valid_data(self):
        """R6.2: Datos válidos en ProductoForm pasan"""
        from .forms import ProductoForm
        from proveedores.models import Proveedor
        prov = Proveedor.objects.create(nombre='TestProv')
        form = ProductoForm(data={
            'nombre': 'Test Product',
            'descripcion': 'Test desc',
            'precio': '10.00',
            'cantidad_stock': 50,
            'categoria': 'otros',
            'stock_minimo': 10,
            'proveedor': str(prov.pk),
        })
        self.assertTrue(form.is_valid(), form.errors)

    def test_form_rejects_negative_stock_minimo(self):
        """R6.3: ProductoForm rechaza stock_minimo negativo"""
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
        """R6.4: ProductoForm NO incluye campo esta_activo"""
        from .forms import ProductoForm
        form = ProductoForm()
        self.assertNotIn('esta_activo', form.fields)


# ========================================
# R7: Pruebas de MovimientoInventarioForm
# ========================================

class MovimientoInventarioFormTest(TestCase):
    """Pruebas para MovimientoInventarioForm."""

    def test_form_excludes_usuario_and_historial(self):
        """R7.1: Formulario excluye campos usuario y historial_clinico"""
        from .forms import MovimientoInventarioForm
        form = MovimientoInventarioForm()
        self.assertNotIn('usuario', form.fields)
        self.assertNotIn('historial_clinico', form.fields)

    def test_form_valid_data(self):
        """R7.2: Formulario válido con producto, tipo, cantidad, motivo"""
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
        """R7.3: Formulario rechaza cantidad < 1"""
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
# R8: Pruebas de Vistas de Producto
# ========================================

class ProductoViewTest(TestCase):
    """Pruebas para vistas de Producto — listado, búsqueda, filtro, eliminación suave."""

    def setUp(self):
        self.vet = create_user_with_role('Veterinario', username='vet_pv', email='vet_pv@test.com')
        self.admin = create_user_with_role('Administrador', username='admin_pv', email='admin_pv@test.com')
        self.cliente = create_user_with_role('Cliente', username='cli_pv', email='cli_pv@test.com')
        self.p1 = create_producto(nombre='Vacuna Rabia', categoria='vacunas', cantidad_stock=5)
        self.p2 = create_producto(nombre='Antipulgas', categoria='medicamentos', cantidad_stock=20)
        self.p3 = create_producto(nombre='Consulta General', categoria='servicios', cantidad_stock=100)

    def test_lista_shows_active_products(self):
        """R8.1: lista_productos muestra solo productos activos"""
        self.p2.esta_activo = False
        self.p2.save()
        self.client.force_login(self.admin)
        resp = self.client.get(reverse('productos:lista'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Vacuna Rabia')
        self.assertNotContains(resp, 'Antipulgas')

    def test_lista_search_by_name(self):
        """R8.2: Búsqueda en lista_productos filtra por nombre"""
        self.client.force_login(self.admin)
        resp = self.client.get(reverse('productos:lista'), {'q': 'Vacuna'})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Vacuna Rabia')
        self.assertNotContains(resp, 'Antipulgas')

    def test_lista_category_filter(self):
        """R8.3: Filtro por categoría en lista_productos"""
        self.client.force_login(self.admin)
        resp = self.client.get(reverse('productos:lista'), {'categoria': 'vacunas'})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Vacuna Rabia')
        self.assertNotContains(resp, 'Antipulgas')

    def test_soft_delete(self):
        """R8.4: delete_product elimina suavemente (establece esta_activo=False)"""
        self.client.force_login(self.vet)
        resp = self.client.post(reverse('productos:eliminar', kwargs={'pk': self.p1.pk}))
        self.assertEqual(resp.status_code, 302)
        # Usar all_objects porque el gestor por defecto filtra inactivos
        self.p1 = Producto.all_objects.get(pk=self.p1.pk)
        self.assertFalse(self.p1.esta_activo)
        # Conteo duro sin cambios
        self.assertEqual(Producto.all_objects.filter(pk=self.p1.pk).count(), 1)

    def test_create_requires_vet_or_admin(self):
        """R8.5: create_product requiere rol Vet/Admin"""
        self.client.force_login(self.cliente)
        resp = self.client.get(reverse('productos:nuevo'))
        self.assertEqual(resp.status_code, 403)

    def test_edit_requires_vet_or_admin(self):
        """R8.6: edit_product requiere rol Vet/Admin"""
        self.client.force_login(self.cliente)
        resp = self.client.get(reverse('productos:editar', kwargs={'pk': self.p1.pk}))
        self.assertEqual(resp.status_code, 403)


# ========================================
# R9: Prueba de Vista Kardex
# ========================================

class KardexViewTest(TestCase):
    """Pruebas para vista Kardex (historial de movimientos de producto)."""

    def setUp(self):
        self.vet = create_user_with_role('Veterinario', username='vet_kx', email='vet_kx@test.com')
        self.cliente = create_user_with_role('Cliente', username='cli_kx', email='cli_kx@test.com')
        self.producto = create_producto(nombre='Vacuna Rabia', categoria='vacunas', cantidad_stock=10)

    def test_kardex_shows_movimientos(self):
        """R9.1: kardex muestra MovimientoInventario de un producto"""
        MovimientoInventario.objects.create(
            producto=self.producto, tipo_movimiento='entrada', cantidad=10,
            usuario=self.vet, motivo='Initial stock',
        )
        self.client.force_login(self.vet)
        resp = self.client.get(reverse('productos:kardex', kwargs={'pk': self.producto.pk}))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Entrada')

    def test_kardex_requires_login(self):
        """R9.2: kardex requiere inicio de sesión"""
        resp = self.client.get(reverse('productos:kardex', kwargs={'pk': self.producto.pk}))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/usuarios/login/', resp.url)


# ========================================
# R10: Prueba de Vista Alertas de Stock
# ========================================

class AlertasViewTest(TestCase):
    """Pruebas para vista alertas_stock — muestra productos con bajo stock."""

    def setUp(self):
        self.vet = create_user_with_role('Veterinario', username='vet_al', email='vet_al@test.com')
        self.admin = create_user_with_role('Administrador', username='admin_al', email='admin_al@test.com')
        self.p_verde = create_producto(nombre='Stock OK', cantidad_stock=100, stock_minimo=10)
        self.p_amarillo = create_producto(nombre='Stock Bajo', cantidad_stock=12, stock_minimo=10)
        self.p_rojo = create_producto(nombre='Stock Critico', cantidad_stock=0, stock_minimo=10)

    def test_alertas_shows_non_verde_products(self):
        """R10.1: alertas muestra productos con estado_stock != 'verde'"""
        self.client.force_login(self.admin)
        resp = self.client.get(reverse('productos:alertas'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Stock Bajo')
        self.assertContains(resp, 'Stock Critico')
        self.assertNotContains(resp, 'Stock OK')

    def test_alertas_requires_login(self):
        """R10.2: alertas requiere inicio de sesión"""
        resp = self.client.get(reverse('productos:alertas'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/usuarios/login/', resp.url)