# Sistema de Reservas de Canchas Deportivas

Este proyecto es un Trabajo Práctico Integrador para la materia Desarrollo de Aplicaciones con Objetos (DAO), enfocado en el desarrollo de una aplicación web completa para la gestión de reservas de canchas deportivas.

El sistema permite a los administradores gestionar clientes, canchas y horarios, mientras que los usuarios pueden registrar y administrar sus reservas de forma sencilla.

---

## Funcionalidades Principales

El sistema cubre todas las operaciones necesarias para la administración de un complejo deportivo.

* **Gestión (ABM):** Administración completa de clientes, canchas y horarios disponibles.
* **Reservas:** Registro de nuevas reservas, asociando un cliente a una cancha en una fecha y hora específicas.
* **Validación de Disponibilidad:** El sistema verifica automáticamente que una cancha no esté ocupada antes de confirmar una nueva reserva.
* **Gestión de Torneos:** Funcionalidad para organizar y administrar campeonatos deportivos con sistema de eliminación directa.
* **Servicios Adicionales:** Control de servicios asociados como la iluminación de la cancha.
* **Gestión de Equipos:** Registro y administración de equipos deportivos para participar en torneos.
* **Fixture Automático:** Generación automática de partidos y calendario de torneos.
* **Registro de Resultados:** Sistema para ingresar resultados de partidos y determinar ganadores automáticamente.

---

## Reportes y Estadísticas

La aplicación es capaz de generar reportes detallados y visualizaciones para el análisis del negocio.

* **Listados Detallados:**
    * Reservas por cliente con totales de gasto.
    * Reservas por cancha en un período de tiempo determinado.
    * Ranking de las canchas más utilizadas con métricas de horas e ingresos.
* **Gráficos Estadísticos:**
    * Visualización del uso mensual de las canchas para analizar tendencias.
    * Gráficos de barras con totales de reservas por mes.

---

## Tecnologías Utilizadas

* **Backend Framework:** Django 5.2.7
* **Base de Datos:** SQLite
* **Frontend:** HTML, CSS (TailwindCSS/DaisyUI), JavaScript
* **Lenguaje:** Python 3.13

---

## Modelo de Base de Datos

El sistema se estructura en torno al siguiente Modelo Entidad-Relación (MER):

![Diagrama Entidad-Relación](/Documentacion/modeloEntidadRelacion.png)

---

## Instalación y Configuración

Sigue estos pasos para levantar el proyecto en tu entorno local.

1.  **Clonar el repositorio:**
    ```bash
    git clone https://github.com/GibertSalva/DAO-Trabjao-Practico-Integrador-Tema-1-G60-.git
    cd DAO-Trabjao-Practico-Integrador-Tema-1-G60-
    ```

2.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Aplicar las migraciones de la base de datos:**
    ```bash
    python manage.py migrate
    ```

4.  **Crear un superusuario (opcional, para acceder al panel de administración):**
    ```bash
    python manage.py createsuperuser
    ```

5.  **Iniciar el servidor de desarrollo:**
    ```bash
    python manage.py runserver
    ```

Una vez iniciado el servidor, puede acceder a la aplicación en `http://127.0.0.1:8000`.

---

## Estructura del Proyecto

```
DAO-Trabjao-Practico-Integrador-Tema-1-G60-/
├── canchas_project/          # Configuración principal de Django
│   ├── settings.py          # Configuración del proyecto
│   ├── urls.py              # URLs principales
│   ├── wsgi.py              # Configuración WSGI
│   └── asgi.py              # Configuración ASGI
├── reservas/                 # Aplicación principal
│   ├── models.py            # Modelos de datos (Cliente, Cancha, Reserva, Torneo, etc.)
│   ├── views.py             # Lógica de vistas y controladores
│   ├── urls.py              # Rutas de la aplicación
│   ├── admin.py             # Configuración del panel de administración
│   ├── templates/           # Plantillas HTML
│   │   └── reservas/        # Templates organizados por módulo
│   ├── static/              # Archivos estáticos
│   │   └── reservas/
│   │       ├── css/         # Estilos personalizados
│   │       └── js/          # Scripts JavaScript
│   ├── migrations/          # Migraciones de base de datos
│   └── management/          # Comandos personalizados de Django
├── documentacion/           # Documentación técnica del proyecto
├── db.sqlite3               # Base de datos SQLite
├── manage.py                # Script de gestión de Django
└── requirements.txt         # Dependencias del proyecto
```

---

## Integrantes del Grupo G60

* [Salvador Gibert]
* [Ignacio Maspero]
* [Tiziana Carrizo]
* [Agustin Rey Laje]
* [Marco Figueroa]