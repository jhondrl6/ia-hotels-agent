# FASE-VERIFY — Certificación formal de los 25 ACs contra artefacto real + integración cross-fase

**ID**: TRIBUNAL-ENFORCEMENT-OBS-2026-09-11 / FASE-VERIFY
**Objetivo**: Certificar que los ACs del plan se cumplen contra los artefactos reales producidos por las seis fases de implementación, **verificando la integración coherente de todos los cambios sobre la ruta de delivery** (lo que ninguna auditoría de fase produjo), y cerrar la matriz de certificación del `10-analisis-post-implementacion.md`. Sustituye a AC-V1 como sesión propia (D-AJUST.4).
**Dependencias**: P1 ✅ · P3-A ✅ · P3-B ✅ · P2 ✅ · P4 ✅ · P5 ✅ (+remediación) · P6 ✅ (+P6-R)
**Presupuesto**: 60 iteraciones (R2.1; corte = commit de evidencia autorizado; D-V2.1 aplica si el instrumento no alcanza el transcript → auto-reporte con unidad declarada)
**Complejidad técnica**: MEDIA
**Modo de ejecución**: **DIRECTO — NO delegable** (§4.6 del executor: "requiere juicio y contexto completo del plan")
**Skill**: `phased_project_executor.md` v2.24.0 §4.6

---

## Contexto

### Por qué se reabre la decisión de P1 (D-AJUST.4)

`dependencias-fases.md` §Decisión FASE-VERIFY cerró la fase como **no activa** el 2026-09-14 sobre tres premisas que hoy están medidas al revés:

| Criterio §4.6 | Al cerrar P1 (2026-09-14) | Medido hoy (2026-09-15) |
|---------------|---------------------------|-------------------------|
| 1. ≥3 fases de implementación | 3 (P3-A, P3-B, P2) | **5** (P3-A, P3-B, P2, P5, P6) + P4 de corrida |
| 2. Al menos una fase con ejecución E2E | "no garantizable": P4 colgaba de T3a, precondición comercial externa | **Satisfecho**: P4 corrió con Hotel Don Alfonso (`BLOQUEADO` + ZIP suprimido) y P6-R añadió matriz contra el flujo real |
| 3. ACs que cruzan fases | 3 familias (E, F, O) | **6 familias**: AC-D1, E0–E5, F1–F6, G1–G5, O0–O2, S1–S4 = **25 ACs** |

Y dos hechos que el criterio no contemplaba porque aún no existían:

- **Dos auto-certificaciones de fase resultaron falsas**, ambas desmentidas por auditoría externa el mismo día del cierre: P5 (fase con 4/8 puntos post-ejecución, afirmación falsa en `NR7-AC-S2-green.txt` y el escaneo staged **muerto** por `NameError` tragado) y P6 (tarea 4 ejecutada con actas a mano pese a la prohibición del propio prompt, `DeliveryPackager` con **0 coincidencias** en los 4 archivos nuevos de test, NR7 sobredichado y la cláusula 2 de AC-G2 sin tocar).
- **AC-V1 no cabía en su contenedor**: RELEASE es DELEGABLE, complejidad BAJA y **30 iteraciones** para once obligaciones (bump, sync, CHANGELOG, GUIA_TECNICA, volcado del `09`, `10-analisis`, write-back QMind, archivado, revisión del diff del `--fix`, tag, commit). El precedente certificó **8 ACs con 41–50 iteraciones en modo DIRECTO**; a esa tasa, 25 ACs ≈ 140.

§4.6 del executor es imperativo ("el orquestador **DEBE** incluir FASE-VERIFY cuando TODOS los criterios se cumplen"). La sustitución por AC-V1 fue la decisión correcta con la información de P1; con la de hoy, la fase corresponde.

### Qué NO es esta fase (para no duplicar lo ya medido)

