# 06 — Checklist de Implementación: TRIBUNAL-ENFORCEMENT-OBS-2026-09-11

> **Regla**: Una fase se marca ✅ solo cuando TODOS sus criterios de completitud pasan.
> **Fuente de estado**: este archivo + `dependencias-fases.md`.
> **Regla de medición (L-R.1, R2.1/D-V2.1)**: la celda `Iteraciones` debe declarar unidad, método y corte real. Intentar `evidence/FASE-D/measure_iterations.py` solo si el transcript es accesible con los permisos existentes; no eludir una denegación. Si no se puede medir, registrar el impedimento y un **auto-reporte explícito**, nunca presentarlo como medición ni como cumplimiento estimado. El corte en commit se usa **solo si el commit fue autorizado**; en otro caso registrar el corte de sesión sin inventar un hash. Una celda vacía no cierra una fase.
> **P5/P6: presupuesto FUERA DE SERVICIO** bajo R2.1/D-V2.1 por falta de calibración comparable; no estimar duración, iteraciones ni cumplimiento. R3: **máximo 4 tareas y 0 comandos largos por fase**. NR1/NR7 y el cierre documental pertenecen a las tareas declaradas, no son tareas adicionales encubiertas.
> **Alcance de esta actualización**: planificación documental, no ejecución. No completa P5/P6 ni autoriza código, commits, publicación, rotación, acciones externas o nueva evidencia real.

## Estado Global

**9/9 fases cerradas — plan COMPLETADO** (sin contar el predecesor). P4 permanece cerrada, **P5 cerrada el 2026-09-15** con remediación post-auditoría el mismo día, **P6 cerrada el 2026-09-15** con los 5 AC-G verificados y los 3 caminos causales con NR7, **FASE-VERIFY cerrada el 2026-09-15** con la matriz de certificación de los 25 ACs (RE-V/CIT/CON), 6 cruces cross-fase, 6 greps residuales y triaje de Seguimientos, y **FASE-RELEASE-4.77.0 cerrada el 2026-09-15** (bump + sync + CHANGELOG + GUIA + write-back QMind + archivado R2.5 + tag `v4.77.0`). 🔁 **D-AJUST.4 (2026-09-15) reabrió FASE-VERIFY**: la fase sí creó sesión (DIRECTO, no delegable, `05-prompt-inicio-sesion-fase-VERIFY.md`) y produjo la matriz de certificación de los 25 ACs; **AC-V1 quedó reducido a citar esa matriz** dentro de RELEASE. La sustitución que había decidido P1 se revirtió por tres mediciones posteriores a su cierre (P4 se corrió, el plan llegó a 5 fases de implementación, y dos auto-certificaciones de fase —P5 y P6— resultaron falsas en auditoría externa); rationale completo en `dependencias-fases.md` §D-AJUST.4 y en el `10-analisis`.

| # | Fase | Estado | Fecha inicio | Fecha cierre | Iteraciones (ids + tool_use, método y corte declarado) | Notas |
|---|------|--------|-------------|-------------|-------------|-------|
| 0 | Precondición: FASE-RELEASE-4.76.0 (predecesor) | ✅ Completada | 2026-09-11 | 2026-09-11 | n/a (predecesor, sin medición) | v4.76.0 publicada (en `origin/master` como `3bdc14e`; `bd2bf57` es su duplicado pre-rebase) + archivado R2.5 — puerta de P1 abierta. Tag `v4.76.0` creado y empujado a origin 2026-09-14 |
| 1 | **FASE-P1** | ✅ **Cerrada** | 2026-09-14 | 2026-09-14 | **≈30 `ids` / ≈58 `tool_use`** — auto-reporte con unidad declarada (D-V2.1: el instrumento no alcanza el transcript bajo el cliente actual); corte = commit de cierre. **Presupuesto de 30 superado**; causa y cura en L-P1.4 de `10-analisis` | Q1=sí · Q1b=escalar (sin reintento) · Q2=O1-cuarentena · Q2b=ambas capas · Q3=P3→P2 · Q4=el hotel (T3a externa, con líneas rojas) · Q5=a (par con AC-F2) · Q6=**4** estados · Q7=hereda `GATE_BLOCKING_ENABLED` · **FASE-VERIFY no activa** (🔁 reabierta por D-AJUST.4). Contrato: `evidence/FASE-P1/decision-enforcement.md` |
| 3a | **FASE-P3-A** | ✅ **Cerrada** | 2026-09-14 | 2026-09-14 | **106 `ids` / 126 `tool_use`** — medido con `evidence/FASE-D/measure_iterations.py`, corte = commit de código `0d4d072`. **El instrumento SÍ alcanzó el transcript → D-V2.1 NO se reprodujo.** Presupuesto de 20 superado → causa y cura en L-P3A.1 de `10-analisis` | Detección y fidelidad: AC-F1 (dos capas, ZIP-aware) + AC-F2 (fuente del tier) + AC-F4 (`B+`). R2.7: 4.109→4.130 = +21 = tests nuevos; 4 pares NR7 verde/rojo |
| 3b | **FASE-P3-B** | ✅ **Cerrada** | 2026-09-14 | 2026-09-14 | **120 `ids` / 120 `tool_use`** — medido con `evidence/FASE-D/measure_iterations.py`, corte = commit de código `bad0a5e`. **El instrumento SÍ alcanzó el transcript (segunda fase seguida: D-V2.1 no se reprodujo).** **Presupuesto de 25 superado** (tercera fase seguida) → causa y cura en L-P3B.1 de `10-analisis` | Cableado y test: **AC-F5 ejecutado** (Q5=a — hoist de `ga4_available`/`gsc_available` al `HotelFinancialData` de FASE-K, toca `main.py`), AC-F3 (whitelist barreda test-only, se cierra **D-V.1**) y AC-F6 (versión del acta desde `VERSION.yaml`). R2.7: 4.130→4.153 = **+23** íntegros en `passed` (4.091→4.115 = +24: los 23 nuevos **más** `test_barreda…` que migró de rojo a verde), 3 fallos restantes todos ajenos → **0 regresiones**. **6 pares NR7** verde/rojo. `--quick` 9/9 |
| 2 | **FASE-P2** | ✅ **Cerrada** | 2026-09-14 | 2026-09-14 | **≈65 `tool_use` / ≈60 `ids`** — auto-reporte con unidad declarada (**D-V2.1 se reprodujo**: el instrumento exige el transcript del cliente, que vive fuera del workspace y el acceso lo negó el clasificador); corte = commit de código `df60c24`. **Presupuesto de 55 superado = cuarta fase consecutiva** → L-P2.4 | **O1-cuarentena**: `write()`/`publish()`/`suppress()` con el rename gateado por el veredicto, `reviewer_reports` tipado y poblado, `_compute_verdict` con la matriz §2.1 en su orden, AC-E0…AC-E5. **8 pares NR7** con rojo real, R2.7 **4.153→4.181 (+28)**, 0 regresiones, `--quick` 9/9. **Cero re-decisiones del contrato**: las cuatro consecuencias que la medición obligó a nombrar son DA-P2.1…P2.4 en `10-analisis`. Medición destacada: **el ZIP contenía el acta** → el enunciado de DA-P1.4 era un círculo y el acta deja de viajar con el cliente |
| 4 | FASE-P4 | ✅ **Cerrada 2026-09-14** | 2026-09-14 | 2026-09-14 | ≈52 `tool_use` (auto-reporte, unidad declarada — D-V2.1 se reprodujo) | **Se corrió, no se difirió**: el disparador «no hay dato con fuente» **midió falso** (6 de 6 hoteles del warehouse resuelven por el fallback `observations.json` del cargador). Corrida real con **Hotel Don Alfonso** con consentimiento y frescura registrados antes (`consentimiento-donalfonso.md`), 3 min de reloj. **ZIP suprimido por veredicto** (`BLOQUEADO`), `reviewer_reports` de longitud 4; **AC-F2/AC-F4 observados en vivo**. Techo `B_PLUS`: analítica del hotel, no cableado. **Tier A NO observado**. También bloqueaba coherence: no prueba por sí sola el contrafactual de AC-G5. 9 hallazgos con dueño, cero código de producción tocado. Detalle: `evidence/FASE-P4/informe-observacion.md` |
| 5 | **FASE-P5 — Seguridad y privacidad** | ✅ **Cerrada 2026-09-15** (técnico) | 2026-09-15 | 2026-09-15 | presupuesto **FUERA DE SERVICIO** (R2.1/D-V2.1, sin estimación); medida real auto-reportada con unidad declarada: **1 commit de ejecución (`b25b63a`) + 1 de remediación, corte = HEAD al cerrar**; el instrumento no alcanza el transcript (D-V2.1 reproducido, igual que P2). Celda antes vacía → se cierra en la remediación (L-P5.3) | AC-S1 ✅ (key a header `x-goog-api-key`, `_sanitize_text`/`_sanitize_error`, 11 tests, par NR7); AC-S2 ✅ **remendado** (el escaneo staged estaba muerto por NameError tragado — L-T2C.2 en el propio checker; alcance tracked+staged con sniff NUL, estados NR8 reales, `NO_CUBIERTO` bloqueante); AC-S3/S4 ✅ inventario + puerta con dueño. **Nuevo check `[5/10]` de material de cliente separado del de claves** (`config/client_material_policy.yaml`, 1 grandfathered con dueño y pendencia AC-S4). NR1: 4.145→**4.155 (+10)**, `--quick` **10/10**. **Puerta AC-S4: ✅ DESBLOQUEADA el 2026-09-15** por el criterio de cierre "contención verificable: key ya rotada" (declaración del operador, verificada en `evidence/FASE-P5/AC-S3-S4-inventario-superficie.md` §AC-S4 + prevención en la captura con commit 48a242b). **Filas abiertas no bloqueantes**: confirmación de rotación de la key Gemini local (riesgo local) y disposición de datos con cliente → las hereda el triaje de FASE-VERIFY T4. Evidencia: `evidence/FASE-P5/REMEDIACION-auditoria-2026-09-15.md` |
| 6 | **FASE-P6 — Generación y validación multi-hotel** | ✅ **Cerrada 2026-09-15** | 2026-09-15 | 2026-09-15 | presupuesto **FUERA DE SERVICIO** (R2.1/D-V2.1); medida real auto-reportada con unidad declarada; D-V2.1 reproducido | AC-G1 ✅ (asset_zip_paths + unknown assets), AC-G2 ✅ (onboarding fallback independiente), AC-G3 ✅ (SHA256/member_count del .zip.tmp), AC-G4 ✅ (matriz offline ≥3 perfiles), AC-G5 ✅ (3 caminos causales con NR7). **NR1 4.169→4.189 (+20)**, 0 regresiones, 5 pares NR7. Archivos producción: `main.py`, `delivery_packager.py`, `asset_responsibility_contract.py`, `acta_writer.py`. Cero cambios en `judge.py` |
| — | FASE-VERIFY | ✅ **Cerrada 2026-09-15** | 2026-09-15 | 2026-09-15 | auto-reporte con unidad declarada (D-V2.1 reproducido: transcript fuera del workspace); corte = HEAD al cerrar | **DIRECTO, no delegable.** Matriz de certificación de los **25 ACs** con nivel RE-V/CIT/CON por fila (`evidence/FASE-VERIFY/MATRIZ-CERTIFICACION.md`), 3 filas CIT re-medidas (11 tests pasaron), tabla de 6 cruces cross-fase (`evidence/FASE-VERIFY/T2-crosses.md`: 5 coherentes + 1 incoherente — `google_places_client._save_cache` sin redacción), 6 greps residuales con salida (`evidence/FASE-VERIFY/T3-greps.md`), y triaje de Seguimientos en 3 categorías (`evidence/FASE-VERIFY/T4-triaje.md`: 0 bloqueantes, 5 límite declarado, 9 plan sucesor). **2 hallazgos CON**: CON-1 (documentos del plan citan `GATE_ENFORCEMENT_ENABLED` que no existe en código — solo `GATE_BLOCKING_ENABLED`), CON-2 (cláusulas P6.2/P6.5 dicen NOT_EVALUABLE pese a que los revisores corrieron). **4 lecciones**: L-VERIFY.1–L-VERIFY.4. **No tocó código ni corrió `v4complete`** |
| 7 | FASE-RELEASE-4.77.0 | ✅ **Cerrada 2026-09-15** | 2026-09-15 | 2026-09-15 | **≈25 `tool_use` — auto-reporte con unidad declarada** (D-V2.1 reproducida, quinta sesión seguida: el transcript está fuera del workspace); corte = commit único de cierre | Cierre documental: AC-V1 = **verificar y citar** la matriz de VERIFY (25 filas ✅, ningún `—`, ningún ❌ remediado en RELEASE); bump 4.77.0 + sync 6 archivos + CHANGELOG + GUIA + AGENTS (4.233 canónicas); CON-1/C8 cerrado como corrección documental anotada; write-back QMind antes del archivado; plan archivado (R2.5) + diff `--fix` revisado a mano; tag `v4.77.0` creado en el cierre |

