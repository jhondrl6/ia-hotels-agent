# Dependencias entre Fases — ESTABILIZACION-PRE-TRIBUNAL-2026-09-03

> Grafo de dependencias, conflictos de archivo y reglas de paralelización.
> **R1 del executor**: una fase por sesión. Este archivo existe para que cada sesión sepa qué NO puede
> tocar y qué debe esperar.

> ⚠️ **Regla transversal (L-A6, `10-analisis` §8) — aplica a TODAS las fases**: las citas de **número de
> línea** de este plan pueden estar **desfasadas**. Cada fase que edita código desplaza las líneas que las
> fases posteriores citan, y nadie las re-verifica. Medido al cerrar FASE-A: **4 citas falsas**, la peor
> repetida **12 veces en 6 archivos** (V6 citaba `v4_diagnostic_generator.py:3189-3194`, que ya era la
> llamada a `detect_pains`; el `except Exception: return brechas` real estaba en `:3197-3202`). Las 4
> quedaron corregidas el 2026-09-03, pero la **clase** sigue viva.
>
> **Antes de editar una región citada**: `grep`/`Read` para confirmar que la línea contiene lo que el plan
> dice. Si difiere → editar la región **correcta**, corregir la cita en el plan y registrarlo en
> `10-analisis` §5. **Preferir símbolos** (`def _pain_to_brecha`) sobre números de línea al citar: los
> símbolos no se desplazan.

---

## 0. Estado de ejecución

| Fase | Estado | Fecha | Qué desbloquea ahora |
|------|--------|-------|----------------------|
| **A** | ✅ Completada | 2026-09-03 | **B**, **C** (vía B), **D** — el canónico existe en `modules/common/service_identity.py` |
| B | ⬜ Pendiente | — | C, E, H |
| C | ⬜ Pendiente | — | F, G, I |
| D | ⬜ Pendiente | — | F, I |
| E | ⬜ Pendiente | — | F, I |
| F | ⬜ Pendiente | — | G, H, I |
| G | ⬜ Pendiente | — | H, I |
| H | ⬜ Pendiente | — | I |
| I | ⬜ Pendiente | — | VERIFY |
| VERIFY | ⬜ Pendiente | — | RELEASE |
| RELEASE | ⬜ Pendiente | — | — |

**Notas de ejecución de FASE-A** (relevantes para las fases que heredan sus archivos):

- El canónico vive en **`modules/common/service_identity.py`** (no en `asset_generation/`, como predecía
  `09` §A). Motivo: `modules/common/` no importa nada del proyecto, así que `asset_generation`,
  `commercial_documents` y `financial_engine` pueden consumirlo sin ciclo. **Cualquier fase que necesite
  identidad servicio↔asset↔pain importa de ahí; crear otra tabla es L-NC4 y el guardián AST la detecta.**
- Arquitectura de **dos capas**: Capa 1 = `PainSolutionMapper.PAIN_SOLUTION_MAP` (27 pains, universo de
  pain_id, contenido intacto). Capa 2 = `SERVICE_IDENTITIES` (8 entradas). Ningún registro puede declarar
  un pain_id ausente de Capa 1 — eso es lo que fijan los contract tests.
- `PROPOSAL_SERVICE_TO_ASSET` es ahora **derivado** y su **orden de inserción es parte del contrato**
  (ordena la tabla de servicios de la propuesta). FASE-C, que reescribe los dos builders de
  `proposal_asset_alignment.py`, debe preservar ese orden o cambiarlo con decisión registrada.
- `v4_proposal_generator.py:1281-1289` (`service_brecha_candidates`) ya **deriva su identidad** del
  canónico; su **lógica** quedó intacta, como exigía A4. FASE-C reescribe la lógica sobre una identidad
  ya unificada.
