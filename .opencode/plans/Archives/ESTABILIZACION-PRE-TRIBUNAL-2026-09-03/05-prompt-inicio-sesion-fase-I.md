# FASE-I — E2E ÚNICA: corrida v4complete Hotel Salento Real

**ID**: ESTABILIZACION-PRE-TRIBUNAL-2026-09-03 / FASE-I
**Objetivo**: Ejecutar la **única** corrida `v4complete` de todo el plan sobre **Hotel Salento Real**
(*"Hotel Salento Real | Quindio, Colombia - Web Oficial"*), preservar la evidencia de forma proactiva y
comparar contra el baseline `output/FASE-D_salentoreal_post_guard/` para demostrar sobre artefactos
reales que los fixes fueron superados.
**Dependencias**: FASE-A ✅ B ✅ C ✅ D ✅ E ✅ F ✅ G ✅ H ✅ — **las ocho**
**Duración estimada**: 1-2 horas (el comando largo ~3 min)
**Complejidad técnica**: **BAJA** (implementación) — el valor está en la comparación, no en el código
**Modo de ejecución**: **MIXTO** — `v4complete` vía subagente (timeout 900, notify); pre-flight, evidencia y comparación en **parent**
**Skill**: `phased_project_executor.md` v2.18.0
**Presupuesto**: ≤25 iteraciones (R2 tope: 60) · **Comandos largos: 1** (R3)
**ACs que verifica**: AC5, AC6, AC9, AC12 sobre artefactos reales · **NR6** · y aporta la evidencia de los 12 ACs + 12 NRs (dos familias: hallazgo NR1-NR6, producto NR7-NR12) para VERIFY

---

## Contexto

El usuario pidió explícitamente **una única ejecución de `v4complete` al término del plan**. Eso es una
decisión de diseño del plan, no una restricción presupuestaria: las fases A-H validan con tests y
fixtures, y **solo al final** se observa el sistema integrado sobre un hotel real.

### Por qué Hotel Salento Real

Es el **corpus de referencia** del dossier completo. Todos los hallazgos (8 caídas silenciosas, 3
candados rotos, A1-A6, B1-B5, V1-V16) fueron medidos sobre la corrida
`output/FASE-D_salentoreal_post_guard/v4_complete/` del **2026-08-31 12:28:03**. Correr sobre el mismo
hotel es lo único que permite una comparación **homóloga**: mismo sitio, mismos datos de entrada,
distinto código.

### Identificación del sitio

| Campo | Valor |
|-------|-------|
| Nombre comercial (usuario) | *"Hotel Salento Real \| Quindio, Colombia - Web Oficial"* (título de la ficha) |
| **URL canónica** | `https://www.hotelsalentoreal.com/` |
| Verificación | Es la URL del baseline y la que figura en el estado persistido (escrito en `main.py:1433` vía `MemoryManager().save_state`; reinyección en `main.py:226-227` — el string `last_url` no vive en `agent_harness/memory.py`) |
| Guard `own_site_guard` (v4.74.0) | **Acepta** — sitio propio, no OTA/red social |
| `target_id` esperado | `hotelsalentoreal.com` (`_normalize_url` netloc-only, `main.py:3604-3615`) |

### Baseline de comparación

`output/FASE-D_salentoreal_post_guard/v4_complete/` — corrida 2026-08-31 12:28:03, re-verificada 2026-09-02.

**Artefactos presentes en el baseline** (verificado por `ls`):