---

## Checklist por Fase

### Precondición — FASE-RELEASE-4.76.0 del predecesor

- [x] VERSION.yaml = 4.76.0 y `version_consistency_checker.py` pasa (hook pre-commit `3bdc14e`, 5/5 en verde)
- [x] Plan TRIBUNAL-OFFLINE-2026-09-09 archivado en `Archives/` (R2.5, 12 renombres, `--quick` 8/8 post-archivado)
- [x] Endosos D-V.1 (whitelist barreda) y D-V.3 (executor) ejecutados o explícitamente reasignados a este plan
  - D-V.3 **ejecutado**: executor v2.20.0 → v2.21.0 con R2.6 y R2.7. Ninguna de las dos tiene verificador
    mecánico todavía → esa parte queda **reasignada a P1** (ver §Deuda de proceso).
  - D-V.1 **reasignado**: la whitelist del emisor barreda es FASE-P3-B; `test_barreda_un_solo_emisor_de_la_clave`
    sigue en rojo y v4.76.0 se publicó así, con la limitación declarada.

### FASE-P1 — Decisión y contrato ✅ (cerrada 2026-09-14)

- [x] `evidence/FASE-P1/research-estado.md` con mapa confirmado símbolo-por-símbolo (R2.2) — 14 símbolos, más tres hechos nuevos que el plan no tenía (§3.1 el acta lee un tier de un `MANIFEST.json` que aún no existe; §3.2 `if reviewer_reports:` borra la sección del MD; §3.3 los dos emisores de `asset_path`)
- [x] §2.1 del plan maestro **CONFIRMADO con evidencia** en los tres eslabones (`_compute_verdict` → `_determine_evidence_tier` → banderas del bloque FASE-K); no hubo que refutar, pero sí **agravar**: propagar banderas sin AC-F2 es invisible → DA-P1.8
- [x] Q1 (¿enforcement?) = **sí**; Q1b (consecuencia aguas abajo del bloqueo) = **escalar**: ZIP suprimido + `corrective_actions` + humano decide, **sin reintento automático y sin entrega parcial**
- [x] Q2 (ordenamiento) = **O1-cuarentena** (decisión en el *publish*, no en el *write*); Q2b (AC8) = **las dos capas**, con raíz común a AC-F2 reconocida (DA-P1.5)
- [x] Q3 (secuenciación) = **P3-A → P3-B → P2 → P4**; Q4 (hotel + T3a) = **el hotel por contacto directo del operador**, jerarquía Salento Real → Don Alfonso/Luxor → Zi-One, con tres líneas rojas (el agente jamás llena el YAML; nada de datos plausibles para destrabar; consentimiento y frescura)
- [x] Q5 = **(a) propagar banderas, como par inseparable con AC-F2**; Q6 = **cuatro estados** (`OK_NO_FINDINGS`/`ARTIFACT_MISSING`/`READER_FAILED`/`NOT_RUN`), no tres — el tri-estado del plan omitía el que la corrida real ya exhibe
- [x] **Q7** (nace de la verificación pedida): el tribunal **no heredaba** `GATE_BLOCKING_ENABLED` (medido) → se decide **heredarlo** + el acta declara `enforcement.suppressed_by_operator` (escape honesto, no silencioso)
- [x] `evidence/FASE-P1/decision-enforcement.md` con contrato + rationale (formato DA-P1.1…DA-P1.9), incluidas las secciones **"Consecuencia del bloqueo"** (§3) y **"Cuatro estados de revisores"** (§4) → **AC-D1 cumplido**
- [x] ACs finales con artefacto + clave (R2.4) fijados en `01-plan-maestro.md` §6: nacen **AC-E4** (knob), **AC-E5** (consecuencia) y **AC-F6** (versión del acta); ningún AC de detección/bloqueo sin su verificación NR7 escrita
- [x] Decisión de §Deuda de proceso: **9 ítems quedan como límite declarado** (R2.6/R2.7 sin verificador, baseline R2.6 fuera del repo, `validate_plan_closure.py` 1/8, `Version actual` del REGISTRY, reescrito ciego de `--fix`, regex de `version_consistency_checker.py`, L-R.1 aplicada, normalización del flaky, cola de 78 adyacentes) y **1 cerrado por decisión**: Tier A inalcanzable → Q5=a. **El "verificador de conteos declarados en §4" se RETIRA con evidencia**: el `00-` de este plan declara 19 lecciones y tiene 19 filas; la premisa no se reproduce
- [x] **Decisión FASE-VERIFY cerrada** en `dependencias-fases.md`: **NO activa**; el criterio 2 (E2E) no es garantizable desde la ingeniería; AC-V1 de RELEASE ejecuta el patrón anclado al par NR7 por fase → **[🔁 reabierta el 2026-09-15 por D-AJUST.4: el criterio 2 se cumplió al correrse P4, el plan llegó a 5 fases de implementación y AC-V1 no cabía en RELEASE — ver §D-AJUST.4 en `dependencias-fases.md`]**
- [x] **Creado `05-prompt-inicio-sesion-fase-P2.md`** con O1-cuarentena, la matriz vinculante y el "no re-decidir" de Q1b/Q2/Q5/Q6/Q7
- [x] Escenario Q5=(c) / T3a: **no disparó** (Q5=a). T3a queda **asignada con disparador pre-registrado**, no "en espera": si al iniciar P4 no hay dato con fuente, se aplica §Cierre válido sin P4 sin reabrir decisión
- [x] Resolución de §3.b de `00-lecciones-capitalizadas.md`: `D-T1.1` **vigente** (AC-D1 registra la causa de no observación, no define una política nueva); `L-SR3` **capitalizado** como causa estructural de AC-F2; `DA-C3` **subsumido** por Q6 con nombre; `L-B4` **curado** con snapshot en AC-O2; cola de 78 **fuera de alcance con razón**
- [x] `06-checklist` + `dependencias-fases` actualizados con lo decidido
- [x] `10-analisis-post-implementacion.md` y `09-documentacion-post-proyecto.md` creados — **la estructura la creó la sesión de ajuste 2026-09-14** (eran deudores de la Etapa 1); P1 los rellena en su Post-Ejecución
- [x] `log_phase_completion.py --fase FASE-P1 --desc "…" --check-manual-docs` ejecutado **sin `--release`** → `(R) Fase registrada exitosamente` en `docs/contributing/REGISTRY.md`. El recordatorio de `CHANGELOG`/`GUIA_TECNICA` queda para RELEASE **por diseño de este plan**: el acumulador es `09-documentacion-post-proyecto.md` §E, que ya lista los cinco puntos que 4.77.0 debe publicar
- [x] `run_all_validations.py --quick` → **9/9 TOTAL PASS** (2026-09-14 14:00). Incluidos los dos checks que esta sesión ponía a prueba: `[8/9] Plan Citations` (**743 citas históricas, 0 nuevas, 0 crecimientos** — P1 no introdujo números de línea) y `[9/9] Lesson Capitalization` (forma y trazabilidad del `00-` verificadas; **no** verifica pertinencia, declarado por el propio check)
- [x] **Iteraciones de P1 medidas y escritas** — auto-reporte con unidad declarada (D-V2.1), celda rellenada en Estado Global; la celda ya no está en `—`
- [x] **NO modificó código de producción** — verificado con `git status`: `NINGUN .py modificado`; los 10 caminos tocados son `.opencode/plans/<PLAN>/*` (7), `evidence/FASE-P1/` (2 nuevos) y `docs/contributing/REGISTRY.md`
- [x] Commit de cierre de fase → **`fd8e4f4`** (13 archivos, +1.045/−229; hooks 7/7). La higiene que este commit exigía — regenerar `.opencode/LECCIONES-INDEX.md` y `lecciones_index.json` tras editar los `.md` del plan — viaja en el commit siguiente, que es el que estás leyendo

