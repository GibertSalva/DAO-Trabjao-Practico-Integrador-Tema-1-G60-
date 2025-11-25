# Sistema de Reservas de Canchas Deportivas

Este proyecto es un Trabajo Práctico Integrador para la materia DAO (Desarrollo de Aplicaciones con Objetos), enfocado en el desarrollo de una aplicación web completa para la gestión de reservas de canchas deportivas.

El sistema permite a los administradores gestionar clientes, canchas, torneos y horarios, mientras que los usuarios pueden registrar y administrar sus reservas de forma sencilla e intuitiva.

---

## Funcionalidades Implementadas

### Gestión Completa (CRUD)
* **Clientes:** Registro, edición, visualización y eliminación de clientes con validación de DNI y email únicos
* **Canchas:** Administración de canchas con diferentes tipos (Fútbol 5, 7, 11, Paddle, Tenis)
* **Reservas:** Sistema completo de gestión de reservas con validación de disponibilidad en tiempo real
* **Torneos:** Creación de torneos con sistema de fixture automático por eliminación directa
* **Equipos:** Gestión de equipos deportivos independientes

### Validaciones Inteligentes
* Verificación automática de disponibilidad de canchas
* Prevención de reservas en horarios ocupados
* Validación de fechas y horarios (no permite reservas en el pasado)
* Control de potencia de 2 para generación de fixtures

### Sistema de Pagos Completo
* Cálculo automático de costos (cancha + servicios adicionales)
* Gestión de estado de pagos (Pendiente, Pagado, Reembolsado)
* Múltiples métodos de pago (Efectivo, Tarjeta, Transferencia, MercadoPago)
* Integración con MercadoPago (preparada para producción)
* Botón de demostración para testing sin MercadoPago

### Servicios Adicionales
* Iluminación
* Vestuarios Premium
* Árbitro
* Buffet

### Sistema de Torneos Avanzado
* Creación y administración de torneos
* Inscripción de equipos
* Generación automática de fixture por eliminación directa
* Registro de resultados de partidos
* Avance automático de ganadores a siguiente ronda
* Control de estado del torneo (Inscripción, En Curso, Finalizado)
* Cálculo de ingresos por inscripciones y reservas

### Reportes y Estadísticas
* Listado de reservas por cliente con gasto total
* Reservas por cancha en período seleccionado
* Ranking de canchas más utilizadas
* Gráfico de utilización mensual de canchas (últimos 6 meses)
* Exportación de reportes a PDF con diseño profesional
* Filtros por mes, año, cliente y cancha

---

## Tecnologías Utilizadas

* **Backend:** Django 5.0.6
* **Base de Datos:** SQLite3
* **Frontend:** HTML5, CSS3 (DaisyUI + TailwindCSS), JavaScript
* **Pagos:** MercadoPago SDK 2.2.0
* **Reportes:** ReportLab 4.2.5
* **Testing:** Django TestCase (28 tests pasando)
* **Python:** 3.13.2

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

## Instalación y Configuración

