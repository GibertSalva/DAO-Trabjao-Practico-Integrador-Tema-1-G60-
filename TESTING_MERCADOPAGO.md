# Guía de Testing - Integración con MercadoPago

## 📋 Resumen

Esta guía te ayudará a probar la integración con MercadoPago en el sistema de reservas de canchas.

## 🔧 Configuración Inicial

### 1. Credenciales de Prueba

Para testing, debes usar las credenciales de **TEST** (modo sandbox) de MercadoPago:

1. Inicia sesión en [MercadoPago Developers](https://www.mercadopago.com.ar/developers/panel)
2. Ve a **"Tus integraciones"** > **"Credenciales de prueba"**
3. Copia el **Access Token de prueba** (empieza con `TEST-`)
4. Copia la **Public Key de prueba**

### 2. Configurar en Django

Edita `canchas_project/settings.py`:

```python
# Usar credenciales de TEST
MERCADOPAGO_ACCESS_TOKEN = 'TEST-1234567890-xxxxxx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx-1234567890'
MERCADOPAGO_PUBLIC_KEY = 'TEST-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'
```

**⚠️ IMPORTANTE:** Las credenciales de TEST empiezan con `TEST-`. Nunca uses credenciales de producción para testing.

## 🧪 Casos de Prueba

### Caso 1: Pago Exitoso

**Objetivo:** Verificar que un pago se procesa correctamente.

**Pasos:**
1. Crear una reserva en el sistema
2. Ir al detalle de la reserva
3. Hacer clic en "Pagar con MercadoPago"
4. Usar tarjeta de prueba **APROBADA**:
   - **Número:** `5031 7557 3453 0604`
   - **Código de seguridad:** `123`
   - **Fecha de vencimiento:** Cualquier fecha futura (ej: `11/25`)
   - **Nombre:** Cualquier nombre

**Resultado Esperado:**
- ✅ Redirección a página de éxito
- ✅ Reserva marcada como "PAGADA"
- ✅ Pago marcado como "PAGADO"
- ✅ Se muestra información del pago de MercadoPago
- ✅ Mensaje de confirmación visible

### Caso 2: Pago Rechazado

**Objetivo:** Verificar el manejo de pagos rechazados.

**Pasos:**
1. Crear una reserva en el sistema
2. Ir al detalle de la reserva
3. Hacer clic en "Pagar con MercadoPago"
4. Usar tarjeta de prueba **RECHAZADA**:
   - **Número:** `5031 4332 1540 6351`
   - **Código de seguridad:** `123`
   - **Fecha de vencimiento:** Cualquier fecha futura
   - **Nombre:** Cualquier nombre

**Resultado Esperado:**
- ⚠️ Mensaje de error en MercadoPago
- ❌ Reserva permanece como "PENDIENTE"
- ❌ Pago permanece como "PENDIENTE"
- 🔄 Posibilidad de reintentar el pago

### Caso 3: Pago Pendiente

**Objetivo:** Verificar el manejo de pagos pendientes.

**Pasos:**
1. Crear una reserva
2. Hacer clic en "Pagar con MercadoPago"
3. Usar un medio de pago que quede pendiente (ej: Rapipago, Pago Fácil)
4. Simular el pago pendiente

**Resultado Esperado:**
- ⏳ Mensaje de pago pendiente
- 📧 Reserva queda como "PENDIENTE"
- 🔔 Sistema espera confirmación vía webhook

### Caso 4: Usuario Cancela el Pago

**Objetivo:** Verificar el comportamiento cuando el usuario cancela.

**Pasos:**
1. Crear una reserva
2. Hacer clic en "Pagar con MercadoPago"
3. En la página de MercadoPago, hacer clic en "Volver" o cerrar la página
4. Volver al sistema

**Resultado Esperado:**
- ❌ Mensaje de "Pago cancelado" o "Pago fallido"
- 📝 Reserva permanece como "PENDIENTE"
- 🔄 Opción de reintentar el pago disponible

## 🎯 Tarjetas de Prueba Completas

### ✅ Tarjetas que APRUEBAN el pago

| Tarjeta | Número | CVV | Vencimiento |
|---------|--------|-----|-------------|
| Mastercard | 5031 7557 3453 0604 | 123 | 11/25 |
| Visa | 4509 9535 6623 3704 | 123 | 11/25 |

### ❌ Tarjetas que RECHAZAN el pago

| Tarjeta | Número | CVV | Vencimiento | Motivo |
|---------|--------|-----|-------------|--------|
| Mastercard | 5031 4332 1540 6351 | 123 | 11/25 | Fondos insuficientes |
| Visa | 4509 9534 8764 2996 | 123 | 11/25 | Tarjeta rechazada |

### ⏳ Otros casos de prueba

| Tarjeta | Número | Resultado |
|---------|--------|-----------|
| Mastercard | 5031 7560 4313 0604 | Pendiente (requiere revisión) |

## 🔍 Verificación del Webhook

### Testing Local del Webhook

**Problema:** MercadoPago no puede enviar webhooks a `localhost`.

**Solución:** Usar **ngrok** para exponer tu servidor local:

1. **Instalar ngrok:**
   ```bash
   # Windows (con Chocolatey)
   choco install ngrok
   
   # O descargar desde: https://ngrok.com/download
   ```

2. **Ejecutar ngrok:**
   ```bash
   ngrok http 8000
   ```

3. **Copiar la URL HTTPS generada:**
   ```
   https://xxxx-xxx-xxx-xxx-xxx.ngrok.io
   ```

4. **Configurar en MercadoPago:**
   - Ve a tu aplicación en el panel de MercadoPago
   - Configura la URL del webhook:
     ```
     https://xxxx-xxx-xxx-xxx-xxx.ngrok.io/mercadopago/webhook/
     ```

5. **Hacer una prueba de pago**

6. **Verificar los logs:**
   - Ver la consola de Django para mensajes de webhook
   - Verificar que el estado del pago se actualiza automáticamente

### Testing Manual del Webhook

Puedes simular un webhook manualmente con `curl`:

```bash
curl -X POST http://localhost:8000/mercadopago/webhook/ \
  -H "Content-Type: application/json" \
  -d '{
    "type": "payment",
    "data": {
      "id": "1234567890"
    }
  }'
```

**Resultado Esperado:** `{"status": "ok"}`

## 📊 Checklist de Verificación

Antes de considerar completa la integración, verifica:

- [ ] Las credenciales de TEST están configuradas en `settings.py`
- [ ] El botón "Pagar con MercadoPago" aparece en el detalle de la reserva
- [ ] Al hacer clic, se redirige correctamente a MercadoPago
- [ ] El pago con tarjeta aprobada funciona y actualiza la reserva
- [ ] El pago con tarjeta rechazada muestra error y mantiene la reserva pendiente
- [ ] Las URLs de retorno (éxito/pendiente/fallo) funcionan correctamente
- [ ] Se guarda el `mp_preference_id` en el modelo Pago
- [ ] Se guarda el `mp_payment_id` después del pago
- [ ] El webhook actualiza automáticamente el estado del pago
- [ ] Los mensajes de confirmación/error se muestran al usuario
- [ ] Se puede reintentar un pago fallido

## 🚀 Preparación para Producción

Cuando estés listo para producción:

1. **Obtener credenciales de producción:**
   - En el panel de MercadoPago, ve a "Credenciales de producción"
   - Copia el Access Token y Public Key de PRODUCCIÓN
   - NO comiences con `TEST-`

2. **Actualizar `settings.py` con variables de entorno:**
   ```python
   import os
   
   MERCADOPAGO_ACCESS_TOKEN = os.environ.get('MERCADOPAGO_ACCESS_TOKEN', '')
   MERCADOPAGO_PUBLIC_KEY = os.environ.get('MERCADOPAGO_PUBLIC_KEY', '')
   ```

3. **Configurar webhook en producción:**
   - URL del webhook debe ser pública y con HTTPS
   - Ejemplo: `https://tudominio.com/mercadopago/webhook/`

4. **Hacer pruebas exhaustivas:**
   - Realizar al menos 3 pagos de prueba con tarjetas reales
   - Verificar que los webhooks funcionan correctamente
   - Monitorear logs durante los primeros días

## 📝 Notas Importantes

- **Seguridad:** Nunca subas credenciales de producción a un repositorio público
- **Testing:** Usa SIEMPRE las credenciales de TEST para desarrollo
- **Webhooks:** En desarrollo local, usa ngrok o similar para recibir webhooks
- **Logs:** Monitorea los logs de Django para detectar errores en webhooks
- **Estado:** El webhook puede tardar unos segundos en llegar, es normal

## 🆘 Solución de Problemas

### Problema: "MercadoPago no está configurado correctamente"
**Solución:** Verifica que las credenciales en `settings.py` sean correctas y NO sean los valores por defecto (`TU_ACCESS_TOKEN_AQUI`).

### Problema: El webhook no actualiza el pago
**Soluciones:**
1. Verifica que la URL del webhook sea accesible públicamente
2. Usa ngrok para desarrollo local
3. Revisa los logs de Django para ver si el webhook está llegando
4. Verifica que el `external_reference` coincida con el ID de la reserva

### Problema: El pago se aprueba pero la reserva no se actualiza
**Solución:** 
1. Verifica la vista `reserva_pago_exitoso` 
2. Confirma que el método `marcar_como_pagado()` se ejecuta correctamente
3. Revisa que el webhook está configurado y funcionando

## 📞 Recursos Adicionales

- **Documentación de MercadoPago:** https://www.mercadopago.com.ar/developers/es/docs
- **SDK de Python:** https://github.com/mercadopago/sdk-python
- **Tarjetas de prueba:** https://www.mercadopago.com.ar/developers/es/docs/checkout-api/testing
- **Webhooks:** https://www.mercadopago.com.ar/developers/es/docs/your-integrations/notifications/webhooks