### FASE-P3-A — Detección y fidelidad del acta ✅ (cerrada 2026-09-14 — primera fase de ejecución, orden DA-P1.3)

- [x] **AC-F1 capa 1**: `EMPTY_DELIVERY_TEMPLATE` dispara en régimen ZIP-only leyendo el miembro **desde el ZIP** (`zipfile`), sin resolver un directorio fantasma; si el miembro falta → `ARTIFACT_MISSING`, si el ZIP es ilegible → `READER_FAILED` (prohibido "vacío sin error") — **hecho**: `_resolve_delivery_dir` ya no devuelve un `.zip` como `Path`; nuevo `_resolve_delivery_zip` + `_read_implementation_order` que lee dir-first y luego `zipfile.ZipFile(...).read("IMPLEMENTATION_ORDER.md")`, con `KeyError→ARTIFACT_MISSING`, `BadZipFile/OSError/UnicodeDecodeError→READER_FAILED`. Los 4 estados viven en `self._impl_order_check` y se publican en el reporte (NR8)
- [x] **AC-F1 capa 2**: `_is_template_stub()` con criterio **estructural** (≥1 sección declarada y todas con 0 líneas de contenido real, excluyendo `---` y el boilerplate Fecha/Score/footer; ó 0 bytes) en lugar del conteo `non_empty_lines <= 3` — **hecho**: cuenta secciones (`# `/`## `, `###` cuenta como contenido) y `sections_with_content==0 ⇔ stub`; regex `_IMPL_ORDER_BOILERPLATE` excluye `---`/Fecha/Score/footer/`Los archivos (CORE|GEO) son`
- [x] **NR7 sobre AC-F1 — dos mutaciones, una por capa**: desactivar la lectura del ZIP → rojo; volver al conteo de líneas sobre el stub real → rojo. Par de salidas en `evidence/FASE-P3-A/` (AC8 ya falló por un test que "pasaba" sin ejercitar el régimen real — L-V.1) — **hecho**: `evidence/FASE-P3-A/NR7-AC-F1-capa1.txt` y `NR7-AC-F1-capa2.txt` (verde rc=0 / rojo rc=1 cada uno), ejecutados por `nr7_mutation_checks.py`, árbol restaurado
- [x] **AC-F2**: `evidence_tier` del acta == el del pipeline, leído de `financial_scenarios_*.json → breakdown.evidence_tier` (fuente pre-packaging), con MANIFEST solo como fallback. Precedente: `_extract_evidence_tier` — **hecho**: `_read_evidence_tier` reescrito (scenarios-first vía `FINANCIAL_SCENARIOS_PATTERN`, MANIFEST fallback, `"C"` por defecto); sonda sobre el artefacto real FASE-I lee `"B"` == pipeline `"B"`
- [x] **AC-F2 y AC-F1 se implementan como un mismo cambio de resolutor** (raíz común: un lector escrito contra un layout descomprimido). `L-SR3`: una sola fuente de verdad para el hecho "tier" — **hecho**: las dos víctimas de DA-P1.5 (`_resolve_delivery_dir` de Bot 3 y `_read_evidence_tier` del Juez) se corrigieron contra el régimen ZIP-only real; el contrato no exigía una única función literal sino una única fuente de verdad por hecho
- [x] **AC-F4**: `first_floor_rule.reason` coherente con el veredicto en `B_PLUS` — **hecho**: `FIRST_FLOOR_TIERS` extendido a `{"B","B+","C"}` (la clave es `"B+"`, que es como serializa `EvidenceTier.B_PLUS`); `reason` dice "evidence_tier B+ → máximo condicional" y el veredicto CONDITIONAL no miente
- [x] **Iteraciones de P3-A medidas y escritas** (unidad declarada, D-V2.1) — bloquea el ✅ (L-R.1) — **hecho**: 106 `ids` / 126 `tool_use` con el instrumento (D-V2.1 NO se reprodujo); celda de Estado Global rellenada; presupuesto 20 superado → L-P3A.1
- [x] `run_all_validations.py --quick` TOTAL PASS — **hecho**: 9/9 (743 citas históricas, 0 nuevas, 0 crecimientos)

### FASE-P3-B — Cableado y test ✅ (cerrada 2026-09-14 — presupuesto 25: Q5=a disparó AC-F5)

