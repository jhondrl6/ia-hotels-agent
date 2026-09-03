# FASE-E — Auditabilidad: A2 persistir snapshot de presencia + A6 poblar `asset_path`

**ID**: ESTABILIZACION-PRE-TRIBUNAL-2026-09-03 / FASE-E
**Objetivo**: Hacer auditables post-hoc los dos datos que hoy se pierden: el **oráculo de presencia**
(A2 — decide `present_in_production` y por tanto `no_breach`, `unresolved`, `coverage_ratio` y G9, y
**no se escribe a disco**) y el **puntero al artefacto** (A6 — `asset_path` se serializa como `null`
incluso para la entrada LINKED cuyo asset sí se generó).
**Dependencias**: FASE-B ✅ (la biyección fija qué pain emite el ledger que el snapshot contextualiza)
**Duración estimada**: 2-3 horas
**Complejidad técnica**: **MEDIA**
**Modo de ejecución**: **DELEGADO** — 2 tracks paralelos localizados; parent integra y valida
**Skill**: `phased_project_executor.md` v2.18.0
**Presupuesto**: ≤30 iteraciones (R2 tope: 60)
**ACs que cierra**: AC9 · **Deudas que cierra**: H7 (parcial), A2, A6 · **Precondiciones del tribunal**: §10 #2 y #3

---

## Contexto

Ambos agujeros son de la misma familia: **el pipeline decide con información que no conserva**. No son
bugs de comportamiento — el sistema produce el resultado correcto hoy — sino de **auditabilidad**. Por
eso el dossier los coloca como precondiciones duras #2 y #3 del tribunal (§10): un revisor independiente
no puede revisar lo que no existe.

### A2 — El oráculo de presencia no se persiste (verbatim del dossier §9.1)

- **Qué**: `site_presence_report` es la entrada que decide `present_in_production` y por tanto
  `no_breach`, `unresolved`, `coverage_ratio` y G9. **No se escribe a disco.**
- **Evidencia**: `find output -iname "*site_presence*"` → **0 resultados en todo el histórico**. Para
  medir hubo que reconstruir el snapshot a mano.
- **Consecuencia**: el número más decisivo del gate de alignment **no es auditable post-hoc**. El Bot 3
  del tribunal no puede revisar lo que no existe y ninguna corrida pasada puede re-evaluarse bajo un
  oráculo distinto.
- **Requisito**: persistir el snapshot canónico — **el concepto ya existe** (`main.py:2535` lo pasa como
  `site_presence_snapshot`, DT4-R2); falta escribirlo junto a los demás artefactos de `v4_audit/`.
- **Linaje (QMind, DT4 residual fixes)**: DT4-N2 ya había diagnosticado **4 rutas de reconstrucción** de
  SitePresence y prescrito *"calcular una vez por ejecución y propagar el snapshot normalizado — los
  gates deben validar, no descubrir ni reconstruir la evidencia primaria"*. **DT4-R2 implementó la
  propagación en memoria; A2 es la mitad pendiente (disco).** El mismo principio fundamenta el oráculo
  único de A4 (FASE-F).

⟹ Esta fase **no diseña nada nuevo**: completa una decisión tomada en DT4-N2 y ejecutada a medias en
DT4-R2.

### A6 — La matriz persistida pierde el puntero al artefacto (verbatim)

- **Qué**: `asset_path` se serializa como `null` incluso para la entrada LINKED cuyo asset sí se generó.
- **Evidencia** (entrada real de `proposal_asset_matrix.json`, versión 2.0):
  ```json
  {"alignment": "linked", "asset_path": null, "asset_type": "llms_txt",
   "confidence": 1.0, "pain_ids": ["ai_crawler_blocked"],
   "service_name": "Optimización para IA Generativa", "status": "LINKED"}
  ```
- **Consecuencia**: la trazabilidad **P6.3** (*"recomendación vendida → asset específico trazable"*)
  **no se puede verificar desde el artefacto**: no hay ruta al archivo. El Bot 3 tendría que adivinar el nombre.