- **FASE-B hereda una precondición dura (N-A1, medida en `evidence/FASE-A/faseA_narratives_audit.txt`)**:
  `_pain_to_brecha` descarta pains en silencio en `v4_diagnostic_generator.py:3346-3347`; `narratives`
  (`:3263-3344`) tiene **16** claves frente a las **27** de Capa 1 ⟹ **11 ausentes**, que son
  exactamente **los 9 pains muertos de V1 + 2 que sí se emiten y sí se descartan hoy**
  (`no_ga4_enhanced`, `low_ota_divergence`). `narratives` y `detect_pains` son las dos mitades del mismo
  agujero: **arreglar solo la emisión deja el fix de B inerte** (los 9 rebotan en `:3346`). La biyección
  de AC4 debe ser **triple**: mapa↔emisión↔narrativa. Ver `10-analisis` §5 S6/S12/S13.
- **Orden forzoso nuevo B→H para `low_ota_divergence`**: V7 (FASE-H) arregla el guard `__iter__` que hoy
  impide que dispare. Si H va sin que B le haya dado entrada en `narratives`, el pain pasa de **«nunca
  dispara»** a **«dispara y se desvanece»** — peor para auditabilidad, porque el test de V7 pasa y la
  caída se vuelve invisible en vez de inexistente. **FASE-H debe verificar** (leer
  `evidence/FASE-B/decision-pains-muertos.md`) que B resolvió ese pain **antes** de tocar el guard.
- **FASE-B hereda también el registro #15 (C-5 / S14)**: los pesos de impacto que sirve `narratives`
  viven en `config/regional_benchmarks.yaml::pain_narratives` — **4 copias literales idénticas** (una por
  región, sin anclajes YAML) + **16 fallbacks hardcodeados** en Python = **80 literales para 16 valores**.
  El censo de A no lo contó (corregido como C-5 en `evidence/FASE-A/censo-registros.md` §8.1). Medido en
  `evidence/FASE-A/faseA_yaml_narratives_audit.txt` y `faseA_yaml_region_blind.txt`. Si B rellena
  `narratives` a 27 sin decidir el origen del peso, los 11 pains nuevos heredan un default en silencio
  (familia V6/P11/S7, dinero-adyacente). Ver `10-analisis` §5 S14.
- **FASE-F hereda**: `PAIN_TO_PRESENCE_ASSET` (6 entradas) **no** se derivó — la derivación completa
  produce 13 y cambia la semántica de `apply_site_verification`. Es exactamente el doble oráculo de
  A4/V15. Ver `10-analisis` §5 S8.
- `pain_ledger.py` y `conditional_generator.py` quedan **liberados** (eran A-exclusivos).
  `proposal_asset_alignment.py` y `v4_proposal_generator.py` pasan a C.
  ⚠️ **`v4_diagnostic_generator.py` ya NO pasa limpio a H**: por N-A1, **B necesita la región
  `:3246-3347`** (`_pain_to_brecha` + `narratives`) y **H necesita `:3197-3202`** (V6) y **`:1953`**
  (V11). Son regiones **disjuntas** del mismo archivo ⟹ B y H pueden convivir, pero los cambios de B
  deben confinarse a su región (regla añadida en `05-prompt-inicio-sesion-fase-B.md` §Restricciones).
  `config/regional_benchmarks.yaml` queda asignado a **B** (S14).

---

## 1. Grafo de dependencias

