# POS MercadoPago QR

## Descripción

Módulo de Odoo 18 que permite integrar el punto de venta (POS) con el sistema de pagos por código QR de MercadoPago. Desarrollado por Axcelere, este módulo facilita que los clientes puedan pagar sus órdenes utilizando códigos QR generados dinámicamente a través de la API de MercadoPago In-Store.

## Características Principales

### 🔧 Funcionalidades de Pago
- **Generación de QR dinámico**: Creación automática de códigos QR para cada transacción
- **Integración API MercadoPago**: Uso de la API v1 de MercadoPago In-Store para órdenes QR
- **Soporte para reembolsos**: Capacidad de procesar devoluciones completas o parciales
- **Cancelación de órdenes**: Posibilidad de cancelar órdenes de pago pendientes
- **Verificación de estado**: Consulta automática del estado de los pagos

### 📱 Interfaz de Usuario
- **Integración POS**: Botón "Send" manual para procesar pagos
- **Manejo de errores**: Sistema de alertas y notificaciones de error
- **Soporte multiidioma**: Preparado para español e inglés

### 🔍 Monitoreo y Logging
- **Sistema de logs**: Registro detallado de todas las transacciones con MercadoPago
- **Seguimiento de estado**: Monitoreo en tiempo real del estado de los pagos
- **Webhook handling**: Gestión de notificaciones de MercadoPago

## Estructura del Proyecto

```
pos_mercadopagoqr/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── pos_payment_method.py    # Configuración de métodos de pago
│   ├── pos_order.py            # Lógica de órdenes y reembolsos
│   └── mp_credential.py        # Configuración de credenciales MP
├── static/src/js/
│   ├── payment_mpqr.js         # Interfaz de pago en el frontend
│   ├── models.js               # Modelos del POS
│   └── PaymentScreen.js        # Pantalla de pagos
├── static/src/xml/
│   └── PaymentScreenPaymentLines.xml
├── views/
│   ├── pos_payment_method_views.xml
│   └── mp_store_box_views.xml
└── i18n/
    └── es.po                   # Traducciones en español
```

## Instalación

### Prerrequisitos
- Odoo 18.0
- Módulo `point_of_sale` 
- Módulo `pos_mercadopago` (dependencia)
- Cuenta y credenciales de MercadoPago

### Pasos de Instalación

1. **Descargar el módulo**: Coloca el módulo en la carpeta de addons de Odoo
2. **Actualizar lista de módulos**: Ir a Apps > Update Apps List
3. **Instalar módulo**: Buscar "Pos MP QR" e instalar
4. **Configurar credenciales**: Configurar las credenciales de MercadoPago en el sistema

## Configuración

### 1. Configuración de MercadoPago
- Acceder a **Configuración > MP Credentials**
- Crear nueva configuración con tipo "MP QR"
- Completar los campos requeridos:
  - `user_id`: ID del usuario de MercadoPago
  - `mp_access_token`: Token de acceso de MercadoPago
  - `mp_url`: URL base de la API de MercadoPago
  - `platform_id`: ID de la plataforma
  - `integrator_id`: ID del integrador

### 2. Configuración del Método de Pago
- Ir a **Punto de Venta > Configuración > Métodos de Pago**
- Crear o editar un método de pago
- Seleccionar **"MP QR"** como terminal de pago
- Asociar la configuración de MercadoPago creada anteriormente

### 3. Configuración del Punto de Venta
- Asegurar que el punto de venta tenga configurado:
  - `sale_point_id` con `external_store_id` y `external_id`
  - El método de pago MP QR habilitado

## Uso

### Realizar un Pago
1. En el POS, agregar productos al carrito
2. Ir a la pantalla de pagos
3. Seleccionar el método de pago "MP QR"
4. Presionar el botón "Send"
5. Se genera automáticamente el código QR
6. El cliente escanea el QR con su app de MercadoPago
7. El pago se procesa automáticamente

