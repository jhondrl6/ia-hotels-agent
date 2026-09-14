# FASE-P1 · Tarea 1 — Research del estado actual (solo lectura, cero código modificado)

> **Método (L-V.2)**: cada afirmación se re-leyó en el artefacto, nada se heredó de las notas del plan.
> **Convención (R2.2)**: se citan símbolos y orden de flujo, nunca números de línea.
> **Fecha**: 2026-09-14 · **Plan**: TRIBUNAL-ENFORCEMENT-OBS-2026-09-11

---

## 1. Mapa del nudo técnico, confirmado símbolo por símbolo

| Símbolo | Qué hace hoy | Estado vs el plan |
|---------|--------------|-------------------|
| `judge.py :: TribunalJudge.evaluate` | Construye el acta con la clave literal `"reviewer_reports": []` y **ningún otro camino la escribe** — no hay método que la puebla en toda la clase | ✅ Confirmado (es inicialización fija del acta, no un residuo de rama condicional) |
| `judge.py :: _compute_verdict(clauses, evidence_tier, first_floor)` | Lee solo `clauses` (P6.1/P6.6 → `BLOQUEADO`; P6.3/P6.4 → `DEVOLVER-CORRECCIONES`), luego `first_floor["applied"]` → condicional, y exige `evidence_tier == "A"` **y** `T1_CERTIFIABLE_CLAUSES` en `PASS` para `APROBADO-PARA-ENTREGA` | ✅ Confirmado: no consume reportes de revisores. Su **docstring** sí promete "Finding CRITICAL de revisores → DEVOLVER-CORRECCIONES": el contrato documentado y el código divergen |
| `judge.py :: blocks_delivery_zip` + `BLOCKING_VERDICTS` | `frozenset({VERDICT_BLOCKED, VERDICT_RETURN})`; `acta is None` **no** bloquea (never-block) | ✅ Confirmado — y resuelve `D-T1.1` (ver §4) |
| `judge.py :: FIRST_FLOOR_TIERS` / `_apply_first_floor_rule` | `{"B", "C"}`; `reason` = `"evidence_tier X → sin restricción de primer piso"` cuando `X` no está en el set | ✅ Confirmado (AC-F4): en `B_PLUS` el acta declara "sin restricción" y el veredicto sale condicional igual, por el guard de Tier A |
| `judge.py :: _resolve_manifest` / `_read_evidence_tier` | Resuelve `deliveries_dir/<hotel_id>_*/MANIFEST.json` por glob ordenado con `st_mtime`; si no existe → `"C"` | ✅ Confirmado + **hecho nuevo §3.1** |
| `main.py` · bloque `FASE-T1: Tribunal Judge` | `judge.evaluate()` → `blocks_delivery_zip()` → `ActaWriter.write()`, todo dentro de un `try/except Exception` que en el `except` pone `tribunal_acta = None` y `_tribunal_blocks = False` | ✅ Confirmado: el Juez corre **antes** del packaging |
| `main.py` · condición de ZIP-skip en `FASE 7` | Un solo `if`: `(delivery_quality_report.status == "FAIL") or _claim_escalated or _tribunal_blocks` → `delivery_zip_path = None`; `else` → `packager.package()` | ✅ Confirmado (NR3 intacta: **una** ruta, tres causas) |
| `main.py` · bloque `FASE-T2/T4: Tribunal Reviewers (4 Bots)` | Los 4 revisores corren **después** del `package()`, cada uno en su propio `try/except Exception` con `[WARN] … never-block` | ✅ Confirmado: llegan tarde para el Juez y su fallo es silencioso por diseño |
| `delivery_packager.py :: package` | Escritura única con `zipfile.ZipFile(zip_path, 'w')` + `zf.writestr` para `README_DELIVERY.md`, `IMPLEMENTATION_ORDER.md` y `MANIFEST.json`; borra `zip_path`/`tmp_zip_path` en las rutas de error | ✅ Confirmado single-write **ZIP-only**: esos tres nombres no existen como archivos en disco |
| `asset_reviewer.py :: _resolve_delivery_dir` | Glob `deliveries_dir/*` por `st_mtime`; devuelve el primer directorio **que contenga** `MANIFEST.json`; si ninguno, **cae a `hotel_dirs[0]`** (que en régimen ZIP-only es el `.zip`) | ✅ Capa 1 de AC8 confirmada |
| `asset_reviewer.py :: _check_implementation_order` | `impl_order = delivery_dir / "IMPLEMENTATION_ORDER.md"`; `if not impl_order.exists(): return findings` | ✅ Capa 1 amplificada: sobre la ruta del `.zip` el `exists()` es falso y el chequeo **retorna vacío sin error** — no es "sin hallazgos", es lector que no leyó |
| `asset_reviewer.py :: _is_template_stub` | `non_empty_lines` cuenta **cualquier** línea no vacía que no empiece con `#` (incluidos `---` y boilerplate); solo declara stub si `non_empty_lines <= 3 and total_content <= 5` | ✅ Capa 2 de AC8 confirmada |
| `honesty_reviewer.py :: _extract_evidence_tier` | Prioridad `manifest.quality_metadata.evidence_tier` → `financial_scenarios.breakdown.evidence_tier` → `"UNKNOWN"` | ✅ Confirmado: existe el precedente de leer el tier **sin** depender del MANIFEST |
| `acta_writer.py` (render MD) | `reviewer_reports = acta.get("reviewer_reports", [])`; `if reviewer_reports:` …renderiza cada elemento como `- \`string\``; footer `*Generado por TribunalJudge v4.76.0*` | ✅ Confirmado (versión hardcodeada, P3-B) + **hecho nuevo §3.2** |

