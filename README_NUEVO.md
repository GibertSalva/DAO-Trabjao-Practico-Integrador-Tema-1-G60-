# ⚽ Sistema de Reservas de Canchas Deportivas

Este proyecto es un **Trabajo Práctico Integrador** para la materia DAO (Desarrollo de Aplicaciones con Objetos), enfocado en el desarrollo de una aplicación web completa para la gestión de reservas de canchas deportivas.

El sistema permite a los administradores gestionar clientes, canchas y horarios, mientras que los usuarios pueden registrar y administrar sus reservas de forma sencilla e intuitiva.

---

## ✨ Funcionalidades Implementadas

### 🎯 Gestión Completa (CRUD)
* **Clientes:** Registro, edición, visualización y eliminación de clientes
* **Canchas:** Administración de canchas con diferentes tipos (Fútbol 5, 7, 11, Paddle, Tenis)
* **Reservas:** Sistema completo de gestión de reservas con validación de disponibilidad

### 🔐 Validaciones Inteligentes
* Verificación automática de disponibilidad de canchas
* Prevención de reservas en horarios ocupados
* Validación de fechas y horarios

### 💰 Sistema de Pagos
* Cálculo automático de costos (cancha + servicios)
* Gestión de estado de pagos (Pendiente, Pagado, Reembolsado)
* Múltiples métodos de pago

### 🎯 Servicios Adicionales
* Iluminación
* Vestuarios Premium
* Árbitro
* Buffet

### 🏆 Gestión de Torneos
* Creación y administración de torneos
* Asociación de reservas con torneos

---

## 🛠️ Tecnologías Utilizadas

* **Backend:** Django 5.2
* **Base de Datos:** SQLite
* **Frontend:** HTML5, CSS3, JavaScript
* **Python:** 3.x

---

## 📁 Estructura del Proyecto

```
├── canchas_project/          # Configuración principal del proyecto
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── reservas/                 # Aplicación principal
│   ├── models.py            # Modelos de datos
│   ├── views.py             # Lógica de negocio
│   ├── urls.py              # Rutas de la aplicación
│   ├── admin.py             # Configuración del panel admin
│   ├── templates/           # Templates HTML
│   └── static/              # Archivos estáticos (CSS, JS)
├── db.sqlite3               # Base de datos
├── manage.py                # Utilidad de Django
├── poblar_db.py             # Script para datos de prueba
└── requirements.txt         # Dependencias
```

---

## 🚀 Instalación y Configuración

### 1️⃣ Clonar el repositorio
```bash
git clone https://github.com/GibertSalva/DAO-Trabjao-Practico-Integrador-Tema-1-G60-.git
cd DAO-Trabjao-Practico-Integrador-Tema-1-G60-
```

### 2️⃣ Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3️⃣ Aplicar migraciones
```bash
python manage.py migrate
```

### 4️⃣ Crear superusuario (opcional - para acceder al admin)
```bash
python manage.py createsuperuser
```

### 5️⃣ Poblar la base de datos con datos de prueba (opcional pero recomendado)
```bash
python manage.py shell < poblar_db.py
```

### 6️⃣ Iniciar el servidor
```bash
python manage.py runserver
```

### 7️⃣ Acceder a la aplicación
* **Aplicación principal:** http://127.0.0.1:8000/
* **Panel de administración:** http://127.0.0.1:8000/admin/

---

## 📱 Uso del Sistema

### Navegación Principal
* **Inicio:** Dashboard con estadísticas generales
* **Clientes:** Gestión completa de clientes
* **Canchas:** Administración de canchas deportivas
* **Reservas:** Sistema de reservas con filtros
* **Admin:** Panel de administración de Django

### Crear una Reserva
1. Ir a **Reservas** → **Nueva Reserva**
2. Seleccionar cliente y cancha
3. Elegir fecha y horario
4. Añadir servicios adicionales (opcional)
5. El sistema validará automáticamente la disponibilidad
6. Se calculará el costo total y se creará el registro de pago

### Gestionar Clientes
* **Listar:** Ver todos los clientes registrados
* **Crear:** Agregar nuevos clientes con DNI, email y teléfono
* **Editar:** Modificar información de clientes existentes
* **Detalle:** Ver perfil completo y historial de reservas
* **Eliminar:** Remover clientes (eliminará sus reservas)

### Administrar Canchas
* **Listar:** Ver todas las canchas con precios
* **Crear:** Agregar nuevas canchas especificando tipo y precio
* **Editar:** Actualizar información de canchas
* **Detalle:** Ver reservas asociadas a cada cancha
* **Eliminar:** Remover canchas del sistema

---

## 💾 Modelo de Datos

### Entidades Principales
* **TipoCancha:** Categorías de canchas (Fútbol 5, 7, 11, etc.)
* **Cliente:** Información de clientes (DNI, email, teléfono)
* **Cancha:** Canchas disponibles con precio por hora
* **Reserva:** Reservas con fechas, horarios y estado
* **Pago:** Información de pagos asociados a reservas
* **Servicio:** Servicios adicionales con costos
* **Torneo:** Torneos deportivos

### Relaciones
* Cliente → Reservas (1:N)
* Cancha → Reservas (1:N)
* Reserva → Pago (1:1)
* Reserva → Servicios (N:N)
* Torneo → Reservas (1:N)

---

## 🎨 Características de la Interfaz

* **Diseño Responsivo:** Funciona en desktop, tablet y móvil
* **Navegación Intuitiva:** Menú claro y accesible
* **Feedback Visual:** Mensajes de éxito, error y advertencia
* **Tarjetas Estadísticas:** Dashboard con métricas clave
* **Filtros Avanzados:** Búsqueda y filtrado de reservas
* **Estados con Colores:** Identificación visual de estados

---

## 🔧 Panel de Administración

El panel de Django Admin incluye:
* Gestión de todos los modelos
* Filtros y búsquedas
* Acciones en lote
* Permisos de usuario

---

## 📊 Próximas Funcionalidades (Roadmap)

- [ ] Reportes y estadísticas avanzadas
- [ ] Gráficos de uso mensual
- [ ] Ranking de canchas más utilizadas
- [ ] Sistema de notificaciones por email
- [ ] API REST para integración móvil
- [ ] Sistema de autenticación de usuarios
- [ ] Exportación de reportes a PDF/Excel

---

## 👥 Integrantes del Grupo 60

* **Salvador Gibert**
* **Ignacio Maspero**
* **Tiziana Carrizo**
* **Agustin Rey Laje**
* **Marco Figueroa**

---

## 📄 Licencia

Este proyecto es un trabajo académico desarrollado para la materia DAO en la Facultad.

---

## 🤝 Contribuir

Este es un proyecto académico, pero cualquier sugerencia o mejora es bienvenida. Puedes:
1. Hacer un fork del repositorio
2. Crear una rama con tu feature (`git checkout -b feature/NuevaFuncionalidad`)
3. Commit de tus cambios (`git commit -m 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/NuevaFuncionalidad`)
5. Abrir un Pull Request

---

¡Gracias por revisar nuestro proyecto! ⚽🏟️
