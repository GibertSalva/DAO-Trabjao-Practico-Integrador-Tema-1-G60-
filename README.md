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

- Django 5.0.6
- Python 3.13.2
- SQLite3
- DaisyUI + TailwindCSS
- MercadoPago SDK 2.2.0
- ReportLab 4.2.5

---

## Instalación Rápida

```bash
# Clonar repositorio
git clone https://github.com/GibertSalva/DAO-Trabjao-Practico-Integrador-Tema-1-G60-.git
cd DAO-Trabjao-Practico-Integrador-Tema-1-G60-

# Instalar dependencias
pip install -r requirements.txt

# Aplicar migraciones
python manage.py migrate

# Poblar base de datos
python manage.py poblar_equipos

# Iniciar servidor
python manage.py runserver
```

Acceder en: http://127.0.0.1:8000/

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

## Notas

- **MercadoPago:** Requiere HTTPS (usar ngrok para testing local). Para demo sin MP, usar botón "Marcar como Pagado"
- **Base de Datos:** SQLite3 (desarrollo), PostgreSQL/MySQL (producción recomendado)
- **Datos de Prueba:** Comando `poblar_equipos` crea 32 equipos para testing de torneos

---

Proyecto académico - Facultad - Materia DAO
