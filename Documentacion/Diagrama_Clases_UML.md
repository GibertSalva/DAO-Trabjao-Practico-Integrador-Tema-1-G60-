# Diagrama de Clases UML
## Sistema de Reservas Deportivas - Grupo 60

```
┌────────────────────────────────────────────────┐
│                  TipoCancha                    │
├────────────────────────────────────────────────┤
│ - id: Integer                                  │
│ - nombre: String [unique]                      │
│ - descripcion: Text [nullable]                 │
├────────────────────────────────────────────────┤
│ + __str__(): String                            │
└────────────────────────────────────────────────┘
                      △
                      │
                      │ 1
                      │
                      │ N
┌────────────────────────────────────────────────┐
│                    Cancha                      │
├────────────────────────────────────────────────┤
│ - id: Integer                                  │
│ - nombre: String                               │
│ - precio_por_hora: Decimal(10,2)              │
│ - activa: Boolean                              │
│ - capacidad_personas: PositiveInteger          │
│ - tipo_cancha: ForeignKey → TipoCancha         │
├────────────────────────────────────────────────┤
│ + __str__(): String                            │
│ + clean(): void                                │
│ + esta_disponible(inicio, fin): Boolean        │
└────────────────────────────────────────────────┘
                      △
                      │
                      │ 1
                      │
                      │ N
┌────────────────────────────────────────────────┐
│                   Reserva                      │
├────────────────────────────────────────────────┤
│ - id: Integer                                  │
│ - fecha_hora_inicio: DateTime                  │
│ - fecha_hora_fin: DateTime                     │
│ - estado: Enum[PENDIENTE,PAGADA,CANCELADA]     │
│ - fecha_creacion: DateTime [auto]              │
│ - observaciones: Text [nullable]               │
│ - cliente: ForeignKey → Cliente                │
│ - cancha: ForeignKey → Cancha                  │
│ - torneo: ForeignKey → Torneo [nullable]       │
│ - servicios: ManyToMany → Servicio             │
├────────────────────────────────────────────────┤
│ + __str__(): String                            │
│ + clean(): void                                │
│ + calcular_costo_total(): Float               │
│ + duracion_horas(): Float                      │
└────────────────────────────────────────────────┘
                      △
                      │
                      │ 1
                      │
                      │ 1
┌────────────────────────────────────────────────┐
│                     Pago                       │
├────────────────────────────────────────────────┤
│ - reserva: OneToOne → Reserva [PK]             │
│ - monto_total: Decimal(10,2)                   │
│ - fecha_pago: DateTime [nullable]              │
│ - metodo_pago: Enum [nullable]                 │
│   [EFECTIVO,ONLINE,TRANSFERENCIA,              │
│    TARJETA_DEBITO,TARJETA_CREDITO]             │
│ - estado: Enum[PENDIENTE,PAGADO,REEMBOLSADO]   │
│ - comprobante: String [nullable]               │
│ - observaciones: Text [nullable]               │
├────────────────────────────────────────────────┤
│ + __str__(): String                            │
│ + clean(): void                                │
│ + marcar_como_pagado(metodo, comprob.): void   │
└────────────────────────────────────────────────┘


┌────────────────────────────────────────────────┐
│                   Cliente                      │
├────────────────────────────────────────────────┤
│ - id: Integer                                  │
│ - nombre: String                               │
│ - apellido: String                             │
│ - dni: String [unique, 7-8 dígitos]            │
│ - email: Email [unique]                        │
│ - telefono: String                             │
│ - fecha_registro: DateTime [auto]              │
│ - activo: Boolean                              │
├────────────────────────────────────────────────┤
│ + __str__(): String                            │
│ + clean(): void                                │
│ + puede_reservar(fecha): Boolean               │
└────────────────────────────────────────────────┘
          △                         △
          │                         │
          │ 1                       │ N (jugadores)
          │                         │
          │ N                       │ 1 (capitan)
          │                         │
┌─────────┴─────────────────────────┴────────────┐
│                    Equipo                      │
├────────────────────────────────────────────────┤
│ - id: Integer                                  │
│ - nombre: String [unique]                      │
│ - fecha_creacion: DateTime [auto]              │
│ - activo: Boolean                              │
│ - logo: String [nullable, max 10 chars]        │
│ - capitan: ForeignKey → Cliente [nullable]     │
│ - jugadores: ManyToMany → Cliente              │
├────────────────────────────────────────────────┤
│ + __str__(): String                            │
│ + clean(): void                                │
│ + jugadores_count(): Integer                   │
│ + torneos_activos(): QuerySet[Torneo]          │
└────────────────────────────────────────────────┘
                      △
                      │
                      │ N
                      │
                      │ M (torneo_equipos)
                      │
                      │ N
┌────────────────────────────────────────────────┐
│                   Torneo                       │
├────────────────────────────────────────────────┤
│ - id: Integer                                  │
│ - nombre: String [unique]                      │
│ - descripcion: Text [nullable]                 │
│ - fecha_inicio: Date                           │
│ - fecha_fin: Date                              │
│ - premio: String [nullable]                    │
│ - costo_inscripcion: Decimal(10,2)             │
│ - reglamento: Text [nullable]                  │
│ - estado: Enum[INSCRIPCION,EN_CURSO,FINALIZADO]│
│ - activo: Boolean                              │
│ - equipos: ManyToMany → Equipo                 │
├────────────────────────────────────────────────┤
│ + __str__(): String                            │
│ + clean(): void                                │
│ + equipos_count(): Integer                     │
│ + puede_agregar_equipos(): Boolean             │
│ + generar_fixture(): void                      │
└────────────────────────────────────────────────┘
                      △
                      │
                      │ 1
                      │
                      │ N
┌────────────────────────────────────────────────┐
│                   Partido                      │
├────────────────────────────────────────────────┤
│ - id: Integer                                  │
│ - ronda: PositiveInteger                       │
│ - numero_partido: PositiveInteger              │
│ - resultado_equipo1: PositiveInteger [nullable]│
│ - resultado_equipo2: PositiveInteger [nullable]│
│ - estado: Enum[PENDIENTE,FINALIZADO,WALKOVER]  │
│ - fecha_hora: DateTime [nullable]              │
│ - observaciones: Text [nullable]               │
│ - torneo: ForeignKey → Torneo                  │
│ - equipo1: ForeignKey → Equipo [nullable]      │
│ - equipo2: ForeignKey → Equipo [nullable]      │
│ - ganador: ForeignKey → Equipo [nullable]      │
│ - partido_anterior_equipo1: FK → Partido [null]│
│ - partido_anterior_equipo2: FK → Partido [null]│
├────────────────────────────────────────────────┤
│ + __str__(): String                            │
│ + clean(): void                                │
│ + save(*args, **kwargs): void                  │
│ + avanzar_ganador(): void                      │
│ + nombre_ronda(): String                       │
│ + get_ronda_display(): String                  │
│ @property siguiente_partido: Partido [nullable]│
└────────────────────────────────────────────────┘


┌────────────────────────────────────────────────┐
│                   Servicio                     │
├────────────────────────────────────────────────┤
│ - id: Integer                                  │
│ - nombre: String [unique]                      │
│ - costo_adicional: Decimal(10,2)               │
│ - activo: Boolean                              │
│ - descripcion: Text [nullable]                 │
├────────────────────────────────────────────────┤
│ + __str__(): String                            │
└────────────────────────────────────────────────┘
```