Las remediaciones **P5 y P6-R ya curaron y midieron** lo que sus auditorías hallaron: el escaneo staged vivo con camino vigilado por test, la matriz contra el flujo real (`tests/test_p6r_full_flow_matrix.py`: `packager.write` → ZIP real → 4 Bots → Juez → `publish`/`suppress`), 5 pares NR7 **por reversión del fix** con restauración verificada por hash, converter honesto y fuente única de la ruta ZIP. **Esta fase no vuelve a ejecutar esa remediación**: la certifica contra su evidencia y solo re-verifica lo declarativo o lo que ninguna de las dos tocó.

### Fuentes de evidencia

| Fuente | Qué aporta |
|--------|-----------|
| `evidence/FASE-P4/corrida/` + `informe-observacion.md` | Único artefacto de pipeline real (acta, MANIFEST, ZIP suprimido) — insumo de T2 |
| `evidence/FASE-P1/decision-enforcement.md` | Contrato: matriz §2.1, consecuencia, cuatro estados, kill switch |
| `evidence/FASE-P2/` (8 pares NR7), `evidence/FASE-P3-A/` (4), `evidence/FASE-P3-B/` (6, `constancia-Q5.md`) | Pares verde/rojo por AC de detección/bloqueo |
| `evidence/FASE-P5/` (`REMEDIACION-auditoria-2026-09-15.md`, `PREVENION-save-cache-2026-09-15.md`, `AC-S3-S4-inventario-superficie.md`, pares S1/S2) | Cierre de AC-S1…AC-S4 y su remediación |
| `evidence/FASE-P6/` (`AUDITORIA-forense-2026-09-15.md`, `nr7_mutation_checks.md` con anotación P6-R, `nr7_p6r_mutation_checks.py`, `nr1_*`) | Cierre de AC-G1…AC-G5 y el registro corregido de NR7 |
| `tests/test_p6r_full_flow_matrix.py`, `tests/test_p5_ac_s2_remediacion.py`, `tests/quality_gates/tribunal/` | Suite causal del tribunal |
| `10-analisis-post-implementacion.md` §Seguimientos Abiertos | 9 hallazgos de P4 + F-P4.5 + exposición de `evidence/FASE-I/corrida/` + divergencia `gsc_available` |

### Metodología (§4.6, 7 pasos, adaptada)

1. Leer los artefactos reales y el contrato de P1 antes de tocar nada.
2. Verificar cada AC contra **artefacto**, no contra declaración documental (nada se acepta por "el checklist dice ✅" — fue el método que falló en P5 y P6).
3. Comparar antes/después donde haya baseline (tier del acta vs MANIFEST; `nr1_baseline_pre/post`).
4. Greps residuales de lo que debió desaparecer (T3).
5. Completar la matriz del `10-analisis` (columnas Real/Status) — hoy **no existe**.
6. Registrar ≥3 lecciones de la verificación.
7. `log_phase_completion.py` **SIN** `--release` + `run_all_validations.py --quick`.

---

## Tareas (R3: 4 tareas, 0 comandos largos)

### T1: Matriz de certificación AC→artefacto, con profundidad escalonada

Las 25 filas con columna **Real** (artefacto + medición) y **Status** (✅ / ⚠️ / ❌). Antes de llenarlas, tres lecturas obligatorias del artefacto que el plan dice que el tribunal publica:

| # | Qué se lee en el acta (`acta_revision.json` + su render MD) | Qué certifica | Regla que lo exige |
|---|-------------------------------------------------------------|---------------|--------------------|
| a | `reviewer_reports[]`: longitud y los `status` de cada uno | que **aparecen los cuatro revisores con sus hallazgos**, no `[]` mudo ni tres de cuatro | AC-D1 y AC-E0/AC-E1 |
| b | `blocks_publish` / `published` (y los caminos causales de la matriz de P6-R) | que **el ZIP no se publica cuando el veredicto lo impide** | AC-E2, AC-E5, AC-G5 |
| c | `enforcement.{blocking_env,enabled,suppressed_by_operator}` | el **kill switch visible** en el documento: la llave está declarada, no inferida | AC-E4, contrato Q7 |

