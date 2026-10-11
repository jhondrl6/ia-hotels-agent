# FASE-C — Juez y acta honesta: precedencia única de tier, texto P6.2 verdadero, N8 visible

**ID**: FASE-C (plan CURA-COSTURA-TRIBUNAL-2026-10-11)
**Objetivo**: unificar la precedencia de `evidence_tier` entre Juez y Bot 4 (N6), corregir el texto vencido del finding de P6.2 que niega al revisor que corrió (AC12) y hacer visibles las excepciones de reglas HARD **y SOFT** en los cuatro sitios de captura de `contradiction_engine` (N8). El cableado del gate `hard_contradictions` queda fuera (deuda `S-CST-1`).
**Dependencias**: FASE-B ✅ (comparte `honesty_reviewer.py` — el orden B→C es obligatorio) y FASE-A ✅.
**Duración estimada**: 1 sesión.
**Complejidad**: MEDIA-ALTA — la unificación de precedencia es una decisión de diseño acotada con dos consumidores; N8 es un módulo vecino independiente.
**Skill**: `.agents/workflows/phased_project_executor.md` (workflow canónico).

## Contexto

El Juez lee el tier con una precedencia (escenarios→MANIFEST→fallback `C`) y Bot 4 con otra (MANIFEST→escenarios→fallback `UNKNOWN`, con el que el check de sobre-presentación ni siquiera corre): con manifest y escenarios en desacuerdo, Bot 4 se silencia mientras el Juez aplica primer piso (N6). El finding de P6.2 del acta dice que Bot 2 «no está implementado» mientras el propio acta publica su report — el artefacto niega al revisor que acaba de correr (L-VERIFY.4). Y `contradiction_engine` traga las excepciones de sus reglas con un `print`, en cuatro sitios de captura (los dos bloques de `detect_conflicts()` y los de `detect_hard_conflicts()` / `detect_soft_conflicts()`): ese silencio es real y se cura aquí (N8). **Lo que este plan no cura** (medido el 2026-10-11, tal como lo declaró la auditoría): el gate blocking `hard_contradictions` **no puede fallar hoy** aunque el motor funcione, porque el único `ValidationSummary` del pipeline se construye con `conflicts=[]` hardcoded, el dataclass `Conflict` no tiene campos `severity` ni `type`, y la clave alternativa `hard_contradictions_count` no tiene productor; la salida de `ConsistencyChecker` se cuelga en `assessment['consistency_report']` después de `run_publication_gates` bajo una clave que ningún gate lee. Por eso el cableado motor→gate es la deuda `S-CST-1` (maestro §5) y **no** una AC de este plan.

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| Preparación | ✅ Completada (2026-10-11) |
| FASE-A | ✅ Completada (contrato 4 estados + cache versionada + recibo) |
| FASE-B | ✅ Completada (consumidores + N5 + N7 + wrapper DEC-A1 eliminado) |

### Base Técnica Disponible

- `modules/quality_gates/tribunal/judge.py` (símbolos: `_compute_verdict`, `T1_CERTIFIABLE_CLAUSES`, la lectura de tier, el finding de P6.2 en la cláusula `NOT_EVALUABLE`, `blocks_delivery_zip`).
- `modules/quality_gates/tribunal/honesty_reviewer.py` (lectura de tier con fallback `UNKNOWN`).
- `data_validation/contradiction_engine.py` — medido: **cuatro** sitios de captura con `print` (el bloque HARD y el bloque SOFT de `detect_conflicts()`, más `detect_hard_conflicts()` y `detect_soft_conflicts()`).
- Actas reales previas en `evidence/` para tests R2.6 si aplica.

### Lecciones capitalizadas aplicables a esta fase

| ID | Lección (una línea) | Qué cambia en ESTA fase |
|----|---------------------|-------------------------|
| L-VERIFY.4 | El acta de Don Alfonso mostró P6.2 NOT_EVALUABLE con revisores corriendo | T2: el texto del finding deja de negar al revisor; la decisión de cláusula se registra con dueño, no se cambia `T1_CERTIFIABLE_CLAUSES` |
| L-T4A.5 | Tests que no alcanzan la rama no certifican | T1/T3: tests de combinaciones de tier y de excepción en regla HARD cuyos datos atraviesan la rama real |
| L-V.2 | VERIFY re-lee artefactos, no hereda conclusiones | T2: la corrección se verifica leyendo un acta generada, no el string del código |

## Tareas

### Tarea 1 — Precedencia única de evidence_tier (AC11, cura N6)

