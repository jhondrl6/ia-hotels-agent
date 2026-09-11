# FASE-T2-C: Limpieza de precondiciones heredadas (S-E2, S9)

**ID**: TRIBUNAL-OFFLINE-2026-09-09 / FASE-T2-C
**Objetivo**: Cerrar los dos residuos heredados que VERIFY del plan `ESTABILIZACION-PRE-TRIBUNAL-2026-09-03` asignó **explícitamente al tribunal**: **S-E2** (NameError latente de `site_presence_report` + bloques `presence_lookup` muertos) y **S9** (`asset_semantics_validator.INVALID_MAPPINGS`, registro #14). No es alcance nuevo: es precondición del tramo offline que el plan no puede dejar caer sin repetir el anti-patrón **DA-V5** (seis filas re-asignadas C→F→G→H y nunca ejecutadas).
**Dependencias**: FASE-T1 ✅ (ambas tocan `main.py`, que T1 también edita → secuencial, nunca paralela; D-T1.3 resuelta — contrato de acta estable)
**Complejidad técnica**: **MEDIA** — dos limpiezas acotadas en archivos ya identificados + tests de contrato
**Modo de ejecución**: **DIRECTO** (agente principal). NO delegable: los tests importan módulos del proyecto y el venv es Windows accedido desde WSL (executor v2.20.0, branch «imports del proyecto + venv Windows → DIRECTA»).
**Skill**: `phased_project_executor.md` v2.20.0

---

## Contexto

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-T1 | ✅ Completada (contrato de acta + integración `main.py`) |
| FASE-T2-C | ← ESTA FASE |

### Base Técnica Disponible

- **S-E2** (fuente: `ESTABILIZACION-PRE-TRIBUNAL-2026-09-03/10-analisis` §5, fila S-E2):
  - **(a)** `site_presence_report` se asigna **solo dentro** de `if generate_proposal:` en `main.py` (símbolo `if generate_proposal`, asignación `site_presence_report = site_presence_snapshot`) y se consume más abajo bajo un `except Exception` amplio ⟹ en una corrida con `generate_proposal=False` el `NameError` muere en el `[WARN]` de cada corrida, invisible.
  - **(b)** 3 bloques `presence_lookup` muertos en `v4_proposal_generator.py` (guard `hasattr` insatisfacible contra el dict canónico) + instanciación muerta en `v4_asset_orchestrator.py`.
- **S9** (fuente: mismo `10-analisis` §5; `modules/quality/asset_semantics_validator.py`):
  - Las **claves de `INVALID_MAPPINGS` ya están corregidas** desde `ecf59f8` (2026-05-27): usan `pain_id` reales (`no_faq_schema`, `no_hotel_schema`, `missing_llmstxt`, `no_whatsapp_visible`), no `asset_type`.
  - **Lo que falta es la certificación**: ningún test fija la forma del registro ni que cada `pain_id` exista en `PAIN_SOLUTION_MAP`. El fósil V3 (`ASSET_TO_PAIN_ID["monthly_report"] = "no_faq_schema"`) sigue **documentado** en `modules/common/service_identity.py` — verificar si sigue vivo en código y, si lo está, curarlo.

### Lecciones aplicables

| Lección | Aplicación |
|---------|-----------|
| DA-V5 (ESTABILIZACION) | No re-diferir por inercia: S-E2/S9 se ejecutan, no se re-asignan |
| L-A6 (`main.py` creció) | Re-verificar las citas de región con `grep`/`Read` antes de editar; citar **símbolos**, no líneas |
| R2.2 | Sin números de línea en ACs ni en el código |
| R2.4 | AC legible en artefacto: test de contrato que lee el registro real |
| Tribunal NO reimplementa gates | Esta fase **no** toca `publication_gates.py` ni `commercial_gate.py` |

---

## Tareas

### Tarea 1: S-E2 — eliminar el NameError latente y el código muerto

**Objetivo**: Que una corrida con `generate_proposal=False` no produzca `NameError` silencioso, y eliminar los bloques muertos.

**Archivos a leer/editar**:
- `main.py` — símbolo `if generate_proposal`, asignación `site_presence_report = site_presence_snapshot`, consumidor `site_presence_report=site_presence_report`
- `modules/commercial_documents/v4_proposal_generator.py` — bloques `presence_lookup` muertos
- `modules/asset_generation/v4_asset_orchestrator.py` — instanciación muerta

**Enfoque (medir antes de tocar)**:
1. `grep`/`Read` para localizar el bloque condicional y su consumidor; confirmar el `except` amplio que lo enmascara.
2. Elegir la cura mínima: **hoist** de la asignación fuera del bloque condicional (la fuente `site_presence_snapshot` ya existe antes), **o** inicializar en `None` + guard en el consumidor. Preferir la que no altere el régimen de `generate_proposal=True`.
3. Verificar con un test/sonda que el camino `generate_proposal=False` ya no lanza `NameError`.
4. Retirar los bloques muertos solo tras confirmar con `grep` que no tienen consumidor vivo (lección «dead-code-before-delete»).

**Criterios de aceptación**:
- [x] El camino `generate_proposal=False` no produce `NameError` (sonda/test) — certificado en auditoría 2026-09-11 (hoist verificado, test verde)
- [ ] El régimen `generate_proposal=True` no cambia de comportamiento (test de no-regresión) — ⚠️ NO CUMPLIDO: los bloques `presence_lookup` fueron reactivados, no retirados; ver adenda D-T2C-A1 al final de este documento
- [ ] Los bloques `presence_lookup` muertos y la instanciación muerta retirados (o justificada su permanencia) — ⚠️ PARCIAL: la instanciación muerta sí se retiró; los 3 bloques no se retiraron ni permanecieron muertos — el guard se corrigió y reactivó a sus consumidores vivos; ver adenda D-T2C-A1
- [x] No se editó ninguna región de gates (verificado en auditoría 2026-09-11)

### Tarea 2: S9 — certificar `INVALID_MAPPINGS` (y curar el fósil V3 si sigue vivo)

**Objetivo**: Fijar por contrato la forma del registro y su coherencia con `PAIN_SOLUTION_MAP`.

**Archivos a leer/editar**:
- `modules/quality/asset_semantics_validator.py` — `INVALID_MAPPINGS`
- `modules/commercial_documents/pain_solution_mapper.py` — símbolo `PAIN_SOLUTION_MAP` (fuente canónica de `pain_id`)
- `modules/common/service_identity.py` — fósil V3 `ASSET_TO_PAIN_ID`

**Enfoque**:
1. `grep` el fósil V3 (`ASSET_TO_PAIN_ID["monthly_report"]`): si sigue vivo, curarlo; si ya no existe, declararlo cerrado con evidencia.
2. Escribir un **test de contrato** que fije: toda clave de `INVALID_MAPPINGS` ∈ `PAIN_SOLUTION_MAP`, y todo valor ∈ `ASSET_CATALOG` (misma forma que `test_service_identity_registry.py`).

**Criterios de aceptación**:
- [x] Test de contrato verde: claves de `INVALID_MAPPINGS` ⊆ `PAIN_SOLUTION_MAP` y valores ⊆ `ASSET_CATALOG` — vía `test_invalid_mappings_valida_contra_capa1` (preexistente; verificado en auditoría 2026-09-11)
- [x] Fósil V3 verificado con `grep`: curado o declarado cerrado con evidencia — solo docstring en `service_identity.py`, candado AST en `test_service_identity_registry.py` (auditoría 2026-09-11)
- [x] `validar_semantica_comercial` conserva su comportamiento (test de no-regresión) — sin test nuevo; cubierto por los tests preexistentes de `tests/test_asset_semantics_validator.py`, verdes en auditoría 2026-09-11

### Tarea 3: Tests + Docs + Post-ejecución

```bash
./venv/Scripts/python.exe -m pytest tests/quality_gates/tribunal/ tests/quality/ -v
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-T2-C \
    --desc "S-E2 y S9: cura del NameError latente de site_presence_report + certificacion de INVALID_MAPPINGS (residuos heredados del tribunal)" \
    --archivos-nuevos "tests/quality_gates/tribunal/test_s_e2_generate_proposal_false.py,tests/quality/test_asset_semantics_registry.py" \
    --archivos-mod "main.py,modules/commercial_documents/v4_proposal_generator.py,modules/asset_generation/v4_asset_orchestrator.py,modules/quality/asset_semantics_validator.py" \
    --tests "N" \
    --check-manual-docs
```

> **Anotación post-auditoría (2026-09-11) — D2**: el entregable `tests/quality/test_asset_semantics_registry.py` de estos comandos **nunca se creó** (el directorio `tests/quality/` tampoco existe; la ruta del primer `pytest` nunca se ejecutó). S9 quedó certificado sin código nuevo por `test_invalid_mappings_valida_contra_capa1` (preexistente en `tests/common/test_service_identity_registry.py`). La ejecución real de `log_phase_completion.py` no registró el archivo fantasma ni `modules/quality/asset_semantics_validator.py` (que `--archivos-mod` listaba como modificado sin estarlo): la entrada en REGISTRY quedó limpia. El texto prescrito se conserva íntegro como evidencia; la discrepancia quedó así registrada.

---

## Post-Ejecución (OBLIGATORIO)

1. **`dependencias-fases.md`**: marcar FASE-T2-C ✅
2. **`README.md` del plan**: actualizar progreso
3. **`09-documentacion-post-proyecto.md`**: Secciones A, B, D, E
4. **`10-analisis-post-implementacion.md`**: fila T2-C + lecciones (mínimo 3) + actualizar filas S-E2/S9 de seguimientos
5. **`evidence/FASE-T2-C/`**: baseline pre/post + evidencia de las sondas
6. **`06-checklist-implementacion.md`**: marcar items T2-C

---

## Criterios de Completitud (CHECKLIST)

- [x] **AC15**: S-E2 cerrado — `generate_proposal=False` no lanza `NameError` (test verde)
- [x] **AC16**: S9 certificado — test de contrato de `INVALID_MAPPINGS` verde
- [x] **NR1**: `passed_post = passed_pre + tests nuevos` (baseline pre/post)
- [x] **NR3**: `run_all_validations.py --quick` TOTAL PASS
- [x] **NR4**: No reimplementa gates
- [x] **Post-ejecución completada**

---

## Restricciones

- **Presupuesto**: 40 iteraciones, corte en commit de código (R2.1)
- **NO ejecutar v4complete** (la corrida E2E es su propia fase, posterior)
- **NO modificar ROADMAP.md ni `judge.py` ni los revisores** (contrato de T1 estable)
- **NO usar números de línea** (R2.2: citar símbolos)
- **NO delegar a subagente** (imports del proyecto + venv Windows desde WSL → DIRECTA)
- **Re-verificar toda cita de región con `grep` antes de editar** (L-A6: `main.py` creció con T1)

---

## Adenda post-auditoría (2026-09-11) — D-T2C-A1

**Desvío registrado**: el AC de Tarea 1 «El régimen `generate_proposal=True` no cambia de comportamiento» NO se cumplió tal como fue redactado. Los 3 bloques `presence_lookup` de `modules/commercial_documents/v4_proposal_generator.py` no se retiraron ni permanecieron muertos: el guard insatisfacible (`hasattr(site_presence_report, 'results')` contra el dict canónico que retorna `normalize_site_presence`) fue corregido a una cascada dict+dataclass, reactivando a los consumidores vivos de la tabla de servicios y de la rama AEO («ℹ️ Presente en sitio»). Sonda de auditoría: con el dict canónico, `presence_lookup` pasa de vacío a poblado, por lo que el contenido de la propuesta comercial cambia en el régimen `True`. El checklist de la fase (06) marcó el ítem equivalente como cumplido bajo la rama «retirados (o justificada su permanencia)» — rama que no ocurrió; los Criterios de aceptación de Tarea 1 de este prompt quedaron sin marcar en el cierre.

**Decisión conservada (no se revierte)**: el propio plan condicionaba el retiro a que los bloques no tuvieran consumidor vivo vía `grep`; sí lo tienen, así que retirarlos habría sido incorrecto. La reactivación alinea `v4_proposal_generator` con `CoherenceValidator._check_promised_assets_exist`, que ya consumía el dict canónico.

**Estado residual**: no existe test que fije la nueva salida contra el código real de producción — los 7 tests de la fase re-implementan la lógica del lookup o leen `main.py` como texto (posición relativa de `site_presence_report = site_presence_snapshot` respecto de `if generate_proposal:`). → **CIERRADO 2026-09-11**: clase `TestPresenceLookupLiveConsumers` (11 tests) en `tests/quality_gates/tribunal/test_s_e2_generate_proposal_false.py`, ejecutando directo `_generate_dynamic_services_table`, `_generate_technical_assets_table` y `_generate_asset_quality_table` con dict canónico (`exists`, `exists_with_issues`, `not_exists`), con `None`, con `results` vacíos, con objeto tipo dataclass (`.results`) y con objeto sin `results` (rama tolerada). El archivo pasó de 7 a 18 tests verdes; colectados 4,018→4,029.

**Riesgo y remediación**: riesgo acotado a FASE-E2E, que debe validar la veracidad de las filas «Presente en sitio» contra el sitio real (no basta el diff contra un output pre-T2-C, cuyo estado anterior era el incorrecto). Remediación acordada: test dirigido a los métodos de `v4_proposal_generator.py` que construyen `presence_lookup`, con dict canónico y con `None`. → **Remediación ejecutada 2026-09-11**; a E2E solo le queda la verificación de veracidad en sitio real (registrada en `dependencias-fases.md`).

**Alcance de esta adenda**: corrige el cierre documental; no toca código, no invalida AC15/AC16/NR3/NR4 y conserva íntegra la evidencia en `evidence/FASE-T2-C/`.