**AC-D1, en concreto** (es un AC de dos mitades y la segunda no la cubre ningún test de fase): (i) ejecutar la regeneración determinista de la matriz recomendación→veredicto y **cotejarla contra `evidence/FASE-P1/decision-enforcement.md`** — si `judge.py` la reimplementa en vez de consumirla, se registra como incumplimiento y **no** se arregla aquí (reimplementar lógica de gates está fuera de contrato); (ii) su consecuencia aguas abajo del bloqueo es la fila b) de esta tabla.

Profundidad declarada por fila — un ✅ "citado" no es un ✅ "re-verificado", y la matriz lo distingue:

| Nivel | Qué se hace | Aplica a |
|-------|-------------|----------|
| **RE-V** | Medir de nuevo sobre el artefacto o la corrida de tests, sin confiar en el registro | AC-S3, AC-S4, AC-O0, AC-O1, AC-O2, AC-G4 (sin par por reversión, declarado), AC-D1 (el contrato es documento, se contrasta contra lo implementado en P2) |
| **CIT** | Citar la medición ya registrada (archivo de evidencia + número medido) y comprobar que el archivo existe y dice eso | AC-E0…AC-E5, AC-F1…AC-F6, AC-G1, AC-G2, AC-G3, AC-G5, AC-S1, AC-S2 |
| **CON** | Contradecir el registro si la realidad no lo sostiene → ❌ con hallazgo y dueño, nunca ⚠️ confortável | transversal a las 25 filas |

Reglas: **R2.4** (AC no legible en artefacto = ⚠️, nunca ✅) · **NR7** (AC de detección/bloqueo sin par verde/rojo = ⚠️) · **NR8** (un lector de artefactos debe distinguir sin-hallazgos / artefacto-ausente / lector-fallido / no-ejecutado en el propio acta).

Muestreo de integridad del registro (obligatorio, mínimo 3 filas CIT re-medidas en disco): elegir las tres cuyas afirmaciones documentales sean más fuertes y comprobarlas con corrida propia de `pytest -q` sobre el test ancla.

**Residuos ya medidos el 2026-09-15** (auditoría sobre `evidence/FASE-P6` + código en disco; entran a la matriz como punto de partida, no como hallazgo nuevo):

| Residuo | Estado medido | Qué hace VERIFY |
|---------|---------------|-----------------|
| `evidence/FASE-P5/NR7-AC-S2-green.txt` | **sigue afirmando** que la mutación del par "es exactamente la rama staged" — la remediación corrigió el par pero no re-escribió el verde | Fila AC-S2: ⚠️/❌ según se re-medida; el archivo es evidencia anotada-pendiente, no cerrada |
| Conteos NR1 de P6-R | **divergen**: 26 funciones en el `10-analisis`, 22 declaradas por el propio test, 29 en el `09` — **NR1 sí es canónico** (4.196 `passed`, restado y verificado por el instrumento) | Fijar un solo número con recuento propio (`grep -rE "^\s*def test_"`) y anotar los otros dos sobre el registro, sin borrarlos |
| Archivo de evidencia de P6-R | **no existe** ningún `evidence/FASE-P6/*remediacion*`: la remediación quedó escrita como anotaciones dentro de `nr7_mutation_checks.md` + la auditoría + las filas del `06` | Declararlo: P6-R no tiene acta de fase propia, y AC-G4 se apoya en un archivo prohibido por I1 que sigue en la suite |
| `evidence/FASE-P6/nr1_post_p6r.txt` | `#` con `pytest tests/ -q` y `collected 4196 items` — **es un log, no un baseline**, pese a nombrarse como los baselines | Corregir el destino del nombre en el registro (RELEASE, no esta fase) y verificar que el `--quick` real es el del `06` |
| **DA-P1.7 vs el código** | La decisión prometió «**un solo botón** para todo lo que suprime entrega» y rechazó expresamente un knob propio del tribunal por «dos switches confundibles». Medido en `judge.finalize` + `delivery_packager._enforcement_enabled`: hoy hay **dos** (`GATE_BLOCKING_ENABLED` y `GATE_ENFORCEMENT_ENABLED`) | Fila AC-E4: certificar cuál es la decisión vigente. Si los dos se quedan, el acta tiene que nombrar los dos y DA-P1.7 se anota como re-decisión de P2 con dueño; si uno sobra, es ❌ con seguimiento (no fix de esta fase) |

