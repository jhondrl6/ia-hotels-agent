---
description: Asistente para el despliegue de kits AEO en sitios WordPress del hotel.
---

# Skill: Deployment Assistant (Instalador WordPress)

> [!NOTE]
> **Trigger**: "ayúdame a instalar", "despliegue en WordPress", "subir cambios".

## Pre-requisitos (Contexto)
- [ ] Directorio `delivery_assets` generado.
- [ ] Credenciales de acceso (WP-API o FTP).

## Fronteras (Scope)
- **Hará**: Preflight de archivos (AEO Kit), Conexión remota, Inyección de JSON-LD y Scripts de seguimiento. Verificación post-despliegue.
- **NO Hará**: No modifica archivos de diseño del tema, solo inyecta fragmentos de código.

## Pasos de Ejecución

### 1. Verificación de Kit (Preflight)
Validar que el kit AEO esté completo para el hotel destino.

*Validación*: Archivos `aeo_config.json` y JSON-LD presentes.

### 2. Ejecución de Despliegue
// turbo
deploy --target {{hotel_name}} --method wp-api

*Validación*: Conexión establecida y archivos inyectados en la ruta `/wp-json/iah/v1/deploy`.

### 3. Prueba de Visibilidad (Post-Deploy)
Verificar mediante un escáner de red si el JSON-LD es visible externamente.

*Validación*: El Rich Result Test puede leer los datos inyectados.

## Criterios de Éxito
- [ ] Instalación completada en menos de 5 minutos.
- [ ] Sin errores de conexión remota.
- [ ] JSON-LD validado externamente.

## Plan de Recuperación (Fallback)
- Si falla el WP-API, intentar el despliegue manual por FTP.
- Si ambos fallan, proveer el kit en un archivo `.zip` con instrucciones paso a paso.
