# Evidencia — FASE-RELEASE-4.75.0 (2026-09-04)

Plan: `ESTABILIZACION-PRE-TRIBUNAL-2026-09-03` · fase 11/11 (cierre documental).
Sesión propia **DIRECTA** (el prompt la declaraba delegable; se ejecutó sin subagente para verificar cada
afirmación contra el árbol — lección L-H2 de FASE-H).

## Pareja pre/post (regla R2.3 del executor v2.19.0)

RELEASE no cambió código, pero **sí reescribió 9 documentos que varios candados leen**, así que corre la
pareja completa.

| Validador | PRE (HEAD `580ec9c`, antes de editar) | POST (con los documentos de RELEASE) |
|-----------|----------------------------------------|---------------------------------------|
| `run_all_validations.py --quick` | `rel_baseline_validations_quick_PRE.txt` → **8/8** | `rel_validations_quick_POST.txt` → **8/8** |
| `validate_agents_md.py` | `rel_baseline_agents_md_PRE.txt` → **5 PASS / 1 FAIL** (`test_count` 3689 vs 3932, 6,2 %) | `rel_validate_agents_md_POST.txt` → **6 PASS / 0 FAIL** (3934 vs 3932, 0,1 %) |
| `validate_document_integration.py` | `rel_baseline_doc_integration_PRE.txt` → sin errores | `rel_validate_doc_integration_POST.txt` → sin errores |
| Batería de contratos A+B+C+D+delivery | 180/0 (registrada por HOTFIX en `evidence/FASE-HOTFIX-PRE-RELEASE/faseHotfix_suites.txt`) | `rel_suites_POST.txt` → **180 passed / 0 failed** (3,67 s) |
| Suite dirigida `quality_gates` + `asset_generation` | 950/2 (registrada por HOTFIX) | `rel_suites_POST.txt` → **950 passed / 2 skipped** (5,90 s) |

**Delta: 0 regresiones.** El único cambio de estado es `test_count` FAIL → PASS: eso **es** S11/S-I6 cerrado.

## Archivos de evidencia

| Archivo | Contenido |
|---------|-----------|
| `rel_baseline_validations_quick_PRE.txt` | `run_all_validations.py --quick` antes de tocar nada (8/8) |
| `rel_baseline_agents_md_PRE.txt` | `validate_agents_md.py` antes — el FAIL de `test_count` con sus 6 checks en JSON |
| `rel_baseline_doc_integration_PRE.txt` | `validate_document_integration.py` antes |
| `rel_log_phase_completion.txt` | registro `FASE-RELEASE-4.75.0` en REGISTRY → **Version Sync Gate PASSED (4.75.0)** |
| `rel_sync_versions.txt` | dos pasadas de `sync_versions.py`: la primera deja `AGENTS.md` «in sync» (el defecto hallado) y la segunda, tras corregir el patrón, lo **actualiza** |
| `rel_regenerate_domain_primer.txt` | `doctor.py --regenerate-domain-primer` → 197 archivos Python, 375 clases, 25 módulos |
| `rel_doctor_status.txt` | `doctor.py --status` → `SYSTEM_STATUS.md` regenerado (paso E6) |
| `rel_validations_quick_POST.txt` | `--quick` al cierre (8/8) |
| `rel_validate_agents_md_POST.txt` | `validate_agents_md.py` al cierre (6/6) |
| `rel_validate_doc_integration_POST.txt` | `validate_document_integration.py` al cierre |
| `rel_suites_POST.txt` | comando explícito + resultado de la batería de contratos y de la suite dirigida (L-HF2: ninguna cifra sin su comando) |
| `rel_qmind_write_back.txt` | refresco de la fuente del plan con **L-HF1**, con su efecto colateral sin resolver |
| `rel_conteos.txt` | los conteos de tests medidos por la fase, con su partición (que **suma** el total) |
| `rel_git_show_stat_release_commit.txt` | `git show --stat 082c9e1` — el commit de release (12 archivos, +343/−51) |

