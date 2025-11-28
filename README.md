# Sistema de Reservas de Canchas Deportivas

Trabajo Práctico Integrador para la materia DAO (Desarrollo de Aplicaciones con Objetos). Sistema web completo para la gestión de reservas de canchas deportivas con administración de clientes, torneos, pagos y reportes estadísticos.

![Diagrama Entidad-Relación](documentacion/modeloEntidadRelacion.png)

---

## Características Principales

- **CRUD Completo:** Clientes, Canchas, Reservas, Torneos y Equipos
- **Validación de Disponibilidad:** Verificación en tiempo real de horarios
- **Sistema de Pagos:** Múltiples métodos + integración MercadoPago
- **Gestión de Torneos:** Fixture automático por eliminación directa
- **Reportes Avanzados:** Estadísticas con exportación a PDF
- **Testing:** 28 tests automatizados

---

## Tecnologías

- **Backend:** Django 5.2.7
- **Lenguaje:** Python 3.10+
- **Base de Datos:** SQLite3 (desarrollo)
- **Frontend:** DaisyUI + TailwindCSS (vía CDN)
- **Pagos:** MercadoPago SDK 2.2.3
- **PDFs:** ReportLab 4.2.5
- **Gráficos:** ApexCharts (vía CDN)

---

## 📋 Requisitos Previos

- **Python 3.10 o superior** (Recomendado: 3.11+)
- **pip** (gestor de paquetes de Python)
- **Git** (para clonar el repositorio)

---

## 🚀 Guía de Instalación

### 1️⃣ Clonar el Repositorio

```bash
git clone https://github.com/GibertSalva/DAO-Trabjao-Practico-Integrador-Tema-1-G60-.git
cd DAO-Trabjao-Practico-Integrador-Tema-1-G60-
```

### 2️⃣ Crear Entorno Virtual (Recomendado)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Instalar Dependencias

```bash
pip install -r requirements.txt
```

**Dependencias principales:**
- Django 5.2.7
- mercadopago 2.2.3
- reportlab 4.2.5
- Pillow 11.0.0

### 4️⃣ Configurar Base de Datos

```bash
# Aplicar migraciones
python manage.py migrate
```

### 5️⃣ Poblar Datos Iniciales (Opcional pero Recomendado)

```bash
# Crear tipos de canchas y equipos básicos
python manage.py poblar_equipos
```

Este comando crea:
- ✅ 4 tipos de canchas (Fútbol 5, Fútbol 7, Fútbol 11, Paddle)
- ✅ 32 equipos para testing de torneos

**Para datos masivos de prueba:**
```bash
# Ejecutar el script de poblado masivo (100 clientes, 20 canchas, 1000 reservas)
python poblar_masivo.py
```

### 6️⃣ Crear Superusuario (Opcional)

```bash
python manage.py createsuperuser
```

Acceso al admin: http://127.0.0.1:8000/admin/

### 7️⃣ Iniciar el Servidor

```bash
python manage.py runserver
```

**Acceder a la aplicación:** http://127.0.0.1:8000/

---

## 🎯 Inicio Rápido (Script Completo)

**Para ejecutar todo de una vez:**

```bash
# Windows
git clone https://github.com/GibertSalva/DAO-Trabjao-Practico-Integrador-Tema-1-G60-.git
cd DAO-Trabjao-Practico-Integrador-Tema-1-G60-
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

```bash
# Linux/Mac
git clone https://github.com/GibertSalva/DAO-Trabjao-Practico-Integrador-Tema-1-G60-.git
cd DAO-Trabjao-Practico-Integrador-Tema-1-G60-
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

---

## 🧪 Ejecutar Tests

```bash
# Todos los tests
python manage.py test reservas

# Con verbosidad
python manage.py test reservas --verbosity=2

# Tests específicos
python manage.py test reservas.tests.TestClienteModel
```

**28 tests automatizados** verifican:
- ✅ Validaciones de modelos
- ✅ CRUD completo
- ✅ Cálculos de costos
- ✅ Lógica de negocio
- ✅ Patrón State (transiciones de estado)

---

## ⚙️ Configuración Adicional

### MercadoPago (Opcional)

Para habilitar pagos con MercadoPago, editar `canchas_project/settings.py`:

```python
# Credenciales de MercadoPago (obtener en developers.mercadopago.com)
MP_PUBLIC_KEY = 'tu_public_key'
MP_ACCESS_TOKEN = 'tu_access_token'
```