```
                        ┌──────────────┐
                        │   FASE-A     │  Fuente única de identidad
                        │    (ALTA)    │  V2/V3/V14 · AC1-AC3
                        └──────┬───────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
      ┌──────────────┐  ┌─────────────┐  ┌──────────────┐
      │   FASE-B     │  │  FASE-D     │  │              │
      │ (MEDIA-ALTA) │  │   (MEDIA)   │  │              │
      │ V1 · AC4     │  │ H10 · AC7-8 │  │              │
      └──────┬───────┘  └─────────────┘  │              │
             │                ▲          │              │
             │                │          │              │
             ▼                │          │              │
      ┌──────────────┐        │          │              │
      │   FASE-C     │────────┘          │              │
      │  (MÁXIMA)    │  (C1 documenta la │              │
      │ Punto 8      │  interacción con  │              │
      │ AC5-AC6      │  V9/G4 p/ ledger  │              │
      └──────┬───────┘  vacío — spec en  │              │
             │          C, severidad en  │              │
             │          G4; SIN dep. dura│              │
             │                           │              │
             ▼                           │              │
      ┌──────────────┐                   │              │
      │   FASE-E     │◀──────────────────┘              │
      │   (MEDIA)    │  E depende de B (biyección       │
      │ A2 + A6      │  fija qué pain emite el ledger   │
      │ AC9          │  que E persiste/consuma)         │
      └──────┬───────┘                                  │
             │                                          │
             ▼                                          │
      ┌──────────────┐                                  │
      │   FASE-F     │◀─────────────────────────────────┘
      │ (MEDIA-ALTA) │  F depende de C (no_breach=0 cambia
      │ A4+A1+N11    │  el insumo del oráculo) y de E
      │ AC10-AC12    │  (snapshot persistido es el insumo
      └──────┬───────┘   del oráculo único)
             │
             ├──────────────────────────┐
             ▼                          ▼
      ┌──────────────┐          ┌──────────────┐
      │   FASE-G     │          │   FASE-H     │
      │ (MEDIA-ALTA) │─────────▶│ (BAJA-MEDIA) │
      │ Nivel 3.7    │ (orden   │ Nivel 3.8    │
      │ NR1-NR4      │  forzoso │ V6/V7/V8/    │
      └──────┬───────┘  por     │ V11/V12/V13  │
             │         conflicto└──────┬───────┘
             │         de archivo)     │
             └──────────┬──────────────┘
                        ▼
                ┌───────────────┐
                │    FASE-I     │  E2E ÚNICA v4complete
                │  (BAJA impl)  │  Hotel Salento Real
                │  NR6 + deltas │  ← requiere A-H ✅
                └───────┬───────┘
                        ▼
                ┌───────────────┐
                │  FASE-VERIFY  │  DIRECTO · no delegable (§4.6)
                │ AC1-12 + NR1-6│
                └───────┬───────┘
                        ▼
                ┌───────────────┐
                │ FASE-RELEASE  │  DELEGABLE · v4.75.0
                │   4.75.0      │
                └───────────────┘
```

---

## 2. Matriz de dependencias

| Fase | Depende de (duro) | Razón de la dependencia | Bloquea a |
|------|-------------------|-------------------------|-----------|
| **A** | — | Es la base: decide cuál registro manda | B, C, D, E, F, G, H |
| **B** | A | El candado de biyección (B3) valida contra el registro canónico de A2; sin él, fijaría una copia parcial | C, E, H |
| **C** | A, B | El punto 8 deriva la promesa del registro canónico (A) y de los pains que realmente se emiten (B). Construirlo antes produciría una propuesta dinámica sobre IDs fantasma | F, G, I |
| **D** | A | La severidad explícita clasifica gates cuyo insumo (`proposal_asset_alignment`) deriva del registro canónico | F, I |
| **E** | B | A2 persiste el snapshot que los consumidores usan para resolver presencia; A6 puebla `asset_path` de assets cuya identidad fija la biyección | F, I |
| **F** | C, E | F1 (oráculo único) consume el snapshot persistido por E1 y opera sobre una matriz donde C ya hizo `no_breach = 0`. F3 (N11) interactúa con la severidad de D | G, H, I |
| **G** | F | G3/G4 cierran escotillas del `_coverage_gate` cuyo criterio de presencia ya unificó F1; cerrarlas antes fijaría el criterio doble | H, I |
| **H** | B, F, **G** | H1 (V7) toca `pain_solution_mapper.py` que G también toca ⟹ **orden forzoso G→H**. H3 (V8) depende de la biyección de B | I |
| **I** | A-H ✅ | Es la validación integrada; correrla antes mediría un sistema a medio refactorizar | VERIFY |
| **VERIFY** | I | Certifica contra evidencia real de la corrida | RELEASE |
| **RELEASE** | VERIFY | El CHANGELOG y GUIA_TECNICA se alimentan de `09` y `10`, que VERIFY completa | — |