```
v4_complete/
├── 01_DIAGNOSTICO_Y_OPORTUNIDAD_20260831_122803.md
├── 02_PROPUESTA_COMERCIAL_20260831_122803.md
├── v4_complete_report.json
├── deliveries/
│   ├── hotelsalentoreal_20260831/          (37 archivos expandidos)
│   └── hotelsalentoreal_20260831.zip       (46.552 bytes)
├── health_dashboard/
└── hotelsalentoreal/
    ├── analytics_setup_guide/
    ├── geo_enriched/
    ├── indirect_traffic_optimization/
    ├── llms_txt/
    ├── monthly_report/
    ├── research_08df2aaeef1f_Hotelsalentoreal.json
    └── v4_audit/
        ├── asset_generation_report.json
        ├── audit_report_20260831_122757.json
        ├── coherence_validation.json
        ├── coherence_validation_post_gen.json
        ├── commercial_gates_report.json                    (3 gates en verde)
        ├── commercial_gates_report_diagnostic_20260831_122803.json   (9 gates; aquí está CG-WHATSAPP-LEAD failed)
        ├── delivery_quality_report.json
        ├── financial_scenarios_20260831_122757.json
        ├── gate_report_20260831_122803.json
        ├── geo_flow_result.json
        ├── human_checklist.md
        ├── ia_readiness_report.json
        ├── pain_ledger.json
        ├── pain_ledger_resolved.json
        └── proposal_asset_matrix.json
```

⚠️ **`site_presence_snapshot` NO existe en el baseline** — es exactamente la deuda **A2/H7** que FASE-E
cerró. Su aparición en la corrida nueva es la prueba positiva de AC9.

⚠️ **Nombres timestamped sin índice** (deuda **H7**): `gate_report_*.json`, `financial_scenarios_*.json`,
`audit_report_*.json`, `commercial_gates_report_diagnostic_*.json`. La comparación debe **resolver el
nombre** primero, no asumir el del baseline.

⚠️ **Los DOS archivos de commercial gates**: el baseline tiene `commercial_gates_report.json` con **3**
gates en verde y `commercial_gates_report_diagnostic_*.json` con los otros **9** — y ahí está el único
fallo real (`CG-WHATSAPP-LEAD`, WARNING, `passed: false`). Leer **ambos**; el conteo real es **12 CG-***.

### Valores del baseline a contrastar

| Métrica | Baseline (2026-08-31 12:28) | Esperado tras A-H |
|---------|------------------------------|-------------------|
| `coherence_score_pre/post/final` | **0.88** (canónico; `0.9133` **no existe** en artefactos — C1) | ≥ 0.80 |
| `is_coherent` | **false** en **3 artefactos / 6 copias** (V16), causa `assets_are_justified 3/4` | **true**, o el campo eliminado (según decisión F3) |
| `overall_score` | 0.88 | ≥ 0.80 |
| Matriz de servicios | 7 servicios: **6 NO_BREACH + 1 LINKED** (`llms_txt`), `delivery_ready: True` | **`no_breach = 0`** (AC5) |
| `pain_ledger_resolved` | **3** entradas (todas MEDIUM, ASSET_GENERATED) | según biyección de FASE-B |
| Assets generados | **4** (`analytics_setup_guide` WARNING, `indirect_traffic_optimization` WARNING, `llms_txt` PASSED, `monthly_report` PASSED), `estimated = 2`, `delivery_ready_percentage = 100.0` | 2 huérfanos con decisión de FASE-C |
| `asset_path` | **null** incluso en la entrada LINKED (A6) | poblado y verificable |
| Publication gates | 13/13 bloqueando (dict plano), perfil `READY_FOR_PUBLICATION` | **11 blocking + 2 advisory** |
| `critical_recall` | **1.0 vacuo** | **< 1.0** |
| `doc_audit_consistency` | PASSED con `value=null` (sin datos) | evaluado de verdad |
| ZIP | `hotelsalentoreal_20260831.zip`, 46.552 B, 37 archivos | **NO debe generarse si `is_coherent` era false** (AC12) |
| `site_presence_snapshot` | **inexistente** | **persistido** |
| PageSpeed | `status=ERROR` (corrida 12:28 **anterior** al fix OPS ~15:08) | debe resolver VERIFIED si `.env` está correcta |
| Evidence tier | Tier B (*"uses default/legacy values"*), `direct_channel_percentage: "default"` | Tier B (se corre CON DEFAULTS) |

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-A … FASE-H | ✅ **Las ocho completadas** (verificar en `06-checklist-implementacion.md` antes de correr) |

⚠️ **Bloqueo duro**: si alguna fase A-H no está ✅, **NO ejecutar**. Una corrida sobre un sistema a medio
refactorizar no es recuperable — y el plan presupuesta **una sola**.