## Constantes del Sistema

```python
HORA_APERTURA = 08:00 AM
HORA_CIERRE = 23:00 PM
DURACION_MINIMA_RESERVA = 1 hora
DURACION_MAXIMA_RESERVA = 4 horas
MAX_RESERVAS_POR_CLIENTE_DIA = 3
```

## Relaciones Detalladas

### Herencia
No hay herencia explícita. Todos los modelos heredan de `django.db.models.Model`

### Asociaciones

#### 1. TipoCancha → Cancha (1:N - Composición)
- **Cardinalidad**: 1 TipoCancha puede tener N Canchas
- **Navegabilidad**: Bidireccional
- **Rol**: tipo_cancha (Cancha) / canchas (TipoCancha)
- **ON DELETE**: PROTECT (no se puede eliminar un tipo si tiene canchas)

#### 2. Cliente → Reserva (1:N - Agregación)
- **Cardinalidad**: 1 Cliente puede tener N Reservas
- **Navegabilidad**: Bidireccional
- **Rol**: cliente (Reserva) / reservas (Cliente)
- **ON DELETE**: CASCADE
- **Constraint**: Máximo 3 reservas por día

#### 3. Cancha → Reserva (1:N - Agregación)
- **Cardinalidad**: 1 Cancha puede tener N Reservas
- **Navegabilidad**: Bidireccional
- **Rol**: cancha (Reserva) / reservas (Cancha)
- **ON DELETE**: CASCADE
- **Constraint**: No superposición de horarios

