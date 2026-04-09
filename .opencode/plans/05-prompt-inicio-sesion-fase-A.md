# FASE-A: Templates Dinámicos — Eliminar Hardcode "LAS 4 BRECHAS"

**ID**: FASE-A
**Objetivo**: Reemplazar las 4 ranuras fijas en ambos templates de diagnóstico por un placeholder dinámico `${brechas_section}` que acepte N brechas.
**Dependencias**: Ninguna
**Duración estimada**: 30-45 min
**Skill**: phased_project_executor

---

## Contexto

El sistema `_identify_brechas()` detecta hasta 10 brechas reales basadas en evidencia del audit. Sin embargo, los templates V4 y V6 tienen exactamente 4 ranuras fijas (`${brecha_1_nombre}` ... `${brecha_4_nombre}`), lo que causa truncamiento de información valiosa para el cliente.

La tabla resumen "BRECHAS → OPORTUNIDADES" también tiene 4 filas fijas y debe ser dinámica.

Ver contexto completo en: `.opencode/plans/context/01-causa-raiz-limite-4-brechas.md`

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| (Ninguna) | — |

### Base Técnica Disponible
- `modules/commercial_documents/templates/diagnostico_v6_template.md` — Template activo principal
- `modules/commercial_documents/templates/diagnostico_v4_template.md` — Template fallback
- `v4_diagnostic_generator.py` — Generador que llena el template (se modifica en FASE-B)

---

## Tareas

### Tarea 1: Modificar diagnostico_v6_template.md

**Objetivo**: Reemplazar las 4 ranuras fijas por un placeholder dinámico.

**Archivo afectado**: `modules/commercial_documents/templates/diagnostico_v6_template.md`

**Cambios específicos**:

1. Líneas 66-87 (sección "LAS 4 BRECHAS CRÍTICAS IDENTIFICADAS"):
   - Cambiar título a: `## 🚨 BRECHAS CRÍTICAS IDENTIFICADAS` (sin "LAS 4")
   - Reemplazar las 4 secciones `[BRECHA 1]`...`[BRECHA 4]` por:
     ```
     ${brechas_section}
     ```

2. Líneas 110-117 (tabla resumen "BRECHAS → OPORTUNIDADES"):
   - Reemplazar las 4 filas fijas por:
     ```
     ${brechas_resumen_section}
     ```

**Criterios de aceptación**:
- [ ] No hay ninguna referencia a "4 BRECHAS" ni "BRECHA 1/2/3/4" en el template V6
- [ ] Los placeholders `${brechas_section}` y `${brechas_resumen_section}` existen
- [ ] El resto del template permanece intacto (scorecards, urgencia, quick wins, etc.)

### Tarea 2: Modificar diagnostico_v4_template.md

**Objetivo**: Mismo cambio para el template V4 (fallback).

**Archivo afectado**: `modules/commercial_documents/templates/diagnostico_v4_template.md`

**Cambios específicos**:

1. Líneas 47-61 (sección "LAS 4 RAZONES EXACTAS"):
   - Cambiar título a: `## 🚨 BRECHAS CRÍTICAS IDENTIFICADAS`
   - Reemplazar las 4 secciones por `${brechas_section}`

**Criterios de aceptación**:
- [ ] No hay "4 RAZONES" ni "RAZÓN 1/2/3/4" en el template V4
- [ ] Placeholder `${brechas_section}` existe

### Tarea 3: Verificar que el default template inline también se actualiza

**Objetivo**: El método `_get_default_template()` en `v4_diagnostic_generator.py` (línea 244-405) tiene un template inline hardcodeado que también dice "LAS 4 RAZONES" (línea 367).

**Archivo afectado**: `modules/commercial_documents/v4_diagnostic_generator.py` (solo el método `_get_default_template`)

**Cambios específicos**:
- Línea 367: Cambiar "LAS 4 RAZONES EXACTAS" a "BRECHAS CRÍTICAS IDENTIFICADAS"
- Líneas 369-383: Reemplazar las 4 ranuras `${brecha_N_nombre/costo/detalle}` por `${brechas_section}`

**Criterios de aceptación**:
- [ ] `_get_default_template()` usa `${brechas_section}` en vez de 4 ranuras fijas

---

## Tests Obligatorios

Los templates son markdown estático. La validación es:

```bash
# Verificar que no quedan "4 BRECHAS" o "4 RAZONES" en los templates
grep -ri "4 BRECHAS\|4 RAZONES\|BRECHA 1\|BRECHA 2\|BRECHA 3\|BRECHA 4\|RAZÓN 1\|RAZÓN 2\|RAZÓN 3\|RAZÓN 4" modules/commercial_documents/templates/
# Debe retornar VACÍO

# Verificar que los placeholders existen
grep -r "brechas_section" modules/commercial_documents/templates/
# Debe mostrar ambos templates

# Tests existentes de brechas aún pasan (no se modifica generator aún)
cd /mnt/c/Users/Jhond/Github/iah-cli && .venv/Scripts/python.exe -m pytest tests/commercial_documents/test_diagnostic_brechas.py -v
```

---

## Post-Ejecución (OBLIGATORIO)

1. **`dependencias-fases.md`**: Marcar FASE-A como ✅ Completada
2. **`06-checklist-implementacion.md`**: Marcar items de FASE-A
3. **`09-documentacion-post-proyecto.md`**: Sección A con templates modificados

---

## Criterios de Completitud (CHECKLIST)

- [ ] Template V6: 4 ranuras eliminadas, placeholder dinámico agregado
- [ ] Template V4: 4 ranuras eliminadas, placeholder dinámico agregado
- [ ] Default template inline: 4 ranuras eliminadas
- [ ] grep confirma 0 ocurrencias de "4 BRECHAS/RAZONES" en templates
- [ ] Tests existentes de brechas pasan sin cambios
- [ ] `dependencias-fases.md` actualizado
