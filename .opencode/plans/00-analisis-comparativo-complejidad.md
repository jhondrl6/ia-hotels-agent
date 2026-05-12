# Analisis Comparativo de Complejidad Tecnica — REFACTOR-COHERENCIA-CASTILLAREAL

> **Fecha**: 2026-05-11
> **Plan**: `.opencode/plans/`
> **Metodologia**: Evaluacion por 7 dimensiones tecnicas, escala 1-10 (10 = maxima complejidad)
> **Proposito**: Identificar la fase de mayor riesgo, presupuestar iteraciones por sesion, y anticipar puntos de friccion.

---

## 1. Resumen Ejecutivo

**Fase de mayor complejidad tecnica: FASE-1-COH** (Unificar CoherenceValidator ↔ CoherenceGate)

Con un puntaje agregado de **60/70**, FASE-1-COH supera a las demas por:
- Es el unico punto donde un cambio mal implementado puede **romper todo el pipeline v4complete** (main.py es monolitico, ~3000 lineas, punto neuralgico).
- Requiere **code archaeology en 5 puntos distintos** del flujo de coherence_score.
- Integra **3 subsistemas distintos**: validator, gate, y report unificado.
- Presenta una **anomalia inexplicada** (score 0.8467 no trazable) que podria ser corrupcion de memoria o race condition.

**Ranking de complejidad (mayor a menor)**:

| Pos | Fase | Puntaje Agregado | Categoria |
|-----|------|-----------------|-----------|
| 1 | FASE-1-COH | 60/70 | CRITICA |
| 2 | FASE-3-CONTENT | 44/70 | MEDIA-ALTA |
| 3 | FASE-2-DEFAULT | 21/70 | BAJA |
| 4 | FASE-4-GATE | 22/70 | BAJA |
| 5 | FASE-5-VERIFY | 15/70 | OPERACIONAL |
| 6 | FASE-RELEASE | 14/70 | ADMINISTRATIVA |

---

## 2. Dimensiones de Evaluacion

### D1 — Alcance de Codigo
Mide cuantos archivos se tocan y que tan criticos son.

