# Análisis Post-Implementación — CURA-COSTURA-TRIBUNAL-2026-10-11

> **Estado**: Preparación completada 2026-10-11 — plan creado; implementación pendiente.
> **Plan**: CURA-COSTURA-TRIBUNAL-2026-10-11
> **Versión objetivo**: 4.81.0
> **Origen**: `.opencode/context/CONTEXT-JEV-COSTURA-V4COMPLETE-2026-10-10.md` (§3 defectos 1-6, §10.2 hallazgos N1-N10, §10.3 blast radius, §10.4 causas raíz)

## Resumen de Ejecución (llenar al cierre de cada fase)

| Fase | Sesión | Estado | Iteraciones (unidad: tool calls) | delegate_task | Notas |
|------|--------|--------|----------------------------------|---------------|-------|
| Preparación | 2026-10-11 | ✅ | (auto-reporte de esta sesión) | No (directo) | Paso 0 + maestro + 6 prompts + checklist + 09/10 |
| Preparación-2 (auditoría aplicada) | 2026-10-11 | ✅ | 12 archivos `.md` editados; 180 líneas nuevas y 120 ajustadas (unidad contable en disco, reproducible con `diff` contra la pre-imagen; `git` no la mide porque la carpeta está untracked) | No (directo) | Rename `JEV-` → `CURA-`; AC13 partida y deuda `S-CST-1`; re-enunciadas AC1, AC4, AC5, AC10, AC11, AC13, AC14; AC17 y AC18 nuevas; `outcome.py` y `acta_writer.py` obligatorios en FASE-B con su orden T3→T2→T1→T4; T0 de E2E sustituido por YAML derivado con el warehouse inmutable; L-T4A.2 capitalizada. **Sin código, sin pytest, sin commit** |
| FASE-A | | ⬜ | | No (decisión arquitectónica) | |
| FASE-B | | ⬜ | | No (costura compartida) | |
| FASE-C | | ⬜ | | No | |
| FASE-E2E | | ⬜ | | Sí (run v4complete, timeout 900) | Run único; parent hace pre-vuelo/evidencia/docs |
| FASE-VERIFY | | ⬜ | | No (no delegable §4.6) | |
| FASE-RELEASE-4.81.0 | | ⬜ | | Delegable | |

## Matriz de Verificación de Hallazgos (llenar en FASE-VERIFY; Expected tomado del contexto de origen)

| # | Hallazgo | Expected | Real | Status |
|---|----------|----------|------|--------|
| 1 | Defecto 1: self-confidence auto-reportada sin consumidor (defecto 1 + N3) | Prompt sin confidence y DTO sin el campo; grep 0 | | |
| 2 | Defecto 2 (+N1, N2): respuesta ilegible → `[]` envenenada cacheable | Cuatro estados; truncamiento → NO_EVALUABLE; cache nunca persiste no-OK (par rojo/verde) | | |
| 3 | Defecto 3 (+N4): cache sin versión de contrato | Clave = `VERSION_PROMPT` + sha del prompt compuesto + sha del texto + **proveedor configurado** declarado (el modelo **no** entra); prompt distinto → clave distinta, medido con el test que lo exige | | |
| 4 | Defecto 4 (+N9): sin recibo | Recibo con digest del texto, digest del prompt compuesto, versión, proveedor servido, modelo **pedido** y **firmado** (si difieren), latencia, usage, digest respuesta cruda, estado y motivo | | |
| 5 | Defecto 5: contenido no-confiable sin frontera | Prompt delimita la propuesta como dato; test de forma | | |
| 6 | Defecto 6: modo auto sin registro de cuál sirvió | Proveedor **servido** en el recibo (`get_provider_name()`) y proveedor **configurado declarado** (`LLM_PROVIDER`) en la clave — no el resuelto en vivo | | |
| 7 | N5: regex de verificación solo sobre citas del LLM | Detección sobre texto completo; cita omitida aún detectada | | |
| 8 | N6: dos precedencias de evidence_tier | Símbolo compartido; mismas combinaciones para Juez y Bot 4 (par rojo/verde) | | |
| 9 | N7: falso positivo CRITICAL por «total» | Superficie medida **con el patrón del código** (`verification_patterns`), publicando ocurrencias literales y coincidencias matcheadas por separado; frontera del `%` curada (`\b` tras `%` no matchea ninguno de los 5 literales `100%` de la propuesta del 2026-10-07) y par rojo/verde | | |
| 10 | N8: reglas HARD y SOFT tragan excepciones con print | **Cuatro** sitios de captura visibles (`detect_conflicts()` en sus dos bloques, `detect_hard_conflicts()`, `detect_soft_conflicts()`) con par rojo/verde. El cableado motor→gate **no** se cura aquí: es `S-CST-1` en Seguimientos, y el verde del gate no prueba la ausencia | | |
| 11 | P6.2: acta niega al revisor que corrió | Texto verdadero; decisión de cláusula con dueño en Seguimientos | | |
| 12 | §10.3: acta se ve sana con extracción fallida | Bot 2/Bot 4 publican estado no evaluado; nunca OK_NO_FINDINGS ante no-OK (AC17 es la pata del acta) | | |
| 13 | AC14: run Don Alfonso | Onboarding inyectado por YAML derivado (warehouse con sha256 igual antes/después) + coherence ≥ 0.8 + acta + recibo en la corrida E2E + **estado de la extracción leído del recibo** con su motivo | | |
| 14 | AC16: no-regresión | Delta R2.3 por fase; resta verificada; quick verde | | |
| 15 | AC17: el acta ante extracción no-OK | `collect_reviewer_reports` + `_compute_verdict` atravesados por test: estado no-OK con `findings: []` no produce `OK_NO_FINDINGS` ni `APROBADO-PARA-ENTREGA`; el miembro nuevo tiene etiqueta en `acta_writer._STATUS_LABELS`; par rojo/verde en `evidence/FASE-B/` | | |
| 16 | AC18: claves de finding de Bot 4 | Un acta generada proyecta el hallazgo de Bot 4 con `finding_type` (hoy `None` en el acta del 2026-10-07); `derive_corrective_actions` lo nombra; 8 lecturas de la clave re-ancladas en los tres archivos de tests de Bot 4 | | |