### Base Técnica Disponible

- **Script de comparación reutilizable**: `evidence/FASE-VUP-D/verificar_no_regresion.py` (creado para
  FASE-D del plan VALIDADOR-URL-PROPIA; hizo 7/7 checks contra este mismo baseline). **Adaptarlo**, no
  reescribirlo desde cero
- **Python**: `./venv/Scripts/python.exe`
- **Estado persistido**: `last_url = https://www.hotelsalentoreal.com/` (coincide con el target)
- **`.env`**: `PAGESPEED_API_KEY` (39 chars, canónica) y `GOOGLE_PAGESPEED_API_KEY` (3 chars, placeholder inválido)

---

## Tareas

### Tarea I1: Pre-flight (parent, ANTES del run)

**Objetivo**: Que la corrida no se contamine por causas ajenas al refactor.

**Criterios de aceptación**:
- [ ] Las 8 fases A-H ✅ en `06-checklist-implementacion.md`
- [ ] `git status` limpio (o los cambios sucios identificados y **no** atribuibles a este plan)
- [ ] **grep de símbolos no definidos en ramas nuevas** antes del run (lección del plan anterior:
      un `NameError` en una rama poco ejercida revienta la corrida a los 3 minutos)
      ```bash
      ./venv/Scripts/python.exe -c "import main; import modules.quality_gates.publication_gates; import modules.asset_generation.proposal_asset_alignment; import modules.commercial_documents.v4_proposal_generator; import modules.commercial_documents.v4_diagnostic_generator; print('imports OK')"
      ```
- [ ] `run_all_validations.py --quick` → 7/7 · `validate_agents_md.py` → 6 PASS / 0 FAIL
- [ ] Baseline de tests verde: `pytest tests/quality_gates tests/asset_generation -q`
- [ ] **`.env` verificada**: `PAGESPEED_API_KEY` presente y de longitud plausible (39). Si solo está la
      placeholder de 3 chars, el run reproducirá el error de PageSpeed y contaminará la comparación —
      registrar como **anomalía de infraestructura**, no como regresión
- [ ] `--output` alternativo confirmado como no existente (no sobrescribir evidencia previa)
- [ ] Espacio en disco y ausencia de procesos pytest colgados (`taskkill` si hace falta)

### Tarea I2: Comando largo — `v4complete` (subagente, timeout 900, notify)

**Objetivo**: La única ejecución del plan.

**Comando**:
```bash
./venv/Scripts/python.exe main.py v4complete --url https://www.hotelsalentoreal.com/ --output output/FASE-I_salentoreal_post_estabilizacion
```

**Criterios de aceptación**:
- [ ] `EXIT_CODE = 0` (el baseline lo logró en ~3 min)
- [ ] Duración registrada (esperable ~3 min; el baseline de FASE-D del plan anterior tardó eso)
- [ ] stdout/stderr capturados a archivo (`> temp/faseI_run.txt 2>&1`)
- [ ] **"Using defaults"** en la salida — equivalencia con el baseline (que corrió CON DEFAULTS)
- [ ] 0 interferencias del guard `own_site_guard` (la URL es sitio propio)

**Restricciones de I2**:
- ❌ **NO poblar `clientes/` con onboarding de Salento Real.** El baseline corrió **CON DEFAULTS**
      (`direct_channel_percentage: "default"`, Tier B evidence) y **no existe YAML de onboarding de
      Salento Real en el repo**. Fabricar onboarding rompería la equivalencia de tier de evidencia,
      pricing y gates (lección **F5** del plan VALIDADOR-URL-PROPIA)
- ❌ **NO pasar `--ga4-property-id`** — cambiaría `use_ga4` y con ello las 2 brechas analytics que
      representan 57% de los $4.04M/mes del baseline
- ❌ **NO pasar `--force`** (semántica dual desde v4.74.0: bypass del guard / sobrescribir PDF) — no hace falta
- ❌ **NO re-correr** si falla: clasificar la falla (regresión del plan vs infraestructura), registrarla
      y llevarla a VERIFY. El plan presupuesta **una** corrida