### 1. Clonar el repositorio
```bash
git clone https://github.com/GibertSalva/DAO-Trabjao-Practico-Integrador-Tema-1-G60-.git
cd DAO-Trabjao-Practico-Integrador-Tema-1-G60-
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Aplicar migraciones
```bash
python manage.py migrate
```

### 4. Poblar la base de datos con datos de prueba (recomendado)
```bash
python manage.py poblar_equipos
```

### 5. Iniciar el servidor
```bash
python manage.py runserver
```

### 6. Acceder a la aplicación
* **Aplicación principal:** http://127.0.0.1:8000/

---

## Uso del Sistema

### Navegación Principal
* **Inicio:** Dashboard con estadísticas generales del sistema
* **Clientes:** Gestión completa de clientes con historial de reservas
* **Canchas:** Administración de canchas deportivas con precios
* **Reservas:** Sistema de reservas con validación de disponibilidad
* **Torneos:** Gestión de torneos con fixture automático
* **Equipos:** Administración de equipos deportivos
* **Reportes:** Estadísticas y gráficos con exportación a PDF

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
* **Listar:** Ver todas las canchas con precios y búsqueda
* **Crear:** Agregar nuevas canchas especificando tipo y precio por hora
* **Editar:** Actualizar información de canchas existentes
* **Detalle:** Ver reservas asociadas y estadísticas de uso
* **Eliminar:** Remover canchas del sistema

### Gestionar Torneos
* **Crear Torneo:** Definir nombre, fechas, premio y costo de inscripción
* **Inscribir Equipos:** Agregar equipos al torneo (debe ser potencia de 2)
* **Generar Fixture:** Crear automáticamente el fixture de eliminación directa
* **Registrar Resultados:** Ingresar resultados de partidos
* **Ver Fixture:** Visualizar todas las rondas del torneo

### Sistema de Pagos
* **Pagar con MercadoPago:** Integración completa para pagos online (requiere HTTPS en producción)
* **Marcar como Pagado (Demo):** Botón de demostración para testing local
* **Métodos de Pago:** Efectivo, Tarjeta, Transferencia, MercadoPago
* **Estados:** Pendiente, Pagado, Reembolsado

### Reportes
* **Filtros:** Por mes, año, cliente y cancha
* **Top 10 Clientes:** Ordenados por gasto total
* **Distribución por Cancha:** Ingresos, horas y número de reservas
* **Ranking de Canchas:** Más utilizadas en el período
* **Gráfico Mensual:** Evolución de uso en últimos 6 meses
* **Exportar a PDF:** Reportes profesionales con tablas y estadísticas

---

## Modelo de Datos

### Entidades Principales
* **TipoCancha:** Categorías de canchas (Fútbol 5, 7, 11, Paddle, Tenis)
* **Cliente:** Información de clientes con DNI, email y teléfono únicos
* **Cancha:** Canchas disponibles con tipo y precio por hora
* **Reserva:** Reservas con fechas, horarios y estado (Pendiente, Pagada, Cancelada)
* **Pago:** Información de pagos con métodos y comprobantes
* **Servicio:** Servicios adicionales con costos (Iluminación, Vestuarios, Árbitro, Buffet)
* **Torneo:** Torneos con fechas, premio, costo de inscripción y estado
* **Equipo:** Equipos deportivos independientes
* **Partido:** Partidos de torneos con resultados y ganadores

### Relaciones
* Cliente → Reservas (1:N)
* Cancha → Reservas (1:N)
* Reserva → Pago (1:1)
* Reserva → Servicios (N:N)
* Torneo → Reservas (1:N)
* Torneo → Equipos (N:N)
* Torneo → Partidos (1:N)
* Partido → Equipo1, Equipo2, Ganador (N:1)

---

## Características de la Interfaz

* **Diseño Responsivo:** Funciona en desktop, tablet y móvil
* **Framework CSS:** DaisyUI + TailwindCSS para diseño moderno
* **Navegación Intuitiva:** Menú claro con iconos SVG
* **Feedback Visual:** Mensajes de éxito, error, advertencia e información
* **Tarjetas Estadísticas:** Dashboard con métricas en tiempo real
* **Filtros Avanzados:** Búsqueda y filtrado por múltiples criterios
* **Estados con Colores:** Identificación visual clara (verde=pagado, amarillo=pendiente, rojo=cancelado)
* **Validación Frontend:** Verificación de disponibilidad en tiempo real
* **Paginación:** Listados paginados de 10-15 elementos

---

## Testing

El proyecto incluye 28 tests automatizados que verifican:
* Modelos y sus métodos
* Validaciones de negocio
* Creación y edición de entidades
* Cálculo de costos
* Sistema de pagos
* Gestión de torneos y fixtures

Para ejecutar los tests:
```bash
python manage.py test reservas
```

---

## Integrantes del Grupo 60

* **Salvador Gibert**
* **Ignacio Maspero**
* **Tiziana Carrizo**
* **Agustin Rey Laje**
* **Marco Figueroa**

---

## Licencia

Este proyecto es un trabajo académico desarrollado para la materia DAO (Desarrollo de Aplicaciones con Objetos) en la Facultad.

---

## Notas Adicionales

### MercadoPago
La integración con MercadoPago está completamente implementada pero requiere:
* HTTPS en producción (puede usar ngrok para testing local)
* Credenciales de TEST válidas en `settings.py`
* Para demostración local, usar el botón "Marcar como Pagado (Demo)"

### Base de Datos
* El proyecto usa SQLite3 para facilitar el desarrollo
* Para producción se recomienda PostgreSQL o MySQL
* Incluye migraciones completas

### Datos de Prueba
* El comando `poblar_equipos` crea 32 equipos para testing de torneos
* Se recomienda crear datos adicionales manualmente para una demostración completa

---
