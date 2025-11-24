# Configuración de MercadoPago

Esta guía te ayudará a configurar la integración con MercadoPago en el sistema de reservas.

## Pasos de Configuración

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Obtener credenciales de MercadoPago

1. Crea una cuenta en [MercadoPago](https://www.mercadopago.com.ar/)
2. Ve a [Tus integraciones](https://www.mercadopago.com.ar/developers/panel/app)
3. Crea una nueva aplicación o selecciona una existente
4. Obtén tu **Access Token** (Token de acceso)
5. Obtén tu **Public Key** (Clave pública)

### 3. Configurar credenciales en Django

Edita el archivo `canchas_project/settings.py` y reemplaza los valores:

```python
MERCADOPAGO_ACCESS_TOKEN = 'TU_ACCESS_TOKEN_AQUI'  # Reemplazar con tu Access Token
MERCADOPAGO_PUBLIC_KEY = 'TU_PUBLIC_KEY_AQUI'  # Reemplazar con tu Public Key
```

**Importante:** En producción, usa variables de entorno para almacenar estas credenciales:

```python
import os

MERCADOPAGO_ACCESS_TOKEN = os.environ.get('MERCADOPAGO_ACCESS_TOKEN', '')
MERCADOPAGO_PUBLIC_KEY = os.environ.get('MERCADOPAGO_PUBLIC_KEY', '')
```

### 4. Configurar URLs de retorno (opcional)

Si tu aplicación está en producción, actualiza las URLs en `settings.py`:

```python
MERCADOPAGO_SUCCESS_URL = 'https://tudominio.com/reservas/{reserva_id}/pago-exitoso/'
MERCADOPAGO_PENDING_URL = 'https://tudominio.com/reservas/{reserva_id}/pago-pendiente/'
MERCADOPAGO_FAILURE_URL = 'https://tudominio.com/reservas/{reserva_id}/pago-fallido/'
```

### 5. Configurar Webhook (Recomendado)

1. En el panel de MercadoPago, ve a tu aplicación
2. Configura la URL del webhook: `https://tudominio.com/mercadopago/webhook/`
3. Selecciona los eventos que quieres recibir (al menos "Pagos")

**Nota:** Para desarrollo local, puedes usar herramientas como [ngrok](https://ngrok.com/) para exponer tu servidor local.

### 6. Aplicar migraciones

```bash
python manage.py migrate
```

### 7. Probar la integración

1. Crea una reserva en el sistema
2. Ve al detalle de la reserva
3. Haz clic en "Pagar con MercadoPago"
4. Serás redirigido a MercadoPago para completar el pago

## Modo de Prueba (Sandbox)

MercadoPago ofrece un modo de prueba para desarrollo:

1. Usa las credenciales de **test** (no las de producción)
2. Puedes usar tarjetas de prueba:
   - **Aprobada:** 5031 7557 3453 0604
   - **Rechazada:** 5031 4332 1540 6351
   - CVV: 123
   - Fecha: Cualquier fecha futura

## Flujo de Pago

1. El usuario hace clic en "Pagar con MercadoPago" en el detalle de la reserva
2. Se crea una preferencia de pago en MercadoPago
3. El usuario es redirigido a MercadoPago para completar el pago
4. Después del pago, MercadoPago redirige al usuario de vuelta:
   - **Éxito:** `/reservas/{id}/pago-exitoso/`
   - **Pendiente:** `/reservas/{id}/pago-pendiente/`
   - **Fallido:** `/reservas/{id}/pago-fallido/`
5. El webhook de MercadoPago notifica al sistema sobre el estado del pago
6. El sistema actualiza automáticamente el estado de la reserva y el pago

## Campos Agregados al Modelo Pago

- `mp_preference_id`: ID de la preferencia de pago en MercadoPago
- `mp_payment_id`: ID del pago en MercadoPago
- `mp_status`: Estado del pago en MercadoPago
- `mp_payment_type`: Tipo de pago utilizado

## Solución de Problemas

### Error: "MercadoPago no está configurado correctamente"
- Verifica que las credenciales estén correctamente configuradas en `settings.py`
- Asegúrate de que el Access Token sea válido

### El webhook no funciona
- Verifica que la URL del webhook sea accesible públicamente
- En desarrollo, usa ngrok o similar
- Verifica que el endpoint acepte POST requests

### El pago no se actualiza automáticamente
- Verifica que el webhook esté configurado correctamente
- Revisa los logs del servidor para ver si hay errores
- Puedes verificar manualmente el estado del pago en el panel de MercadoPago

## Recursos Adicionales

- [Documentación de MercadoPago](https://www.mercadopago.com.ar/developers/es/docs)
- [SDK de Python](https://github.com/mercadopago/sdk-python)
- [API de Preferencias](https://www.mercadopago.com.ar/developers/es/reference/preferences/_checkout_preferences/post)

