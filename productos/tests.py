from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Producto
from usuarios.models import Rol

User = get_user_model()


class ProductosCRUDTests(TestCase):
    def setUp(self):
        self.rol, _ = Rol.objects.get_or_create(nombre="Cliente", defaults={"descripcion": "Cliente del servicio"})
        self.password = "testpass123"
        self.user = User.objects.create_user(
            username="produser",
            email="produser@example.com",
            password=self.password,
            rol=self.rol,
        )

    def test_lista_requires_login(self):
        resp = self.client.get(reverse("productos:lista"))
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith("/usuarios/"))

    def test_lista_authenticated_ok(self):
        # Autenticar sesión directamente para el modelo de usuario personalizado
        self.client.force_login(self.user)
        resp = self.client.get(reverse("productos:lista"))
        self.assertEqual(resp.status_code, 200)

    def test_create_product_valid(self):
        self.client.force_login(self.user)
        data = {
            "nombre": "Collar para perro",
            "descripcion": "Collar ajustable de nylon",
            "precio": "19.99",
            "cantidad_stock": 10,
        }
        resp = self.client.post(reverse("productos:nuevo"), data)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Producto.objects.count(), 1)

    def test_edit_and_delete_product(self):
        self.client.force_login(self.user)
        producto = Producto.objects.create(
            nombre="Juguete",
            descripcion="Pelota de goma",
            precio="9.99",
            cantidad_stock=5,
        )

        # Editar producto
        edit_data = {
            "nombre": "Juguete actualizado",
            "descripcion": "Pelota de goma grande",
            "precio": "12.50",
            "cantidad_stock": 7,
        }
        resp_edit = self.client.post(reverse("productos:editar", args=[producto.pk]), edit_data)
        self.assertEqual(resp_edit.status_code, 302)
        producto.refresh_from_db()
        self.assertEqual(producto.nombre, "Juguete actualizado")

        # Eliminar producto
        resp_delete_get = self.client.get(reverse("productos:eliminar", args=[producto.pk]))
        self.assertEqual(resp_delete_get.status_code, 200)
        resp_delete_post = self.client.post(reverse("productos:eliminar", args=[producto.pk]))
        self.assertEqual(resp_delete_post.status_code, 302)
        self.assertEqual(Producto.objects.count(), 0)