- **Requisito**: poblar `asset_path` cuando el asset existe; es el campo que hace auditable P6.3.

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-A — Fuente única de identidad | ✅ Completada |
| FASE-B — Biyección mapa↔emisión | ✅ Completada |
| FASE-C — Punto 8 propuesta dinámica | ✅ Completada |
| FASE-D — Severidad 11+2 | ✅ Completada |

⚠️ **FASE-C cambió el contenido de la matriz** (`no_breach = 0` por construcción). Verificar el estado
real de `proposal_asset_matrix.json` post-C antes de asumir que la entrada de evidencia de A6 sigue
siendo representativa — el `asset_type: "llms_txt"` LINKED sí persiste (es el único LINKED del baseline),
pero la matriz ahora tendrá menos entradas NO_BREACH.

### Base Técnica Disponible

- `main.py:2535` — punto donde `site_presence_snapshot` ya se propaga en memoria (DT4-R2)
- `modules/asset_generation/site_presence_checker.py:73` — `PRODUCTION_PRESENT_STATUSES = ("exists", "exists_with_issues")` (oráculo permisivo, decisión FASE-SR-E H7/L-SR3)
- `modules/quality_gates/delivery_quality_report.py:223` — `asset_path=e.get("asset_path")` (el consumer que recibe `null`)
- Directorio de artefactos: `output/*/v4_complete/*/v4_audit/`
- **Baseline**: 848 passed / 2 skipped + delta A/B/C/D

---

## Tareas

### Tarea E1: A2 — Persistir `site_presence_snapshot` en `v4_audit/`  · *Track 1 (subagente)*

**Objetivo**: Escribir a disco el snapshot que ya se propaga en memoria, junto a los demás artefactos de
`v4_audit/`.

**Archivos afectados**:
- `main.py:2535` (y la región de escritura de artefactos de `v4_audit/`)
- Posible writer nuevo o extensión de uno existente

**Criterios de aceptación**:
- [ ] Tras una corrida, `find output -iname "*site_presence*"` → **≥1 resultado**
- [ ] El snapshot persistido contiene los campos que los **seis** consumidores leen (identificados en E4)
- [ ] Formato JSON estable y versionado (precedente: `proposal_asset_matrix.json` versión 2.0)
- [ ] Encoding **UTF-8 explícito** en el writer (FASE-P0-C / v4.46.1 ENCODING-SAFETY: Windows crashea sin él)
- [ ] **No se reconstruye** el snapshot en el writer: se serializa el objeto ya propagado por DT4-R2
      (*"los gates deben validar, no descubrir ni reconstruir la evidencia primaria"* — DT4-N2)
- [ ] Unicidad: **un solo** archivo por corrida, no uno por consumidor

### Tarea E2: A6 — Poblar `asset_path` en el caller del builder  · *Track 2 (subagente)*

**Objetivo**: Que `asset_path` deje de ser `null` cuando el asset existe.

**Archivos afectados**:
- El **caller** del builder aguas arriba de `delivery_quality_report.py:223` — identificarlo por grep
  (el consumer recibe `e.get("asset_path")`, así que el campo se pierde **antes**, en quien construye la entrada)
- `modules/asset_generation/proposal_asset_alignment.py` (los builders `:575` y `:748`) **solo si** el
  campo se pierde ahí

**Criterios de aceptación**:
- [ ] `asset_path` poblado para toda entrada cuyo asset fue generado
- [ ] La ruta es **verificable**: apunta a un archivo que existe en el output de la corrida
- [ ] `asset_path` sigue siendo `null` (o un estado explícito) cuando el asset **no** existe — no inventar rutas
- [ ] **NO modificar la forma pública de la entrada** más allá de poblar el campo existente
- [ ] ⚠️ **NO tocar las rutas de skip silencioso** (`:609-612`, `:792-794`) ni unificar los dos
      builders: la trampa **A5** y la decisión de builder único pertenecen al costado de FASE-C/F. Si
      FASE-C ya las trató, no re-abrirlo aquí