### T2: Certificación de la integración cross-fase sobre la ruta de delivery

Ninguna auditoría de fase cubre esto: cuatro fases tocaron **el mismo camino** y cada una certificó su tramo local.

| Cruce | Qué verificar | Artefacto |
|-------|---------------|-----------|
| P2 × P6 | `write()` deja `.zip.tmp` → los 4 Bots leen **ese** ZIP → Juez → `publish()` **o** `suppress()`, y la huella (`package_evidence.sha256` / `member_count`) es del `.zip.tmp` real leído por los revisores | `evidence/FASE-P4/corrida/` + corrida de `tests/test_p6r_full_flow_matrix.py` |
| P3-A × P2 | Detección de plantilla vacía leyendo **desde el ZIP**, con el rename gateado: el `EMPTY_DELIVERY_TEMPLATE` ya no puede observar un archivo que aún no existe | `acta_revision.json` → checks + `_impl_order_check` |
| P3-A × P3-B | Fidelidad del acta: `evidence_tier` coincide con `financial_scenarios.breakdown.evidence_tier` y `first_floor_rule.source_artifact` nombra el archivo que realmente aportó el valor; `reason` en `B_PLUS` describe por qué el veredicto es condicional | acta MD vs JSON, sin literales |
| P3-B × P4 | Las banderas reales (`ga4_available` / `gsc_available`) llegan al `HotelFinancialData` del bloque FASE-K y el techo observado (`B_PLUS`) es atribuible a la analítica del hotel, no al cableado | MANIFEST de la corrida + `informe-observacion.md` §punto 9 |
| P5 × todo | `_save_cache` redacta secretos y el acta/MANIFEST de una corrida real **no** introducen clave ni material de cliente en ruta versionable | barrido propio sobre `evidence/FASE-P4/corrida/` |
| P1 × P2 × P6 | El bloqueo depende de **dos llaves**, no de una (corregido por medición el 2026-09-15): `blocks_publish` es el `and` de tres condiciones —hallazgos de revisores, gates y `GATE_BLOCKING_ENABLED`— **más** `GATE_ENFORCEMENT_ENABLED` en `finalize`. `GATE_BLOCKING_ENABLED` es solo el padre heredado (Q7). Verificar que el acta declara **ambas** y que apagar solo la del tribunal no reactiva el rename por otro camino | `acta_revision.json` → `enforcement.{blocking_env,enabled,suppressed_by_operator}` + el `and` en `judge.finalize` |

Entregable: tabla de 6 cruces con **coherente / incoherente (hallazgo con dueño)**, más el diff narrativo antes/después del defecto que motivó el plan: **hoy el veredicto consume las objeciones de sus propios revisores** — demostrarlo sobre el artefacto, no sobre el enunciado.

### T3: Greps residuales