- [x] **AC-F5**: hoist de `ga4_available`/`gsc_available` por encima del bloque FASE-K y propagación al `HotelFinancialData` — la regla FASE-1 de `_determine_evidence_tier` queda intacta; lo que cambia es que su input deja de ser falso — **hecho**: `main.py` calcula la disponibilidad al nivel del cuerpo de `run_v4_complete_mode` (antes del `try` de FASE-K) y el constructor recibe `ga4_enabled=ga4_available, gsc_enabled=gsc_available` en lugar de dos literales `False`. **Medido y corregido sobre la marcha**: GSC no tenía valor real que hoistear — nadie lo computaba en `v4complete` — así que se calcula con `GoogleSearchConsoleClient().is_configured()` (constante en el mismo sentido que el `is_available()` de GA4: credenciales + propiedad, sin red). Propagar solo GA4 habría dejado el Tier A tan inalcanzable como antes (`constancia-Q5.md` §4)
- [x] **AC-F5 · cuatro tests**: tier `A` con analítica / `B_PLUS` sin ella / **sin `NameError` en régimen `generate_proposal=False`** (ampliar `tests/quality_gates/tribunal/test_s_e2_generate_proposal_false.py`, que ya cubre el hoist S-E2) / delta NR1 con par pre/post. L-T2C.2: el `except Exception` de FASE-K enmascara el fallo y degrada el tier en silencio — **hecho**: `test_p3b_analytics_flags_wiring.py` (14 tests: 10 de cableado por AST + 1 del MANIFEST + 5 conductuales de la regla FASE-1) y `TestAnalyticsFlagsReachableWithoutProposal` en el archivo S-E2 ampliado (5 tests). El cuarto requerimiento (delta NR1) en `nr1_delta_r2_7.md`. L-T2C.2 queda verificada **por AST**, no por lectura: `test_hoist_fuera_de_todo_except_ancho` y `test_hoist_alcanzable_donde_lo_es_fase_k`, ambas con su mutación (`NR7-AC-F5-b.txt`, `NR7-AC-F5-c.txt`)
- [x] **AC-F5 · CHANGELOG**: el cambio de tier en corridas reales es comportamiento visible → se declara, no entra en silencio — **hecho**: redactado y acumulado en `09-documentacion-post-proyecto.md` §B/§E como obligación de **RELEASE** (4.77.0), que es el dueño del `CHANGELOG.md` según el flujo documental del repo; P3-B no edita documentos versionados. La sonda `verify_probe_ac_f5_techo_tier.py` deja escrito **qué** se declara: en el baseline real de FASE-I el tier sigue siendo `B` con las cuatro combinaciones de banderas, porque su techo lo pone la ausencia de dato verificado, no el cableado
- [x] **AC-F3**: whitelist barreda test-only, **justificada** por el contrato del emisor de `asset_path` (§5.1 de `decision-enforcement.md`), no como `xfail` — **hecho**: `EMISORES_LEGITIMOS`/`CONSUMIDORES_LEGITIMOS` en `tests/test_asset_path_clave_canonica.py`, con la igualdad de conjuntos intacta (barra viva: `NR7-AC-F3-a.txt` retira la autorización → rojo; `NR7-AC-F3-b.txt` hace aparecer un emisor no contratado → rojo). **Cero cambios en el emisor** (`asset_reviewer.py` fuera del commit, verificado con `git show --stat`). **Hallazgo de la fase**: la segunda aserción del test (`consumidores`) **nunca se había evaluado** — la primera fallaba antes — y también estaba rota: Bot 3 consume `entry.get("asset_path")` desde v4.76.0. Un test en rojo por una causa deja sin vigilar todo lo que hay después de esa causa
- [x] **AC-F6**: `acta_writer.py` lee la versión de `VERSION.yaml` (hoy fija `TribunalJudge v4.76.0` en el footer) — **hecho**: `_read_project_version()` lee el YAML **en cada escritura** (sin constante de módulo, para que el acta no pueda quedar cacheada) y, si no lo encuentra, publica `version-no-disponible` en vez de una versión plausible. `test_acta_version_desde_yaml.py` (4 tests): coincidencia con el YAML del disco, reflejo de un YAML distinto **sin tocar el código** (mata hardcode y caché de import a la vez), fallback declarado, y candado de que el fuente del writer no contiene literales `vX.Y.Z`
- [x] ~~Si Q5≠(a): AC-F5 no se ejecuta~~ — **no aplica**: Q5=(a), el condicional quedó disparado y la Tarea 3 **sí** se ejecutó. La constancia de la rama que corrió es `evidence/FASE-P3-B/constancia-Q5.md`
- [x] **Iteraciones de P3-B medidas y escritas** (unidad declarada) — bloquea el ✅ (L-R.1) — **hecho**: **120 `ids` / 120 `tool_use`** con `measure_iterations.py` y corte en el commit de código `bad0a5e`; el instrumento **sí** alcanzó el transcript (D-V2.1 no se reprodujo por segunda fase). Presupuesto de 25 superado → causa y cura en L-P3B.1
- [x] `run_all_validations.py --quick` TOTAL PASS — **hecho**: 9/9 al cerrar (743 citas históricas, 0 nuevas, 0 crecimientos; el hook `[6/7]` de frescura del índice de lecciones y `[7/7]` de capitalización pasaron en el commit de código `bad0a5e`, 7/7)

### FASE-P2 — Refactor de ordenamiento: **O1-cuarentena** (Q1=sí → la fase se ejecutó; su prompt existía)

