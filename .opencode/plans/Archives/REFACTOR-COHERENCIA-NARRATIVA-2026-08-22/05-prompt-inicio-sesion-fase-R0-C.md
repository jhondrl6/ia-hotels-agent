# FASE-R0-C — Fix B3+B5: Título Sección 1 condicional + contador dinámico Sección 6

**ID**: FASE-R0-C
**Objetivo**: Hacer condicional la mención de WhatsApp en el título y la intro de la Sección 1 del diagnóstico (solo cuando hay conflicto real) y reemplazar el contador fijo "3" de la Sección 6 por el contador dinámico existente.
**Dependencias**: FASE-R0-B ✅ (hard: el test estático de template exige B1+B4 ya aplicados).
**Duración estimada**: 45 minutos
**Skill**: phased_project_executor v2.15.0
**Lectura previa obligatoria**: `.opencode/context/Historico/CONTEXT-REFACTOR-COHERENCIA-NARRATIVA-FUGAS-WHATSAPP-2026-08-22.md` — §2 (Bug 3, Bug 5), §4.3 (Opción B), §4.5, §8 (AC10)

---

## Contexto

El título de la Sección 1 ("HOY HAY RESERVAS ESCAPÁNDOSE POR WHATSAPP, GOOGLE MAPS E IA") y la cláusula "o el número de WhatsApp no responde" (L39) asumen genéricamente un problema de WhatsApp sin condicionarse a los datos. El método `_build_whatsapp_conflict_note()` (L2635-2675) ya es correcto (retorna "" sin conflicto), pero el texto hardcoded de L29/L39 no usa esa verificación. Adicionalmente, la Sección 6 dice "Detecta las 3 fugas digitales" con número fijo (B5) cuando el contador dinámico `${brechas_total_count}` ya existe en el render dict.

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-R0-A | ✅ Completada (B2: Quick Win #1) |
| FASE-R0-B | ✅ Completada (B1+B4: Sección 4 dinámica) |

### Base Técnica (verificada contra código vivo 2026-08-22)

- **Template** `modules/commercial_documents/templates/diagnostico_v6_template.md`:
  - L29: `## 1. 🚨 HOY HAY RESERVAS ESCAPÁNDOSE POR WHATSAPP, GOOGLE MAPS E IA`
  - L37: `${whatsapp_conflict_business_note}` — dinámico, CORRECTO (conservar).
  - L39: `Cada día que pasa, viajeros potenciales buscan su hotel en Google Maps, le preguntan a ChatGPT o comparan en Booking.com - y algunos se van sin reservar porque no encuentran lo que buscan o el número de WhatsApp no responde.`
  - L89: `IA Hoteles Agent es el sistema que acaba de analizar su hotel. Detecta las 3 fugas digitales, calcula la fuga financiera aproximada y genera un plan de recuperación personalizado.`
- **Generador** `v4_diagnostic_generator.py`:
  - `_build_whatsapp_conflict_note(audit_result)` L2635-2675: patrón de referencia para detectar conflicto real de WhatsApp (números web vs GBP, con soporte multi-sede FASE-P1-D).
  - Dict de renderizado (zona `'brechas_section'`): `'brechas_total_count'` YA existe — para B5 no se requiere código nuevo en el generador, solo el template.
- **Tests**: `tests/commercial_documents/test_template_conditionals.py` (64 líneas — tests estáticos del template; ampliar aquí).
- **Base de tests**: 3,365 funciones tras R0-A+R0-B. Esta fase agrega 3 tests.
- **Nota**: los números de línea del template pueden haberse desplazado tras R0-B — anclar por contenido.

---

## Modo de Ejecución: DIRECTO (agente principal)

**Justificación** (executor): código+tests puro con venv Windows (regla venv WSL prevalece sobre cualquier consideración de paralelismo). Sin comandos largos.

**Presupuesto de iteraciones** (R2, máx. 60): ~8 investigación + ~12 implementación + ~12 tests + ~10 docs + margen.

---

## Decisiones de Diseño (pre-aprobadas)

| ID | Decisión | Rationale |
|----|----------|-----------|
| **D-NC4** | B3 vía **Opción B del CONTEXT §4.3** (variable dinámica de canales), no Opción A (texto estático alternativo) | La Opción A reemplaza una fosilización por otra. La variable dinámica deriva del mismo signal que `_build_whatsapp_conflict_note()` (única fuente de conflicto) |
| **D-NC5** | B5 reutiliza la variable EXISTENTE `${brechas_total_count}` — cero código nuevo en generador | Lección L16 del CONTEXT: antes de agregar variables, verificar si ya existen. El gap está en el caller (template), no en el generador |

---

## Tareas

### Tarea 1: Título y cláusula de Sección 1 condicionales (B3)

**Archivos afectados**: `diagnostico_v6_template.md` (L29, L39) + `v4_diagnostic_generator.py` (render dict)

**Template — después**:
```markdown
## 1. 🚨 HOY HAY RESERVAS ESCAPÁNDOSE POR ${seccion_1_canales}

Cada día que pasa, viajeros potenciales buscan su hotel en Google Maps, le preguntan a ChatGPT o comparan en Booking.com - y algunos se van sin reservar porque no encuentran lo que buscan${seccion_1_whatsapp_clausula}.
```

**Generador — inyectar en el render dict** (reutilizar el MISMO signal de conflicto que `_build_whatsapp_conflict_note()` — extraerlo a un helper o calcularlo igual; NO crear una segunda fuente de verdad):

```python
# FUGAS-WHATSAPP (B3): canales del título S1 y cláusula WhatsApp condicionales
# al mismo signal de conflicto real que usa _build_whatsapp_conflict_note().
'seccion_1_canales': "WHATSAPP, GOOGLE MAPS E IA" if whatsapp_conflict else "GOOGLE MAPS E IA",
'seccion_1_whatsapp_clausula': " o el número de WhatsApp no responde" if whatsapp_conflict else "",
```

**Reglas**:
- El signal de `whatsapp_conflict` debe derivarse del mismo criterio de `_build_whatsapp_conflict_note()` (conflicto real web vs GBP, con soporte multi-sede) — idealmente extrayendo un método compartido (lección L21: extender la lógica existente, no crear mecanismo paralelo).
- Sin conflicto: el título NO menciona WhatsApp y la frase L39 termina en "…no encuentran lo que buscan."
- `${whatsapp_conflict_business_note}` (L37) se conserva tal cual.

### Tarea 2: Contador dinámico en Sección 6 (B5)

**Archivos afectados**: `diagnostico_v6_template.md` (L89)

**Cambio** (D-NC5 — solo template, la variable ya existe):
```markdown
# Antes:
Detecta las 3 fugas digitales, calcula la fuga financiera aproximada y genera un plan de recuperación personalizado.

# Después:
Detecta las ${brechas_total_count} fugas digitales, calcula la fuga financiera aproximada y genera un plan de recuperación personalizado.
```

### Tarea 3: Tests nuevos

**Archivos afectados**: `tests/commercial_documents/test_template_conditionals.py` (+ ampliar si hace falta en `test_diagnostic_generator.py`)

| Test | Verifica |
|------|----------|
| `test_seccion1_titulo_condicional` | Con conflicto real: título contiene "WHATSAPP, GOOGLE MAPS E IA" y la cláusula "no responde" aparece. Sin conflicto (tipo Zione): título = "GOOGLE MAPS E IA", cláusula ausente |
| `test_seccion6_contador_dinamico` | Output contiene "Detecta las {N} fugas digitales" con N = `${brechas_total_count}` real del audit (AC10); el template NO contiene "las 3 fugas" |
| `test_template_no_hardcoded_fugas` | **Test estático del template** (lee el archivo .md): NO contiene `LAS 3 FUGAS`, NO contiene `Detecta las 3 fugas`, NO contiene `Fuga 1 — Contacto perdido`, y NO contiene `WHATSAPP` en L29-título sin `${` (cualquier mención de canal debe estar parametrizada o dentro de la nota dinámica) |

### Tarea 4: Verificación de no-regresión

```bash
./venv/Scripts/python.exe -m pytest tests/commercial_documents/test_template_conditionals.py tests/commercial_documents/test_diagnostic_generator.py tests/regression/ -v
```

- [ ] 3 tests nuevos pasan
- [ ] `test_diagnostic_generator.py` pasa (incluye tests de R0-B — el contrato de variables sigue íntegro)
- [ ] `tests/regression/` pasa (26 tests)

### Tarea 5: Post-ejecución documental

Ver sección **Post-Ejecución**.

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| 3 tests nuevos (Tarea 3) | `tests/commercial_documents/test_template_conditionals.py` | 3/3 pasan |
| Suite diagnostic_generator | `tests/commercial_documents/test_diagnostic_generator.py` | 0 fallos |
| Regresión | `tests/regression/` | 26/26 |

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

1. **`dependencias-fases.md`**: FASE-R0-C ✅ + notas.
2. **`README.md` del plan**: tabla de progreso actualizada.
3. **`06-checklist-implementacion.md`**: fila FASE-R0-C ✅.
4. **`09-documentacion-post-proyecto.md`**:
   - Sección B: título S1 condicional + contador S6 dinámico.
   - Sección D: +3 tests (3,368).
   - Sección E: `diagnostico_v6_template.md`, `v4_diagnostic_generator.py`, `test_template_conditionals.py`.
5. **`10-analisis-post-implementacion.md`**:
   - Resumen de Ejecución: fila FASE-R0-C.
   - Decisiones Arquitectónicas: D-NC4, D-NC5 (confirmar implementación).
   - Lecciones Aprendidas: mínimo 3.
   - Matriz de Verificación: filas B3 y B5.
6. **Registrar la fase**:

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-R0-C \
    --desc "Fix B3+B5: titulo S1 condicional a conflicto WhatsApp + contador dinamico S6" \
    --archivos-mod "modules/commercial_documents/templates/diagnostico_v6_template.md,modules/commercial_documents/v4_diagnostic_generator.py" \
    --tests "3" \
    --check-manual-docs
```

> **SIN flag `--release`**.

7. **Validación final**:
```bash
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```
> Fallos "Version Sync"/"Document Integration" → `sync_versions.py` + re-validar (NO re-ejecutar tests).

8. **Regenerar DOMAIN_PRIMER**:
```bash
./venv/Scripts/python.exe scripts/doctor.py --regenerate-domain-primer
```

---

## Criterios de Completitud (CHECKLIST)

⚠️ Verificar ANTES de marcar como ✅ COMPLETADA ⚠️

- [ ] 3 tests nuevos pasan (incluido el estático `test_template_no_hardcoded_fugas`)
- [ ] Suites obligatorias pasan (template_conditionals + diagnostic_generator + regression)
- [ ] El template NO contiene "3 fugas" ni "LAS 3 FUGAS" ni fugas hardcoded (verificado por test estático)
- [ ] El título S1 y la cláusula L39 derivan del mismo signal que `_build_whatsapp_conflict_note()`
- [ ] `log_phase_completion.py` ejecutado (SIN `--release`)
- [ ] `dependencias-fases.md`, `README.md`, `06-checklist`, `09`, `10` actualizados
- [ ] `run_all_validations.py --quick` TOTAL PASS

**NO marcar la fase como completada si algún criterio falla.**

---

## Restricciones

- Máximo 60 iteraciones (R2). Si se alcanza: `⏳ INCOMPLETA` + checkpoint + cerrar sesión.
- **NO ejecutar `v4complete`** (reservado a FASE-R0-E).
- NO tocar la Sección 4 del template (ya dinámica tras R0-B) ni `_build_quick_wins()` (R0-A) ni el proposal generator (R0-D).
- NO crear una segunda fuente de verdad para el conflicto de WhatsApp (extender `_build_whatsapp_conflict_note` o extraer helper compartido).
- NO bump de versión ni CHANGELOG (FASE-RELEASE-4.72.1).
- NO ejecutar la suite completa de tests.
- `log_phase_completion.py` SIN `--release`.
