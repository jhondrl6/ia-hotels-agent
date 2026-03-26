# Prompt: FASE-H-02 - Investigar y Arreglar Causa Raíz WhatsApp

## Proyecto: iah-cli | hotelvisperas.com
## Fecha: 2026-03-26

---

## Pre-requisito

**FASE-H-01 DEBE estar completada.**
El documento `CAUSA_RAIZ_WHATSAPP.md` contiene el diagnóstico completo con las hipótesis a verificar.

---

## Contexto

**H-01 Descubrió que la cadena de flujo SÍ funciona:**

| Paso | Módulo | Estado |
|------|--------|--------|
| 1 | CrossValidator detecta CONFLICT | ✅ Funciona |
| 2 | V4ComprehensiveAuditor almacena | ✅ Funciona |
| 3 | main.py crea ValidatedField con CONFLICT | ✅ Funciona |
| 4 | PainSolutionMapper.detect_pains() crea Pain("whatsapp_conflict") | ✅ Funciona |
| 5 | Special case fuerza can_generate=True | ✅ Existe |

**El problema NO está en la cadena de detección. Está en:**

> *Cómo el orchestrator procesa el resultado o en la verificación post-generación.*

**3 Hipótesis por verificar (de CAUSA_RAIZ_WHATSAPP.md):**

| # | Hipótesis |
|---|-----------|
| H1 | Orchestrator filtra assets por `is_asset_implemented()` antes de verificar `can_generate` |
| H2 | Asset se genera pero falla en validación de contenido |
| H3 | Special case no se ejecuta si `pain_id` no coincide exactamente con "whatsapp_conflict" |

---

## Tareas de FASE-H-02

### 1. Verificar las 3 Hipótesis

**H1: Investigar V4AssetOrchestrator**
- Buscar cómo usa `can_generate` del special case
- Verificar si hay filtro adicional que impida la generación
- Archivo: `modules/asset_generation/v4_asset_orchestrator.py` o similar

**H2: Verificar Validación de Contenido**
- ¿El asset whatsapp_button generado pasa la validación?
- ¿Hay logs de error durante la generación?

**H3: Verificar Nombre del Pain**
- El special case usa `pain_id == "whatsapp_conflict"` (línea 491-492)
- Confirmar que `PainSolutionMapper.detect_pains()` crea exactamente ese ID

### 2. Aplicar Fix (solo si alguna hipótesis se confirma)

Según la hipótesis confirmada, aplicar el fix en el archivo exacto.

### 3. Verificación Unitaria

```bash
python -m pytest tests/commercial_documents/test_pain_solution_mapper.py::test_detect_pain_whatsapp_conflict -v
```

### 4. Verificación de Regresión

```bash
python -m pytest tests/commercial_documents/test_pain_solution_mapper.py tests/data_validation/test_cross_validator.py -v
```

### 5. Verificación de Integración (si existe)

Ejecutar test end-to-end que valide la generación del whatsapp_button con conflicto.

---

## Documentos de Referencia

- **CAUSA_RAIZ_WHATSAPP.md** - Diagnóstico completo con flujo verificado paso a paso
- **Comandos de verificación** - En CAUSA_RAIZ_WHATSAPP.md líneas 136-181

---

## Post-Ejecución

1. **Marcar checklist**: Editar `06-checklist-GAPS-V4COMPLETE.md`:
   - [x] FASE-H-02 completada
   - Hipótesis verificada (indicar cuál)
   - Fix aplicado (si aplica)

2. **Documentar**: Crear documento `H-02_RESULTADO.md` con:
   - Qué hipótesis se confirmó
   - Qué se cambió
   - Por qué se cambió
   - Cómo verificar

3. **Siguiente paso**: FASE-H-04 puede ejecutarse después de este fix

---

## Criterios de Completitud

- [ ] Las 3 hipótesis verificadas (con evidencia)
- [ ] Fix aplicado (si alguna hipótesis se confirmó)
- [ ] Test unitario pasando
- [ ] Suite de regresión pasando (28/28)
- [ ] Documentación del resultado creada
- [ ] Checklist actualizado

---

## Notas

- La cadena de flujo WhatsApp SÍ funciona - no tocar ese código
- Enfocarse en el orchestrator y la validación post-generación
- Si ninguna hipótesis se confirma, documentar y escalar a H-03 o crear nueva hipótesis

---

*Prompt modificado: 2026-03-26*
*Proyecto: iah-cli | hotelvisperas.com*
*Depende de: FASE-H-01 (CAUSA_RAIZ_WHATSAPP.md)*