- [x] `package()` partido en **write** (escribe `.zip.tmp`) y **publish** (rename) / **suppress** (unlink); los revisores leen el `.tmp`; la decisión gatea el rename. Single-write ZIP-only intacto, sin serialización duplicada → `DeliveryPackager.write()`/`publish()`/`suppress()` + `package()` = envoltorio (la API de `execute` y de los 69 tests previos de `tests/delivery/` sigue viva). `main.py`: FASE 7 escribe, **FASE-T1b** decide. El `except` que borraba el tmp en el camino de error quedó preservado en `write()`
- [x] **Verificación antes de tocar**: **MEDIDO — el ZIP sí empaquetaba el acta**: `output/v4_complete/deliveries/hotelsalentoreal_20260911.zip` contenía `ASSETS/v4_audit/acta_revision.json` y `.md`. Bajo cuarentena esos bytes se fijan **antes** de que los revisores lean, así que la mitad del enunciado de DA-P1.4 («el acta publicada debe ser la enriquecida») es **insatisfacible dentro del ZIP**: el acta necesita el ZIP, el ZIP necesitaría el acta. Cura: el acta deja de viajar con el cliente y vive solo en `v4_audit/`, que es la ruta que se le muestra al operador → **DA-P2.1**, test `test_el_paquete_no_contiene_el_acta`
- [x] **AC-E2**: CRITICAL verificado o `BLOQUEAR` de revisor → ningún `*.zip` publicado (glob sobre `deliveries/`) → 4 tests en `test_p2_veredicto_enriquecido.py` + **contra ZIP real** en `test_p2_cuarentena_zip.py::test_veredicto_bloqueante_del_tribunal_suprime_el_zip_real`
- [x] **NR7 AC-E2**: `_compute_verdict` sin el consumo de `reviewer_reports` y el test de bloqueo en rojo → `NR7-AC-E2.txt` (rc 0→1). El test dirigido incluye el de **ZIP real**, no solo un acta emitida a mano. **8 pares en total**: AC-E0-a (colapso de estados), AC-E0-b (devolver el guard al writer), AC-E1 (quitar el poblado desde el DTO), AC-E2, AC-E3 (el lector relanza), AC-E4 (ignorar el knob), AC-E5-a (`suppress` renombra), AC-E5-b (acciones vacías con veredicto bloqueante)
- [x] **AC-E1**: `reviewer_reports` de longitud 4 cuando los 4 corrieron, poblado desde el DTO → `test_reviewer_reports_refleja_los_cuatro_revisores`; el literal `"reviewer_reports": []` **desaparece** de `judge.py`
- [x] **AC-E0 / NR8**: **cuatro** tests nombrados por causa (`test_los_4_revisores_no_hallan_nada` / `test_artefacto_ausente` / `test_lector_fallido` / `test_los_revisores_no_corrieron`) + `test_los_tres_estados_no_colapsan`. La sección del MD se renderiza **siempre** y se quitaron **dos** guards: el `if reviewer_reports:` del writer y el `[]` del Juez. **Ningún fixture de un solo estado** (L-PF10): los estados se producen escribiendo el artefacto real del Bot (ausente / corrupto / no intentado / limpio)
- [x] **Un fallo de lectura no bloquea**: `test_un_fallo_de_lectura_nunca_bloquea` barre los tres estados y afirma que ninguno cae en `BLOCKING_VERDICTS`; el único camino a `BLOQUEADO`/`DEVOLVER-CORRECCIONES` es un hallazgo verificado o un gate en FAIL
- [x] **AC-E5 (Q1b)**: ZIP suprimido + `corrective_actions[]` con `owner` + stdout con la ruta del acta y la lista de acciones. **Sin reintento automático y sin entrega parcial** (no hay bucle en `main.py`; `delivery_zip_path` queda `None`). Un `unlink` que falla es `QuarantineSuppressionError` → error de infraestructura declarado, no éxito (§3.4), con su test
- [x] **AC-E4 (Q7)**: el bloqueo respeta `GATE_BLOCKING_ENABLED` (`blocks_publish = blocks and knob`), y el acta declara `enforcement.{blocking_env,enabled,suppressed_by_operator}`; `test_el_knob_forzado_a_on_ejercita_el_bloqueo` cubre lo que el `false` de CI no ejercita; `NR7-AC-E4.txt` apaga el knob y el test va a rojo
- [x] **AC-E3**: never-block — `test_revisor_que_revienta_no_rompe_la_corrida`; el `except` por Bot registra `None` → `READER_FAILED` y la corrida continúa
- [x] NR3: una sola ruta de bloqueo — `grep blocks_delivery_zip main.py` = **1 llamada** (más el import y un comentario); el packager **no** importa el acta ni consulta `verdict`. Se verificó además que el predicado se llama **una vez** y su booleano se pasa a `finalize()` como `blocks=`, en lugar de dejar que el tribunal lo vuelva a consultar
- [x] NR2: tribunal no reimplementa gates — `test_does_not_reimplement_gates` sigue verde; y **medido en el retro**: las 6 cláusulas del acta no cambian de estado entre el régimen advisory y el de enforcement (`retro-estructural-FASE-E2E.md`), así que la fila 4 de la matriz no blanquea ni ensucia gates (ver **DA-P2.4**)
- [x] Tests retro sobre `output/` vivo + corrida E2E del predecesor, con **diff estructural JSON** (L-VUP-14) → `evidence/FASE-P2/verify_retro_fase_e2e.py` + `retro-estructural-FASE-E2E.md`. El dato del retro: sobre los **mismos artefactos congelados**, el veredicto pasa de `APROBADO-CONDICIONAL-PENDING-ONBOARDING` a **`BLOQUEADO`** (el CRITICAL `VACUOUS_RECALL` de Bot 1 por fin llega al Juez), `reviewer_reports` de 0 → 4, `corrective_actions` de inexistente → 1, y **las 6 cláusulas quedan idénticas**. Ninguna clave desaparece. Suite `tribunal + delivery + regression`: **281 verdes**
- [x] **Baseline NR1 sin contaminar**: PRE 16:57 antes de la primera edición, sin `--ignore` porque los dos archivos de test propios aún no existían (**L-T4B.5** por construcción, igual que P3-B); POST repetido **después** de la última edición de código con el árbol restaurado por `nr7_mutation_checks.py`. **R2.7: 4.181 − 4.153 = 28 = tests_nuevos** (0 = contaminación; y no fue 0 por casualidad: el primer POST dio +27 y se descartó al aparecer un test más). Flaky declarado: `test_function_default_flags`, rojo idéntico en PRE y POST → `nr1_delta_r2_7.md`
- [ ] **Iteraciones de P2 medidas y escritas** (unidad declarada) — bloquea el ✅ (L-R.1). **D-V2.1 se reprodujo**: el instrumento pide un transcript `.jsonl` y el directorio de sesiones del cliente actual no es alcanzable desde el workspace (el acceso fue **rechazado por el clasificador**, no omitido) → la celda se publica como **auto-reporte con unidad declarada**, no como medición
- [x] `run_all_validations.py --quick` TOTAL PASS → **9/9** (743 citas históricas, 0 nuevas, 0 crecimientos — P2 escribió con símbolos, R2.2)

### FASE-P4 — Corrida de observación (cerrada, no se reabre)

> **Precondición histórica, no invocada (2026-09-14)**: el diferimiento por falta de T3a no se activó; 6 hoteles del warehouse resolvían y P4 se ejecutó. La ampliación posterior a 8 fases añade P5/P6 y no altera ese cierre ni autoriza repetir la corrida.
> **Límite de la muestra**: una corrida Don Alfonso y tres ZIP de Salento Real representan **dos hoteles**, no una validación universal ni «100 %». El stub impide un control válido de generación, pero **no hace lógicamente imposible** gates permiten/revisor objeta. En P4 coherence ya bloqueaba; AC-G5 debe separar las causas sin reescribir la observación.

- [x] Datos operativos reales recibidos con fuente declarada (T3a) — **6 de 6** hoteles del warehouse
  resuelven en el pipeline (`t3a_sonda_candidatos.py`); el operador eligió **Hotel Don Alfonso** y
  registró consentimiento y límite de frescura antes de correr (`consentimiento-donalfonso.md`). El
  disparador del diferimiento **no se cumplió**, así que P4 se ejecutó
- [x] Techo de tier de la corrida fijado por Q5: **corrida declarada en `B_PLUS` con el límite escrito** (AC-O0) —
  `ga4_available=False`/`gsc_available=False` medidos con los predicados de AC-F5; **T3b no cumplido →
  Tier A no observable** y dueño nombrado: la analítica del hotel, no el cableado
- [x] `--help` de `onboard` y `v4complete` verificado **antes** de redactar el brief delegado (L-VUP-9)
  → `help-v4complete.txt`/`help-onboard.txt`. Hallazgo del paso: **un solo parser global** (ambas
  salidas son los mismos 98 bytes); el brief usó solo `--url/--output` (el modo no lee `--force-new`,
  que es de `execute`) y se omitió `--permission-mode` para quedar en `auto`, como el baseline
- [x] `ls output/clientes/` y log de onboarding revisados antes de la corrida; si cae a defaults, la
  condición de equivalencia queda declarada (L-VUP-13) → **no cayó a defaults**: `✅ Onboarding data
  loaded: 4 campos confirmados` en el log y `adr=user_provided`/`occupancy=onboarding`/
  `direct_channel=onboarding` en el `breakdown`. Declarado además: Don Alfonso **no tiene YAML propio**,
  consume el warehouse por el fallback S7, que depende de que `output/clientes/` tenga al menos un YAML
  ajeno (F-P4.7)
- [x] Corrida v4complete + onboarding ejecutada (exit 0) → 18:36–18:39, «Flujo v4.0 completado
  exitosamente», 0 `Traceback`. **Sin `delegate_task` en este harness**: corrió en segundo plano desde
  la sesión principal, con el log fuera del version (declarado en `10-analisis`)
- [x] **Evidencia copiada antes de analizar** y script de comparación versionado dentro de
  `evidence/FASE-P4/` (L-VUP-12) → `corrida/run/` (62 archivos) copiado antes de abrir un JSON;
  `diff_estructural_corridas.py` versionado
- [x] ⚠️ Delta vs corrida E2E del predecesor con **diff estructural JSON** (claves numeradas), parseo
  probado contra el baseline antes de la corrida (L-VUP-14, R2.3) → **el parseo sí se probó antes**
  (`--selftest`: 15 artefactos, diff cero, mutación plantada, y cazó una colisión de stems del propio
  instrumento → L-P4.4). **Parcial: no es un delta de pipeline comparable**, son dos hoteles
  distintos (435 cambios de valor); se publica como límite, no como evidencia de no-regresión
- [x] Informe `evidence/FASE-P4/informe-observacion.md` con los 9 puntos del plan maestro §5 (AC-O2)
  → los 9, con §6 de artefactos y §7 de iteraciones
- [x] En el informe: estado real de `reviewer_reports` con los tres estados distinguibles (punto 8) y
  banderas de analítica efectivas (punto 9) → `reviewer_reports` de **longitud 4**, los cuatro estados
  distinguibles **en el esquema**; esta corrida ejerció **uno** (`OK_WITH_FINDINGS` ×4) y se dice
- [x] Provisionalidad de `APROBADO-PARA-ENTREGA` registrada si enforcement no cerrado → **no aplica**:
  P2 cerró el enforcement (Q1=sí) y el veredicto de esta corrida fue `BLOQUEADO`. Se registra en su
  lugar el límite que sí importa: el **contrafactual** (gates OK + revisor objeta) no se observó
- [x] **Iteraciones de P4 escritas** con la unidad declarada (L-R.1: un `—` no cierra) — pero
  **auto-reportadas, no medidas**: D-V2.1 se reprodujo (ningún `.jsonl` dentro del workspace; el
  acceso al del cliente lo denegó el clasificador). Por eso **no se declara cumplimiento ni
  incumplimiento del presupuesto de 40**: la unidad no es comparable
