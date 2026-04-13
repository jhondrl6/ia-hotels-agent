---
description: FASE-TEMPLATE-DEBT — Sincronizar template embebido vs V6 + typo fix
version: 1.0.0
---

# FASE-TEMPLATE-DEBT: Sincronizar Template Embebido vs V6 + Typo Fix

**ID**: FASE-TEMPLATE-DEBT  
**Objetivo**: Resolver deuda técnica de templates desalineados y fixear typo "debeproveer"  
**Dependencias**: Ninguna (paralela, independiente)  
**Duración estimada**: 1 hora  
**Skill**: `iah-cli-phased-execution`

---

## Contexto

### Problema (D5 + D1 del AUDIT)

```
D5: Template embebido vs V6 desalineados — IMPACTO BAJO (deuda técnica)

v4_diagnostic_generator.py tiene DOS templates:
1. Embebido (líneas ~390-460): 4 filas con nombres diferentes (GEO, Competitive, SEO, AEO) — NO tiene IAO
2. V6 (diagnostico_v6_template.md): 4 filas (SEO Local, Google Maps, AEO, IAO) — SÍ tiene IAO

El V6 se carga primero (línea 263). El embebido es fallback.
Si el V6 se elimina o el path cambia, el output perdería el pilar IAO.

---

D1: Typo "debeproveer" en propuesta — IMPACTO BAJO

Línea 61 de propuesta: "lo que debeproveer" (falta espacio: "debe prover")
El content scrubber no lo detecta porque no es error de idioma sino de espaciado.
```

### Problema Adicional (D6 del AUDIT)

```
D6: package_name dead code — IMPACTO BAJO

Código línea 532: 'package_name': "Kit Hospitalidad 4.0"
Template V6 hardcodea "Kit Hospitalidad Digital" en línea 39 y NO usa ${package_name}
Variable es dead code en contexto V6.
```

---

## Tareas

### Tarea 1: Auditar template embebido vs V6

**Ubicación**: `modules/commercial_documents/v4_diagnostic_generator.py` líneas ~390-460

**Comparar**:
- Template embebido: ¿qué filas tiene? ¿qué pilares?
- Template V6: ¿qué filas tiene? ¿qué pilares?
- ¿Cuál es la diferencia exacta?

**Decisión de Fix**: Elegir una de dos opciones:

**Opción A (Recomendada)**: Eliminar template embebido completamente
- Requerir que V6 siempre exista
- Si V6 no se puede cargar, fallar con error claro (no fallback silencioso)
- Eliminar ~70 líneas de código dead

**Opción B**: Sincronizar embebido con V6
- Agregar IAO al embebido
- Quitar "Competitive" del embebido (no es un pilar)
- Mantener ambos sincronizados

---

### Tarea 2: Fix typo "debeproveer"

**Ubicación**: `modules/commercial_documents/templates/propuesta_v6_template.md` línea 61

**Fix**:
```markdown
lo que debeproveer → lo que debe prover
```

**Verificar** si hay otros typos similares con palabras pegadas.

---

### Tarea 3: Sincronizar package_name

**Dos opciones**:
1. Elegir "Kit Hospitalidad Digital" (V6) y eliminar la variable dead del código
2. O usar "Kit Hospitalidad 4.0" consistentemente en ambos lugares

**Recomendación**: Usar "Kit Hospitalidad Digital" (más descriptivo, orientado al cliente).

---

## Restricciones

- NO modificar cálculos financieros
- NO alterar los 4 pilares (SEO Local, Google Maps, AEO, IAO)
- El template V6 de diagnóstico NO se toca — está correcto
- Mantener backward compat: si se elimina embebido, V6 debe existir siempre

---

## Tests Obligatorios

No hay tests unitarios específicos para templates. La validación es:

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
# Buscar "debeproveer" en el template
grep -r "debeproveer" modules/commercial_documents/templates/

# Verificar que template embebido y V6 son consistentes
# (esto se hace manualmente revisando ambos archivos)
```

---

## Criterios de Completitud (CHECKLIST)

- [ ] **Template embebido eliminado o sincronizado**: Ya no hay riesgo de fallback incorrecto
- [ ] **Typo corregido**: "debeproveer" → "debe prover" en propuesta_v6_template.md
- [ ] **package_name resuelto**: Un solo nombre consistente
- [ ] **No hay regresión**: El diagnóstico sigue generando con V6
- [ ] **`dependencias-fases.md` actualizado**: FASE-TEMPLATE-DEBT ✅ Completada

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

1. **`dependencias-fases.md`**: Marcar FASE-TEMPLATE-DEBT como ✅ Completada
2. **`06-checklist-implementacion.md`**: Marcar Tareas 1-3 como completadas
3. **`09-documentacion-post-proyecto.md`**:
   - Sección E: Archivos de template modificados
   - Sección D: Deuda técnica resuelta