**Delegación**: subagente con `timeout=900` y `notify_on_complete=True`. El subagente **solo ejecuta y
captura** — no interpreta resultados ni toca código. La interpretación es del parent (executor L30 RC1-RC2).

### Tarea I3: Protocolo de Evidencia Proactiva (parent, INMEDIATO post-run)

**Objetivo**: Copiar los artefactos críticos **antes** de cualquier análisis. Si algo los regenera o
sobrescribe, la evidencia se pierde.

**Archivos afectados**: `evidence/FASE-I/` (nuevo)

**Criterios de aceptación** — copiar con **rutas explícitas** (Git Bash sin globstar; estructura anidada):
- [ ] `v4_complete_report.json`
- [ ] `01_DIAGNOSTICO_Y_OPORTUNIDAD_*.md` y `02_PROPUESTA_COMERCIAL_*.md`
- [ ] De `hotelsalentoreal/v4_audit/`: **todos** los JSON listados en el baseline **más** el nuevo
      `site_presence_snapshot*` (prueba de AC9)
- [ ] **Ambos** `commercial_gates_report.json` **y** `commercial_gates_report_diagnostic_*.json`
- [ ] `pain_ledger.json` y `pain_ledger_resolved.json`
- [ ] `proposal_asset_matrix.json` (prueba de AC5/AC6)
- [ ] `asset_generation_report.json` (prueba de AC6/V16)
- [ ] `delivery_quality_report.json` (prueba de AC11 + `asset_path` de AC9)
- [ ] `coherence_validation.json` y `coherence_validation_post_gen.json` (prueba de AC12)
- [ ] `gate_report_*.json`, `financial_scenarios_*.json`, `audit_report_*.json` (timestamped — resolver nombre)
- [ ] `human_checklist.md` (prueba del consumidor nombrado de AC7/D2)
- [ ] `geo_flow_result.json`, `ia_readiness_report.json`
- [ ] El ZIP y su directorio expandido **si se generaron** (prueba de AC12)
- [ ] `temp/faseI_run.txt` (stdout/stderr del run)
- [ ] **Manifiesto** `evidence/FASE-I/MANIFIESTO.md` con: fecha/hora del run, exit code, duración,
      comando exacto, lista de archivos copiados con tamaño, y los nombres timestamped resueltos

### Tarea I4: Comparación contra baseline (parent)

**Objetivo**: Demostrar sobre artefactos reales qué fixes fueron superados.

**Archivos afectados**: `evidence/FASE-I/comparacion-vs-baseline.md` (nuevo) + adaptación de
`evidence/FASE-VUP-D/verificar_no_regresion.py`

**Criterios de aceptación**:
- [ ] Script de comparación adaptado y ejecutado, con salida por check (PASS/FAIL + valor baseline + valor nuevo)
- [ ] **AC5 verificado**: `no_breach` 6 → **0** en `proposal_asset_matrix.json`
- [ ] **AC6 verificado**: `is_coherent` en los 3 artefactos (6 copias) que lo declaraban (o su ausencia si F3 lo eliminó)
- [ ] **AC9 verificado**: `site_presence_snapshot` **existe** (`find output/FASE-I_salentoreal_post_estabilizacion -iname "*site_presence*"` → ≥1) y `asset_path` poblado
- [ ] **AC12 verificado**: coherencia entre `is_coherent` y el veredicto de publicación / la generación del ZIP
- [ ] **AC7 verificado**: el perfil de los 13 gates refleja 11 blocking + 2 advisory
- [ ] **NR1/NR2 verificados**: `doc_audit_consistency` con `value` no nulo; `critical_recall < 1.0`
- [ ] **NR6 verificado**: `coherence_score ≥ 0.80` y perfil de gates esperado
- [ ] Tabla de las **8 caídas silenciosas** del dossier §4 → cuáles aparecen ahora en el diagnóstico
- [ ] **Anomalías clasificadas**: cada diferencia se marca como (i) fix esperado del plan,
      (ii) regresión del plan, (iii) anomalía de infraestructura preexistente (gemini 403, PageSpeed key),
      (iv) variación natural del sitio vivo (el sitio puede haber cambiado desde el 31-08)