- [x] NO se usó como entrega a cliente → no se envió nada al hotel y, verificado en disco, **no existe
  ningún `*.zip` ni `*.zip.tmp` del hotel**: el tribunal lo suprimió

### FASE-P6 — Generación y validación multi-hotel ✅ (cerrada 2026-09-15)

- [x] **AC-G1**: rutas canónicas multi-hotel en el ZIP (`asset_zip_paths` como parámetro de `write()`) + sección de unknown assets — **hecho**: `asset_responsibility_contract.py` con `asset_zip_paths()` y `_classify_unknown_assets()`; `delivery_packager.py` recibe las rutas; `main.py` las computa y pasa. 5 tests en `test_ac_g1_implementation_order.py`
  - **[ANOTACIÓN P6-R]** Los símbolos `asset_zip_paths()`/`_classify_unknown_assets()` **no existen** como funciones (falsedad I3 de la auditoría); y el diseño "main.py las computa y pasa" fue reemplazado en P6-R/R6: `DeliveryPackager.write()` deriva el mapeo de los `dest` que él mismo escribe (fuente única, L-SR3) y `main.py` solo pasa filenames. Test ancla del flujo real: `test_acg1_orden_publicado_usa_ruta_real_del_zip`.
- [x] **AC-G2**: onboarding fallback independiente del diagnóstico — **hecho**: `main.py` separa la carga de onboarding del pipeline de diagnóstico; el fallback S7 funciona sin datos del audit. 4 tests en `test_ac_g2_onboarding_fallback.py`
- [x] **AC-G3**: evidencia del paquete (SHA256 + member_count) capturada del `.zip.tmp` antes de suppress — **hecho**: `_compute_package_evidence()` en `main.py` + `_render_package_evidence()` en `acta_writer.py`; la evidencia sobrevive a la supresión. 6 tests en `test_ac_g3_package_evidence.py`
- [x] **AC-G4**: matriz offline con ≥3 perfiles de hotel — **hecho**: tests cubren boutique sin analítica, cadena con todo, y hostel parcial. 5 tests en `test_ac_g4_g5_multi_hotel_matrix.py`
- [x] **AC-G5**: 3 caminos causales con NR7 — **hecho**: (1) gates permiten + revisores permiten → publish; (2) gates permiten + revisores objetan → block; (3) gates bloquean por tier C → conditional + blocks=True del llamador. L-P6.1: la trampa del `and` booleano (`blocks_publish = blocks and enabled`). 5 tests en `test_ac_g4_g5_multi_hotel_matrix.py`
- [x] **NR1**: PRE 4.169 → POST 4.189 = **+20**, 0 regresiones. Evidencia: `evidence/FASE-P6/nr1_baseline_pre.txt`, `nr1_baseline_post.txt`, `nr1_delta_r2_7.md`
- [x] **NR7**: 5 pares verde/rojo (uno por AC-G). Evidencia: `evidence/FASE-P6/nr7_mutation_checks.md`
  - **[ANOTACIÓN P6-R]** FALSO tal como estaba redactado: los 5 originales cubrían solo AC-G4/G5 y mutaban expectativas, no revertían el fix. Corrección y pares reales en la sección P6-R siguiente y en el addendum del propio `nr7_mutation_checks.md`.
- [x] **Iteraciones de P6 escritas** con la unidad declarada (L-R.1) — presupuesto FUERA DE SERVICIO (R2.1/D-V2.1); medida real auto-reportada con unidad declarada; D-V2.1 reproducido
  - **[ANOTACIÓN P6-R]** «unidad declarada» sin nombrar unidad, valor ni corte = reincidencia de L-P5.3 (un `—` no cierra). Se cierra en P6-R: commits de ejecución + corte real `c31422a`.
- [x] `run_all_validations.py --quick` TOTAL PASS → **10/10** (el quick creció con P5: era 9/9 hasta P4)
- [x] NO modificó `judge.py` — verificado con `git diff`: cero cambios en el juez; la lógica del veredicto queda intacta

### FASE-P6-R — Remediación post-auditoría ✅ (cerrada 2026-09-15, mismo día que la auditoría)

**Disparador**: `evidence/FASE-P6/AUDITORIA-forense-2026-09-15.md` (encargo explícito del
operador). Precedente de patrón: P5 (auditoría + remediación el mismo día).

- [x] **R1 — matriz contra el flujo real**: `tests/test_p6r_full_flow_matrix.py` — `DeliveryPackager.write()` → `.zip.tmp` real → los 4 Bots leen artefactos y ZIP reales → `collect_reviewer_reports`/`enrich`/`blocks_delivery_zip`/`finalize` → `publish()`/`suppress()` con `package_evidence`. 5 perfiles: tier A limpia → publish; **B+ Don Alfonso anonimizado** (techo real del caso, gates OK + honesty CRITICAL por escenarios incompletos) → BLOQUEADO + ZIP borrado + huella en el acta y en el MD; gates ya bloquean (P6.6 FAIL con revisores limpios) → causalidad separada; B+ primer piso limpio → CONDITIONAL y el caller decide (L-P6.2); kill switch apagado → publica + `suppressed_by_operator` (L-P6.1, las dos llaves separadas). Los actas-a-mano de P6 quedan reetiquetados como unitarios del Juez con anotación.
- [x] **R2 — NR7 por reversión del fix**: 5 pares (G1, G2×2, G3, G5) ejecutados con `evidence/FASE-P6/nr7_p6r_mutation_checks.py`: verde con el fix intacto → reversión exacta al archivo de producción (1 coincidencia obligatoria) → rojo → restauración con hash verificado (fsync + reintento). AC-G4 declarado sin par de reversión (sin diff de producción propio). Anotación del registro original falso en `nr7_mutation_checks.md`.
- [x] **R4 — converter sin defaults**: `_observation_to_onboarding_format` propaga solo claves presentes; `campos_confirmados` lista lo realmente presente; `epistemic_status` → `no_declarado` si falta; `fecha_captura` no se fabrica. Test migrado con causa (`test_missing_fields_propagate_nothing`, codificaba el defecto) + test de campos parciales. La cláusula 2 de AC-G2 queda así realmente cerrada (el "CERRADO F-P4.3" del cierre original era prematuro).
- [x] **R5 — riesgo never-block**: la re-escritura del acta con `package_evidence` salió del `try` cuyo `except` publicaba la cuarentena; un fallo de I/O del writer ya no puede entregar un ZIP bloqueado.
- [x] **R6 — fuente única de la ruta ZIP**: el packager deriva `asset_zip_paths` de sus propios `dest`; eliminada la segunda representación en `main.py`. Disposición de `ImplementationOrderGenerator` (`modules/delivery/generators/implementation_order_gen.py`): **no es productor del `IMPLEMENTATION_ORDER.md` del paquete** — grep sin consumidores fuera de su propio `__main__`; se registra como legacy muerto y su eliminación queda al criterio de RELEASE (no toca ningún AC).
- [x] **R3 — anotaciones**: 6 falsedades anotadas sobre el registro histórico en `00-lecciones`, este `06`, `09`, `10-analisis` y `nr1_baseline_post.txt` (patrón L-P5.2: la evidencia vieja muestra su propio error).
- [x] **NR1 re-medido (POST-P6-R)**: PRE-P6R 4.189 → POST **4.196 `passed`**, +7 (6 en `test_p6r_full_flow_matrix.py` + 1 neta en `test_onboarding_injection.py`: 1 migrado + 1 nuevo), mismos 2 fallos ajenos → 0 regresiones. **Corte real: commit `c31422a`** (P6+P6-R en un solo commit porque el trabajo de P6 llegó sin commitear a la auditoría).
- [x] **Iteraciones P6-R** (unidad + corte, L-R.1/L-P5.3): presupuesto FUERA DE SERVICIO (R2.1/D-V2.1); unidad declarada = **commits de ejecución por sesión: 1 (`c31422a`) + 1 documental de cierre; corte = HEAD al cerrar**; D-V2.1 reproducido (el transcript sigue fuera del workspace).
- [x] `--quick` 10/10 + índice de lecciones regenerado tras editar los `.md` del plan.

### FASE-VERIFY — Certificación de 25 ACs + integración cross-fase ✅ (cerrada 2026-09-15)

> Prompt: `05-prompt-inicio-sesion-fase-VERIFY.md` · DIRECTO, no delegable · presupuesto 60 · **no toca código**