## Lecciones Aprendidas (llenar; «sin lecciones nuevas» es un resultado válido, sin cuota)

Formato: **qué pasó / por qué / qué lo previene** + pertinencia (INCLUIR/EXCLUIR)

### Lecciones capitalizadas de planes anteriores (espejo de `00-lecciones-capitalizadas.md` §2)

| Lección | Aplicación en este plan |
|---------|-------------------------|
| L-T4A.3 | Cache de tests con tmp_path (FASE-A T3) — resultado real: (completar) |
| L-T4A.5 | Tests que alcancen la rama; cruce bidireccional (FASE-B T1/T2) — resultado real: (completar) |
| L-T4A.1 | Protocol runtime_checkable (FASE-A T1) — resultado real: (completar) |
| L-T4A.2 | Utilidad compartida para el mapeo de estados y el des-cercado de fences, no dentro de `LLMPromiseExtractor` (FASE-A T1, capitalizada en Preparación-2) — resultado real: (completar) |
| DA-T4A | Contrato en la interfaz; sin implementaciones nuevas (DEC-A1) — resultado real: (completar) |
| L-VERIFY.4 | Texto P6.2 verdadero (FASE-C T2) — resultado real: (completar) |
| L-VUP-13 | Sonda de onboarding pre-vuelo (FASE-E2E T0) — resultado real: (completar) |
| S-H13 | Clave de cache de contenido, no de identidad (FASE-A T3) — resultado real: (completar) |
| L-V.2 | VERIFY re-lee artefactos — resultado real: (completar) |

### Lecciones nuevas de este plan

(Registrar al cierre de cada fase; numeración L-CST-n si aplica.)

## Deudas definidas por este plan

| ID | Enunciado | Dueño |
|----|-----------|-------|
| `S-CST-1` | El gate blocking `hard_contradictions` no puede fallar en producción: el único `ValidationSummary` del pipeline se construye con `conflicts=[]` hardcoded, el dataclass `Conflict` no tiene los campos `severity`/`type` por los que el gate filtra, y la clave alternativa `hard_contradictions_count` no tiene productor | Operador |

## Seguimientos abiertos (llenar conforme avancen las fases)

| Tema | Estado | Acción futura |
|------|--------|---------------|
| `S-CST-1` — El gate **blocking** `hard_contradictions` no puede fallar en producción | **Abierta con dueño: Operador** (registrada el 2026-10-11 por la auditoría; fuera de alcance de este plan, maestro §5) | Fase propia: cablear motor→gate. Toca `main.py` (el único sitio que construye `ValidationSummary`, hoy con `conflicts=[]` **hardcoded**), `data_structures.Conflict` (no tiene campos `severity` ni `type`, y el gate filtra por ellos) y `publication_gates.py` (la vía alternativa lee `hard_contradictions_count`, clave **sin productor**). Los conflictos reales existen en `audit_result.validation.conflicts`, y la salida de `ConsistencyChecker` se cuelga en `assessment['consistency_report']` **después** de `run_publication_gates` bajo una clave que ningún gate lee. **Mientras tanto el gate no puede fallar**: su verde no es evidencia de que el motor operó |
| ¿P6.2 pasa a cláusula evaluable? | Diferida con dueño (operador) | Plan futuro cambia `T1_CERTIFIABLE_CLAUSES` |
| Dirección `modules/` → `scripts/` y SDK fuera del venv | Diferida con dueño (operador) | Plan de integración Jev (maestro §5) |
| Comparación de proveedores con recibo (opción C del contexto) | Diferida | Plan nuevo con pre-registro propio |
| Sobre-encaje inverso del matching difuso (L-T4A.4) | Sin medir | Medición propia si un incidente lo pide |
| Techo de crecimiento de la cache del extractor | (completar según lo que declare FASE-A) | Decisión con dueño o seguimiento |