**Forma original prometida para `reviewer_reports`** (prompt del predecesor `05-prompt-inicio-sesion-fase-T1.md`):
una lista de **nombres de archivo** (`["revision_diagnostico.json", …]`). `acta_writer` la renderiza como
lista de strings. Es decir: el contrato heredado nunca transportó hallazgos ni severidades —
aun poblado, no permitiría decidir sobre él ni distinguir los tres estados de NR8.

---

## 2. §2.1 del plan maestro (Tier A inalcanzable) — **CONFIRMADO** en los tres eslabones

1. `judge.py :: _compute_verdict` → `APROBADO-PARA-ENTREGA` exige `evidence_tier == "A"` **y** `T1_CERTIFIABLE_CLAUSES = ("P6.1","P6.3","P6.4","P6.6")` en `PASS`. Confirmado literalmente.
2. `scenario_calculator.py :: _determine_evidence_tier` → devuelve `EvidenceTier.A` solo si `ga4_enabled and gsc_enabled and has_verified_data`; la rama siguiente (`has_verified_data and not (ga4_enabled and gsc_enabled)`) devuelve `EvidenceTier.B_PLUS`. Confirmado, con su comentario de origen "FASE-1: Sin GA4+GSC conectados, NUNCA devuelve A".
3. `main.py` · bloque `FASE-K` → `HotelFinancialData(... ga4_enabled=False, gsc_enabled=False)` **fijos**, y el resultado alimenta `financial_breakdown = _sc.calculate_breakdown(...)` dentro de un `try/except Exception` que solo imprime un warning. `ga4_available = ga4_client.is_available()` se calcula **después**, en el bloque de analítica, y `analytics_data["use_ga4"] = ga4_available`. Confirmado: hace falta **hoist** para propagar la disponibilidad real.

**Consecuencia obligatoria**: **Q5 es una decisión debida, no opcional** (el prompt la lista como no diferible; aquí se corrobora que el defecto existe).

**Agravante no registrado en el plan** (se mide en §3.1): en el régimen ZIP-only del pipeline real,
aun corrigiendo el cableado, `_read_evidence_tier` no ve MANIFEST → el Juez opera con `"C"`.
El tier del acta y el tier del `HotelFinancialData` son **dos hechos distintos** y ambos deben arreglarse
para que `APROBADO-PARA-ENTREGA` sea observable.

---

## 3. Hechos nuevos que el plan no tenía medidos

### 3.1 El acta no lee el tier que el pipeline ya escribió; lo lee de un artefacto que aún no existe

`_read_evidence_tier` depende de `MANIFEST.json`, pero `MANIFEST.json` lo escribe el `packager` **después** del Juez y solo dentro del ZIP. En el flujo real, por tanto, el Juez siempre cae en `"C"`. No es un "error de timing" incidental: es una dependencia estructural del resolutor.

Mientras tanto, `main.py` **sí** tiene el tier correcto antes del Juez: `_breakdown_dict['evidence_tier']` (derivado de `financial_breakdown.evidence_tier` en FASE-K) y lo serializa en `financial_scenarios_*.json` → clave `breakdown.evidence_tier`, en `v4_audit_dir`, **antes** del bloque FASE-T1. `packager._quality_metadata["evidence_tier"]` toma exactamente ese mismo valor, que es lo que aterriza en el MANIFEST.

- **Cura AC-F2**: que `_read_evidence_tier` lea `financial_scenarios_*.json → breakdown.evidence_tier` (mismo orden de prioridad que `_extract_evidence_tier`), con MANIFEST solo como fallback. Barato, sin reordenar el flujo.
- **Lectura L-SR3**: la divergencia `C` vs `B` no es un bug de lectura sino **dos emisores del mismo hecho** sin fuente única. Es el hallazgo §3.b `L-SR3` que el plan postergó: aplica a este AC y debe nombrarse en el contrato.

### 3.2 `reviewer_reports` vacío borra la sección entera del acta MD

`acta_writer` renderiza `## Reportes de Revisores` **solo si la lista no está vacía**. En el acta en Markdown, "no corrieron", "corrieron limpios" y "fallaron" son **indistinguibles**: el mismo documento. Es `DA-C3` (`vacío ≠ ausente`) en su forma más literal, y confirma que NR8 no puede cerrarse poblando la lista: exige cambiar la **forma** del dato (por revisor, con estado) y suprimir el `if`.

