"""Tests for Tienda app — Cliente shopping flow.

Covers: catalogo, agregar_carrito, carrito, actualizar_cantidad,
eliminar_carrito, vaciar_carrito, checkout.
"""
from django.test import TestCase, Client
from django.urls import reverse
from decimal import Decimal

from usuarios.models import Usuario, Rol
from productos.models import Producto


class TiendaCatalogoTest(TestCase):
    """Test catalog browsing and search."""

    def setUp(self):
        User = Usuario
        self.client_rol = Rol.objects.get(nombre='Cliente')
        self.cliente = User.objects.create_user(
            username='tienda_cli', email='tienda_cli@test.com',
            password='testpass123', rol=self.client_rol,
        )
        self.prod1 = Producto.objects.create(
            nombre='Dog Chow Adulto', descripcion='Alimento para perros adultos',
            categoria='alimentos', precio=Decimal('45000'), cantidad_stock=50,
        )
        self.prod2 = Producto.objects.create(
            nombre='Rabies Vaccine', descripcion='Vacuna antirrábica',
            categoria='vacunas', precio=Decimal('25000'), cantidad_stock=20,
        )
        self.prod_out = Producto.objects.create(
            nombre='Out of Stock', descripcion='Agotado',
            categoria='insumos', precio=Decimal('1000'), cantidad_stock=0,
        )
        self.client = Client()

    def test_catalogo_shows_active_products_with_stock(self):
        """Catalog shows only products with stock > 0."""
        self.client.force_login(self.cliente)
        resp = self.client.get(reverse('tienda:catalogo'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Dog Chow Adulto')
        self.assertContains(resp, 'Rabies Vaccine')
        # Out-of-stock should NOT appear
        self.assertNotContains(resp, 'Out of Stock')

    def test_catalogo_requires_login(self):
        """Unauthenticated user redirected to login."""
        resp = self.client.get(reverse('tienda:catalogo'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/usuarios/login/', resp.url)

    def test_catalogo_search_by_name(self):
        """Search filters products by name."""
        self.client.force_login(self.cliente)
        resp = self.client.get(reverse('tienda:catalogo') + '?q=Dog')
        self.assertContains(resp, 'Dog Chow Adulto')
        self.assertNotContains(resp, 'Rabies Vaccine')

    def test_catalogo_filter_by_category(self):
        """Filter by category shows only matching products."""
        self.client.force_login(self.cliente)
        resp = self.client.get(reverse('tienda:catalogo') + '?categoria=vacunas')
        self.assertContains(resp, 'Rabies Vaccine')
        self.assertNotContains(resp, 'Dog Chow Adulto')


class TiendaCarritoTest(TestCase):
    """Test cart add, view, update quantity, remove, empty."""

    def setUp(self):
        User = Usuario
        self.client_rol = Rol.objects.get(nombre='Cliente')
        self.cliente = User.objects.create_user(
            username='cart_cli', email='cart_cli@test.com',
            password='testpass123', rol=self.client_rol,
        )
        self.prod1 = Producto.objects.create(
            nombre='Test Product A', precio=Decimal('10000'),
            cantidad_stock=10, categoria='alimentos',
        )
        self.prod2 = Producto.objects.create(
            nombre='Test Product B', precio=Decimal('20000'),
            cantidad_stock=5, categoria='medicamentos',
        )
        self.c = Client()

    def test_agregar_carrito_adds_product(self):
        """POST agregar_carrito adds product to session cart."""
        self.c.force_login(self.cliente)
        resp = self.c.post(reverse('tienda:agregar_carrito', args=[self.prod1.pk]))
        self.assertEqual(resp.status_code, 302)
        cart = self.c.session.get('cart', {})
        self.assertIn(str(self.prod1.pk), cart)
        self.assertEqual(cart[str(self.prod1.pk)]['quantity'], 1)

    def test_agregar_carrito_increments_existing(self):
        """Adding same product again increments quantity."""
        self.c.force_login(self.cliente)
        self.c.post(reverse('tienda:agregar_carrito', args=[self.prod1.pk]))
        self.c.post(reverse('tienda:agregar_carrito', args=[self.prod1.pk]))
        cart = self.c.session.get('cart', {})
        self.assertEqual(cart[str(self.prod1.pk)]['quantity'], 2)

    def test_agregar_carrito_respects_stock_limit(self):
        """Cannot add more than available stock."""
        self.c.force_login(self.cliente)
        # Stock is 10, try adding 11
        for _ in range(10):
            self.c.post(reverse('tienda:agregar_carrito', args=[self.prod1.pk]))
        resp = self.c.post(reverse('tienda:agregar_carrito', args=[self.prod1.pk]))
        # Should get a warning message, quantity stays at 10
        cart = self.c.session.get('cart', {})
        self.assertEqual(cart[str(self.prod1.pk)]['quantity'], 10)

    def test_agregar_carrito_out_of_stock_blocked(self):
        """Cannot add out-of-stock product."""
        prod_out = Producto.objects.create(
            nombre='No Stock', precio=Decimal('5000'),
            cantidad_stock=0, categoria='otros',
        )
        self.c.force_login(self.cliente)
        resp = self.c.post(reverse('tienda:agregar_carrito', args=[prod_out.pk]))
        cart = self.c.session.get('cart', {})
        self.assertNotIn(str(prod_out.pk), cart)

    def test_ver_carrito_shows_items(self):
        """Carrito view displays cart items."""
        self.c.force_login(self.cliente)
        self.c.post(reverse('tienda:agregar_carrito', args=[self.prod1.pk]))
        resp = self.c.get(reverse('tienda:carrito'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Test Product A')

    def test_actualizar_cantidad_changes_qty(self):
        """POST actualizar_cantidad changes item quantity."""
        self.c.force_login(self.cliente)
        self.c.post(reverse('tienda:agregar_carrito', args=[self.prod1.pk]))
        resp = self.c.post(reverse('tienda:actualizar_cantidad', args=[self.prod1.pk]),
                           {'quantity': 5})
        self.assertEqual(resp.status_code, 302)
        cart = self.c.session.get('cart', {})
        self.assertEqual(cart[str(self.prod1.pk)]['quantity'], 5)

    def test_actualizar_cantidad_zero_removes_item(self):
        """Setting quantity to 0 removes item from cart."""
        self.c.force_login(self.cliente)
        self.c.post(reverse('tienda:agregar_carrito', args=[self.prod1.pk]))
        resp = self.c.post(reverse('tienda:actualizar_cantidad', args=[self.prod1.pk]),
                           {'quantity': 0})
        cart = self.c.session.get('cart', {})
        self.assertNotIn(str(self.prod1.pk), cart)

    def test_eliminar_carrito_removes_item(self):
        """POST eliminar_carrito removes item from cart."""
        self.c.force_login(self.cliente)
        self.c.post(reverse('tienda:agregar_carrito', args=[self.prod1.pk]))
        resp = self.c.post(reverse('tienda:eliminar_carrito', args=[self.prod1.pk]))
        cart = self.c.session.get('cart', {})
        self.assertNotIn(str(self.prod1.pk), cart)

    def test_vaciar_carrito_clears_all(self):
        """POST vaciar_carrito empties entire cart."""
        self.c.force_login(self.cliente)
        self.c.post(reverse('tienda:agregar_carrito', args=[self.prod1.pk]))
        self.c.post(reverse('tienda:agregar_carrito', args=[self.prod2.pk]))
        resp = self.c.post(reverse('tienda:vaciar_carrito'))
        cart = self.c.session.get('cart', {})
        self.assertEqual(len(cart), 0)

    def test_carrito_get_redirects(self):
        """GET agregar_carrito redirects to catalog."""
        self.c.force_login(self.cliente)
        resp = self.c.get(reverse('tienda:agregar_carrito', args=[self.prod1.pk]))
        self.assertEqual(resp.status_code, 302)


class TiendaCheckoutTest(TestCase):
    """Test checkout flow — only Cliente can place orders."""

    def setUp(self):
        User = Usuario
        self.client_rol = Rol.objects.get(nombre='Cliente')
        self.admin_rol = Rol.objects.get(nombre='Administrador')
        self.domiciliario_rol = Rol.objects.get(nombre='Domiciliario')
        self.cliente = User.objects.create_user(
            username='checkout_cli', email='checkout_cli@test.com',
            password='testpass123', rol=self.client_rol,
            telefono='3001112222',
        )
        # Create a domiciliario for auto-assignment
        self.domiciliario = User.objects.create_user(
            username='checkout_dom', email='checkout_dom@test.com',
            password='testpass123', rol=self.domiciliario_rol,
        )
        self.prod1 = Producto.objects.create(
            nombre='Checkout Product A', precio=Decimal('15000'),
            cantidad_stock=50, categoria='alimentos',
        )
        self.prod2 = Producto.objects.create(
            nombre='Checkout Product B', precio=Decimal('30000'),
            cantidad_stock=20, categoria='medicamentos',
        )
        self.c = Client()

    def _fill_cart(self):
        """Helper: add products to cart."""
        self.c.force_login(self.cliente)
        self.c.post(reverse('tienda:agregar_carrito', args=[self.prod1.pk]))
        self.c.post(reverse('tienda:agregar_carrito', args=[self.prod2.pk]))

    def test_checkout_creates_pedido(self):
        """Checkout creates Pedido with PedidoItems from cart."""
        self._fill_cart()
        from entregas.models import Pedido, PedidoItem
        resp = self.c.post(reverse('tienda:checkout'), {
            'direccion_entrega': 'Calle 10 # 25-30',
            'telefono_contacto': '3001112222',
            'notas': 'Dejar en portería',
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Pedido.objects.filter(cliente=self.cliente).count(), 1)
        pedido = Pedido.objects.get(cliente=self.cliente)
        self.assertEqual(pedido.items.count(), 2)
        self.assertEqual(pedido.estado, 'pendiente')
        self.assertEqual(pedido.direccion_entrega, 'Calle 10 # 25-30')
        self.assertEqual(pedido.telefono_contacto, '3001112222')

    def test_checkout_auto_assigns_domiciliario(self):
        """Checkout auto-assigns first available Domiciliario."""
        self._fill_cart()
        from entregas.models import Pedido
        self.c.post(reverse('tienda:checkout'), {
            'direccion_entrega': 'Calle 10 # 25-30',
            'telefono_contacto': '3001112222',
        })
        pedido = Pedido.objects.get(cliente=self.cliente)
        self.assertEqual(pedido.domiciliario, self.domiciliario)

    def test_checkout_clears_cart(self):
        """Cart is emptied after successful checkout."""
        self._fill_cart()
        self.c.post(reverse('tienda:checkout'), {
            'direccion_entrega': 'Calle 10 # 25-30',
            'telefono_contacto': '3001112222',
        })
        self.assertEqual(len(self.c.session.get('cart', {})), 0)

    def test_checkout_redirects_to_mis_pedidos(self):
        """After checkout, redirects to mis_pedidos."""
        self._fill_cart()
        resp = self.c.post(reverse('tienda:checkout'), {
            'direccion_entrega': 'Calle 10 # 25-30',
            'telefono_contacto': '3001112222',
        })
        self.assertRedirects(resp, reverse('entregas:mis_pedidos'))

    def test_checkout_requires_direccion(self):
        """Checkout fails without direccion_entrega."""
        self._fill_cart()
        resp = self.c.post(reverse('tienda:checkout'), {
            'telefono_contacto': '3001112222',
        })
        self.assertEqual(resp.status_code, 200)  # Returns form with error
        from entregas.models import Pedido
        self.assertEqual(Pedido.objects.filter(cliente=self.cliente).count(), 0)

    def test_checkout_requires_telefono(self):
        """Checkout fails without telefono_contacto."""
        self._fill_cart()
        resp = self.c.post(reverse('tienda:checkout'), {
            'direccion_entrega': 'Calle 10 # 25-30',
        })
        self.assertEqual(resp.status_code, 200)
        from entregas.models import Pedido
        self.assertEqual(Pedido.objects.filter(cliente=self.cliente).count(), 0)

    def test_checkout_empty_cart_redirects(self):
        """Checkout with empty cart redirects to catalogo."""
        self.c.force_login(self.cliente)
        resp = self.c.get(reverse('tienda:checkout'))
        self.assertEqual(resp.status_code, 302)

    def test_checkout_non_cliente_gets_403(self):
        """Admin user gets 403 on checkout."""
        admin = Usuario.objects.create_user(
            username='checkout_admin', email='checkout_admin@test.com',
            password='testpass123', rol=self.admin_rol,
        )
        self.c.force_login(admin)
        self.c.post(reverse('tienda:agregar_carrito', args=[self.prod1.pk]))
        resp = self.c.get(reverse('tienda:checkout'))
        self.assertEqual(resp.status_code, 403)

    def test_checkout_total_correct(self):
        """Pedido total matches cart total (15000 + 30000 = 45000)."""
        self._fill_cart()
        from entregas.models import Pedido
        self.c.post(reverse('tienda:checkout'), {
            'direccion_entrega': 'Calle 10 # 25-30',
            'telefono_contacto': '3001112222',
        })
        pedido = Pedido.objects.get(cliente=self.cliente)
        self.assertEqual(pedido.total, Decimal('45000'))