# Guía de Integración MercadoPago

## Estado de la Implementación

✅ **COMPLETADO** - La integración con MercadoPago está totalmente implementada y funcional.

## Características Implementadas

### 1. Pago de Reservas
- ✅ Creación de preferencias de pago en MercadoPago
- ✅ Redirección automática al checkout de MercadoPago
- ✅ URLs de retorno (éxito, pendiente, fallo)
- ✅ Actualización automática del estado de pago

### 2. Webhooks
- ✅ Endpoint de webhook configurado (`/mercadopago/webhook/`)
- ✅ Procesamiento de notificaciones de pago
- ✅ Actualización automática del estado de reservas
- ✅ Manejo de estados: approved, pending, rejected, refunded

### 3. URLs Configuradas
```
/reservas/<id>/pagar-mercadopago/    - Crear pago en MercadoPago
/reservas/<id>/pago-exitoso/         - Callback de pago exitoso
/reservas/<id>/pago-pendiente/       - Callback de pago pendiente
/reservas/<id>/pago-fallido/         - Callback de pago fallido
/mercadopago/webhook/                - Webhook para notificaciones
```

## Configuración

### 1. Obtener Credenciales de MercadoPago

#### Para Testing (Credenciales de Prueba)
1. Ir a https://www.mercadopago.com.ar/developers/panel
2. Hacer login con tu cuenta de MercadoPago
3. Ir a "Tus integraciones" > "Credenciales"
4. Usar las credenciales de **TEST** (NO producción)

**Credenciales necesarias:**
- **Access Token de TEST**: `TEST-XXXXX-XXXXX-XXXXX-XXXXX`
- **Public Key de TEST**: `TEST-XXXXX-XXXXX-XXXXX-XXXXX`

### 2. Configurar en Django

Editar `canchas_project/settings.py`:

```python
# Configuración de MercadoPago
MERCADOPAGO_ACCESS_TOKEN = 'TEST-1234567890-123456-XXXXXXXX'  # Tu access token de TEST
MERCADOPAGO_PUBLIC_KEY = 'TEST-XXXXXXXX-XXXXXXXX'              # Tu public key de TEST
MERCADOPAGO_WEBHOOK_SECRET = ''  # Opcional

# URL base para callbacks de MercadoPago
MERCADOPAGO_SUCCESS_URL = 'http://localhost:8000/reservas/{reserva_id}/pago-exitoso/'
MERCADOPAGO_PENDING_URL = 'http://localhost:8000/reservas/{reserva_id}/pago-pendiente/'
MERCADOPAGO_FAILURE_URL = 'http://localhost:8000/reservas/{reserva_id}/pago-fallido/'
```

### 3. Verificar Instalación

```bash
# Verificar que mercadopago SDK está instalado
pip list | grep mercadopago

# Si no está instalado:
pip install mercadopago
```

## Flujo de Pago

### 1. Usuario Crea una Reserva
```
Usuario → Formulario Reserva → Guardar Reserva (estado: PENDIENTE)
```

### 2. Usuario Inicia Pago
```
Detalle Reserva → Botón "Pagar con MercadoPago"
```

### 3. Proceso de Pago
```
1. Sistema crea objeto Pago (si no existe)
2. Sistema crea preferencia en MercadoPago
3. Usuario es redirigido a checkout de MercadoPago
4. Usuario completa el pago
5. MercadoPago redirige según resultado:
   - Éxito → /reservas/<id>/pago-exitoso/
   - Pendiente → /reservas/<id>/pago-pendiente/
   - Fallo → /reservas/<id>/pago-fallido/
6. Webhook actualiza el estado final
```

### 4. Actualización por Webhook
```
MercadoPago → POST /mercadopago/webhook/
↓
Sistema verifica payment_id
↓
Actualiza Pago y Reserva
↓
Si approved: Reserva pasa a PAGADA
```

## Testing con Tarjetas de Prueba

### Tarjetas de Test de MercadoPago

**APROBADA:**
- Número: `5031 7557 3453 0604`
- CVV: `123`
- Fecha: cualquier fecha futura
- Nombre: cualquier nombre

**RECHAZADA (fondos insuficientes):**
- Número: `5031 4332 1540 6351`
- CVV: `123`
- Fecha: cualquier fecha futura

**PENDIENTE (revisión manual):**
- Número: `5031 4332 1540 9878`
- CVV: `123`
- Fecha: cualquier fecha futura

**Usuarios de Test:**
```
APRO (aprobado): test_user_12345678@testuser.com
OTHE (otro medio): test_user_87654321@testuser.com
CONT (contracargo): test_user_11111111@testuser.com
CALL (rechazado): test_user_22222222@testuser.com
FUND (fondos insuficientes): test_user_33333333@testuser.com
SECU (seguridad): test_user_44444444@testuser.com
EXPI (tarjeta expirada): test_user_55555555@testuser.com
FORM (error en formulario): test_user_66666666@testuser.com
```

## Modelo de Datos