**Archivos afectados**:
- `modules/quality_gates/tribunal/judge.py`
- `modules/quality_gates/tribunal/honesty_reviewer.py` (solo su lectura de tier)
- `tests/quality_gates/tribunal/`

**Criterios de aceptación**:
- [ ] Un símbolo compartido resuelve el tier con UNA precedencia y UN fallback, consumido por Juez y Bot 4.
- [ ] El fallback elegido queda documentado en el símbolo y **es el mismo para ambos consumidores**; los tests cubren coinciden / falta una fuente / el fallback. **No se certifica el caso «MANIFEST y escenarios en desacuerdo»**: es una rama no producible en el régimen ZIP-only — `_resolve_manifest` de `judge.py` lo documenta (el glob `{hotel_id}_*/MANIFEST.json` buscaba un directorio descomprimido que el régimen ZIP-only nunca crea, L-E2E.1) y en la corrida real del 2026-10-07 Juez y Bot 4 leyeron los dos `B+`. Declarar certificada esa rama con un fixture que producción no genera está prohibido; la fila de la matriz lo declara con su motivo.
- [ ] Tests por causa + **mutation check** (invertir la precedencia → rojo; reactivar → verde; par en `evidence/FASE-C/`).
- [ ] Con `UNKNOWN` (o su equivalente unificado) el check de sobre-presentación de Bot 4 **deja de silenciarse**: publica el estado de no-evaluable según el contrato de FASE-B. Hoy `UNKNOWN` está en la lista que devuelve `None` antes de evaluar, así que el check no corre.

### Tarea 2 — Texto P6.2 verdadero + decisión de cláusula registrada (AC12)

**Archivos afectados**:
- `modules/quality_gates/tribunal/judge.py`
- `10-analisis-post-implementacion.md` del plan (§Seguimientos)

**Criterios de aceptación**:
- [ ] El finding de P6.2 describe el estado real (Bot 2 implementado y corriendo; cláusula no certificable por decisión de contrato), sin negar al revisor.
- [ ] La decisión «¿P6.2 pasa a cláusula evaluable?» queda registrada como diferida con dueño (maestro §5) — **no** se cambia `T1_CERTIFIABLE_CLAUSES` en esta fase.
- [ ] Verificación leyendo un acta generada por la suite (no el string del código).

### Tarea 3 — Reglas HARD y SOFT que no callan (AC13, cura N8)

**Archivos afectados**:
- `data_validation/contradiction_engine.py`
- `tests/data_validation/` (tests del engine)

**Criterios de aceptación**:
- [ ] Una excepción dentro de una regla **HARD o SOFT** produce un estado distinguido y visible (R2.9: sin hallazgos / lector fallido), nunca un `print` que deja `hard_contradictions` en verde.
- [ ] Los **cuatro** sitios de captura quedan cubiertos, con su test nombrado por la causa: los dos bloques de `detect_conflicts()` (el de reglas HARD y el de reglas SOFT) más `detect_hard_conflicts()` y `detect_soft_conflicts()`.
- [ ] **Mutation check** (revertir → rojo; reactivar → verde; par en `evidence/FASE-C/`).
- [ ] El **cableado del gate** `hard_contradictions` queda **fuera** de esta fase y del plan: es la deuda `S-CST-1` (maestro §5) con dueño Operador. Queda declarado en la evidencia que un motor que no pudo operar todavía no puede fallar el gate, para que nadie lea el verde del gate como prueba de esta cura.
- [ ] Sin clasificador tipado ni Jev aquí (fuera de alcance, maestro §4).

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| Combinaciones de tier | tests del tribunal | misma precedencia y mismo fallback para Juez y Bot 4; el desacuerdo manifest/escenarios **se declara no certificable** (régimen ZIP-only, L-E2E.1) y no se fuerza con fixture |
| Mutation check precedencia | ídem | par rojo/verde en evidence/FASE-C/ |
| Acta P6.2 | ídem | acta generada sin el texto que niega al revisor |
| Regla que revienta, por sitio de captura | tests/data_validation | cuatro rojos distinguibles: `detect_conflicts()` HARD, `detect_conflicts()` SOFT, `detect_hard_conflicts()`, `detect_soft_conflicts()`; estado visible, no verde silencioso; mutation check par rojo/verde |