#### 4. Reserva ↔ Servicio (N:M - Asociación)
- **Cardinalidad**: N Reservas pueden tener M Servicios
- **Navegabilidad**: Bidireccional
- **Rol**: servicios (Reserva) / reservas (Servicio)
- **Tabla intermedia**: reserva_servicios (generada automáticamente)

#### 5. Reserva → Pago (1:1 - Composición)
- **Cardinalidad**: 1 Reserva tiene exactamente 1 Pago
- **Navegabilidad**: Bidireccional
- **Rol**: pago (Reserva) / reserva (Pago)
- **ON DELETE**: CASCADE
- **Nota**: Pago usa reserva_id como PK

#### 6. Torneo → Reserva (1:N - Agregación opcional)
- **Cardinalidad**: 1 Torneo puede tener N Reservas (opcional)
- **Navegabilidad**: Bidireccional
- **Rol**: torneo (Reserva) / reservas (Torneo)
- **ON DELETE**: SET NULL
- **Constraint**: Reserva puede existir sin torneo

#### 7. Cliente → Equipo - Capitán (1:N)
- **Cardinalidad**: 1 Cliente puede ser capitán de N Equipos
- **Navegabilidad**: Bidireccional
- **Rol**: capitan (Equipo) / equipos_capitaneados (Cliente)
- **ON DELETE**: SET NULL

#### 8. Cliente ↔ Equipo - Jugadores (N:M)
- **Cardinalidad**: N Clientes pueden estar en M Equipos
- **Navegabilidad**: Bidireccional
- **Rol**: jugadores (Equipo) / equipos (Cliente)
- **Tabla intermedia**: equipo_jugadores (generada automáticamente)

#### 9. Equipo ↔ Torneo (N:M - Asociación)
- **Cardinalidad**: N Equipos pueden participar en M Torneos
- **Navegabilidad**: Bidireccional
- **Rol**: equipos (Torneo) / torneos (Equipo)
- **Tabla intermedia**: torneo_equipos (generada automáticamente)
- **Constraint**: Solo se pueden agregar equipos si estado = INSCRIPCION

#### 10. Torneo → Partido (1:N - Composición)
- **Cardinalidad**: 1 Torneo tiene N Partidos
- **Navegabilidad**: Bidireccional
- **Rol**: torneo (Partido) / partidos (Torneo)
- **ON DELETE**: CASCADE
- **Constraint**: Sistema de eliminación directa

#### 11. Equipo → Partido (Múltiples asociaciones)
- **equipo1**: Primer equipo del partido
- **equipo2**: Segundo equipo del partido
- **ganador**: Equipo ganador (nullable hasta que termine)
- **ON DELETE**: CASCADE (equipo1, equipo2), SET NULL (ganador)

#### 12. Partido → Partido (Auto-referencia - Árbol de eliminación)
- **partido_anterior_equipo1**: De dónde viene equipo1
- **partido_anterior_equipo2**: De dónde viene equipo2
- **Navegabilidad**: Unidireccional (padre → hijo)
- **ON DELETE**: SET NULL
- **Constraint**: Construye el bracket de eliminación directa

## Métodos Importantes por Clase

### Cliente
- `puede_reservar(fecha)`: Valida límite de 3 reservas por día
- `clean()`: Valida formato de datos (nombre sin números, DNI, etc.)

### Cancha
- `esta_disponible(fecha_inicio, fecha_fin)`: Verifica disponibilidad
- `clean()`: Valida precio > 0

### Reserva
- `clean()`: Validaciones exhaustivas (horario, duración, disponibilidad, etc.)
- `calcular_costo_total()`: Cancha + servicios adicionales
- `duracion_horas()`: Calcula duración en horas

### Pago
- `marcar_como_pagado(metodo, comprobante)`: Actualiza estado y fecha
- `clean()`: Valida que pago PAGADO tenga fecha y método

### Torneo
- `generar_fixture()`: Crea partidos de eliminación directa
- `puede_agregar_equipos()`: Solo si estado = INSCRIPCION
- `equipos_count()`: Cantidad de equipos inscritos