## Métricas de Ejecución (referencias, no copias)

- Por fase: **ver `09-documentacion-post-proyecto.md` §D** y los pares `*_baseline_pre/post.txt` de `evidence/FASE-*/`.
- Run E2E: gate report, acta y recibos en `evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-E2E/`.

## Decisiones Arquitectónicas

| ID | Decisión | Rationale | Alternativas rechazadas | Fase |
|----|----------|-----------|-------------------------|------|
| DEC-A1 | API checked convive con wrapper transicional (no-OK → `[]` sin cachear) y FASE-B lo elimina | El cambio de contrato no puede romper consumidores en la misma fase (R3); el estado intermedio no envenena entradas nuevas y deja recibo | Editar los consumidores en FASE-A (viola el conteo R3 y mezcla dos superficies en una sesión); congelar la API vieja para siempre (shim permanente prohibido) | FASE-A/B |
| DEC-C1 | Sin migración de cache: claves viejas inalcanzables bajo la clave versionada | Precedente de la casa: migración = NO-EVALUABLE sin back-fill; las 3 entradas viejas son inertes | Back-fill de las 3 entradas (pisa el pasado sin valor) | FASE-A |
| DEC-A2 | `outcome.py` y `acta_writer.py` son **edición obligatoria** de FASE-B (antes: «si el estado exige publicarse») | Medido: `collect_reviewer_reports` computa `OK_NO_FINDINGS` **solo desde `findings_count`** y `_compute_verdict` decide con `status.blocks_approval`; sin ellos, un report con `extraccion: NO_EVALUABLE` y `findings: []` deja el acta sana y el veredicto aprobable — la cura quedaría sin efecto (AC17) | Dejar el acta como espejo del conteo de hallazgos (es el defecto); publicar el estado solo en el report del revisor y no en el acta (el humano lee el acta) | FASE-B |
| DEC-A3 | `llm_provider` se extiende **por vía aditiva** (método o metadatos nuevos), sin cambiar el tipo de retorno de `chat_completion` | Medido con `grep -rn "unified_request(" --include=*.py modules/ main.py scripts/ agent_harness/ data_validation/` (sin la definición): 6 sitios de producción delegan en `chat_completion` fuera del tribunal y ninguno consume `finish_reason`/`usage`/modelo firmado; cambiar el retorno obligaría a tocar 4 módulos ajenos al alcance de este plan | Romper el retorno y adaptar los 6 consumidores en FASE-A (viola R3 y mezcla superficies); que el extractor lea el objeto crudo del proveedor por la puerta de atrás (contrato implícito sin test) | FASE-A |
| DEC-A4 | El warehouse `data/hotel_observations/observations.json` es **fuente inmutable**; el onboarding del run entra por el YAML derivado con el productor versionado de FASE-H | El loader mira primero `clientes_dir` y solo después el warehouse, así que editar `website` era innecesario y falsificaba la procedencia; el registro del warehouse tiene otro dominio (`https://hoteldonalfonso.com/`) y su rama no casaría con la URL del run; `tests/test_fase_h_onboarding_procedencia.py` ya declara la rama YAML como la única favorable y el warehouse como inmutable (sha256 antes/después) | Alinear el campo `website` del warehouse + `validate.py` (la formulación anterior de T0); copiar el YAML sin procedencia ni sha; rellenar el dato a mano en el run | FASE-E2E |

## Checklist de Cierre (llenar en FASE-RELEASE-4.81.0)

- [ ] Todas las fases ✅ en `06-checklist-implementacion.md` y `dependencias-fases.md`
- [ ] Matriz de verificación completa (Real/Status en todas las filas)
- [ ] Seguimientos con dueño; lecciones registradas o «sin lecciones nuevas»
- [ ] Release 4.81.0 con CHANGELOG/GUIA_TECNICA/versiones sincronizadas; quick verde; modo completo publicado
- [ ] Write-back QMind `--upload` 0 y `--strict` N/N; orden R2.5/R2.10 respetado; plan en `Archives/`