### Tarea E3: Tests retro-testeables de ambos  · *Parent*

**Objetivo**: Fijar con tests lo que E1/E2 agregan, de modo que una corrida pasada pueda re-evaluarse.

**Archivos afectados**:
- `tests/test_site_presence_persistence.py` (nuevo)
- `tests/quality_gates/test_delivery_asset_path.py` (nuevo)

**Criterios de aceptación**:
- [ ] Test que carga un snapshot persistido desde un fixture y verifica que los consumidores lo leen
- [ ] Test que falla si el writer deja de escribir el archivo
- [ ] Test de `asset_path` no nulo para un asset generado, y explícitamente nulo/estado para uno no generado
- [ ] **Test de no-reconstrucción**: verifica que el snapshot persistido es el mismo objeto propagado,
      no uno recalculado (anti-regresión de DT4-N2)
- [ ] Encoding UTF-8 testeado con un nombre de hotel con acentos/ñ (precedente: Salento Real, Castilla Real, Vísperas)

### Tarea E4: Verificar los seis consumidores  · *Parent*

**Objetivo**: Confirmar que los seis consumidores de `site_presence_report` leen el snapshot persistido
y no reconstruyen uno propio.

**Archivos afectados**: ninguno (verificación) + salida nueva `evidence/FASE-E/consumidores-snapshot.md`

**Criterios de aceptación**:
- [ ] Los 6 consumidores identificados por grep con `archivo:línea` exactos
- [ ] Por cada uno: ¿lee el snapshot propagado o reconstruye? (DT4-N2 diagnosticó **4 rutas de
      reconstrucción** — verificar cuántas siguen vivas)
- [ ] Las rutas de reconstrucción restantes quedan registradas como **insumo de FASE-F** (F1 unifica el
      oráculo; necesita saber cuántas fuentes de reconstrucción quedan)
- [ ] Salida escrita en `evidence/FASE-E/consumidores-snapshot.md`

---

## Delegación

| Track | Tareas | Agente | Justificación |
|-------|--------|--------|---------------|
| 1 | E1 | Subagente 1 | Persistencia localizada: replicar el patrón de writers de `v4_audit/` ya existente, sin decisión de diseño |
| 2 | E2 | Subagente 2 | Poblar un campo existente en un caller identificable por grep |
| Integración | E3, E4 | **Parent** | Requiere visión de los 6 consumidores y del contrato de DT4-N2 |

Los dos tracks no comparten archivo (ver `dependencias-fases.md` §3) ⟹ paralelizables sin conflicto.

**Prompt de delegación**: cada subagente recibe su tarea con los criterios de aceptación completos, la
restricción de NO tocar skip silencioso / builders, y la instrucción de reportar archivos modificados +
tests agregados. El subagente **no** decide el formato del snapshot (lo fija el parent en E3).

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| Persistencia del snapshot | `tests/test_site_presence_persistence.py` | Verde; falla si el writer no escribe |
| No-reconstrucción | ídem | Verde (anti-regresión DT4-N2) |
| Encoding UTF-8 | ídem | Verde con nombre con acentos/ñ |
| `asset_path` poblado | `tests/quality_gates/test_delivery_asset_path.py` | Verde; `null` solo cuando el asset no existe |
| Baseline | `tests/quality_gates` + `tests/asset_generation` | 848/2 + delta A/B/C/D preservado |
| Validadores | `scripts/` | `run_all_validations.py --quick` 7/7 |

**Comando de validación**:
```bash
./venv/Scripts/python.exe -m pytest tests/test_site_presence_persistence.py tests/quality_gates/test_delivery_asset_path.py -v > temp/faseE_persist.txt 2>&1
./venv/Scripts/python.exe -m pytest tests/quality_gates tests/asset_generation -q > temp/faseE_baseline.txt 2>&1
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
find output -iname "*site_presence*" | head -20   # 0 antes de E1; ≥1 después (sobre una corrida existente)
grep -rn "asset_path" modules/quality_gates/delivery_quality_report.py modules/asset_generation/proposal_asset_alignment.py
```

