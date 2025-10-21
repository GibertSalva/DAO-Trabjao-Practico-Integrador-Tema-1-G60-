# Diagrama Entidad-Relación (DER)
## Sistema de Reservas Deportivas - Grupo 60

```
┌─────────────────────┐
│   TipoCancha        │
├─────────────────────┤
│ id (PK)             │
│ nombre              │
│ descripcion         │
└──────────┬──────────┘
           │
           │ 1
           │
           │ N
┌──────────▼──────────┐         N ┌─────────────────────┐ N
│   Cancha            ├──────────►│   Servicio          │
├─────────────────────┤           ├─────────────────────┤
│ id (PK)             │           │ id (PK)             │
│ nombre              │           │ nombre              │
│ precio_por_hora     │           │ costo_adicional     │
│ activa              │           │ activo              │
│ capacidad_personas  │           │ descripcion         │
│ tipo_cancha_id (FK) │           └──────────┬──────────┘
└──────────┬──────────┘                      │
           │                                 │
           │ 1                               │
           │                                 │ N
           │ N                               │
┌──────────▼──────────┐         N ┌──────────▼──────────┐
│   Reserva           ├──────────►│ reserva_servicios   │ (Many-to-Many)
├─────────────────────┤           └─────────────────────┘
│ id (PK)             │
│ fecha_hora_inicio   │
│ fecha_hora_fin      │           ┌─────────────────────┐
│ estado              │        1  │   Cliente           │
│ fecha_creacion      ├──────────►├─────────────────────┤
│ observaciones       │        N  │ id (PK)             │
│ cliente_id (FK)     │           │ nombre              │
│ cancha_id (FK)      │           │ apellido            │
│ torneo_id (FK)      │           │ dni (UNIQUE)        │
└──────────┬──────────┘           │ email (UNIQUE)      │
           │                      │ telefono            │
           │ 1                    │ fecha_registro      │
           │                      │ activo              │
           │ 1                    └──────────┬──────────┘
┌──────────▼──────────┐                     │
│   Pago              │                     │ N (capitan)
├─────────────────────┤                     │
│ reserva_id (PK, FK) │                     │ N (jugadores)
│ monto_total         │           ┌─────────▼──────────┐
│ fecha_pago          │           │   Equipo            │
│ metodo_pago         │           ├─────────────────────┤
│ estado              │           │ id (PK)             │
│ comprobante         │           │ nombre (UNIQUE)     │
│ observaciones       │           │ fecha_creacion      │
└─────────────────────┘           │ activo              │
                                  │ logo                │
                                  │ capitan_id (FK)     │
           ┌──────────────────────┴──────────┬──────────┘
           │                                 │
           │ N                               │ N
           │                                 │
┌──────────▼──────────┐           ┌──────────▼──────────┐
│ equipo_jugadores    │           │ torneo_equipos      │ (Many-to-Many)
│ (Many-to-Many)      │           └──────────┬──────────┘
└─────────────────────┘                      │
                                             │ N
                                  ┌──────────▼──────────┐
                                  │   Torneo            │
                                  ├─────────────────────┤
                                  │ id (PK)             │
                                  │ nombre (UNIQUE)     │
                                  │ descripcion         │
                                  │ fecha_inicio        │
                                  │ fecha_fin           │
                                  │ premio              │
                                  │ costo_inscripcion   │
                                  │ reglamento          │
                                  │ estado              │
                                  │ activo              │
                                  └──────────┬──────────┘
                                             │
                                             │ 1
                                             │
                                             │ N
                                  ┌──────────▼──────────┐
                                  │   Partido           │
                                  ├─────────────────────┤
                                  │ id (PK)             │
                                  │ ronda               │
                                  │ numero_partido      │
                                  │ resultado_equipo1   │
                                  │ resultado_equipo2   │
                                  │ estado              │
                                  │ fecha_hora          │
                                  │ observaciones       │
                                  │ torneo_id (FK)      │
                                  │ equipo1_id (FK)     │
                                  │ equipo2_id (FK)     │
                                  │ ganador_id (FK)     │
                                  │ partido_ant_eq1(FK) │
                                  │ partido_ant_eq2(FK) │
                                  └─────────────────────┘
```

## Cardinalidades y Relaciones

### Relaciones Principales

1. **TipoCancha → Cancha**: 1:N
   - Un tipo de cancha puede tener muchas canchas
   - Una cancha pertenece a un solo tipo

2. **Cliente → Reserva**: 1:N
   - Un cliente puede tener muchas reservas
   - Una reserva pertenece a un solo cliente

3. **Cancha → Reserva**: 1:N
   - Una cancha puede tener muchas reservas
   - Una reserva es para una sola cancha

4. **Reserva ↔ Servicio**: N:M (Many-to-Many)
   - Una reserva puede tener muchos servicios adicionales
   - Un servicio puede estar en muchas reservas

5. **Reserva → Pago**: 1:1
   - Una reserva tiene un único pago
   - Un pago pertenece a una única reserva