### Realizar un Reembolso
1. Desde la pantalla de órdenes, seleccionar la orden a reembolsar
2. Crear una orden de reembolso
3. Seleccionar el método de pago MP QR
4. El sistema automáticamente procesa el reembolso a través de la API

### Cancelar una Orden
- Las órdenes pendientes pueden cancelarse automáticamente
- El sistema maneja timeouts y cancelaciones por inactividad

## API y Métodos Principales

### Backend (Python)

#### `pos.payment.method`
- `mpqr_make_payment()`: Genera una orden de pago QR
- `_get_payment_terminal_selection()`: Añade MP QR a las opciones

#### `pos.order`
- `mpqr_get_payment_status()`: Consulta el estado de un pago
- `mpqr_make_refunds()`: Procesa reembolsos
- `mpqr_make_cancel()`: Cancela órdenes pendientes
- `mpqr_updating_order()`: Actualiza órdenes con información de pago

### Frontend (JavaScript)

#### `PaymentMpqr`
- `send_payment_request()`: Inicia el proceso de pago
- `_mpqrMakePayment()`: Ejecuta el pago
- `_mpqrFetchPaymentIntent()`: Obtiene la intención de pago
- `_showError()`: Muestra errores al usuario

## Estructura de Datos

### Payload de Pago (API Request)
```json
{
    "type": "qr",
    "total_amount": "100.00",
    "description": "Compra en punto de venta",
    "expiration_time": "PT5M",
    "external_reference": "order_uuid",
    "items": [...],
    "config": {
        "qr": {
            "external_pos_id": "pos_id",
            "mode": "static"
        }
    }
}
```

### Respuesta de la API
```json
{
    "id": "payment_id",
    "status": "created",
    "total_amount": "100.00"
}
```

## Logging y Monitoreo

El módulo incluye un sistema completo de logging que registra:
- Todas las llamadas a la API de MercadoPago
- Headers y payloads de las requests
- Respuestas y códigos de estado
- Errores y excepciones

Los logs se almacenan en el modelo `mp.log` para auditoría y debugging.

## Manejo de Errores

### Errores Comunes
- **Configuración incompleta**: Verificar credenciales y configuración del punto de venta
- **Token expirado**: Renovar el access token de MercadoPago
- **Conexión fallida**: Verificar conectividad y URLs de la API
- **Pago rechazado**: El cliente debe intentar con otro método de pago

### Sistema de Reintentos
- Los pagos fallidos permiten reintento manual
- Las órdenes pueden cancelarse y regenerarse
- Sistema de estados claro (`waiting`, `done`, `retry`)

## Seguridad

- **Tokens seguros**: Los access tokens se almacenan de forma segura
- **Claves de idempotencia**: Prevención de pagos duplicados
- **Validación de datos**: Verificación de integridad en todas las transacciones
- **Logging auditado**: Registro completo para auditorías de seguridad

## Dependencias

### Módulos de Odoo
- `point_of_sale`: Funcionalidad base del POS
- `pos_mercadopago`: Módulo base de MercadoPago

### Librerías Python
- `requests`: Para llamadas HTTP a la API
- `json`: Manejo de datos JSON
- `uuid`: Generación de claves únicas
- `logging`: Sistema de logs

## Versionado

- **Versión actual**: 18.0.0.0
- **Compatibilidad**: Odoo 18.0
- **Licencia**: GPL-3.0

## Soporte

Para soporte técnico y consultas:
- **Desarrollador**: Axcelere
- **Sitio web**: https://www.axcelere.com
- **Documentación**: Ver código fuente para detalles de implementación

## Notas Importantes

⚠️ **Advertencias**:
- Asegurar que las credenciales de MercadoPago estén correctamente configuradas
- Verificar que el punto de venta tenga los IDs externos requeridos
- Probar en ambiente de desarrollo antes de producción
- Mantener los tokens de acceso actualizados

💡 **Tips**:
- Utilizar el sistema de logs para troubleshooting
- Verificar la conectividad con la API de MercadoPago regularmente
- Entrenar al personal en el uso del sistema de pagos QR