**Nota:** MercadoPago requiere HTTPS. Para testing local usar [ngrok](https://ngrok.com/).

---

## 📂 Estructura del Proyecto

```
DAO-Trabjao-Practico-Integrador-Tema-1-G60-/
├── canchas_project/          # Configuración Django
│   ├── settings.py           # Configuración principal
│   ├── urls.py               # URLs del proyecto
│   └── wsgi.py              
├── reservas/                 # App principal
│   ├── models.py             # Modelos de datos
│   ├── views.py              # Lógica de vistas
│   ├── urls.py               # URLs de la app
│   ├── admin.py              # Panel de administración
│   ├── tests.py              # Tests automatizados
│   ├── templates/            # Plantillas HTML
│   ├── static/               # CSS/JS
│   └── management/           # Comandos personalizados
│       └── commands/
│           └── poblar_equipos.py
├── documentacion/            # Diagramas y docs
├── db.sqlite3               # Base de datos (generada)
├── manage.py                # CLI de Django
├── requirements.txt         # Dependencias
├── poblar_masivo.py         # Script de datos masivos
└── README.md                # Este archivo
```

---

## Funcionalidades

### Gestión de Entidades
- **Clientes:** CRUD con validación de DNI y email únicos
- **Canchas:** Tipos (Fútbol 5/7/11, Paddle, Tenis) con precios por hora
- **Reservas:** Validación de disponibilidad, cálculo automático de costos
- **Torneos:** Inscripción de equipos, fixture automático, registro de resultados
- **Equipos:** Gestión independiente para torneos

### Sistema de Pagos
- Métodos: Efectivo, Tarjeta, Transferencia, MercadoPago
- Estados: Pendiente, Pagado, Reembolsado
- Integración completa con MercadoPago (requiere HTTPS en producción)
- Botón de demostración para testing local

### Reportes y Estadísticas
- Top 10 clientes por gasto total
- Distribución de ingresos por cancha
- Ranking de canchas más utilizadas
- Gráfico de utilización mensual (últimos 6 meses)
- Exportación profesional a PDF

---

## Modelo de Datos

![Diagrama Entidad-Relación](documentacion/modeloEntidadRelacion.png)

### Entidades Principales
- **TipoCancha:** Categorías de canchas
- **Cliente:** DNI, email, teléfono (únicos)
- **Cancha:** Tipo y precio por hora
- **Reserva:** Fechas, horarios, estado
- **Pago:** Métodos, comprobantes, integración MP
- **Servicio:** Adicionales (Iluminación, Vestuarios, Árbitro, Buffet)
- **Torneo:** Fechas, premio, costo inscripción
- **Equipo:** Equipos deportivos
- **Partido:** Resultados de torneos

### Relaciones Clave
- Cliente → Reservas (1:N)
- Reserva → Pago (1:1)
- Reserva → Servicios (N:N)
- Torneo → Equipos (N:N)
- Torneo → Partidos (1:N)

---

## 🔍 Uso del Sistema

### Navegación Principal

1. **Home:** Dashboard con accesos rápidos
2. **Clientes:** CRUD completo con búsqueda y filtros
3. **Canchas:** Gestión de canchas y tipos
4. **Reservas:** Crear y gestionar reservas con validación de disponibilidad
5. **Torneos:** Crear torneos, inscribir equipos, generar fixture, registrar resultados
6. **Equipos:** Gestión de equipos deportivos
7. **Reportes:** Estadísticas avanzadas con exportación a PDF

### Flujo Típico de Reserva

1. **Crear Cliente** (si no existe)
2. **Verificar Disponibilidad** de cancha
3. **Crear Reserva** (seleccionar fecha, horario, cancha, servicios opcionales)
4. **Generar Pago** (automático al crear reserva)
5. **Pagar Reserva** (efectivo, tarjeta, transferencia o MercadoPago)

### Gestión de Torneos

1. **Crear Torneo** (nombre, fechas, premio, reglamento)
2. **Inscribir Equipos** (mínimo 2, debe ser potencia de 2: 2, 4, 8, 16, 32...)
3. **Generar Fixture** (automático por eliminación directa)
4. **Registrar Resultados** de cada partido
5. **Ver Avances** en la tabla de fixture

---

## 🎨 Características Destacadas

### Validaciones Inteligentes
- ✅ DNI argentino (7-8 dígitos)
- ✅ Email y DNI únicos por cliente
- ✅ Disponibilidad de canchas en tiempo real
- ✅ Horarios de apertura/cierre (8:00 - 23:00)
- ✅ Duración de reservas (1-4 horas)
- ✅ Máximo 3 reservas por cliente por día
- ✅ Validación de fixture (equipos potencia de 2)

### Cálculo Automático de Costos
- **Base:** Precio por hora × duración + servicios
- **Descuentos:** 
  - 10% clientes frecuentes (5+ reservas pagadas)
  - 15% horario matutino (8:00-12:00)
  - 25% reservas de torneo
- **Recargos:**
  - 20% horario pico (18:00-22:00)

### Estados de Reserva (Patrón State)
- **PENDIENTE:** Puede pagar o cancelar
- **PAGADA:** Solo puede cancelar (genera reembolso)
- **CANCELADA:** Estado final, no puede modificarse

---

## 📊 Reportes Disponibles

1. **Top 10 Clientes por Gasto Total**
   - Gráfico de barras horizontales
   - Detalle de reservas por cliente
   
2. **Distribución de Ingresos por Cancha**
   - Gráfico de dona
   - Ingresos totales y horas jugadas
   
3. **Ranking de Canchas Más Utilizadas**
   - Tabla ordenada por número de reservas
   - Métricas: reservas, horas, ingresos
   
4. **Utilización Mensual (últimos 6 meses)**
   - Gráfico de barras: cantidad de reservas
   - Gráfico de línea: total de horas

**Exportación:** Botón "Descargar PDF" genera reporte completo en formato profesional.

---

## 🐛 Solución de Problemas

### Error: "No module named 'django'"
```bash
pip install -r requirements.txt
```

### Error: "Table doesn't exist"
```bash
python manage.py migrate
```

### Base de datos corrupta
```bash
# Windows
del db.sqlite3
python manage.py migrate

# Linux/Mac
rm db.sqlite3
python manage.py migrate
```

### Puerto 8000 ocupado
```bash
python manage.py runserver 8080
```

### Tests fallan
```bash
# Reinstalar dependencias
pip install --force-reinstall -r requirements.txt
python manage.py test reservas
```

---

## Testing

28 tests automatizados verifican modelos, validaciones, CRUD, cálculos y lógica de negocio.

```bash
python manage.py test reservas
```

---

## Integrantes - Grupo 60

- Salvador Gibert
- Ignacio Maspero
- Tiziana Carrizo
- Agustin Rey Laje
- Marco Figueroa

---

## Documentación Adicional

- **DER:** `documentacion/DER_Sistema_Reservas.md`
- **Diagrama UML:** `documentacion/Diagrama_Clases_UML.md`
- **Setup MercadoPago:** `MERCADOPAGO_SETUP.md`

---

## 💡 Notas Importantes

### MercadoPago
- Requiere HTTPS en producción
- Para testing local sin HTTPS, usar el botón "Marcar como Pagado"
- Configurar credenciales en `settings.py` (opcional)
- Documentación: [MercadoPago Developers](https://www.mercadopago.com.ar/developers)

### Base de Datos
- **Desarrollo:** SQLite3 (incluida, no requiere instalación)
- **Producción:** PostgreSQL o MySQL recomendados
- Archivo: `db.sqlite3` (se genera automáticamente)

### Datos de Prueba
- `poblar_equipos`: 32 equipos para torneos
- `poblar_masivo.py`: 100 clientes, 20 canchas, 1000 reservas

### Seguridad
- `SECRET_KEY` en settings.py debe cambiarse en producción
- `DEBUG = False` en producción
- Usar variables de entorno para credenciales sensibles

---

##  Patrones de Diseño Implementados

### Patrón Strategy (Cálculo de Costos)
5 estrategias diferentes para calcular el costo de una reserva:
- Costo base
- Descuento cliente frecuente
- Descuento horario matutino
- Recargo horario pico
- Descuento torneo

### Patrón State (Estados de Reserva)
Gestión de transiciones de estado con validaciones:
- PENDIENTE → PAGADA (método `pagar()`)
- PENDIENTE/PAGADA → CANCELADA (método `cancelar()`)
- Validaciones: `puede_pagar()`, `puede_cancelar()`, `puede_editar()`

---

## 👥 Integrantes - Grupo 60

- Salvador Gibert
- Ignacio Maspero
- Tiziana Carrizo
- Agustin Rey Laje
- Marco Figueroa

---