### Partido
- `avanzar_ganador()`: Avanza ganador a siguiente ronda automáticamente
- `nombre_ronda()`: Retorna "Final", "Semifinal", "Cuartos", etc.
- `siguiente_partido`: Property para obtener el partido de la siguiente ronda

## Validaciones y Reglas de Negocio

### A nivel de Modelo (método clean())

**Cliente:**
- DNI: 7-8 dígitos numéricos únicos
- Email: Único y válido
- Nombre/Apellido: Sin números, auto-capitalize
- Teléfono: 8-20 caracteres válidos

**Cancha:**
- precio_por_hora > 0
- capacidad_personas: 2-50
- activa = True para permitir reservas

**Reserva:**
1. fecha_hora_fin > fecha_hora_inicio
2. No reservar en el pasado
3. Horario: 08:00 - 23:00
4. Duración: 1-4 horas
5. Mismo día (no cruzar medianoche)
6. Sin superposición en misma cancha
7. Cliente activo y no excede 3 reservas/día
8. Cancha activa

**Pago:**
- monto_total > 0 y <= $999,999.99
- Si PAGADO → fecha_pago y metodo_pago obligatorios

**Torneo:**
- fecha_fin >= fecha_inicio
- Para fixture: Equipos potencia de 2 (2,4,8,16...)
- Mínimo 2 equipos

**Partido:**
- No empates en eliminación directa
- Si hay resultado → Ganador automático
- Resultado completo (ambos equipos)

### A nivel de Base de Datos (constraints)

**UNIQUE:**
- TipoCancha.nombre
- Cliente.dni
- Cliente.email
- Servicio.nombre
- Torneo.nombre
- Equipo.nombre

**UNIQUE_TOGETHER:**
- Partido(torneo, ronda, numero_partido)
- Reserva(cancha, fecha_hora_inicio)

**CHECK:**
- precio_por_hora > 0
- capacidad_personas >= 2 AND <= 50
- monto_total > 0 AND <= 999999.99

## Patrones de Diseño Utilizados

### 1. Active Record
- Cada modelo encapsula su lógica de negocio y persistencia
- Métodos `clean()`, `save()`, validaciones en el modelo

### 2. Observer (implícito en Django)
- Señales `post_save`, `pre_save` (no implementadas pero disponibles)
- `Partido.save()` → `avanzar_ganador()` (observer manual)

### 3. State Pattern
- Estados de Reserva: PENDIENTE → PAGADA / CANCELADA (la fecha de pago se establece automáticamente al marcar como PAGADA)
- Estados de Pago: PENDIENTE → PAGADO / REEMBOLSADO
- Estados de Torneo: INSCRIPCION → EN_CURSO → FINALIZADO
- Estados de Partido: PENDIENTE → FINALIZADO / WALKOVER

### 4. Composite (estructura de árbol)
- Bracket de eliminación directa en Partido
- Auto-referencia: `partido_anterior_equipo1`, `partido_anterior_equipo2`

### 5. Strategy (implícito)
- Diferentes métodos de pago (EFECTIVO, ONLINE, TRANSFERENCIA, etc.)
- Extensible para agregar nuevas estrategias

## Diagramas de Secuencia Clave

### Secuencia 1: Crear Reserva
```
Cliente → Reserva.clean()
  → Validar horarios
  → Validar duración
  → Cancha.esta_disponible()
  → Cliente.puede_reservar()
  → Reserva.save()
    → Pago.create(monto_total)
```

### Secuencia 2: Generar Fixture de Torneo
```
Torneo.generar_fixture()
  → Validar estado = INSCRIPCION
  → Validar equipos >= 2
  → Validar equipos = potencia de 2
  → Eliminar partidos anteriores
  → Crear partidos de ronda 1
  → Torneo.estado = EN_CURSO
```

### Secuencia 3: Registrar Resultado de Partido
```
Partido.clean()
  → Validar resultados completos
  → Validar no empate
  → Determinar ganador
  → Partido.save()
    → avanzar_ganador()
      → Buscar siguiente_partido
      → Asignar ganador a siguiente ronda
```

---

## Autores
**Grupo 60 - UTN FRC - DAO 2025**
- Gibert
- Maspero
- Carrizo
- Rey Laje
- Figueroa