**Camino crítico**: A → B → C → F → G → H → I → VERIFY → RELEASE (9 sesiones).
D y E están fuera del camino crítico y pueden ejecutarse en cualquier hueco tras A y B respectivamente.

---

## 3. Conflictos de archivo (quién toca qué)

| Archivo | Fases que lo tocan | Orden forzoso | Naturaleza del conflicto |
|---------|--------------------|---------------|--------------------------|
| `modules/commercial_documents/pain_solution_mapper.py` | **B**, **G**, **H** | B → G → H | B edita `PAIN_SOLUTION_MAP` (`:60`) y `detect_pains` (`:339`); G amplía `_identify_critical_issues` que lo consume; H1 reemplaza el guard `__iter__` (`:453`) y H3 deduplica `low_organic_visibility` (`:677-701`) |
| `modules/quality_gates/publication_gates.py` | **D**, **F**, **G** | D → F → G | D reestructura `self.gates` (`:181-195`) y `check_publication_readiness` (`:1919`); F3 modifica `_coherence_gate` (`:458`); G1/G3/G4 modifican `_doc_audit_consistency_gate` (`:1464`) y `_coverage_gate` (`:1244`) |
| `modules/asset_generation/proposal_asset_alignment.py` | **A**, **C** | A → C | A3 migra `PROPOSAL_SERVICE_TO_ASSET` (`:22`) al canónico; C3 modifica los dos builders (`:575`, `:748`) y sus rutas de skip silencioso (`:609-612`, `:792-794`) |
| `modules/quality_gates/alignment_result.py` | **C**, **F** | C → F | C3 toca `_from_entries` (`:222-276`) y `compute_unresolved` (`:175-212`); F1 toca `_presence_resolved` (`:62`) — **la misma región** |
| `modules/quality_gates/delivery_quality_report.py` | **E**, **F** | E → F | E2 puebla `asset_path` (`:223`); F2 modifica la región de skip (`:251-255`), el summary (`:310-319`) y los defaults (`:325`) — adyacentes |
| `modules/commercial_documents/v4_proposal_generator.py` | **A**, **C** | A → C | A4 corrige el drift «8 vs 7» (`:1332`) — ✅ cerrado; C2 reescribe `service_brecha_candidates` (`:1281-1289`). ⚠️ **Corregido 2026-09-03**: esta fila atribuía a H2 «el `except Exception` de `_identify_brechas`», pero ese método **solo existe en `v4_diagnostic_generator.py:3116`** (`grep -rn "def _identify_brechas"` = 1 resultado) y el prompt de FASE-H no menciona este archivo. H2 ya está correctamente asignado en la fila siguiente |
| `modules/commercial_documents/v4_diagnostic_generator.py` | **A**, **B**, **H** | A → B → H | A3/A4 migran `ELEMENTO_KB_TO_PAIN_ID` (`:135-157`, `:160`, `:3067-3086`) — ✅ cerrado; **B edita `_pain_to_brecha` + `narratives` (`:3246-3347`) por N-A1**; H2 reemplaza el `except Exception: return brechas` + caché en **`:3197-3202`** (⚠️ el dossier V6 citaba `:3189-3194`, que hoy es la **llamada a `detect_pains`** — cita fósil verificada y corregida el 2026-09-03 en los 6 archivos del plan que la repetían) y H3 limpia residuos D6 (`:1953`, V11 — el dossier citaba `:1952`, off-by-one). Regiones **disjuntas** ⟹ convivibles, pero B debe confinarse a la suya |
| `config/regional_benchmarks.yaml` | **B** | — | B decide el origen de los pesos `pain_narratives` (4 copias literales idénticas + 16 fallbacks Python = 80 literales para 16 valores). Hallazgo C-5 / S14, post-censo de A |
| `modules/asset_generation/pain_ledger.py` | **A** | — | A3 migra `NORMALIZATION_RULES` / `PAIN_TO_PRESENCE_ASSET` (`:52-94`) |
| `modules/asset_generation/conditional_generator.py` | **A** | — | A3 migra `PAIN_TO_ASSET` (`:234-257`) y el import de `ELEMENTO_KB_TO_PAIN_ID` (`:314-326`) |
| `modules/commercial_documents/coherence_validator.py` | **C** (lectura), **F** (decisión) | C → F | C4 **no** puede apoyarse en `promised_assets_exist` (`:670`, acotado por `if not generated_assets:`, P12/A3); F3 decide sobre `is_coherent` (`:185-188`) |
| `AGENTS.md` | **D**, **RELEASE** | D → RELEASE | D3 corrige la tabla Módulos Activos y el bloque FASE 4.5; RELEASE corre `sync_versions.py` sobre el mismo archivo |
| `VERSION.yaml` | **RELEASE** únicamente | — | Ninguna fase intermedia toca la versión |