| Patrón / hecho | Scope | Esperado |
|----------------|-------|----------|
| Actas construidas a mano como **sustituto** del flujo | `tests/test_ac_g4_g5_multi_hotel_matrix.py` (sigue en la suite y **no** referencia `DeliveryPackager`, medido con `grep -l`) + los otros 3 archivos nuevos de P6 | Decidir y escribir: ¿es **complementario** del flujo real (`test_p6r_full_flow_matrix.py`) o **sustituto** de AC-G4/G5? Si complementario, su docstring debe decir qué cubre y qué no; si sustituto, ❌ con dueño |
| Defaults inventados en `_observation_to_onboarding_format` (`epistemic_status='verified'`, `rooms=10`, `canal_directo_pct=20.0`, `campos_confirmados` fijo) | **`main.py`** — el converter vive ahí, **no** en `modules/` (un grep limitado a `modules/**` da 0 coincidencias y parece conforme) | **0** por defecto: la ausencia no puede volverse `verified` (cláusula 2 de AC-G2) |
| Duplicación del prefijo/derivación de ruta ZIP (familia I5, `L-SR3`) | `main.py` + `modules/commercial_documents/implementation_order_generator.py` | La derivación ya no se duplica en `main.py`: vive en `DeliveryPackager.write()` (R6 ✅). Pero **el consumo** en `generate_delivery_template` vuelve a escribir el literal `ASSETS/` al mirar `asset_names`, y `ImplementationOrderGenerator` conserva su propio camino divergente (dispuesto como legacy sin consumidores). Verificar que **ambos residuos están declarados** en el registro, no que hayan desaparecido |
| Lista de claves/secretos hardcodeada en vez de `config/client_material_policy.yaml` | `scripts/`, `modules/` | centralizada |
| `reviewer_reports` omitido del acta MD | `modules/quality_gates/tribunal/acta_writer.py` + acta real | **0** — la sección siempre visible con los cuatro estados |
| `judge.py` modificado por P6 (declaración del checklist: cero cambios) | `git diff` simbólico contra el corte `c31422a` | confirmado conforme |

Cada fila con el comando literal y su salida; 0 coincidencias o justificado en la matriz.

**Antes/después exigido por §4.6 (paso 3)**: la fase que tocó la superficie de secretos fue **P5**, y después de ella **no se volvió a correr el pipeline** — P6 y P6-R certificaron con tests offline. El contraste es entonces **artefacto de P4 (pre-P5) contra artefacto de P6-R (post-P5, generado por tests)**, nunca dos corridas reales:

| Superficie | Pre-P5 (P4) | Post-P5 (P6-R) | Qué probaría lo contrario |
|------------|-------------|----------------|---------------------------|
| URL del provider en el log de la corrida | clave en texto plano (F-P4.5) | sanitizada por `_sanitize_text`/`_sanitize_error` | que la ruta real que produjo el log de P4 no pase por el saner (hallazgo con dueño, no fix en esta fase) |
| Contenido versionable bajo `evidence/` | material de cliente en `origin/master` | alcance tracked + `NO_CUBIERTO` bloqueante | que un archivo ya versionado siga sin cobertura del checker |
| Superficie pública (AC-S3) | inventario declarado | mismo inventario re-medido con el check `[5/10]` activo | que el conteo dependa de la ruta de ejecución y no del árbol |

**Riesgo residual que la matriz debe declarar explícitamente**: ninguna verificación de esta fase sustituye una corrida real posterior a P5. Si T1 o T2 detectan que alguna ruta de producción quedó sin cubrir, el hallazgo va a ❌ con dueño y se propone sesión de recuperación con su propia corrida y consentimiento (§4.6 prohíbe correr `v4complete` aquí).

### T4: Triaje de Seguimientos + lecciones + write-back

- **Triaje** de `10-analisis` §Seguimientos Abiertos en tres casillas, con dueño nombrado: **bloquea RELEASE** / **se-documenta-como-límite** / **va a plan sucesor con AC propio**. Candidatos ya sobre la mesa: los 9 hallazgos de P4, F-P4.5 (clave en texto plano en log y cobertura del `_check_no_secrets`: solo `*.py`, 4 patrones de asignación), los 59 archivos versionados de `evidence/FASE-I/corrida/` (material de cliente en `origin/master`), la divergencia `analytics_status.gsc_available` que hace al diagnóstico afirmar "datos de búsqueda orgánica incluidos" sin incluirlos, y **las dos filas que el inventario de AC-S4 dejó abiertas al desbloquear la publicación** (`evidence/FASE-P5/AC-S3-S4-inventario-superficie.md` §AC-S4): confirmación de rotación de la key Gemini **local** (riesgo declarado local, no verificado) y **disposición de datos con cliente**. Verificar que ninguna se lee hoy como "cerrada" en el `10-analisis`.
- **Dos superficies rojas ya medidas, para asignar dueño en el triaje** (no son de este plan, pero VERIFY las encuentra al correr las validaciones): `python main.py --doctor` da **40 fallaron / 0 pasaron** (causa preexistente: skills bajo `.agents/skills/` sin `SKILL.md`, en `c31422a` antes y después de P6, `--quick` no lo invoca), y los documentos versionados siguen describiendo el tribunal **pre-enforcement** — `AGENTS.md` fila de `modules/quality_gates/tribunal/` ("Juez corre antes del packaging… `reviewer_reports` queda `[]`", ya falso) y `GUIA_TECNICA.md` "los 4 Bots **no alimentan** el veredicto". El segundo es de RELEASE con el bump; el primero necesita dueño propio.
- **≥3 lecciones de la verificación** (qué pasó / por qué / qué lo previene + INCLUIR/EXCLUIR), en `10-analisis` §Lecciones.
- **Write-back**: persistir las lecciones en la memoria del proyecto y re-ingresar el `10-analisis` al notebook `iah-cli-lecciones` **con título nuevo** si su contenido cambió tras la última ingesta (la idempotencia es por título).