**Comando de validación**:
```bash
./venv/Scripts/python.exe -m pytest tests/quality_gates/tribunal/ tests/data_validation/ -v
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

## Post-Ejecución (OBLIGATORIO)

⚠️ Ver template §5:

1. `dependencias-fases.md`: FASE-C ✅ con fecha y notas.
2. README del plan: progreso; métricas por referencia a `09` §D.
3. `09-documentacion-post-proyecto.md`: secciones A/B/D/E.
4. `10-analisis-post-implementacion.md`: Resumen de Ejecución + lecciones + **Seguimientos: la decisión de cláusula P6.2 con dueño** + decisiones arquitectónicas (unificación de precedencia, con alternativas rechazadas).
5. `00-lecciones-capitalizadas.md` §2: qué pasó realmente.
6. `evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-C/`: pares pre/post (R2.3), mutantes, pares rojo/verde de T1 y T3.
7. Registro de fase:
   ```bash
   ./venv/Scripts/python.exe scripts/log_phase_completion.py \
       --fase FASE-C --fecha <FECHA_DE_CIERRE_DE_ESTA_FASE> \
       --desc "Precedencia unica de evidence_tier; texto P6.2 verdadero; reglas HARD sin fallo silencioso" \
       --archivos-mod "modules/quality_gates/tribunal/judge.py,modules/quality_gates/tribunal/honesty_reviewer.py,data_validation/contradiction_engine.py" \
       --tests <TESTS_NUEVOS_DE_ESTA_FASE> --check-manual-docs
   ```
8. DOMAIN_PRIMER regenerado.
9. Pregunta de aporte durable de cualquier `CONTEXT-*.md` escrito en la sesión.

## Criterios de Completitud (CHECKLIST)

⚠️ Ver template §6. Resumen:

- [ ] AC11/12/13 legibles en sus artefactos
- [ ] `S-CST-1` (cableado motor→gate) registrado en `10-analisis` §Seguimientos con dueño Operador, y declarado en la evidencia de T3 para que el verde del gate no se lea como prueba de esta cura
- [ ] Mutation checks con pares rojo/verde en evidence/FASE-C/
- [ ] Decisión P6.2 registrada con dueño en seguimientos
- [ ] Delta R2.3 verificado restando; `--quick` verde; `log_phase_completion.py` ejecutado
- [ ] Cinco cortes declarados; sin commit (requiere autorización + pathspec)

## Restricciones

- **Presupuesto (R2.1)**: ~45 tool calls; unidad `tool calls`; corte: hasta listo para revisión (sin autorización de commit).
- **No tocar** `alignment_reviewer.py`, `llm_extractor.py`, `llm_provider.py`, `main.py`, `modules/quality_gates/publication_gates.py`. El cableado del gate `hard_contradictions` (motor→assessment→gate) está **fuera** del plan: es `S-CST-1` con dueño Operador (maestro §5); tocar `publication_gates.py` o `main.py` aquí ampliaría la fase sin AC que lo cubra.
- **No cambiar** `T1_CERTIFIABLE_CLAUSES` ni introducir clasificador tipado en `contradiction_engine` (fuera de alcance).
- Citas por símbolo (R2.2). Sin commit sin autorización + pathspec.
- **No delegable a subagente**: decisión de precedencia compartida entre dos consumidores que exigen contexto completo.

## Prompt de Ejecución

```
Actúa como agente de implementación del plan CURA-COSTURA-TRIBUNAL-2026-10-11.

Ejecuta únicamente FASE-C del plan .opencode/plans/CURA-COSTURA-TRIBUNAL-2026-10-11/
Lee 01-plan-maestro.md (§1 ACs y §4 restricciones), 00-lecciones-capitalizadas.md (§2 y §4), dependencias-fases.md y el workflow canónico.

OBJETIVO: Una precedencia de evidence_tier compartida por Juez y Bot 4; el finding de P6.2 describe el estado real y la decisión de cláusula queda con dueño; las reglas HARD de contradiction_engine no callan sus excepciones.

CONTEXTO:
- Fases previas completadas: Preparación, FASE-A, FASE-B
- Base técnica: judge.py, honesty_reviewer.py, data_validation/contradiction_engine.py
- No delegates a subagente

TAREAS:
1. T1 Precedencia única de tier con símbolo compartido y fallback único (AC11, mutation check; el desacuerdo manifest/escenarios se declara no certificable en régimen ZIP-only)
2. T2 Texto P6.2 verdadero + decisión registrada con dueño (AC12)
3. T3 Excepciones de reglas HARD y SOFT visibles en los CUATRO sitios de captura (AC13, mutation check); el cableado del gate hard_contradictions queda fuera (S-CST-1)

CRITERIOS:
- AC11/12/13 legibles en artefactos; tests por causa; delta R2.3; decision P6.2 en seguimientos; ningún fixture que producción no genera

VALIDACIONES:
- pytest tests/quality_gates/tribunal/ tests/data_validation/ -v
- run_all_validations.py --quick
- log_phase_completion.py --fase FASE-C --fecha <fecha de cierre>
```