**Regla**: ninguna sesión puede editar un archivo cuya fase dueña anterior no esté ✅ en
`06-checklist-implementacion.md`. Si una fase necesita tocar un archivo "protegido", lo registra como
seguimiento abierto en `10-analisis-post-implementacion.md` y NO lo edita.

---

## 4. Paralelización permitida (dentro de una fase)

R1 prohíbe paralelizar **fases**. Dentro de una fase, la delegación paralela es:

| Fase | Tracks paralelos | Integración |
|------|------------------|-------------|
| **D** | Track 1 (D1+D2 estructura de severidad, DIRECTO) ‖ Track 2 (D3 corrección documental, DELEGADO) | Parent hace D4 (candado) y verifica que D3 y D1 queden en el **mismo commit** |
| **E** | Subagente 1 (E1 snapshot) ‖ Subagente 2 (E2 asset_path) | Parent hace E3 (tests) + E4 (verificación de los 6 consumidores) |
| **H** | Subagente 1 (H1+H2 en `pain_solution_mapper`/`v4_proposal_generator`) ‖ Subagente 2 (H3+H4 en `v4_diagnostic_generator`/`metadata_validator`) | Parent verifica que no haya solapamiento con G ya cerrado |
| **I** | Subagente único para I2 (comando largo, timeout 900, notify) | Parent hace I1 (pre-flight), I3 (evidencia) e I4 (comparación) |

Fases **A, B, C, F, G, VERIFY**: sin paralelización (decisión arquitectónica o juicio de plan).

---

## 5. Puntos de no-retorno

| Punto | Qué se cierra | Consecuencia si se rompe |
|-------|---------------|--------------------------|
| Fin de **FASE-A** | El registro canónico existe y los ≥9 derivan de él | Cualquier fase posterior que cree una tabla paralela re-fosiliza el drift (L-NC4) |
| Fin de **FASE-C** | `no_breach = 0` por construcción | Volver a la lista estática re-introduce la tautología de coverage y el `is_coherent = false` estructural (B5) |
| Fin de **FASE-D** | Severidad 11+2 en código **y** en docs, mismo commit | Docs y código vuelven a divergir (estado actual: docstrings dicen 10+3, código bloquea con 13) |
| Fin de **FASE-F** | `is_coherent` respetado o eliminado con decisión registrada | La deuda P9 (la más grave) sigue abierta y ningún acta futura hereda el veredicto real |
| **FASE-I** | Única corrida E2E del plan | Si falla, no hay segunda oportunidad presupuestada: se registra la anomalía, se clasifica (regresión vs infraestructura) y se decide en VERIFY |