---

## Post-Ejecución (OBLIGATORIO)

1. `dependencias-fases.md` → FASE-VERIFY ✅ con fecha y corte.
2. `06-checklist-implementacion.md` → sección §FASE-VERIFY ítem a ítem + fila de la tabla global.
3. `10-analisis-post-implementacion.md` → **matriz de certificación completa** (las 25 filas con Real/Status y nivel RE-V/CIT/CON), lecciones, triaje de Seguimientos.
4. `evidence/FASE-VERIFY/` → `MATRIZ-CERTIFICACION.md` + salidas de greps y corridas + tabla de los 6 cruces.
5. Registro **SIN** `--release`:
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-VERIFY --desc "Certificacion de 25 ACs contra artefacto real + integracion cross-fase de la ruta de delivery (P2 x P3A x P3B x P6)" \
    --check-manual-docs
```
6. `python scripts/run_all_validations.py --quick` (10/10) + commit de evidencia y docs.

---

## Criterios de Completitud (CHECKLIST)

- [ ] 25 filas de AC en la matriz, cada una con Real + Status + nivel RE-V/CIT/CON declarado
- [ ] Muestreo de integridad: ≥3 filas CIT re-medidas en disco con corrida propia y resultado escrito
- [ ] Tabla de 6 cruces cross-fase certificada sobre el artefacto real de P4
- [ ] Greps residuales con salida literal y 0 coincidencias o justificados
- [ ] Triaje de Seguimientos con las tres casillas y dueño por ítem
- [ ] ≥3 lecciones de la verificación + write-back a memoria
- [ ] Iteraciones medidas y escritas (R2.1; unidad declarada si D-V2.1)
- [ ] `run_all_validations.py --quick` TOTAL PASS
- [ ] Ninguna fila en `—` sin que su fase esté diferida por decisión registrada (L-R.1)

---

## Restricciones

- **NO modifica código fuente ni templates.** Un AC que falla va a ❌ con hallazgo y dueño en Seguimientos, y se planifica sesión de recuperación separada (patrón P5-R / P6-R). Está terminantemente escribir el acta de un AC a mano como sustituto del flujo.
- **NO ejecuta `v4complete` ni `v4audit`**: la corrida E2E ya ocurrió en P4; repetirla exige otra sesión, consentimiento y frescura registrados.
- **Mutaciones transitorias solo con instrumento versionado** (`nr7_p6r_mutation_checks.py`, que revierte, mide rojo y restaura con hash verificado). Prohibido editar archivos de producción a mano para probar un rojo.
- **Máximo 60 iteraciones** (R2.1), **R3** (4 tareas, 0 comandos largos), **R2.2** (citar símbolos, no números de línea).
- **NO** usar `--release` ni tocar `VERSION.yaml`: el bump, el tag y el archivado son de RELEASE, que ahora **cita** esta matriz en vez de producirla.
- **NO cierra el plan**: un ❌ aquí no se remedia en la misma sesión.