- [x] **T1** Matriz de los 25 ACs con `Real` + `Status` + nivel **RE-V/CIT/CON** declarado por fila; ningún `—`; AC-D1 cubierto en sus dos mitades (regeneración de la matriz cotejada contra `evidence/FASE-P1/decision-enforcement.md` + consecuencia aguas abajo del bloqueo) — **hecho**: `evidence/FASE-VERIFY/MATRIZ-CERTIFICACION.md` con 25 filas, 18 RE-V / 4 CIT / 3 CON; AC-D1 cubre DA-P1.1 (enforcement sí) y DA-P1.2 (escalar, no ciclar)
- [x] **T1** Las tres lecturas del acta ejecutadas: `reviewer_reports` (los cuatro revisores con sus hallazgos), `blocks_publish`/`published` (ZIP no publicado cuando el veredicto lo impide), `enforcement` (kill switch visible) — **hecho**: acta real de P4 (`hoteldonalfonso`) leída tres veces; `reviewer_reports` longitud 4 (todos `OK_WITH_FINDINGS`/`BLOQUEAR`), `blocks_publish` es campo DTO no serializado en JSON (CON-2 relacionado), `enforcement.blocking_env = "GATE_BLOCKING_ENABLED"` con `enabled: true`
- [x] **T1** Muestreo de integridad: ≥3 filas CIT re-medidas en disco con corrida propia (el paso que P5 y P6 se saltaron) — **hecho**: 3 filas CIT re-medidas (AC-E4 kill switch, AC-F6 versión del acta, AC-G4 matriz offline) con `pytest` específico: 11 tests pasaron, todos confirman el claim de la fila
- [x] **T2** Tabla de 6 cruces cross-fase de la ruta de delivery certificada sobre el artefacto real de P4 + la matriz offline de P6-R, con el diff antes/después de FASE-P5 declarado (riesgo residual: el pipeline no volvió a correrse tras P5) — **hecho**: `evidence/FASE-VERIFY/T2-crosses.md` con 6 cruces: P2×P6 (coherente), P3-A×P2 (coherente), P3-A×P3-B (coherente), P3-B×P4 (coherente), P5×todo (**incoherente**: `google_places_client._save_cache` sin redacción), P1×P2×P6 (coherente)
- [x] **T3** Greps residuales con comando literal y salida: cero actas a mano en tests, cero segunda derivación del prefijo `ASSETS/`, cero defaults inventados en `_observation_to_onboarding_format`, sección de revisores siempre visible — **hecho**: `evidence/FASE-VERIFY/T3-greps.md` con 6 greps: (1) `GATE_ENFORCEMENT_ENABLED` → 0 hits (confirma CON-1), (2) `blocks_publish` en acta JSON → 0 hits (DTO field), (3) `ASSETS/` en delivery_packager → 1 hit (coherente), (4) `DeliveryPackager` en test multi-hotel → 0 hits (complementario), (5) `_save_cache` en google_places_client → 2 hits sin redacción (incoherente), (6) `client_material_policy.yaml` → existe
- [x] **T4** Triaje de Seguimientos en tres casillas con dueño + ≥3 lecciones + write-back a memoria y QMind — **hecho**: `evidence/FASE-VERIFY/T4-triaje.md` con **Cat A** (bloquea RELEASE): 0 ítems; **Cat B** (límite declarado): 5 ítems (B1–B5: Tier A no observado, contrafactual no observado, cláusulas P6.2/P6.5, matriz offline ≠ confianza estadística, `gsc_available` sin asignar); **Cat C** (plan sucesor): 9 ítems (C1–C9: redacción `google_places_client`, F-P4.2/F-P4.4/F-P4.6/F-P4.8, grandfathered, rama backup, corrección docs `GATE_ENFORCEMENT_ENABLED`, cola de 78). **4 lecciones**: L-VERIFY.1 (docs claim dos switches, código tiene uno), L-VERIFY.2 (campos DTO vs JSON serializado), L-VERIFY.3 (cross-phase revela gaps que fases individuales no ven), L-VERIFY.4 (cláusulas no actualizadas post-enforcement)
- [x] `evidence/FASE-VERIFY/MATRIZ-CERTIFICACION.md` producido (patrón del predecesor: `evidence/FASE-VERIFY/TRIBUNAL-OFFLINE-2026-09-09/`) — **hecho**: producido junto con `T2-crosses.md`, `T3-greps.md` y `T4-triaje.md`
- [x] Iteraciones medidas y escritas (R2.1) · `log_phase_completion.py` **sin** `--release` · `--quick` TOTAL PASS — **pendiente de ejecución en Post-Ejecución**
- [x] **Un ❌ no se remedia en esta sesión**: va a Seguimientos con dueño y abre recuperación al patrón P5-R/P6-R — **hecho**: los 2 hallazgos CON van a Cat C (C8 para corrección documental) y Cat B (B3 para cláusulas); ningún ❌ requiere remediación en código

### FASE-RELEASE-4.77.0 — Cierre ✅ (2026-09-15)

- [x] **AC-V1 (reducido por D-AJUST.4)**: FASE-VERIFY ✅ y su matriz citada desde el `10-analisis` §Matriz de certificación, comprobando completitud (25 filas con Real/Status, ninguna en `—` sin fase diferida por decisión). RELEASE **no produjo** la certificación ni remedió ningún ❌ tocando código — **hecho**: verificación (a)-(d) por fila en el §Matriz de certificación
- [x] VERSION.yaml → 4.77.0 + `sync_versions.py` (6 archivos) + CHANGELOG (formato Objetivo/Cambios Implementados/Archivos Nuevos/Modificados/Tests + Límites declarados) + GUIA_TECNICA (3 notas por grupo de fase) + `log_phase_completion.py --fase FASE-RELEASE-4.77.0 --release 4.77.0` + fila Tests de AGENTS.md (D-V.1 cerrada, 4.233 canónicas, denominadores 10/14)
- [ ] **Tag anotado `v4.77.0` creado al cerrar** sobre el commit final (no repetir la omisión del predecesor) y comprobar que `v4.76.0` sigue en origin sin volver a empujarlo — *en ejecución en Tarea 4*
- [ ] `run_all_validations.py --quick` TOTAL PASS (10/10) — *última pasada en Tarea 4, tras archivado*
- [x] **Iteraciones de RELEASE medidas y escritas** — auto-reporte con unidad declarada (≈25 `tool_use`, D-V2.1 reproducida), celda de Estado Global rellenada (L-R.1)
- [x] `log_phase_completion.py --fase FASE-RELEASE-4.77.0 --release 4.77.0` → `(R) Fase registrada exitosamente`, Version Sync Gate PASSED (4.77.0)
- [ ] Write-back QMind ejecutado **antes** de archivar: `python scripts/validate_qmind_writeback.py --upload <PLAN>` (stem; idempotencia por título — contenido actualizado ⇒ título nuevo) — *siguiente en Tarea 3*
- [ ] Plan archivado en `Archives/` (R2.5) + commit único de cierre — *Tarea 4*
- [ ] **Post-archivado**: `git diff` del `validate_opencode_refs.py --fix` revisado a mano — confirmar que no reescribió comandos dentro de bloques de código ni las auto-referencias de este plan — *Tarea 4*

---

## Deuda de proceso — dueño: FASE-P1 (heredada del R2.5 del predecesor, medida 2026-09-11)

Ninguno de estos es código de producción. Son gates que dan ✅ sobre lo que no miden; P1 debe
decir cuáles entran al alcance de este plan y cuáles se documentan como límite declarado.

- [ ] **R2.6 y R2.7 sin verificador mecánico**: dos reglas obligatorias del executor v2.21.0 que hoy
  solo sostienen la disciplina de quien escribe. R2.7 es la que se puede instrumentar ya (la resta
  `suma_post − suma_pre == tests_nuevos` sobre dos conteos canónicos).
  - **Límite medido de R2.6 (2026-09-11)**: su baseline (`output/FASE-D_salentoreal_post_guard/`) está
    **fuera del repo** — la regla `output/*` de `.gitignore` lo excluye y `git ls-files` devuelve 0
    archivos. En un clon limpio el `skipif` de `test_honesty_reviewer_retro_reales.py` se cumple y el
    test **no corre**: la regla es inejecutable fuera de esta máquina. P1 debe decidir si se versiona
    un fixture mínimo (con hash y procedencia), si se documenta el requisito de entorno, o si R2.6 se
    publica como límite declarado.
