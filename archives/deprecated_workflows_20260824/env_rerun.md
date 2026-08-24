---
description: Solucionar fallos de entorno y configuración de API Keys.
---

# Skill: Environment Rerun (Auto-Configurador)

> [!NOTE]
> **Trigger**: "Fallo de API key", "No LLM API key configured", "error de conexión".

## Pre-requisitos (Contexto)
- [ ] Acceso al sistema de archivos local (`.env`).
- [ ] API Keys del proveedor.

## Fronteras (Scope)
- **Hará**: Verificación de `.env` contra `.env.example`, configuración interactiva de llaves, test de conexión liviano.
- **NO Hará**: No genera diagnósticos ni accede a la red sin permiso del usuario.

## Pasos de Ejecución

### 1. Diagnóstico de Configuración
// turbo
setup --preflight

*Validación*: Se detectan variables ausentes o llaves inválidas.

### 2. Configuración Interactiva
// turbo
setup

*Validación*: El usuario ingresa las llaves y se guardan de forma segura (Keychain/.env).

### 3. Test de Salud (Health Check)
// turbo
spark --url example.com

*Validación*: La auditoría rápida se ejecuta sin errores de autenticación.

## Criterios de Éxito
- [ ] Sistema configurado correctamente.
- [ ] Llaves validadas con el proveedor.
- [ ] Sin fallos de entorno persistentes.

## Plan de Recuperación (Fallback)
- Si el Keychain falla, revertir a guardado en `.env` plano.
- Si la llave es inválida, pedir al usuario generar una nueva en el dashboard del proveedor.
