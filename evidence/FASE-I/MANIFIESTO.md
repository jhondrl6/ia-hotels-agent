# MANIFIESTO DE EVIDENCIA — FASE-I (única corrida E2E del plan)

**Plan**: `ESTABILIZACION-PRE-TRIBUNAL-2026-09-03` / FASE-I
**Corrida**: `v4complete` sobre Hotel Salento Real — **única ejecución presupuestada por el plan**
**Fase anterior en cerrar**: FASE-H (2026-09-04) · **Este cierre**: 2026-09-04

---

## 1. El comando

```bash
./venv/Scripts/python.exe main.py v4complete --url https://www.hotelsalentoreal.com/ \
  --output output/FASE-I_salentoreal_post_estabilizacion > temp/faseI_run.txt 2>&1
```

| Campo | Valor |
|-------|-------|
| Inicio | `2026-09-04T12:01:24-05:00` (epoch 1788541284) |
| Fin | `2026-09-04T12:04:18-05:00` (epoch 1788541458) |
| Duración | **174 s** (≈ 2 min 54 s; presupuestado ~3 min) |
| **EXIT_CODE** | **0** |
| Tracebacks en stdout | **0** (`grep -c Traceback` = 0) |
| `"Using defaults"` en la salida | presente (1 ocurrencia) → equivalencia de Tier B con el baseline |
| Interferencias `own_site_guard` | **0** (URL de sitio propio aceptada) |
| HEAD del repo al correr | `1cf9634` (rama `master`, working tree limpio) |
| Flags omitidos (deliberadamente) | `--force`, `--force-new`, `--ga4-property-id`, `--debug`; sin poblar `clientes/` |

Ejecutada por subagente delegado que **solo ejecutó y capturó** (modo MIXTO del prompt de fase). La
interpretación es de el parent y vive en `comparacion-vs-baseline.md`.

**Verificación previa de que la corrida corre fresca** (no recicla el análisis del 31-08):
`find_latest_v4_analysis` se llama **solo** en la rama `execute` (`main.py:776`); `cmd_v4complete`
no la invoca. Los `research_*.json` se escriben pero no se leen de caché entre corridas
(único hit: `modules/providers/autonomous_researcher.py:86`). Confirmado empíricamente: el
`research_id` cambió (`08df2aaeef1f` → `ec24b7e8fed4`).

---

## 2. Pre-flight I1 (antes del run)

| Check | Resultado |
|-------|-----------|
| Fases A-H ✅ en `README.md §Progreso` | **8/8 ✅** (bloqueo duro satisfecho) |
| `git status` | limpio, rama `master`, HEAD `1cf9634` |
| Imports `main` + 5 módulos tocados | `imports OK` |
| Símbolos globales indefinidos (21 fuentes del plan, AST `symtable`) | **0** |
| Archivos eliminados por el plan sin imports colgantes | OK (`publication_state`, `modules/data_validation/metadata_validator` → 0 referencias vivas; la ruta viva es `data_validation/metadata_validator`) |
| `run_all_validations.py --quick` | **7/7** |
| `validate_agents_md.py` | **5 PASS / 1 FAIL** — `test_count` 3689 (AGENTS) vs 3889 (pytest) = 5.1 % > ±5 %. Deriva **documental**, preexistente en HEAD, ajena a esta fase → registradas como S-I6 |
| Suite base `tests/quality_gates tests/asset_generation` | **944 passed, 2 skipped** en 6.31 s |
| `.env` | `PAGESPEED_API_KEY` 39 chars **OK**; `GOOGLE_PAGESPEED_API_KEY` 3 chars **placeholder** (trampa V12 conocida); `GEMINI_API_KEY` **AUSENTE** |
| `--output` destino | inexistente antes del run (no se sobrescribió evidencia) |
| Disco | 686 GB libres |

---

## 3. Nombres timestamped resueltos (deuda H7)

La comparación **resolvió** los nombres por glob en cada lado; ninguno se asumió.

| Artefacto | Baseline (31-08) | Esta corrida (04-09) |
|-----------|------------------|----------------------|
| `audit_report_*.json` | `audit_report_20260831_122757.json` | `audit_report_20260904_120404.json` |
| `financial_scenarios_*.json` | `financial_scenarios_20260831_122757.json` | `financial_scenarios_20260904_120404.json` |
| `gate_report_*.json` | `gate_report_20260831_122803.json` | `gate_report_20260904_120413.json` |
| `commercial_gates_report_diagnostic_*.json` | `..._20260831_122803.json` | `..._20260904_120413.json` |
| `commercial_gates_report.json` | sin timestamp | sin timestamp |
| Diagnóstico | `01_..._20260831_122803.md` | `01_..._20260904_120413.md` |
| Propuesta | `02_..._20260831_122803.md` | `02_..._20260904_120413.md` |
| Research | `research_08df2aaeef1f_Hotelsalentoreal.json` | `research_ec24b7e8fed4_Hotelsalentoreal.json` |
| Entrega ZIP | `hotelsalentoreal_20260831.zip` (46.552 B / 37 archivos) | `hotelsalentoreal_20260904.zip` (47.358 B / 38 archivos) |
| **`site_presence_snapshot.json`** | **INEXISTENTE** (deuda A2/H7) | **1.421 B — existe** (prueba positiva de AC9) |