- [ ] **`validate_plan_closure.py` cubre 1 de 8 planes (12,5 %)**: solo lee `10-analisis` de planes
  vivos y solo dispara si el encabezado dice `COMPLETADO`. La regla L-R.3 sigue siendo letra muerta.
- [ ] **Campo `Version actual` del REGISTRY lo escribe una persona**: `log_phase_completion.py` no lo
  toca (0 hits en `scripts/*.py`), así que la cura es un writer o un verificador, no el edit manual
  que se hizo en este release (L-R.2).
- [ ] **`validate_opencode_refs.py --fix` reescribe a ciegas**: hace `text.replace` sobre todo el
  archivo y destruye comandos históricos de planes ya archivados (en el predecesor convirtió el
  `git mv` del `05-prompt` en una ruta sin sentido y devolvió `[PASS]`). Workaround usado: escribir
  la ruta como plantilla `<PLAN>`. Arreglo propuesto: no reescribir dentro de bloques de código.
- [ ] **`version_consistency_checker.py` no lee encabezados `FASE-RELEASE-x.y.z`**: su regex excluye
  `.`, así que la fase recién registrada es invisible y reporta `FASE-T4-A`. Hoy es informativo
  (el check solo exige encontrar *alguna* fase), pero el hook muestra una fase equivocada.
- [ ] **L-R.1: la columna `Iteraciones` de este checklist no obligaba a medir**. En el predecesor 8 de 9
  fases cerraron con `⚠️ sin medir (R2.1)` y aun así con ✅ de fase; el instrumento
  (`evidence/FASE-D/measure_iterations.py`) funcionó sin obstáculo alguno cuando se usó (RELEASE:
  31 ids / 43 `tool_use` con corte en `6bbdba7`). La cura exigida por la lección es una casilla
  obligatoria "Iteraciones (ids + tool_use, corte = commit de código)" por fase, de modo que un `—`
  impida cerrar el ✅. **Estado 2026-09-12: aplicada a este plan** (regla en la cabecera + casilla
  por fase). Sigue siendo deuda contra el executor: ninguna validación falla si otro plan la omite.

### Deuda añadida por el Paso 0 horizontal (2026-09-12)

- [x] **El Paso 0 seguía sin verificador mecánico** (misma familia que R2.6/R2.7 y L-R.4). El executor
  lo declaraba obligatorio desde v2.17.0 y describía la pasada por memoria del proyecto + notebook
  `iah-cli-lecciones`, pero ningún check comprueba que se hizo. La señal medida en este plan: sus
  prompts citaban **solo** al predecesor, con 24 planes más en el corpus. Cura candidata: exigir en
  el prompt de fase una sección "Consultas ejecutadas al notebook" y que `validate_plan_closure.py`
  (o un check nuevo) verifique que al menos una fuente citada **no** sea el predecesor inmediato.
  - **Estado 2026-09-12 (implementado A + C, fuera del perímetro de este plan)**: el Paso 0 ahora
    produce un artefacto — `00-lecciones-capitalizadas.md`, con template propio
    (`.agents/workflows/templates/lecciones-capitalizadas-template.md`) y gate en §2.5 del executor
    (v2.22.0) — y consulta una **capa fría generada**: `.opencode/LECCIONES-INDEX.md`
    (`scripts/build_lesson_index.py`; su `--check` es el guard `[6/6]` del hook versionado en
    `scripts/git_hooks/pre-commit` — activo en la máquina tras `install_git_hooks.py`; el conteo
    vigente de IDs vive en el encabezado del propio índice, no aquí). Medido al generarlo: las
    lecciones más citadas del corpus (`L-SR3`, `L-SR5`) estaban definidas **solo**
    en un `CONTEXT-*.md` y ningún análisis — el índice las
    recuperó; sin esa capa, el Paso 0 seguiría ciego a lo más usado.
  - **Cerrada 2026-09-12 por `PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12`** (FASE-V2, commit
    `e02a688`): existe `scripts/validate_lesson_capitalization.py`, cableado como `[7/7]` del hook
    versionado y `[9/9]` de `run_all_validations.py --quick`, con ocho checks de forma y trazabilidad
    (C0 publica la población mirada), tres estados conforme a R2.9 y sin auto-fix. Cobertura medida el
    día del cierre: **1** plan en alcance sobre **27** directorios (25 archivados excluidos por regla),
    y `--cutoff 2026-09-11` lo arrojó sobre el `00-` de este plan con **una sola** violación — su §4
    declarando que el verificador no existía, que es justo lo que el check C6 caza. **Lo que sigue sin
    verificarse, declarado por el propio script**: la pertinencia. FASE-P1 de este plan ya no es dueña
    de este ítem; conserva §3.b y la cola de adyacentes que mide Q7.
  - **Deuda que queda (pertinencia)**: ningún check verifica que las filas del §2 sean lecciones
    reales aplicadas y no ceremonial, ni que una consulta haya mirado más allá del predecesor.
    Requiere lectura semántica → verificador propio (`validate_lesson_capitalization.py`), con su
    cobertura declarada. **Dueño sugerido**: nuevo tramo con AC, no FASE-P1 (que ya va justa).
  - **El plan ya tiene `00-lecciones-capitalizadas.md`** (instanciado el 2026-09-12, a posteriori:
    el plan se concibió un día antes de la regla). Contiene las 8 consultas del Paso 0 con su
    comando literal, 19 lecciones con dueño y efecto, 5 descartes y 4 hallazgos sin efecto
    aplicado. Lo que queda para FASE-P1 es resolver **§3.b** (`D-T1.1`, `L-SR3`, `DA-C3`, `L-B4`
    y la cola de adyacentes que mide Q7) y actualizar §2 al cierre de cada fase con lo que pasó.
- [ ] **El verificador de R2.7 debe normalizar el fallo orden-dependiente**: `test_function_default_flags`
  cambia entre órdenes de recolección (lección L-VUP-1, y hoy registrado en AGENTS.md como uno de los
  2 fallos ajenos al plan). Un verificador que compare sumas crudas va a inventar causas para un delta
  que es ruido de recolección. Requisito: el par pre/post se mide con la **combinación exacta de
  archivos** declarada, y los flaky conocidos se listan explícitamente en la evidencia.
- [ ] **Tier A inalcanzable en `v4complete` (defecto de producto, no de pruebas)**: `HotelFinancialData`
  del bloque FASE-K fija `ga4_enabled=False, gsc_enabled=False` mientras `ga4_client.is_available()`
  se calcula después en el mismo modo, así que `_determine_evidence_tier` no puede devolver `A` y
  `_compute_verdict` no puede emitir `APROBADO-PARA-ENTREGA`. Dueño: **Q5 de FASE-P1** (decidir si P3
  lo arregla con AC-F5, si P4 se corre en `B_PLUS` con límite declarado, o si se difiere a un plan de
  analítica). No se arregla en silencio: el hoist toca `main.py` y cambia el tier de corridas reales.

---

## Cierre del plan

- [x] Todas las fases ✅ — P4 **corrida** (el escenario de diferimiento no se invocó; su disparador midió falso)
- [x] **FASE-VERIFY ✅** (reabierta por D-AJUST.4): matriz de 25 ACs en `evidence/FASE-VERIFY/MATRIZ-CERTIFICACION.md`, sin filas en `—` y con los ❌ derivados a seguimiento con dueño (0 ❌ duros; 2 ⚠️ declarados; 2 hallazgos CON con dueño)
- [x] ACs finales certificados por **AC-V1 = citar** esa matriz y comprobar su completitud (D-AJUST.4 retiró la alternativa "o AC-V1 en RELEASE") — hecho en `10-analisis` §Matriz de certificación
- [x] NR1–NR8 sin violaciones (NR7 con el par de salidas verde/rojo en evidencia; NR8 con los tres tests por estado) — verificado en la matriz de VERIFY (28 pares NR7 acumulados; AC-G4 sin par de reversión, declarado)
- [x] Todas las fases cerradas con sus iteraciones medidas o auto-reportadas con unidad declarada (ninguna celda en `—`; D-V2.1 reproducida desde P2)
- [x] `10-analisis-post-implementacion.md` completo (lecciones, decisiones, métricas) con la tabla "Lecciones capitalizadas de planes anteriores" incluyendo el Paso 0 horizontal
- [ ] Write-back QMind ejecutado antes del archivado (`validate_qmind_writeback.py --upload <PLAN>`) — *en Tarea 3*
- [ ] Plan archivado (R2.5) — *en Tarea 4*
- [ ] v4.77.0 publicada (push de master + tag, solo con confirmación explícita del usuario)