⚠️ `find output` sobre una corrida **existente** devolverá 0 (histórico sin snapshot). La verificación
positiva real ocurre en **FASE-I**. Aquí se valida con fixture + una corrida de prueba corta si hace falta.

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

1. **`dependencias-fases.md`** — marcar FASE-E ✅, fecha, notas
2. **`README.md` del plan** — tabla de progreso
3. **`06-checklist-implementacion.md`** — fila FASE-E, AC9, trazabilidad A2/A6 y deuda H7
4. **`09-documentacion-post-proyecto.md`** — Sección A (writer/archivo nuevo), B (auditabilidad),
   D (métricas), E (archivos afiliados)
5. **`10-analisis-post-implementacion.md`**
   - Resumen de Ejecución: fila FASE-E (iteraciones, notas de la delegación)
   - **Seguimientos abiertos**: rutas de reconstrucción de SitePresence que siguen vivas → **insumo de FASE-F**
   - Lecciones + Métricas
6. **`evidence/FASE-E/`** — `consumidores-snapshot.md` + logs de tests

**Cierre con script**:
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-E --desc "A2 persistir site_presence_snapshot + A6 poblar asset_path" --check-manual-docs
```
**SIN `--release`.**

---

## Criterios de Completitud (CHECKLIST)

⚠️ **Verificar ANTES de marcar como ✅ COMPLETADA** ⚠️

- [ ] **Tests nuevos pasan**: persistencia, no-reconstrucción, encoding, `asset_path`
- [ ] **AC9 cerrado (parcial — la prueba positiva es FASE-I)**: writer implementado + `asset_path` poblado
- [ ] **Los 6 consumidores identificados** en `evidence/FASE-E/consumidores-snapshot.md`
- [ ] **Rutas de reconstrucción restantes registradas** como insumo de FASE-F
- [ ] **Encoding UTF-8 explícito** en el writer nuevo
- [ ] **Un solo archivo de snapshot por corrida**
- [ ] **NO se tocaron** skip silencioso ni builders
- [ ] **Integración de los 2 tracks verificada por el parent** (no solo reportes de subagente)
- [ ] **Baseline preservado**: 848/2 + delta A/B/C/D
- [ ] **Validaciones**: `run_all_validations.py --quick` 7/7
- [ ] **Los 5 archivos de plan actualizados**
- [ ] **Evidencia preservada**: `evidence/FASE-E/`
- [ ] **`log_phase_completion.py` ejecutado SIN `--release`**
- [ ] **Commit hecho** referenciando FASE-E

---

## Restricciones

**Alcance — qué NO está en esta fase**:
- ❌ **NO unificar el oráculo de presencia** (A4) — FASE-F. Aquí se **persiste** el existente
- ❌ **NO unificar los dos builders** ni tocar el skip silencioso (A5) — ya tratado en FASE-C
- ❌ **NO modificar `BLOCKING_GATE_NAMES`** ni la lógica de skip de G9 (A1) — FASE-F
- ❌ **NO tocar `publication_gates.py`** — FASE-F/G
- ❌ **NO tocar `VERSION.yaml`** — FASE-RELEASE
- ❌ **NO ejecutar un `v4complete` completo**: la única corrida E2E del plan es FASE-I

**Restricciones técnicas**:
- Python del venv: `./venv/Scripts/python.exe`
- Pytest en lotes pequeños con salida a archivo; **nunca** `tests/commercial_documents` completo
- Writers con encoding UTF-8 explícito (v4.46.1 ENCODING-SAFETY)
- Los subagentes en Windows **no pueden** importar `bs4`/`selenium` — si un track lo necesitara,
  ejecutarlo en el parent (lección del executor)

**Dependencia que no se puede modificar**: la propagación en memoria de DT4-R2 (`main.py:2535`). Esta
fase **escribe** lo que ya se propaga; no cambia cómo se propaga.

---

## Prompt de Ejecución

```
Actúa como integrador senior en el repo iah-cli (Python, Windows, ./venv/Scripts/python.exe).
Vas a delegar 2 tracks en paralelo e integrar tú los tests y la verificación.

