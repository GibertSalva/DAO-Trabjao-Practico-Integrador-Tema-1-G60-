# Estructura de Templates - Sistema de Reservas Deportivas

## 📁 Organización de Carpetas

Los templates han sido reorganizados en carpetas por entidad para mayor claridad y mantenibilidad:

```
reservas/
├── templates/
│   └── reservas/
│       ├── base.html           # Template base con navbar y estilos
│       ├── home.html            # Página principal del sistema
│       │
│       ├── clientes/            # Templates de Clientes
│       │   ├── lista.html
│       │   ├── detalle.html
│       │   ├── form.html
│       │   └── confirmar_eliminar.html
│       │
│       ├── canchas/             # Templates de Canchas
│       │   ├── lista.html
│       │   ├── detalle.html
│       │   ├── form.html
│       │   └── confirmar_eliminar.html
│       │
│       └── reservas/            # Templates de Reservas
│           ├── lista.html
│           ├── detalle.html
│           ├── form.html
│           └── confirmar_eliminar.html
```

## 📝 Convención de Nombres

### Antes (nomenclatura antigua):
- `cliente_lista.html`, `cliente_detalle.html`, `cliente_form.html`, etc.
- `cancha_lista.html`, `cancha_detalle.html`, `cancha_form.html`, etc.
- `reserva_lista.html`, `reserva_detalle.html`, `reserva_form.html`, etc.

### Ahora (nueva estructura):
- `clientes/lista.html`, `clientes/detalle.html`, `clientes/form.html`, etc.
- `canchas/lista.html`, `canchas/detalle.html`, `canchas/form.html`, etc.
- `reservas/lista.html`, `reservas/detalle.html`, `reservas/form.html`, etc.

## 🎯 Beneficios de esta Estructura

1. **Mayor Claridad**: Es más fácil identificar a qué entidad pertenece cada template
2. **Mejor Organización**: Los archivos relacionados están agrupados en la misma carpeta
3. **Escalabilidad**: Agregar nuevos templates es más simple y organizado
4. **Mantenimiento**: Es más fácil encontrar y modificar templates específicos
5. **Convención Django**: Sigue las mejores prácticas de organización de Django

## 🔧 Archivos Modificados

### `views.py`
Todas las referencias a templates fueron actualizadas:
- `'reservas/cliente_lista.html'` → `'reservas/clientes/lista.html'`
- `'reservas/cancha_detalle.html'` → `'reservas/canchas/detalle.html'`
- `'reservas/reserva_form.html'` → `'reservas/reservas/form.html'`
- etc.

## 📌 Templates Compartidos

Los siguientes templates permanecen en la raíz de `reservas/`:
- **base.html**: Template base con estructura HTML, navbar, estilos CSS y fuentes
- **home.html**: Página principal con estadísticas y acciones rápidas

## 🚀 Cómo Usar

No hay cambios necesarios en el uso del sistema. Todas las URLs y vistas funcionan exactamente igual. Esta reorganización solo afecta la estructura interna de archivos.

## 📊 Resumen de Archivos por Entidad

| Entidad   | Archivos                                                           |
|-----------|-------------------------------------------------------------------|
| Clientes  | lista, detalle, form, confirmar_eliminar                          |
| Canchas   | lista, detalle, form, confirmar_eliminar                          |
| Reservas  | lista, detalle, form, confirmar_eliminar                          |
| Comunes   | base, home                                                        |

---

**Fecha de Reorganización**: 20 de Octubre, 2025  
**Versión Django**: 5.2.7  
**Componentes UI**: DaisyUI 4.4.19 con tema "corporate"