6. **Torneo → Reserva**: 1:N (Opcional)
   - Un torneo puede tener muchas reservas asociadas
   - Una reserva puede estar asociada a un torneo (opcional)

### Relaciones de Equipos y Torneos

7. **Cliente → Equipo**: N:M (jugadores) + 1:N (capitán)
   - Un cliente puede ser jugador de varios equipos
   - Un cliente puede ser capitán de varios equipos
   - Un equipo tiene muchos jugadores
   - Un equipo tiene un capitán

8. **Equipo ↔ Torneo**: N:M (Many-to-Many)
   - Un equipo puede participar en varios torneos
   - Un torneo tiene varios equipos inscritos

9. **Torneo → Partido**: 1:N
   - Un torneo tiene muchos partidos
   - Un partido pertenece a un solo torneo

10. **Equipo → Partido**: Múltiples relaciones
    - equipo1: Primer equipo del partido
    - equipo2: Segundo equipo del partido
    - ganador: Equipo que ganó el partido
    - Un equipo puede participar en muchos partidos

11. **Partido → Partido**: Auto-referencia (eliminación directa)
    - partido_anterior_equipo1: De qué partido viene el equipo1
    - partido_anterior_equipo2: De qué partido viene el equipo2
    - Permite construir el árbol de eliminación directa

## Restricciones de Integridad

### Claves Primarias (PK)
- Todas las tablas tienen un `id` como PK, excepto `Pago` que usa `reserva_id`

### Claves Únicas (UNIQUE)
- `TipoCancha.nombre`
- `Cliente.dni`
- `Cliente.email`
- `Servicio.nombre`
- `Torneo.nombre`
- `Equipo.nombre`
- `Partido` → UNIQUE_TOGETHER(torneo, ronda, numero_partido)
- `Reserva` → UNIQUE_TOGETHER(cancha, fecha_hora_inicio)

### Claves Foráneas (FK)
- `Cancha.tipo_cancha_id` → TipoCancha (ON DELETE PROTECT)
- `Reserva.cliente_id` → Cliente (ON DELETE CASCADE)
- `Reserva.cancha_id` → Cancha (ON DELETE CASCADE)
- `Reserva.torneo_id` → Torneo (ON DELETE SET NULL)
- `Pago.reserva_id` → Reserva (ON DELETE CASCADE, 1:1)
- `Equipo.capitan_id` → Cliente (ON DELETE SET NULL)
- `Partido.torneo_id` → Torneo (ON DELETE CASCADE)
- `Partido.equipo1_id` → Equipo (ON DELETE CASCADE)
- `Partido.equipo2_id` → Equipo (ON DELETE CASCADE)
- `Partido.ganador_id` → Equipo (ON DELETE SET NULL)
- `Partido.partido_anterior_equipo1` → Partido (ON DELETE SET NULL)
- `Partido.partido_anterior_equipo2` → Partido (ON DELETE SET NULL)

### Validaciones a Nivel de Dominio

#### Cliente
- DNI: 7-8 dígitos numéricos
- Nombre/Apellido: No contienen números
- Email: Formato válido
- Teléfono: 8-20 caracteres (números, espacios, guiones, paréntesis)
- Límite: Máximo 3 reservas por día

#### Cancha
- precio_por_hora > 0
- capacidad_personas: Entre 2 y 50

#### Reserva
- fecha_hora_fin > fecha_hora_inicio
- No se puede reservar en el pasado
- Horario: Entre 08:00 y 23:00
- Duración: Mínimo 1 hora, máximo 4 horas
- Las fechas deben ser del mismo día
- No puede haber superposición de horarios para la misma cancha

#### Pago
- monto_total > 0 y <= 999,999.99
- Si estado = PAGADO → Debe tener fecha_pago y metodo_pago

#### Torneo
- fecha_fin >= fecha_inicio
- Para generar fixture: Mínimo 2 equipos
- Número de equipos debe ser potencia de 2 (2, 4, 8, 16...)

#### Partido
- No puede haber empate (eliminación directa)
- Si hay resultados → Ambos resultados deben estar presentes
- Si hay resultados → Debe determinarse un ganador

## Enumeraciones (CHOICES)

### Reserva.estado
- PENDIENTE
- PAGADA (la fecha de pago se establece automáticamente al cambiar a este estado)
- CANCELADA

### Pago.estado
- PENDIENTE
- PAGADO
- REEMBOLSADO

### Pago.metodo_pago
- EFECTIVO
- ONLINE
- TRANSFERENCIA
- TARJETA_DEBITO
- TARJETA_CREDITO

### Torneo.estado
- INSCRIPCION (Abierto para inscripciones)
- EN_CURSO
- FINALIZADO

### Partido.estado
- PENDIENTE
- FINALIZADO
- WALKOVER (Un equipo no se presentó)

---

## Autores
**Grupo 60 - UTN FRC - DAO 2025**
- Gibert
- Maspero
- Carrizo
- Rey Laje
- Figueroa