OBJETIVO: Auditabilidad — A2 persistir el snapshot de presencia (hoy decide no_breach/unresolved/
coverage_ratio/G9 y NO se escribe a disco: find output -iname "*site_presence*" → 0 en todo el
histórico) + A6 poblar asset_path (hoy null incluso para la entrada LINKED cuyo asset sí se generó).

CONTEXTO:
- Plan: .opencode/plans/ESTABILIZACION-PRE-TRIBUNAL-2026-09-03/
- Dossier §9.1 A2 y A6 (verbatim), §10 precondiciones #2 y #3
- Linaje: DT4-N2 diagnosticó 4 rutas de reconstrucción de SitePresence y prescribió "calcular una vez
  y propagar — los gates validan, no reconstruyen". DT4-R2 implementó la propagación EN MEMORIA
  (main.py:2535 site_presence_snapshot). A2 es la mitad pendiente: DISCO.
- FASE-A/B/C/D ✅ completadas
- Evidence de A6: proposal_asset_matrix.json v2.0 tiene {"asset_type":"llms_txt","status":"LINKED",
  "asset_path":null,...}

DELEGACIÓN:
- Subagente 1 → E1: writer del snapshot en v4_audit/. UTF-8 explícito. NO reconstruir: serializar el
  objeto ya propagado. Un solo archivo por corrida, formato JSON estable y versionado.
- Subagente 2 → E2: poblar asset_path en el CALLER del builder (identificar por grep aguas arriba de
  delivery_quality_report.py:223). Ruta verificable; null solo si el asset no existe.
- Los tracks no comparten archivo → paralelizables.

PARENT (tú):
- E3: tests/test_site_presence_persistence.py + tests/quality_gates/test_delivery_asset_path.py,
  incl. test de NO-reconstrucción y de encoding UTF-8 con acentos/ñ
- E4: identificar los 6 consumidores de site_presence_report por grep con archivo:línea; cuántos leen
  el snapshot vs cuántos reconstruyen. Salida: evidence/FASE-E/consumidores-snapshot.md
- Integrar los 2 tracks y verificar tú mismo (no confiar solo en los reportes de subagente)

CRITERIOS:
- AC9: writer implementado + asset_path poblado (la prueba positiva real es FASE-I)
- Baseline 848/2 + delta A/B/C/D preservado; run_all_validations.py --quick 7/7

RESTRICCIONES (críticas):
- NO unificar el oráculo de presencia (A4 → FASE-F); NO unificar builders ni tocar skip silencioso
  (A5 → ya tratado en FASE-C); NO tocar BLOCKING_GATE_NAMES ni el skip de G9 (A1 → FASE-F)
- NO tocar publication_gates.py; NO tocar VERSION.yaml
- NO ejecutar un v4complete completo (la única corrida E2E es FASE-I)
- Pytest en lotes pequeños con salida a archivo; NUNCA tests/commercial_documents completo (~8GB)
- Los subagentes en Windows no pueden importar bs4/selenium

POST-EJECUCIÓN (obligatoria):
Actualizar dependencias-fases.md, README.md, 06-checklist-implementacion.md,
09-documentacion-post-proyecto.md (A/B/D/E), 10-analisis-post-implementacion.md (Seguimientos: rutas de
reconstrucción vivas → insumo de FASE-F), evidence/FASE-E/.
Luego: log_phase_completion.py --fase FASE-E --desc "..." --check-manual-docs  (SIN --release).
Commit referenciando FASE-E.
```
