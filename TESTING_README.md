# Guía de Tests con Pytest

## 📋 Descripción
Suite de tests completa para el sistema de reservas de canchas usando **pytest** y **pytest-django**.

## 🚀 Instalación

```bash
pip install -r requirements.txt
```

## 🧪 Ejecutar Tests

### Ejecutar todos los tests
```bash
pytest
```

### Ejecutar con salida detallada
```bash
pytest -v
```

### Ejecutar solo tests unitarios
```bash
pytest -m unit
```

### Ejecutar solo tests de integración
```bash
pytest -m integration
```

### Ejecutar solo tests end-to-end
```bash
pytest -m e2e
```

### Ejecutar un archivo específico
```bash
pytest reservas/tests/test_models.py
pytest reservas/tests/test_views.py
pytest reservas/tests/test_e2e.py
```

### Ejecutar un test específico
```bash
pytest reservas/tests/test_models.py::TestReserva::test_no_permite_reservar_en_pasado
```

### Ejecutar con reporte de cobertura
```bash
pytest --cov=reservas --cov-report=html
```

Luego abre `htmlcov/index.html` en tu navegador para ver el reporte detallado.

### Ejecutar tests que fallaron anteriormente
```bash
pytest --lf
```

### Ejecutar en modo watch (requiere pytest-watch)
```bash
pip install pytest-watch
ptw
```

## 📊 Estructura de Tests

```
reservas/tests/
├── __init__.py
├── conftest.py              # Fixtures reutilizables
├── test_models.py           # Tests unitarios (18 tests)
├── test_views.py            # Tests de integración (14 tests)
└── test_e2e.py             # Tests end-to-end (8 tests)
```

**Total: 40 tests**
- ~45% Tests unitarios (modelos, lógica de negocio)
- ~35% Tests de integración (vistas, HTTP)
- ~20% Tests end-to-end (flujos completos)

## 🎯 Marcadores (Markers)

Los tests están organizados con marcadores:

- `@pytest.mark.unit` - Tests unitarios de modelos
- `@pytest.mark.integration` - Tests de integración de vistas
- `@pytest.mark.e2e` - Tests end-to-end de flujos completos

## 🔧 Fixtures Disponibles

Definidas en `conftest.py`:

### Modelos básicos:
- `cliente` - Cliente de prueba
- `cancha` - Cancha básica
- `cancha_2` - Segunda cancha
- `servicio` - Servicio (pelotas)
- `servicio_iluminacion` - Servicio de iluminación
- `torneo` - Torneo básico

### Datos complejos:
- `reserva_futura` - Reserva en estado PENDIENTE
- `reserva_con_servicios` - Reserva con servicios adicionales
- `pago_pendiente` - Pago no realizado
- `pago_pagado` - Pago completado
- `equipos_torneo` - 4 equipos inscritos

### Fechas:
- `fecha_futura` - Fecha válida para reservas
- `fecha_pasada` - Fecha para tests de validación

## 📈 Cobertura de Tests

### Tests Unitarios (test_models.py)
- ✅ Validación de datos (DNI, email, precios)
- ✅ Reglas de negocio (fechas pasadas, solapamientos)
- ✅ Cálculos (costos, duraciones)
- ✅ Límites (horarios, cantidad de reservas)

### Tests de Integración (test_views.py)
- ✅ Formularios (GET, POST, validación)
- ✅ CRUD completo (crear, editar, eliminar)
- ✅ Preservación de datos en errores
- ✅ Mensajes de error
- ✅ Transiciones de estado

### Tests End-to-End (test_e2e.py)
- ✅ Flujo completo: crear → pagar reserva
- ✅ Flujo error → corrección → éxito
- ✅ Flujo múltiples reservas
- ✅ Flujo torneos con fixture
- ✅ Reportes mensuales

## 🐛 Debugging

### Ver output de print()
```bash
pytest -s
```

### Modo verbose + stack trace completo
```bash
pytest -vv --tb=long
```

### Detener en el primer error
```bash
pytest -x
```

### Ejecutar con debugger (pdb)
```bash
pytest --pdb
```

## 📝 Convenciones

1. **Nombres de tests**: Descriptivos y en español
   - ✅ `test_no_permite_reservar_en_pasado`
   - ❌ `test_1`, `test_validacion`

2. **Estructura AAA**:
   - **Arrange**: Preparar datos
   - **Act**: Ejecutar acción
   - **Assert**: Verificar resultado

3. **Assertions con mensajes claros**:
   ```python
   assert reserva.estado == 'PENDIENTE'
   assert 'pasado' in error_msg.lower()
   ```

4. **Usar fixtures** en lugar de `setUp()`

## ⚙️ Configuración (pytest.ini)

```ini
[pytest]
DJANGO_SETTINGS_MODULE = canchas_project.settings
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

## 🔄 Integración Continua

Para CI/CD, ejecuta:
```bash
pytest --cov=reservas --cov-report=xml --junitxml=junit.xml
```

## 📚 Recursos

- [Documentación pytest](https://docs.pytest.org/)
- [pytest-django](https://pytest-django.readthedocs.io/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)

## 🎓 Ejemplos de Uso

### Ejecutar tests relacionados con "fecha"
```bash
pytest -k fecha
```

### Ejecutar tests que NO sean e2e
```bash
pytest -m "not e2e"
```

### Ejecutar con warnings visibles
```bash
pytest -W all
```

### Generar reporte en terminal + HTML
```bash
pytest --cov=reservas --cov-report=term --cov-report=html
```