- [ ] Salida escrita en `evidence/FASE-I/comparacion-vs-baseline.md`

⚠️ **Regla de oro** (lección ROADMAP v4.0→v4.1): la comparación debe ser contra **salidas reales**, no
contra citas de código. Y una diferencia no explicada **no** se clasifica como "variación natural" para
cerrar el check — se registra como seguimiento abierto.

---

## Tests Obligatorios

Esta fase **no agrega tests de unidad** — agrega **evidencia**. Su validación es:

| Check | Medio | Criterio de Éxito |
|-------|-------|-------------------|
| Run completo | exit code + duración | `EXIT_CODE = 0` en ~3 min |
| No-regresión de suite | `pytest tests/quality_gates tests/asset_generation -q` | 848/2 + delta A-H preservado |
| Validadores | `run_all_validations.py --quick` | 7/7 **después** del run también |
| Comparación | `verificar_no_regresion.py` adaptado | Todos los checks PASS o con anomalía clasificada |
| Evidencia | `evidence/FASE-I/MANIFIESTO.md` | Completo, con tamaños y nombres timestamped resueltos |

**Comando de validación**:
```bash
# I1 pre-flight
./venv/Scripts/python.exe -c "import main; print('imports OK')"
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
./venv/Scripts/python.exe -m pytest tests/quality_gates tests/asset_generation -q > temp/faseI_pre_baseline.txt 2>&1

# I2 run (subagente, timeout 900)
./venv/Scripts/python.exe main.py v4complete --url https://www.hotelsalentoreal.com/ --output output/FASE-I_salentoreal_post_estabilizacion > temp/faseI_run.txt 2>&1

# I3 evidencia
find output/FASE-I_salentoreal_post_estabilizacion -iname "*site_presence*"
ls -la output/FASE-I_salentoreal_post_estabilizacion/v4_complete/hotelsalentoreal/v4_audit/

# I4 comparación
./venv/Scripts/python.exe temp/comparar_faseI_vs_baseline.py > temp/faseI_comparacion.txt 2>&1
```

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

1. **`dependencias-fases.md`** — marcar FASE-I ✅, fecha, notas (exit code, duración, anomalías)
2. **`README.md` del plan** — tabla de progreso + métricas de la corrida
3. **`06-checklist-implementacion.md`** — fila FASE-I, NR6, y **actualizar la columna Evidencia de los
   AC1-AC12 y NR1-NR12** con las rutas de `evidence/FASE-I/` (es el insumo directo de VERIFY)
4. **`09-documentacion-post-proyecto.md`** — Sección C (E2E: comando, resultado, métricas), D (métricas acumulativas)
5. **`10-analisis-post-implementacion.md`**
   - Resumen de Ejecución: fila FASE-I
   - **Métricas de Ejecución**: coherence nuevo vs 0.88, `no_breach` nuevo vs 6, `is_coherent` nuevo vs
     false, nº de gates por severidad, `critical_recall` nuevo vs 1.0
   - **Anomalías clasificadas** (i-iv) — insumo crítico de VERIFY
   - Seguimientos abiertos
6. **`evidence/FASE-I/`** — artefactos + `MANIFIESTO.md` + `comparacion-vs-baseline.md`

