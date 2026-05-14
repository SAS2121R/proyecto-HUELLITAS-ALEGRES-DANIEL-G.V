# 🐾 Huellitas Alegres

**Sistema Integral de Gestión para Clínicas Veterinarias**

Plataforma web desarrollada con Django que permite administrar de forma completa una clínica veterinaria: gestión de pacientes (mascotas), citas médicas, historial clínico, inventario de productos, tienda en línea con domicilio, y un panel administrativo con métricas de negocio.

---

## 📋 Tabla de Contenidos

- [Descripción General](#-descripción-general)
- [Roles del Sistema](#-roles-del-sistema)
- [Funcionalidades por Rol](#-funcionalidades-por-rol)
- [Diseño Visual](#-diseño-visual)
- [Características Técnicas Destacadas](#-características-técnicas-destacadas)
- [Tecnologías](#-tecnologías)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Instalación](#-instalación)
- [Creación del Superusuario](#-creación-del-superusuario)
- [Ejecución](#-ejecución)
- [Pruebas](#-pruebas)
- [Autor](#-autor)

---

## 🏥 Descripción General

**Huellitas Alegres** es un sistema de información diseñado para cubrir todas las necesidades operativas de una clínica veterinaria. Desde el registro de mascotas y la programación de citas, hasta la venta de productos con entrega a domicilio y la generación de reportes financieros en PDF y Excel.

El sistema implementa un modelo de **roles diferenciados** donde cada tipo de usuario accede únicamente a las funcionalidades correspondientes a su perfil, garantizando seguridad y fluidez en la operación diaria.

La interfaz sigue un **sistema de diseño Material Design** con paleta personalizada (documentada en `DESIGN.md`), tipografía Plus Jakarta Sans para encabezados y Manrope para cuerpo, e iconos Material Symbols Outlined. La Landing Page pública recibe al visitante y redirige automáticamente al dashboard del rol correspondiente tras autenticación.

---

## 👥 Roles del Sistema

| Rol | Descripción |
|-----|-------------|
| 🩺 **Veterinario** | Gestiona citas, atiende pacientes, registra historial clínico y genera reportes |
| 🚗 **Domiciliario** | Gestiona pedidos asignados, cambia estados de entrega, sube evidencia fotográfica |
| 👤 **Cliente** | Registra mascotas, solicita citas, compra en la tienda y consulta su historial |
| 👑 **Administrador** | Control total: usuarios, métricas, configuración, torre de control y disponibilidad |

---

## ⚙️ Funcionalidades por Rol

### 🩺 Veterinario
- Dashboard con citas del día y pacientes recientes
- CRUD de disponibilidades (bloques horarios)
- Gestión de citas (crear, confirmar, cancelar)
- Historial clínico completo con adjuntos (hasta 5 MB)
- Atención de citas con registro directo al historial
- Catálogo de servicios veterinarios con tarifas en pesos colombianos
- Reportes en PDF/Excel de citas, historial, inventario y servicios

### 🚗 Domiciliario
- Dashboard con pedidos asignados y acciones inline (Iniciar Entrega, Confirmar, Cancelar)
- Cambio de estado con transiciones validadas (pendiente → en camino → entregado)
- Evidencia obligatoria: foto y firma para confirmar entrega
- Deducción automática de inventario al entregar pedidos
- Registro de incidentes con motivo obligatorio al cancelar
- Resumen diario de entregas con totales
- Comprobante PDF con datos dinámicos de la clínica (NIT, dirección, teléfono)

### 👤 Cliente
- Landing Page pública con información de la clínica
- Registro de cuenta propia con auto-asignación de rol
- Dashboard personalizado con sus mascotas y citas
- CRUD completo de sus mascotas
- Solicitud y cancelación de citas
- **Tienda en línea**: catálogo con imágenes de productos, badges de disponibilidad, carrito en sesión, checkout con asignación automática de domiciliario
- Consulta de pedidos realizados con seguimiento
- Historial clínico de sus mascotas (solo lectura)
- Mi Perfil: edición de datos, foto y cambio de contraseña

### 👑 Administrador
- Dashboard con métricas: usuarios, mascotas, citas, ingresos del mes
- **Gestión de Usuarios**: crear, editar, activar/desactivar, asignar contraseña temporal
- **Torre de Control**: vista global de pedidos con reasignación inline de domiciliario, tabla de domiciliarios con estado de disponibilidad y botones Reincorporar/Desactivar
- **Métricas de Negocio**: Top 5 Productos, Productividad de Staff, Tasa de Cumplimiento (anillo de progreso SVG animado)
- **Exportación de Métricas**: PDF y Excel con datos dinámicos de ConfiguraciónClínica
- **Configuración Clínica**: modelo singleton (NIT, dirección, teléfono, email) reflejado en todos los PDF
- **Gestión de Proveedores**: CRUD completo con vinculación al inventario
- **Gestión de Productos**: CRUD con campos de tarifa (formato pesos colombianos) y subida de imágenes con redimensionamiento automático
- Reportes PDF/Excel de citas, historial, inventario y servicios

---

## 🎨 Diseño Visual

El sistema cuenta con un **sistema de diseño cohesivo** basado en Material Design 3, implementado con Tailwind CSS CDN y documentado en `DESIGN.md`:

- **Paleta**: Primary=#37563b, Primary Container=#4f6f52, Surface=#f8f9fa, Error=#ba1a1a, con variantes para containers, outlines y estados
- **Tipografía**: Plus Jakarta Sans (encabezados) + Manrope (cuerpo y etiquetas)
- **Iconografía**: Material Symbols Outlined con variante FILL para estados activos
- **Componentes**: Cards con colored-header, status pills, danger/confirmation cards, progress rings SVG, formularios con `.tw-form`
- **Sidebar**: Navegación condicional por rol, con indicador activo y colapso en móvil
- **Navbar**: Slim con avatar del usuario, dropdown Alpine.js y enlace de inicio de sesión

La **Landing Page** (`/`) es standalone (no extiende `base.html`) y presenta la clínica al visitante. Al autenticarse, redirige automáticamente al dashboard del rol correspondiente mediante `get_redirect_url()`.

---

## 🚀 Características Técnicas Destacadas

### 🔄 Asignación Round-Robin de Domiciliarios
El sistema asigna automáticamente pedidos al domiciliario **disponible con menos carga** (pedidos activos: pendiente + en camino). Cuando un domiciliario cancela por incidente, se marca como **no disponible** y el Admin puede reincorporarlo desde la Torre de Control con un solo clic.

### 📊 Anillo de Progreso SVG Animado
Las métricas de negocio muestran la tasa de cumplimiento como un **anillo de progreso SVG animado** con umbrales de color: >90% verde, 70-89% esmeralda, <70% naranja. Se llena suavemente al cargar la página.

### 🛒 Tienda con Estados de Disponibilidad
Los productos en el catálogo muestran badges inteligentes según el stock:
- 🟢 **Disponible** (stock > 10)
- 🟠 **¡Últimas unidades!** (stock 1-10)
- 🔴 **Agotado** (stock = 0, botón deshabilitado)
- El stock exacto solo lo ve el Administrador

### 🖼️ Imágenes de Producto con Optimización Automática
Los productos pueden tener fotos de referencia subidas por el Admin. El sistema **redimensiona automáticamente** a 800x800px con compresión JPEG calidad 85%, reduciendo fotos de celular de 5MB a ~150KB. Los productos sin imagen muestran un placeholder elegante.

### 💵 Formato Pesos Colombianos
Las tarifas y precios se muestran con **puntos de miles** ($85.000 en vez de $85000) mediante filtros de template personalizados. El formulario de servicios acepta entrada con o sin puntos (85.000 o 85000).

### 🔐 Control de Acceso por Roles
Cada vista está protegida por decoradores de rol (`@role_required`, `@admin_required`, `@veterinario_required`) que verifican autenticación y permisos. Las vistas que manejan datos sensibles (métricas de negocio, exportación PDF/Excel) están restringidas exclusivamente a Administradores.

### 📝 Evidencia Obligatoria de Entrega
Para confirmar una entrega, el domiciliario **debe** subir foto de evidencia y firma del cliente. Ambos campos son obligatorios en modelo, formulario y vista. Un pedido no puede pasar a "entregado" sin ellos.

---

## 🛠️ Tecnologías

| Componente | Tecnología |
|------------|-----------|
| **Backend** | Django 5.2 (Python 3.12+) |
| **Base de Datos** | SQLite (desarrollo) / PostgreSQL (producción) |
| **Frontend** | Tailwind CSS CDN + Alpine.js + Material Symbols Outlined |
| **Plantillas** | Django Templates con herencia y bloques |
| **PDF** | xhtml2pdf |
| **Excel** | openpyxl |
| **Imágenes** | Pillow (redimensionamiento automático) |
| **Autenticación** | Django AUTH_USER_MODEL personalizado (email como USERNAME_FIELD) |
| **Autorización** | Modelo Rol personalizado + decoradores por rol |
| **Sesiones** | Django Sessions (carrito de compras) |
| **Zona Horaria** | America/Bogota (timezone.localdate()) |

---

## 📁 Estructura del Proyecto

```
huellitas_alegres/
├── agenda/                # Disponibilidades y Citas
│   ├── models.py          # Disponibilidad, Cita (estados: Programada, Atendida, Cancelada)
│   ├── forms.py           # DisponibilidadForm, CitaForm, CitaClienteForm
│   └── views.py           # Dashboard vet, CRUD disponibilidades y citas
├── entregas/              # Pedidos y Domicilio
│   ├── models.py          # Pedido (estados: pendiente, en_camino, entregado, cancelado), PedidoItem
│   ├── forms.py           # PedidoForm, CambiarEstadoForm, EvidenciaForm, ReasignarDomiciliarioForm
│   ├── views.py           # Dashboard, detalle, torre de control, asignar_domiciliario_disponible()
│   └── urls.py            # toggle_disponibilidad, comprobante_pdf, etc.
├── historial/             # Historial Clínico y Adjuntos
├── huellitas_alegres/     # Configuración del proyecto Django
│   ├── settings.py        # TIME_ZONE = 'America/Bogota', AUTH_USER_MODEL
│   ├── urls.py            # URLs principales con namespaces por app
│   └── templatetags/      # Filtros personalizados
├── mascotas/              # Mascotas (pacientes)
├── productos/             # Inventario y Kardex
│   ├── models.py          # Producto (con imagen + auto-resize), MovimientoInventario
│   ├── forms.py           # ProductoForm (tarifa como CharField con limpieza de puntos)
│   └── views.py           # CRUD con request.FILES para imágenes
├── proveedores/           # Proveedores (CRUD)
├── reportes/              # Reportes PDF/Excel y Métricas Admin
│   └── views.py           # admin_metricas, admin_metricas_pdf, admin_metricas_excel
├── servicios/              # Catálogo de Servicios Veterinarios
│   ├── forms.py           # ServicioForm (tarifa CharField con limpieza de puntos)
│   └── templatetags/      # formato.py (filtros: pesos, miles)
├── tienda/                # Catálogo, Carrito y Checkout
│   └── views.py           # Checkout con asignación round-robin de domiciliario
├── usuarios/              # Usuarios, Roles, Perfil, Configuración Clínica
│   ├── models.py          # Usuario (con is_disponible), Rol, Perfil, ConfiguracionClinica
│   ├── decorators.py      # role_required, admin_required, veterinario_required
│   └── views.py           # Auth, dashboards, gestión de usuarios
├── templates/             # Plantillas con diseño Material Design
│   ├── base.html          # Layout unificado: navbar + sidebar + contenido
│   ├── landing.html       # Landing Page pública (standalone)
│   ├── inicio.html        # Dashboard fallback con cards por rol
│   ├── includes/          # admin_sidebar, vet_sidebar, cliente_sidebar, domiciliario_sidebar, back_button
│   ├── agenda/            # Dashboard vet, citas, disponibilidades
│   ├── entregas/          # Dashboard, detalle, torre_control, resumen, mis_pedidos
│   ├── historial/         # Historial clínico con adjuntos y atender cita
│   ├── mascotas/          # CRUD mascotas + cliente_dashboard
│   ├── productos/          # CRUD productos, kardex, alertas
│   ├── proveedores/       # CRUD proveedores
│   ├── reportes/          # admin_metricas (SVG ring), reportes PDF
│   ├── servicios/          # CRUD servicios
│   ├── tienda/            # Catálogo, carrito, checkout
│   └── usuarios/          # Auth, perfil, admin (dashboard, users, configuración)
└── DESIGN.md              # Sistema de diseño (paleta, tipografía, componentes)
```

---

## 🚀 Instalación

1. **Clonar el repositorio:**

```bash
git clone https://github.com/DANIELSPROGRAMMING/proyecto-HUELLITAS-ALEGRES-DANIEL-G.V.git
cd proyecto-HUELLITAS-ALEGRES-DANIEL-G.V
```

2. **Crear y activar entorno virtual:**

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate
```

3. **Instalar dependencias:**

```bash
pip install -r requirements.txt
```

4. **Aplicar migraciones:**

```bash
python manage.py migrate
```

5. **Cargar datos iniciales (roles):**

```bash
python manage.py shell < seed_roles.py
```

---

## 👑 Creación del Superusuario

Como el modelo `Usuario` tiene un campo `rol` obligatorio (ForeignKey), no se puede usar `createsuperuser` directamente. Usá el shell de Django:

```bash
python manage.py shell
```

Dentro del shell:

```python
from usuarios.models import Usuario, Rol

rol_admin = Rol.objects.get(nombre='Administrador')

usuario = Usuario.objects.create_superuser(
    username='admin',
    email='admin@huellitasalegres.com',
    password='TU_CONTRASEÑA_SEGURA',
    rol=rol_admin,
)

print(f"✅ Superusuario creado: {usuario.email}")
```

Escribí `exit()` para salir del shell.

---

## ▶️ Ejecución

```bash
python manage.py runserver
```

El servidor se inicia en `http://127.0.0.1:8000/`

- `/` — Landing Page (pública, redirige al dashboard si ya estás autenticado)
- `/usuarios/auth/` — Login / Registro
- `/inicio/` — Dashboard genérico (fallback)

---

## 🧪 Pruebas

Ejecutar todas las pruebas:

```bash
python manage.py test
```

Ejecutar pruebas de una app específica:

```bash
python manage.py test proveedores
python manage.py test usuarios.tests.ConfiguracionClinicaTest
```

---

## 👨‍💻 Autor

**Daniel G.V.** — Proyecto formativo SENA (ADSO)

---

## 📄 Licencia

Este proyecto es de uso educativo como parte del programa de formación del SENA.