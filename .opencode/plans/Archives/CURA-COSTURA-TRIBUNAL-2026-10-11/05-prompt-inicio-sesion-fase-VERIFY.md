# FASE-VERIFY — Certificación formal de ACs contra el output E2E real

**ID**: FASE-VERIFY (plan CURA-COSTURA-TRIBUNAL-2026-10-11)
**Objetivo**: certificar formalmente AC1..18 contra el output E2E real de FASE-E2E y la evidencia de las fases A-C. Sin código, sin v4complete.
**Dependencias**: TODAS las fases de implementación ✅ (A, B, C, E2E) — dependencia dura del executor.
**Duración estimada**: 1 sesión.
**Complejidad**: MEDIA — juicio de certificación con contexto completo del plan.
**Skill**: `.agents/workflows/phased_project_executor.md` §4.6 (workflow canónico).

## Contexto

Activación §4.6: ≥3 fases de implementación ✓, E2E ✓, ACs cross-fase ✓. Cada fase de implementación verificó sus criterios locales; esta fase verifica la **integración coherente** de todos los cambios sobre el artefacto que el sistema produce. Regla L-V.2: se re-leen los artefactos, no se heredan conclusiones de las notas de las fases.

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| Preparación | ✅ |
| FASE-A | ✅ |
| FASE-B | ✅ |
| FASE-C | ✅ |
| FASE-E2E | ✅ (output en `evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-E2E/` y `output/v4_complete/`) |

### Base Técnica Disponible

- Baseline y outputs: `evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-{A,B,C,E2E}/` (pares pre/post, mutantes, mediciones, run completo).
- La suite del tribunal y del engine (para re-corridas de tests que SUSTENTAN ACs; correr tests está permitido, escribir código no).
- `tests/` con su cifra canónica: `grep -rE "^\s*def test_" tests --include=*.py`.

### Lecciones capitalizadas aplicables a esta fase

| ID | Lección (una línea) | Qué cambia en ESTA fase |
|----|---------------------|-------------------------|
| L-V.2 | VERIFY re-lee los artefactos, no hereda conclusiones | Cada AC se certifica leyendo gate report/acta/recibos/tests de evidence/, no la nota de la fase |
| L-T4A.5 | Test que no alcanza la rama no certifica | Al certificar ACs de detección (AC2/10/11/13) se exige el par rojo/verde en evidence/, no solo el verde |
| L-VERIFY.4 | El acta puede mostrar cláusulas NOT_EVALUABLE con revisores corriendo | La certificación del acta de la corrida E2E distingue «no evaluado» legítimo de «sano falso» |

## Metodología (§4.6, 7 pasos)

| Paso | Acción | Entregable |
|------|--------|------------|
| 1 | Leer output post-fix y baseline | Contexto de comparación |
| 2 | Verificar cada AC contra output real | Columna «Real» de la matriz |
| 3 | Comparar antes/después (diff narrativo de los defectos 1-6 + N1-N9: qué rompía / qué lo previene ahora) | Diff documentado en el informe |
| 4 | Greps residuales de lo que debió desaparecer (wrapper DEC-A1, campo `confidence` del DTO/prompt, `print` silencioso de reglas HARD y SOFT, `[]` como retorno de no-OK, la clave `"type"` en los findings de Bot 4) | Tabla de patrones con 0 matches |
| 5 | Completar la matriz de verificación del `10-analisis` (defectos 1-6 + N1-N9 con Expected/Real/Status) | Matriz completa |
| 6 | Registrar lecciones de la verificación (o «sin lecciones nuevas») | Lecciones reales, sin cuota |
| 7 | `log_phase_completion.py` (SIN `--release`) + `run_all_validations.py --quick` | Registro + validación |

## Tabla de verificación por AC (método de lectura)

| AC | Método |
|----|--------|
| AC2..7 | Lectura de tests + mutantes + recibos reales en `evidence/FASE-A/`; greps 0 (confidence, wrapper) |
| AC1 | **Se certifica en FASE-B con AC15**: tests por causa sobre el objeto devuelto por la API checked (no el decorator `runtime_checkable`) + grep 0 del wrapper |
| AC2/10/11/13 | Par rojo/verde presente en evidence/ (R2.8: sin el lado rojo el AC queda ⚠️, nunca ✅). AC10 exige además las **dos cifras** (literales vs matcheadas) tomadas **con el patrón del código**; AC11 declara la rama manifest/escenarios no certificable en régimen ZIP-only |
| AC8/9 | Report del revisor en el acta de la corrida E2E + tests por estado |
| AC17 | Acta JSON y acta MD de un run de tests: un revisor con estado no-OK **no** proyecta `OK_NO_FINDINGS` y el veredicto no es `APROBADO-PARA-ENTREGA`; la etiqueta del miembro nuevo aparece legible en el MD |
| AC18 | Acta generada: el finding de Bot 4 proyecta `finding_type` (no `None`); grep 0 de la clave `"type"` en los findings de `honesty_reviewer.py` |
| AC5 | Recibo real de la corrida E2E con sus claves (modelo pedido y firmado, digest del prompt compuesto, usage) |
| AC14 | stdout («Onboarding data loaded») + gate report (coherence) + acta + recibo de la corrida + **estado de la extracción leído del recibo** con su motivo |
| AC15 | Grep 0 del wrapper en modules/ |
| AC16 | Resta de los pares pre/post de cada fase + `--quick` de la corrida de cierre |