---

## 4. Copia de evidencia (protocolo proactivo, ANTES del análisis)

`cp -r output/FASE-I_salentoreal_post_estabilizacion/v4_complete evidence/FASE-I/corrida` se ejecutó
inmediatamente después del run y antes de cualquier lectura analítica. **49 archivos** en
`evidence/FASE-I/` al cierre de esta fase.

Árbol copiado (`corrida/` = réplica exacta del `v4_complete/` generado):

```
evidence/FASE-I/
├── MANIFIESTO.md                      (este archivo)
├── comparacion-vs-baseline.md         (I4)
├── comparacion_resultados.json        (salida máquina de los 16 checks)
├── faseI_run.txt                      stdout/stderr del run (15.560 B)
├── faseI_pre_baseline.txt             suite pre-flight
├── faseI_validations_quick.txt        7/7
├── faseI_probe_base.txt               sonda de estructura del baseline
├── faseI_ocho_caidas_{new,base}.txt   dossier §4 re-evaluado en ambos lados
├── faseI_comparacion.txt              stdout de la comparación
├── faseI_repro_g2.py                  repro mínimo del camino G2/NR2 (medición)
├── comparar_faseI_vs_baseline.py      script de comparación adaptado
├── faseI_ocho_caidas.py / faseI_probe.py / faseI_env_check.py / faseI_undefined_names.py
└── corrida/
    ├── 01_DIAGNOSTICO_Y_OPORTUNIDAD_20260904_120413.md   (14.584 B)
    ├── 02_PROPUESTA_COMERCIAL_20260904_120413.md          (14.990 B)
    ├── v4_complete_report.json                            (13.954 B)
    ├── deliveries/hotelsalentoreal_20260904.zip           (47.358 B, 38 archivos)
    ├── health_dashboard/                                  (html 14.258 B + summary)
    └── hotelsalentoreal/
        ├── v4_audit/  (16 archivos: los del baseline + site_presence_snapshot.json)
        ├── analytics_setup_guide/ indirect_traffic_optimization/
        ├── llms_txt/ monthly_report/ geo_enriched/
        └── research_ec24b7e8fed4_Hotelsalentoreal.json
```

Archivos de `v4_audit/` con tamaño (esta corrida):

| Archivo | Bytes |
|---------|-------|
| `audit_report_20260904_120404.json` | 10.214 |
| `asset_generation_report.json` | 6.351 |
| `gate_report_20260904_120413.json` | 6.756 |
| `geo_flow_result.json` | 5.634 |
| `commercial_gates_report_diagnostic_20260904_120413.json` | 2.655 |
| `pain_ledger_resolved.json` | 1.748 |
| `proposal_asset_matrix.json` | 1.501 |
| `delivery_quality_report.json` | 1.521 |
| `site_presence_snapshot.json` | **1.421 (NUEVO)** |
| `coherence_validation.json` / `coherence_validation_post_gen.json` | 1.382 c/u |
| `pain_ledger.json` | 1.574 |
| `commercial_gates_report.json` | 890 |
| `financial_scenarios_20260904_120404.json` | 2.061 |
| `ia_readiness_report.json` | 621 |
| `human_checklist.md` | 424 |

**No copiado / ausente**: el baseline tenía además `deliveries/hotelsalentoreal_20260831/` (37 archivos
expandidos en disco). Esta corrida **no** produjo ese directorio, solo el ZIP. El contrato documentado
de `modules/delivery/delivery_packager.py:5-8` es `deliveries/{hotel_id}_{date}.zip` — la expansión del
baseline fue un paso manual de aquella fase, no una salida del empaquetador. Registrado en S-I5.

**Integridad**: el ZIP nuevo trae **38 archivos vs 37 del baseline**. El diferencial normalizado por
timestamps es exactamente uno: `ASSETS/v4_audit/site_presence_snapshot.json` — es decir, la deuda A2
cerrada por FASE-E viaja **dentro del entregable al cliente**, no solo en el árbol de trabajo.