**Cierre con script**:
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-I --desc "E2E unica v4complete Hotel Salento Real post-estabilizacion + evidencia proactiva + comparacion vs baseline" --check-manual-docs
```
**SIN `--release`.**

---

## Criterios de Completitud (CHECKLIST)

⚠️ **Verificar ANTES de marcar como ✅ COMPLETADA** ⚠️

- [ ] **Las 8 fases A-H estaban ✅ ANTES del run**
- [ ] **I1 pre-flight completo**: imports OK, validadores 7/7, `.env` verificada, grep de símbolos
- [ ] **Run ejecutado una sola vez** con `EXIT_CODE = 0`
- [ ] **Sin poblar `clientes/`** y sin `--ga4-property-id` (equivalencia con el baseline)
- [ ] **I3 evidencia copiada ANTES del análisis**, con `MANIFIESTO.md` completo
- [ ] **`site_presence_snapshot` presente** en la evidencia (prueba positiva de AC9)
- [ ] **Ambos archivos de commercial gates** copiados
- [ ] **Nombres timestamped resueltos** y registrados en el manifiesto
- [ ] **I4 comparación ejecutada** con todos los checks clasificados
- [ ] **AC5/AC6/AC9/AC12 verificados sobre artefactos reales**
- [ ] **NR1/NR2/NR6 verificados**
- [ ] **Las 8 caídas silenciosas re-evaluadas** contra el diagnóstico nuevo
- [ ] **Anomalías clasificadas** en las 4 categorías, sin diferencias sin explicar
- [ ] **Suite de tests intacta tras el run**
- [ ] **Los 5 archivos de plan actualizados**
- [ ] **`log_phase_completion.py` ejecutado SIN `--release`**
- [ ] **Commit hecho** referenciando FASE-I (evidencia incluida, sin el ZIP si pesa demasiado)

---

## Restricciones

**Alcance — qué NO está en esta fase**:
- ❌ **NO corregir código**: si la corrida revela un defecto, se **registra** y se lleva a VERIFY. Esta
      fase no arregla nada — mide
- ❌ **NO re-correr** el `v4complete`: el plan presupuesta **una sola** ejecución
- ❌ **NO poblar `clientes/`** con onboarding fabricado
- ❌ **NO pasar flags que cambien el tier de evidencia** (`--ga4-property-id`, etc.)
- ❌ **NO sobrescribir el baseline** `output/FASE-D_salentoreal_post_guard/` — es solo lectura
- ❌ **NO tocar `VERSION.yaml`** — FASE-RELEASE

**Restricciones técnicas**:
- Python del venv: `./venv/Scripts/python.exe`
- Comando largo delegado con `timeout=900` y `notify_on_complete=True`
- `cp` con **rutas explícitas** (Git Bash sin globstar)
- Si el run se cuelga: `taskkill` al proceso, no dejarlo corriendo en background
- No interpretar resultados dentro del subagente — solo capturar

---

## Prompt de Ejecución

```
Actúa como integrador senior en el repo iah-cli (Python, Windows, ./venv/Scripts/python.exe).
Esta fase NO corrige código: MIDEN una corrida y compara contra el baseline.