**Estados de certificación**: ✅ legible en artefacto · ⚠️ no legible en artefacto (R2.4) · ❌ falla real → «Seguimientos abiertos» con dueño, sin parches.

## Reglas Específicas (§4.6)

- **Modo DIRECTO** (agente principal). No delegable.
- **NO modifica código**; un AC fallido se documenta en Seguimientos y se planifica recuperación aparte.
- **NO ejecuta `v4complete`** (el E2E ya ocurrió; el run del plan es único).
- No se re-transcriben cifras: la matriz referencia `09` §D y los artefactos de evidence/.

## Post-Ejecución (OBLIGATORIO)

1. `dependencias-fases.md`: FASE-VERIFY ✅.
2. README del plan: progreso.
3. `09-documentacion-post-proyecto.md`: §D métricas de la certificación si las hay.
4. `10-analisis-post-implementacion.md`: **Matriz de Verificación de Hallazgos completa (Real/Status)** + lecciones de la verificación + seguimientos.
5. `00-lecciones-capitalizadas.md` §2: qué pasó realmente.
6. `evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-VERIFY/`: greps residuales, resultado por AC, corridas de tests que sustentan la certificación.
7. Registro:
   ```bash
   ./venv/Scripts/python.exe scripts/log_phase_completion.py \
       --fase FASE-VERIFY --fecha <FECHA_DE_CIERRE_DE_ESTA_FASE> \
       --desc "Certificacion AC1..18 contra output E2E Don Alfonso" \
       --tests "<TESTS_NUEVOS_SI_LOS_HUBO>" --check-manual-docs --force-skip-docs --skip-reason "no-aplica: fase de verificacion sin codigo"
   ```
8. Pregunta de aporte durable de cualquier `CONTEXT-*.md` escrito en la sesión.

## Criterios de Completitud (CHECKLIST)

- [ ] AC1..18 con Real/Status leído de artefactos (los ⚠️ declarados, no maquillados)
- [ ] Matriz del `10-analisis` completa
- [ ] Greps residuales con 0 matches (tabla en evidence/FASE-VERIFY/)
- [ ] `--quick` verde; `log_phase_completion.py` ejecutado
- [ ] Cinco cortes declarados; sin commit (requiere autorización + pathspec)

## Restricciones

- **Presupuesto (R2.1)**: ~35 tool calls; unidad `tool calls`; corte: hasta listo para revisión.
- NO código, NO v4complete, NO cambios de templates. Correr tests está permitido; escribirlos no.
- Citas por símbolo (R2.2). Sin commit sin autorización + pathspec.

## Prompt de Ejecución

```
Actúa como verificador certificador del plan CURA-COSTURA-TRIBUNAL-2026-10-11.

Ejecuta únicamente FASE-VERIFY del plan .opencode/plans/Archives/CURA-COSTURA-TRIBUNAL-2026-10-11/
Lee 01-plan-maestro.md (§1 tabla de ACs y §4), 00-lecciones-capitalizadas.md (§2 y §4), dependencias-fases.md, 10-analisis-post-implementacion.md (matriz a completar) y el workflow canónico.

OBJETIVO: Certificar AC1..18 contra el output E2E real de FASE-E2E y la evidencia de FASE-A/B/C; completar la matriz de verificación; registrar lecciones de la verificación.

CONTEXTO:
- Fases previas completadas: Preparación, A, B, C, E2E
- Output E2E en evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-E2E/ y output/v4_complete/
- Modo DIRECTO: sin código, sin v4complete, sin subagentes

TAREAS:
1. Leer baseline y output; verificar cada AC con su método (tabla de este prompt)
2. Greps residuales (wrapper, confidence, print silencioso, [] de no-OK)
3. Completar matriz del 10-analisis (Expected/Real/Status) + lecciones
4. log_phase_completion + run_all_validations.py --quick

CRITERIOS:
- Cada AC con Real/Status legible en artefacto; los ⚠️ declarados; seguimientos con dueño

VALIDACIONES:
- run_all_validations.py --quick
- log_phase_completion.py --fase FASE-VERIFY --fecha <fecha de cierre>
```