**Observación del pre-commit** (`version-consistency`, paso 2/3): reporta **«Ultima fase: FASE-G»** aunque
`docs/contributing/REGISTRY.md` ya contiene `FASE-RELEASE-4.75.0` (y HOTFIX, I y VERIFY). El check da ✅ y no
bloquea, pero **lee un marcador distinto del encabezado `## FASE-…`**, así que su lectura de «última fase» no
refleja lo que la fase escribió. No es de RELEASE corregirlo (es código del checker, y aquí no se toca
código) ⟹ queda registrado como indicador de fase engañoso, misma clase que S-I8.

## Lo que la fase encontró y corrigió en la causa raíz

`scripts/sync_config.yaml` → regla `agents_version_comment`:

```
patrón  antes: '<!--\s*agents_version:\s*[\d.]+\s*\|'   ← no casa con «v4.74.1»
plantilla antes: '<!-- agents_version: {version} |'     ← emitiría sin «v»
patrón  ahora: '<!--\s*agents_version:\s*v?[\d.]+\s*\|'
plantilla ahora: '<!-- agents_version: v{version} |'
```

Por qué importaba: `validate_document_integration.py` **exige** el prefijo `v` en esa cabecera
(«AGENTS.md: version … missing 'v' prefix»), así que el patrón del sync era incompatible con el criterio de
su propio validador. La regla nunca disparaba y `sync_versions.py` respondía **«in sync»** release tras
release mientras `AGENTS.md:1` seguía en la versión anterior. Se corrigió el **patrón**, no la cabecera a
mano (editar a mano la habría vuelto a romper en la próxima release, y `09` prohíbe fijar versiones fuera
del flujo de sync).

## Alcance: lo que esta fase NO hizo

- **No re-ejecutó la suite ancha** (`python -m pytest tests/`). S-H15/S-H16/S-H17/S-I8 **siguen abiertos**
  por eso. El alcance del prompt declara **«Comandos largos: 0»**, así que correrla habría excedido el
  alcance, no cumplido el criterio. Las cifras de «0 regresiones» valen sobre la ventana medida arriba y
  **no** deben leerse como «los 3.934 tests pasan».
- **No tocó** `S-HF1` (AC10), la mitad estructural de `S-C3` (P12) ni `S-I1` (NR2 ❌): criterio de negocio
  cuyo dueño es el **tribunal** (DA-V5). Se publicaron **como ⚠️ y ❌**, no como verde.
- **No editó** `.env` (V12 es decisión OPS; `09` §Nota OPS).

## Iteraciones

**≈65 llamadas de herramienta / ≤25 ⟹ INCUMPLIDO ≈2,6×** — auto-reporte en unidad `tool_use`, declarado.
`evidence/FASE-D/measure_iterations.py` sigue sin ser ejecutable bajo esta política de permisos
**quinto caso consecutivo** (H, I, VERIFY, HOTFIX, RELEASE) ⟹ R2.1 del executor v2.19.0 quedó escrita en
la sesión anterior y esta volvió a incumplirla por la misma causa: no hay instrumento, hay convención.

## Pendencia abierta al cerrar → **RESUELTA el mismo día**

El refresco de QMind creó una fuente **nueva** (`01a06ebb-…`) porque el conector no expone actualización ni
borrado. La fuente de VERIFY (`01a06dae-…`, 62 chunks, **sin L-HF1**) quedó recuperable en el notebook
`iah-cli-lecciones` con el **mismo título**, lo que rompía la regla «una fuente por plan» y dejaba una
versión caduca que un `Paso 0` futuro podía leer (41 lecciones donde hay 43).

**El borrado lo ejecutaste tú desde la UI y está verificado**: `list_sources` pasó de **45 a 44** fuentes,
`01a06dae-…` ya no figura, y un `retrieve` a nivel notebook sobre L-HF1 devuelve 5 chunks **todos** de
`01a06ebb-…` (top score 0,986). Detalle en `rel_qmind_write_back.txt`.