OBJETIVO: Única ejecución v4complete del plan sobre Hotel Salento Real
("Hotel Salento Real | Quindio, Colombia - Web Oficial" → https://www.hotelsalentoreal.com/),
evidencia proactiva y comparación contra output/FASE-D_salentoreal_post_guard/.

CONTEXTO:
- Plan: /.opencode/plans/Archives/ESTABILIZACION-PRE-TRIBUNAL-2026-09-03/
- FASE-A…H ✅ (las ocho). Si alguna no está ✅, NO EJECUTAR — la corrida no es recuperable
- Baseline: corrida 2026-08-31 12:28:03. Valores clave: coherence 0.88, is_coherent=FALSE en 3
  artefactos (6 copias en disco), matriz 7 servicios con 6 NO_BREACH + 1 LINKED, pain_ledger_resolved 3 entradas,
  4 assets generados (2 huérfanos), asset_path=null, 13/13 gates bloqueando, critical_recall 1.0 vacuo,
  doc_audit_consistency PASSED con value=null, ZIP hotelsalentoreal_20260831.zip 46.552 B / 37 archivos,
  site_presence_snapshot INEXISTENTE, Tier B con defaults
- Script reutilizable de comparación: evidence/FASE-VUP-D/verificar_no_regresion.py (hizo 7/7 checks
  contra este mismo baseline) → ADAPTARLO, no reescribirlo
- Nombres TIMESTAMPED sin índice (deuda H7): gate_report_*, financial_scenarios_*, audit_report_*,
  commercial_gates_report_diagnostic_* → resolver el nombre, no asumir el del baseline
- DOS archivos de commercial gates: commercial_gates_report.json (3 gates) Y
  commercial_gates_report_diagnostic_*.json (9 gates, ahí está CG-WHATSAPP-LEAD failed). Leer AMBOS

TAREAS:
1. I1 Pre-flight (tú): las 8 fases ✅ · git status · grep de símbolos no definidos (import de main y de
   los 5 módulos tocados) · run_all_validations.py --quick 7/7 · validate_agents_md.py 6/0 · suite
   baseline verde · .env verificada (PAGESPEED_API_KEY presente, ~39 chars; la placeholder
   GOOGLE_PAGESPEED_API_KEY de 3 chars es trampa conocida V12) · --output no existe
2. I2 Comando largo (SUBAGENTE, timeout 900, notify):
   ./venv/Scripts/python.exe main.py v4complete --url https://www.hotelsalentoreal.com/ --output output/FASE-I_salentoreal_post_estabilizacion
   El subagente SOLO ejecuta y captura stdout/stderr a temp/faseI_run.txt. No interpreta, no toca código.
3. I3 Protocolo de Evidencia Proactiva (tú, INMEDIATO post-run, ANTES de analizar): copiar a
   evidence/FASE-I/ con rutas explícitas todos los artefactos críticos (ver prompt de fase) + el NUEVO
   site_presence_snapshot + AMBOS commercial_gates + el ZIP si se generó + MANIFIESTO.md con fecha,
   exit code, duración, comando exacto, archivos con tamaño y nombres timestamped resueltos
4. I4 Comparación (tú): adaptar verificar_no_regresion.py y verificar AC5 (no_breach 6→0), AC6
   (is_coherent), AC9 (snapshot + asset_path), AC12 (coherencia is_coherent↔veredicto↔ZIP), AC7
   (11 blocking + 2 advisory), NR1 (doc_audit con value no nulo), NR2 (critical_recall < 1.0), NR6
   (coherence ≥ 0.80). Re-evaluar las 8 caídas silenciosas del dossier §4 contra el diagnóstico nuevo.
   Salida: evidence/FASE-I/comparacion-vs-baseline.md

CRITERIOS:
- EXIT_CODE = 0 en ~3 min, "Using defaults" en la salida, 0 interferencias del own_site_guard
- Todos los checks PASS o con anomalía CLASIFICADA en: (i) fix esperado (ii) regresión del plan
  (iii) infraestructura preexistente (gemini 403, PageSpeed key) (iv) variación natural del sitio vivo
- Suite de tests intacta tras el run

RESTRICCIONES (críticas):
- NO corregir código en esta fase: si aparece un defecto, se REGISTRA y se lleva a VERIFY
- NO re-correr el v4complete (el plan presupuesta UNA sola ejecución)
- NO poblar clientes/ con onboarding fabricado (el baseline corrió CON DEFAULTS y no existe YAML de
  onboarding de Salento Real; fabricarlo rompería la equivalencia de tier/pricing/gates — lección F5)
- NO pasar --ga4-property-id (cambiaría use_ga4 y con ello 2 brechas = 57% de los $4.04M/mes) ni --force
- NO sobrescribir el baseline (solo lectura); NO tocar VERSION.yaml
- Una diferencia NO explicada no se clasifica como "variación natural" para cerrar el check: va a
  seguimientos abiertos
- Pytest en lotes pequeños con salida a archivo; NUNCA tests/commercial_documents completo (~8GB)

POST-EJECUCIÓN (obligatoria):
Actualizar dependencias-fases.md, README.md, 06-checklist-implementacion.md (columna EVIDENCIA de los
AC1-12 y NR1-12 con rutas de evidence/FASE-I/ — es el insumo directo de VERIFY),
09-documentacion-post-proyecto.md (sección C E2E + D), 10-analisis-post-implementacion.md (métricas
nuevo vs baseline + anomalías clasificadas), evidence/FASE-I/ (artefactos + MANIFIESTO + comparación).
Luego: log_phase_completion.py --fase FASE-I --desc "..." --check-manual-docs  (SIN --release).
Commit referenciando FASE-I.
```
