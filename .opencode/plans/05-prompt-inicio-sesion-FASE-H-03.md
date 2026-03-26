# Prompt: FASE-H-03 - Verificación Optimization Guide

## Proyecto: iah-cli | hotelvisperas.com
## Fecha: 2026-03-26

---

## Pre-requisito

Ninguno. Esta fase puede ejecutarse en paralelo con FASE-H-01.

---

## Contexto

El asset `optimization_guide` falla en validación de contenido:

**Error reportado**:
```
Content validation failed: placeholder: Placeholder detected: \.\.\.; generic_phrase: Generic phrase detected: 'no configurado'
```

**Experiencia previa (FASE-G 2026-03-25)**:
- Se identificó BUG-02: `conditional_generator.py` contenía placeholders "..." y "pendiente"
- Se aplicó fix: Reemplazar "..." con texto descriptivo como "(resumen de 80 caracteres)"
- Se reemplazó "pendiente" con "⚠️ Pendiente de configurar"
- **PROBLEMA**: "pendiente" está en la lista negra del content_validator

---

## Tareas de FASE-H-03

### 1. Localizar Placeholders

Buscar todos los placeholders problemáticos en el código:

```bash
# Buscar ellipsis
grep -rn "\.\.\." modules/asset_generation/conditional_generator.py

# Buscar "pendiente"
grep -rn "pendiente" modules/asset_generation/conditional_generator.py

# Buscar "no configurado"
grep -rn "no configurado" modules/asset_generation/conditional_generator.py

# Buscar otros términos genéricos
grep -rn "por definir\|pendiente\|no disponible\|N/A\|\.\.\." modules/asset_generation/
```

### 2. Verificar Content Validator

Ver qué exactamente rechaza el validator:

```bash
# Leer asset_content_validator.py
grep -n "blacklist\|generic_phrase\|placeholder" modules/asset_generation/asset_content_validator.py -B 2 -A 2
```

### 3. Verificar Fix BUG-02

Verificar si el fix de FASE-G está presente:

```bash
# Buscar si hay texto como "(resumen de 80 caracteres)"
grep -rn "resumen de 80 caracteres" modules/asset_generation/
```

### 4. Identificar Ubicación Exacta

Documentar línea exacta donde se generan los placeholders.

---

## Post-Ejecución

1. **Marcar checklist**: Editar `06-checklist-GAPS-V4COMPLETE.md`:
   - [x] FASE-H-03 completada
   - Causa raíz documentada

2. **Documentar**: Crear documento `CAUSA_RAIZ_OPTIMIZATION_GUIDE.md` con:
   - Lugar exacto donde se generan placeholders
   - Lista completa de términos rechazados
   - Próximo paso

---

## Criterios de Completitud

- [ ] Placeholders localizados (archivo:línea)
- [ ] Lista negra del validator documentada
- [ ] Causa raíz clara
- [ ] Checklist actualizado

---

## Notas

- La diferencia entre FASE-H-01 y FASE-H-03 es que H-01 es sobre WhatsApp, H-03 es sobre Optimization Guide
- Pueden ejecutarse en paralelo si hay capacidad

---

*Prompt creado: 2026-03-26*
*Proyecto: iah-cli | hotelvisperas.com*
*Puede ejecutarse en paralelo con: FASE-H-01*