### 3.3 Dos emisores de `"asset_path":` — causa exacta de `test_barreda_un_solo_emisor_de_la_clave` en rojo

`tests/test_asset_path_clave_canonica.py :: TestDocumentacionDelContrato.test_barreda_un_solo_emisor_de_la_clave`
abarca `modules/**/*.py` y **afirma** `emisores == {"asset_generation/proposal_asset_alignment.py"}`.
Grep verificado: hoy emiten además `quality_gates/tribunal/asset_reviewer.py` (cinco claves `asset_path`
en sus hallazgos). La cura de D-V.1 sigue siendo test-only, pero el test no es decorativo: su docstring
declara que un segundo emisor es una segunda superficie del mismo hecho sin contrato. **El contrato del
P1 debe decir qué emite Bot 3** (una ruta de artefacto ya resuelta por el revisor, no un hecho nuevo),
y la whitelist de P3-B se registra con esa justificación, no como `xfail`.

---

## 4. Deuda y endosos del predecesor: estado verificado

| Ítem | Estado medido en P1 |
|------|---------------------|
| **D-V.3** (endurecer executor) | **Ejecutado**: `.agents/workflows/phased_project_executor.md` está en **v2.24.0** y su descripción ya nombra el gate del Paso 0 con `00-lecciones-capitalizadas.md` + `validate_lesson_capitalization.py` (`[7/7]`). R2.6/R2.7 siguen **sin verificador mecánico**: el propio executor dice "Ningún check de `run_all_validations.py` ni del pre-commit comprueba que `evidence/FASE-X/`…". Límite confirmado, no reabierto. |
| **Baseline R2.6 fuera del repo** | Confirmado por `.gitignore`: la regla `output/*/` excluye `output/FASE-D_salentoreal_post_guard/`. Sigue inejecutable en clon limpio → **límite declarado**, sin dueño de código en este plan. |
| **D-V.1** (barreda) | Causa exacta verificada (§3.3). Dueño **P3-B**, cura test-only + justificación en el contrato. |
| **Endoso de versión hardcodeada** (`acta_writer.py`) | Confirmado: `TribunalJudge v4.76.0` en el footer. Dueño **P3-B** (leer `VERSION.yaml`). |
| **`D-T1.1`** (hallazgo §3.b: "DEVOLVER-CORRECCIONES bloquea igual que BLOQUEADO, la política vive en un único punto") | **VIGENTE en código**: `BLOCKING_VERDICTS` incluye `VERDICT_RETURN` y el único consumidor es `blocks_delivery_zip`, llamado una vez en `main.py`. Por tanto **AC-D1 no define una consecuencia nueva**: registra por qué no se observó → la causa medida es que `_compute_verdict` nunca recibe los hallazgos, así que el veredicto salió condicional por gates + primer piso, nunca `DEVOLVER-CORRECCIONES`. |
| **`DA-C3`** (hallazgo §3.b: `vacío ≠ ausente`) | **NR8 lo subsume**, y con nombre propio: §3.2 muestra el colapso en el MD. Q6/AC-E0 lo citan. |
| **`L-SR3`** (hallazgo §3.b: una sola fuente de verdad para el estado de un servicio) | **Aplica**: es la causa estructural de AC-F2 (§3.1). Entra al contrato. |
| **`L-B4`** (hallazgo §3.b: dos planes pueden compartir el nombre de la carpeta de evidencia) | **Confirmado**: `evidence/` es raíz global y este plan lee `evidence/FASE-E2E/`, `evidence/FASE-VERIFY/`, `evidence/FASE-T1/`, `evidence/FASE-D/` escritos por otros planes. Cura: snapshot del baseline ajeno dentro de `evidence/FASE-P4/`. Solo es efecto si **P4 no se difiere** → se deja como cláusula condicional del brief de P4. |
| **Cola de 78 adyacentes sin evaluar (Q7)** | Sin efecto sobre los símbolos que este plan toca; P1 la **declara fuera de alcance** (razón en `decision-enforcement.md`), no la borra. |
| **"Verificador de conteos declarados en §4"** (deuda que llega del plan PASO0, con premisa corregida) | **Re-verificado y retirado**: el §4 de este `00-lecciones-capitalizadas.md` declara "19 lecciones" y el §2 tiene **exactamente 19 filas** (conteo manual en P1). No hay caso real en este plan → se retira el ítem con su medición, en lugar de heredarlo. |
| **Existencia de `evidence/FASE-P1/`** | No existía al abrir la sesión; se crea con este entregable. |

---

## 5. Cero modificaciones de código

Confirmado al cerrar la tarea: `git status` solo muestra archivos de plan y evidencia (`evidence/FASE-P1/`,
`.opencode/plans/TRIBUNAL-ENFORCEMENT-OBS-2026-09-11/`). Ningún `.py` tocado.