| Fase | Archivos | Lineas estimadas | Centralidad | Score |
|------|----------|-----------------|-------------|-------|
| FASE-1-COH | coherence_gate.py, main.py | ~50-80 modificadas | main.py = punto neuralgico del pipeline | **8/10** |
| FASE-2-DEFAULT | open_graph_generator.py, conditional_generator.py | ~10-20 modificadas | Generadores perifericos | **3/10** |
| FASE-3-CONTENT | local_content_generator.py, financial_engine/*, proposal_asset_alignment.py | ~30-50 modificadas | financial_engine afecta todos los deliveries | **6/10** |
| FASE-4-GATE | publication_gates.py (o equivalente) | ~5-15 modificadas | Un solo gate | **2/10** |
| FASE-5-VERIFY | Ninguno (solo lectura output/) | 0 | Verificacion pura | **1/10** |
| FASE-RELEASE | docs/*, VERSION.yaml | ~20-30 modificadas | Documentacion | **2/10** |

### D2 — Complejidad de Logica
Mide branching, estados, cascadas y numero de condiciones.

| Fase | Descripcion de la logica | Score |
|------|------------------------|-------|
| FASE-1-COH | Facade pattern, 5 scores divergentes, integrar 2 clases, unificar 3 consumidores | **9/10** |
| FASE-2-DEFAULT | Eliminar 3 strings hardcodeados, anadir 2 validaciones ValueError | **3/10** |
| FASE-3-CONTENT | 3 problemas en 3 dominios: validacion pre-LLM, unificacion de tier, renombrado con alias | **6/10** |
| FASE-4-GATE | Condicional simple: all() vs any() vs none() | **2/10** |
| FASE-5-VERIFY | Comandos de probe predefinidos, interpretacion de JSON | **3/10** |
| FASE-RELEASE | Procedimiento repetitivo (E1-E8) | **2/10** |

### D3 — Riesgo de Regresion
Mide la probabilidad de que un cambio rompa funcionalidad existente.

| Fase | Por que es riesgoso | Score |
|------|---------------------|-------|
| FASE-1-COH | main.py es el orchestrador. Un error en coherence_score afecta TODOS los deliveries (diagnostico, propuesta, gate, report). | **10/10** |
| FASE-2-DEFAULT | Solo afecta open_graph. Si la validacion es muy estricta, podria romper hoteles sin datos completos. | **3/10** |
| FASE-3-CONTENT | financial_engine afecta pricing de TODOS los hoteles. evidence_tier inconsistente podria cambiar tier de deliveries existentes. | **7/10** |
| FASE-4-GATE | Cambia estado de gate de WARNING a BLOCKED. Podria bloquear deliveries que antes pasaban. | **5/10** |
| FASE-5-VERIFY | Sin riesgo, solo lectura. | **1/10** |
| FASE-RELEASE | Sin riesgo de regresion funcional. Riesgo menor de docs desincronizadas. | **3/10** |

### D4 — Dificultad de Testing
Mide el esfuerzo de mocks, fixtures, edge cases y validacion.

| Fase | Que hace dificil el testing | Score |
|------|----------------------------|-------|
| FASE-1-COH | Requiere mock de CoherenceValidator dentro de CoherenceGate, verificar main.py wiring, y probar v4_complete_report JSON schema | **8/10** |
| FASE-2-DEFAULT | Validacion de inputs straightforward. Mock de hotel_data simple. | **4/10** |
| FASE-3-CONTENT | evidence_tier requiere mock de financial_sources con 3 fuentes. 3 modulos = 3 suites de tests. | **7/10** |
| FASE-4-GATE | 3 casos logicos + empty edge case. Simple. | **3/10** |
| FASE-5-VERIFY | No escribe tests, solo ejecuta probes. | **1/10** |
| FASE-RELEASE | No aplica testing de codigo. | **1/10** |

### D5 — Backwards Compatibility
Mide el cuidado necesario para no romper callers existentes.

| Fase | Compatibilidad requerida | Score |
|------|------------------------|-------|
| FASE-1-COH | execute() tiene firma publica. Si se cambia, hay que evaluar callers en main.py y posiblemente otros modulos. | **7/10** |
| FASE-2-DEFAULT | Los defaults eliminados NUNCA deberian usarse (eran bugs). Pero si alguien dependia del fallback silencioso... | **2/10** |
| FASE-3-CONTENT | all_aligned es publico, requiere alias deprecado. financial_engine cambia propagacion de tier. | **6/10** |
| FASE-4-GATE | Tests existentes podrian asumir WARNING para 100% ESTIMATED. Necesitan actualizarse. | **5/10** |
| FASE-5-VERIFY | N/A | **1/10** |
| FASE-RELEASE | N/A | **1/10** |

### D6 — Investigacion Requerida (Code Archaeology)
Mide cuanto hay que explorar antes de poder implementar.

| Fase | Que hay que investigar | Score |
|------|----------------------|-------|
| FASE-1-COH | Trazar 5 puntos de coherence_score en main.py. Explicar anomalia 0.8467. Entender facade H10 FIX. | **9/10** |
| FASE-2-DEFAULT | Localizar 3 lineas exactas. grep por otros defaults. | **3/10** |
| FASE-3-CONTENT | Encontrar donde computa evidence_tier en 2 sistemas (JSON writer + diagnostic generator). | **6/10** |
| FASE-4-GATE | Localizar donde vive asset_confidence (publication_gates.py o coherence_gate.py). | **3/10** |
| FASE-5-VERIFY | Interpretar output JSON (probes ya definidos). | **3/10** |
| FASE-RELEASE | Verificar formato CHANGELOG actual. | **2/10** |

### D7 — Puntos de Integracion
Mide cuantos subsistemas diferentes se conectan.

| Fase | Subsistemas conectados | Score |
|------|----------------------|-------|
| FASE-1-COH | CoherenceValidator, CoherenceGate, main.py (orchestrator), v4_complete_report, diagnostic YAML, gate_report | **9/10** |
| FASE-2-DEFAULT | OpenGraphGenerator, ConditionalGenerator | **3/10** |
| FASE-3-CONTENT | LocalContentGenerator, FinancialEngine, ProposalAssetAlignment, DiagnosticGenerator | **6/10** |
| FASE-4-GATE | AssetConfidenceGate (unico) | **2/10** |
| FASE-5-VERIFY | Consume TODOS los subsistemas (pipeline completo) | **5/10** |
| FASE-RELEASE | sync_versions, doctor, run_all_validations, git | **3/10** |

---

## 3. Radar de Complejidad (Textual)

```
DIMENSION              FASE-1  FASE-2  FASE-3  FASE-4  FASE-5  RELEASE
                       COH     DEFAULT CONTENT GATE    VERIFY
Alcance de codigo      8       3       6       2       1       2
Complejidad logica     9       3       6       2       3       2
Riesgo regresion       10      3       7       5       1       3
Dificultad testing     8       4       7       3       1       1
Backwards compat       7       2       6       5       1       1
Investigacion          9       3       6       3       3       2
Puntos integracion     9       3       6       2       5       3
                       ----    ----    ----    ----    ----    ----
TOTAL                  60      21      44      22      15      14
```

---

## 4. Presupuesto de Iteraciones Recomendado

Basado en la experiencia de fases anteriores (CHAN-2: ~34 iteraciones, FIN-4B: ~30 iteraciones) y la complejidad evaluada:

| Fase | Iteraciones trabajo | Iteraciones docs/verif | Total estimado | Margen de seguridad |
|------|--------------------|----------------------|----------------|-------------------|
| FASE-1-COH | 40-45 | 15-20 | **55-65** | RIESGO: Podria agotar 60 iteraciones. Considerar dividir en FASE-1-A (investigacion+fix gate) + FASE-1-B (fix main.py+tests) si T1/T2 consumen > 30 iteraciones. |
| FASE-2-DEFAULT | 15-20 | 10-12 | **25-32** | Seguro dentro del limite. |
| FASE-3-CONTENT | 30-35 | 15-18 | **45-53** | Seguro, pero cerca del limite. Priorizar T2 (evidence_tier) si se acorta el tiempo. |
| FASE-4-GATE | 15-20 | 10-12 | **25-32** | Seguro dentro del limite. |
| FASE-5-VERIFY | 10 (prep) + 1 cmd | 20 (verif+analisis) + 10 docs | **41** | Seguro. v4complete cuenta como 1 tool call aunque dure 10 min. |
| FASE-RELEASE | 25-30 | 10-15 | **35-45** | Seguro. |

---

## 5. Puntos de Friccion Anticipados

### FASE-1-COH — Riesgos especificos

| Riesgo | Probabilidad | Impacto | Mitigacion |
|--------|-------------|---------|------------|
| Anomalia 0.8467 es corrupcion de memoria / race condition | Media | Alto | Si no es trazable, documentar como "known issue" y mover a FASE-6-HOTFIX. No bloquear FASE-1. |
| execute() tiene callers externos ademas de main.py | Media | Alto | Buscar con grep todos los usos de `CoherenceGate().execute(` antes de cambiar firma. |
| main.py L2955-2960 depende de variables que se setean en scopes anidados | Alta | Medio | Leer 50 lineas antes y despues de cada punto de modificacion. No confiar solo en los numeros de linea del contexto. |
| Tests de quality_gates usan fixtures que dependen de execute() antiguo | Media | Medio | Ejecutar tests existentes ANTES de modificarlos para establecer baseline. |

### FASE-3-CONTENT — Riesgos especificos

| Riesgo | Probabilidad | Impacto | Mitigacion |
|--------|-------------|---------|------------|
| evidence_tier se computa en mas de 2 lugares (audit report, proposal, etc.) | Media | Medio | grep por `evidence_tier` en todo el repo antes de asumir solo 2 fuentes. |
| `all_aligned` tiene muchos consumidores externos | Baja | Medio | grep por `all_aligned` en todo el repo. Si hay > 5 consumidores, evaluar migracion progresiva. |
| local_content_generator usa `hotel_data["city"]` en multiples prompts | Alta | Bajo | grep por `"city"` en el archivo. Reemplazar TODAS las ocurrencias. |

### FASE-5-VERIFY — Riesgos especificos

| Riesgo | Probabilidad | Impacto | Mitigacion |
|--------|-------------|---------|------------|
| v4complete falla por un bug introducido en FASE-1-COH | Media | Alto | Si falla, identificar si es por cambio en main.py. Si es regresion, FASE-1 necesita hotfix. |
| hotelcastillareal output no se genera (problema de red/API) | Baja | Medio | Reintentar una vez. Si persiste, documentar y usar auditoria existente como baseline. |
| G6 (hotel_schema poblado) requiere onboarding que no existe | Alta | Bajo | G6 es EXPECTED FAIL. Documentar en analisis: "G6 requiere onboarding Tier B+, no disponible para Castilla Real". |

---

## 6. Recomendaciones de Ejecucion

### Para FASE-1-COH (CRITICA)
1. **Dividir si es necesario**: Si T1 (investigacion) consume > 15 iteraciones, considerar FASE-1-A (investigacion + fix gate) y FASE-1-B (fix main.py + tests + docs).
2. **Baseline de tests**: Ejecutar `pytest tests/quality_gates/` ANTES de tocar codigo. Guardar resultado.
3. **Firma publica**: Usar `execute_from_validator()` en vez de modificar `execute()` si hay callers externos.
4. **Anomalia 0.8467**: Si no es trazable en < 10 iteraciones, documentar como RIESGO conocido y continuar. No dejar que bloquee la fase.

### Para FASE-3-CONTENT (MEDIA-ALTA)
1. **Priorizar T2 (evidence_tier)**: Es el cambio con mayor impacto en todos los deliveries. Si hay que recortar, mantener T2 y posponer T3 (all_aligned) a otra fase.
2. **grep primero**: Antes de modificar, `grep -r "all_aligned" modules/` para contar consumidores.

### Para FASE-5-VERIFY
1. **G6 es EXPECTED FAIL**: hotel_schema requiere onboarding. No contar G6 como fallo de la refactorizacion.
2. **Umbral de exito**: 7/10 garantias en PASS = refactorizacion exitosa. G6 y G7 pueden ser EXPECTED FAIL.

---

## 7. Glosario de Categorias

| Categoria | Score Agregado | Significado |
|-----------|---------------|-------------|
| CRITICA | > 50 | Requiere atencion especial. Alta probabilidad de agotamiento o regresion. Considerar subdivision. |
| MEDIA-ALTA | 40-50 | Cuidado con el presupuesto de iteraciones. Priorizar tareas si el tiempo escasea. |
| BAJA | 20-35 | Segura dentro del limite de 60 iteraciones. Ejecucion directa. |
| OPERACIONAL | 10-20 | No modifica codigo. Riesgo tecnico minimo. |
| ADMINISTRATIVA | < 15 | Procedimiento repetitivo. Riesgo de olvidar pasos, no de bugs. |

---

*Documento generado como parte del plan maestro REFACTOR-COHERENCIA-CASTILLAREAL. Actualizar si el scope de alguna fase cambia durante la ejecucion.*