### Campos en Pago para MercadoPago
```python
class Pago(models.Model):
    # ... otros campos ...
    
    # Campos MercadoPago
    mp_preference_id = models.CharField(max_length=255, blank=True, null=True)
    mp_payment_id = models.CharField(max_length=255, blank=True, null=True)
    mp_status = models.CharField(max_length=50, blank=True, null=True)
    mp_payment_type = models.CharField(max_length=50, blank=True, null=True)
```

## Debugging

### Ver Logs de Webhook
Los webhooks imprimen información en consola:
```python
print(f"Webhook: Pago {resource_id} actualizado - Estado: {payment.get('status')}")
```

### Verificar Estado de Pago
```python
# En Django shell
from reservas.models import Pago

# Ver todos los pagos con MercadoPago
pagos_mp = Pago.objects.filter(mp_preference_id__isnull=False)
for p in pagos_mp:
    print(f"Reserva {p.reserva.id}: {p.mp_status} - {p.estado}")
```

### Probar Webhook Manualmente
```bash
curl -X POST http://localhost:8000/mercadopago/webhook/ \
  -H "Content-Type: application/json" \
  -d '{
    "type": "payment",
    "data": {
      "id": "12345678"
    }
  }'
```

## Estados de Pago MercadoPago

| Estado MP | Descripción | Acción Sistema |
|-----------|-------------|----------------|
| `approved` | Pago aprobado | Marca reserva como PAGADA |
| `pending` | Pendiente de confirmación | Mantiene PENDIENTE |
| `in_process` | En proceso | Mantiene PENDIENTE |
| `rejected` | Rechazado | Mantiene PENDIENTE (permite reintentar) |
| `cancelled` | Cancelado por usuario | Mantiene PENDIENTE |
| `refunded` | Reembolsado | Marca como REEMBOLSADO y reserva CANCELADA |
| `charged_back` | Contracargo | Marca como REEMBOLSADO y reserva CANCELADA |

## Seguridad

### CSRF Exempt en Webhook
El endpoint webhook usa `@csrf_exempt` porque MercadoPago no puede enviar CSRF tokens.

**Recomendaciones para producción:**
1. Validar IPs de MercadoPago
2. Verificar firma del webhook con `MERCADOPAGO_WEBHOOK_SECRET`
3. Usar HTTPS obligatorio
4. Rate limiting en el endpoint

### Validación de Webhook (Opcional)
```python
# En producción, agregar validación de firma
import hmac
import hashlib

def validate_webhook(request):
    signature = request.headers.get('X-Signature')
    request_id = request.headers.get('X-Request-Id')
    
    secret = settings.MERCADOPAGO_WEBHOOK_SECRET
    # Validar firma HMAC
    # ...
```

## Producción

### Checklist para ir a Producción

- [ ] Cambiar a credenciales de PRODUCCIÓN
- [ ] Configurar HTTPS en el servidor
- [ ] Configurar dominio real en URLs de callback
- [ ] Configurar webhook con IP pública accesible
- [ ] Implementar validación de firma de webhook
- [ ] Configurar logs de producción
- [ ] Hacer pruebas con tarjetas reales (pequeños montos)
- [ ] Configurar notificaciones por email al usuario
- [ ] Implementar retry logic para webhooks fallidos

### URLs de Producción
```python
MERCADOPAGO_SUCCESS_URL = 'https://tudominio.com/reservas/{reserva_id}/pago-exitoso/'
MERCADOPAGO_PENDING_URL = 'https://tudominio.com/reservas/{reserva_id}/pago-pendiente/'
MERCADOPAGO_FAILURE_URL = 'https://tudominio.com/reservas/{reserva_id}/pago-fallido/'
```

## Recursos

- **Documentación MercadoPago:** https://www.mercadopago.com.ar/developers/es/docs
- **SDK Python:** https://github.com/mercadopago/sdk-python
- **Panel de Desarrolladores:** https://www.mercadopago.com.ar/developers/panel
- **Tarjetas de Prueba:** https://www.mercadopago.com.ar/developers/es/docs/test-cards

## Troubleshooting

### Error: "MercadoPago no está configurado correctamente"
**Solución:** Verificar que `MERCADOPAGO_ACCESS_TOKEN` no sea `'TU_ACCESS_TOKEN_AQUI'`

### Error: "Error al crear la preferencia de pago"
**Solución:** 
1. Verificar credenciales en settings.py
2. Ver el mensaje de error específico en el mensaje flash
3. Verificar que el monto sea válido (> 0)

### Webhook no se ejecuta
**Solución:**
1. En desarrollo local, usar ngrok o similar para exponer localhost
2. Verificar que la URL esté configurada en el panel de MercadoPago
3. Ver logs de consola para errores

### Pago aprobado pero reserva sigue PENDIENTE
**Solución:**
1. Verificar que el webhook se esté ejecutando
2. Revisar logs de consola
3. Verificar en Django admin el estado de `Pago.mp_status`
4. Ejecutar manualmente: `pago.marcar_como_pagado('MERCADOPAGO', payment_id)`

## Soporte

Para problemas específicos de MercadoPago:
- **Soporte MercadoPago:** https://www.mercadopago.com.ar/ayuda
- **Comunidad:** https://www.mercadopago.com.ar/developers/es/support
