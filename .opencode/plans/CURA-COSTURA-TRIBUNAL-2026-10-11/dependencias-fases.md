# Dependencias de Fases — CURA-COSTURA-TRIBUNAL-2026-10-11

## Diagrama de dependencias

```
Preparacion (esta sesion)
        │
        ▼
    FASE-A  ── contrato 4 estados + cache versionada + recibo
        │         (llm_extractor.py, llm_provider.py)
        ▼
    FASE-B  ── consumidores: Bot 2 / Bot 4 + N5 + N7 + elimina wrapper DEC-A1
        │         (orden interno T3 -> T2 -> T1 -> T4)
        │         (alignment_reviewer.py, honesty_reviewer.py, outcome.py, acta_writer.py)
        ▼
    FASE-C  ── Juez/acta honesta + N8
        │         (judge.py, data_validation/contradiction_engine.py, honesty_reviewer.py*)
        ▼
    FASE-C2 ── AC19: el CRITICAL verificado bloquea aunque el insumo sea no-OK
        │         (outcome.py: verified_critical/verified_block + derive_corrective_actions; judge.py solo docstring)
        ▼
    FASE-E2E ── run UNICO v4complete Don Alfonso + evidencia + verificacion + docs
        │         (sin codigo; YAML de onboarding derivado bajo output/, warehouse intacto)
        ▼
    FASE-VERIFY ── certificacion AC1..18 contra output E2E (sin codigo)
        │
        ▼
    FASE-RELEASE-4.81.0 ── version bump + docs oficiales + write-back + archivado
```

(*) `honesty_reviewer.py` se toca en FASE-B (estados, N5, N7) y en FASE-C (N6, precedencia del tier). Por eso la secuencia A→B→C es obligatoria: ejecutar C antes que B produciría conflicto de edición sobre el mismo archivo.

## Conflicts de archivos por fase

| Archivo | FASE-A | FASE-B | FASE-C | FASE-E2E | FASE-VERIFY | RELEASE |
|---------|--------|--------|--------|----------|-------------|---------|
| `modules/quality_gates/tribunal/llm_extractor.py` | **EDITA** | — | — | — | — | — |
| `modules/providers/llm_provider.py` | **EDITA** | — | — | — | — | — |
| `modules/quality_gates/tribunal/alignment_reviewer.py` | — | **EDITA** | — | — | — | — |
| `modules/quality_gates/tribunal/honesty_reviewer.py` | — | **EDITA** | **EDITA** (N6) | — | — | — |
| `modules/quality_gates/tribunal/outcome.py` | — | **EDITA — obligatorio** (no condicional): `collect_reviewer_reports` computa el estado del revisor solo desde `findings_count`; es la pata de AC17 | — | — | — | — |
| `modules/quality_gates/tribunal/acta_writer.py` | — | **EDITA — obligatorio**: `_STATUS_LABELS` (5 etiquetas, reserva `.get(status, status)`) necesita la etiqueta del miembro nuevo de AC17 | — | — | — | — |
| `modules/quality_gates/tribunal/judge.py` | — | — | **EDITA** | — | — | — |
| `data_validation/contradiction_engine.py` | — | — | **EDITA** (N8, cuatro sitios de captura) | — | — | — |
| `modules/quality_gates/publication_gates.py` | — | — | — (fuera del plan: `S-CST-1`) | — | — | — |
| `main.py` | — | — | — (fuera del plan: `S-CST-1`) | — | — | — (cero cambios de código en el plan salvo los listados) |
| `output/<clientes_dir>/hotel_don_alfonso_onboarding.yaml` (derivado; `output/*/` esta en `.gitignore`, no se versiona) | — | — | — | **CREA** (T0 con `derivar_onboarding.py`; su copia y la procedencia van a `evidence/`) | — | — |
| `data/hotel_observations/observations.json` | — | — | — | **NO SE TOCA** (invariante con sha256 antes y despues en `pre-vuelo.md`; DEC-A4) | — | — |
| `tests/quality_gates/tribunal/*` | **EDITA** | **EDITA** | **EDITA** | — | — | — |
| `tests/data_validation/*` (contradiction) | — | — | **EDITA** | — | — | — |
| Docs del plan (`00/01/06/09/10`, `dependencias-fases.md`) | todas | todas | todas | todas | todas | todas |
| `VERSION.yaml`, `CHANGELOG.md`, `GUIA_TECNICA.md`, `docs/` | — | — | — | — | — | **EDITA** |

No hay dos fases que editen el mismo archivo de producción en paralelo (una fase = una sesión, secuenciales por R1). Los toques repetidos están resueltos por orden: `honesty_reviewer.py` (B→C) y —desde la decisión del Operador del 2026-10-12— `outcome.py` y `judge.py` (C→C2; en C2 el toque de `judge.py` es solo el docstring de la matriz, el predicado vive en `outcome.py`).

**Orden interno de FASE-B: T3 → T2 → T1 → T4** (la numeración de tareas y las ACs no cambian). Razón medida: encender el texto completo de la propuesta en Bot 4 (T2) antes de ajustar el patrón de CRITICAL (T3) mete ≥1 hallazgo espurio sobre la propuesta real del 2026-10-07 — de sus 5 coincidencias del grupo de cuantificadores, 3 son totales financieros o de tabla — y `verified_critical` **suprime el ZIP** en la corrida única de FASE-E2E, que no se puede repetir.

## Conflictos con trabajo ajeno

- El índice trae **staged** de otra sesión: 12 packs `briefing/FASE-*.md` de `Archives/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/` y `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-E2E/captura_stdout.txt`. Este plan **no los toca, no los despega, no los limpia**. Todo commit del plan lleva pathspec explícito.
- `.cache/tribunal/` tiene 3 entradas de formato viejo: quedan inertes con la clave versionada de FASE-A (sin migración, DEC del maestro).

## Puntos de decisión antes de fases

| Decisión | Resuelta | Efecto si cambia |
|----------|----------|------------------|
| URL canónica del run Don Alfonso | **SÍ — operador 2026-10-11**: `https://www.donalfonsohotel.com/`. La diferencia con el warehouse (allí el registro tiene `website: https://hoteldonalfonso.com/`) se resuelve **en el YAML derivado**, no editando el warehouse (DEC-A4) | Si el dominio no responde en el pre-vuelo de FASE-E2E, o si redirige a un dominio distinto del del derivado, la fase se detiene y consulta (checkpoint) |
| ¿P6.2 evaluable? | **NO — diferida con dueño** (maestro §5) | Un plan futuro cambia `T1_CERTIFIABLE_CLAUSES`; este plan solo corrige el texto vencido |
| ¿Alinear el warehouse antes del run? | **NO — revocado por la auditoría 2026-10-11** (DEC-A4 del maestro) | El warehouse es fuente inmutable con su sha256 publicado antes y después en `pre-vuelo.md`. El onboarding entra por el YAML derivado con `derivar_onboarding.py` (productor versionado de FASE-H) y su procedencia copiada a `evidence/`. Volver a editar `observations.json` falsifica la procedencia que `tests/test_fase_h_onboarding_procedencia.py` declara inmutable |
| ¿Cablear el gate `hard_contradictions` en FASE-C? | **NO — es `S-CST-1`, con dueño Operador** (maestro §5) | Requiere tocar `main.py` (`ValidationSummary.conflicts`), `data_structures.Conflict` (campo de severidad) y `publication_gates.py` en una fase propia. Mientras tanto el gate no puede fallar, y su verde no es evidencia de la cura de N8 |

## Estado de fases

| Fase | Estado | Fecha | Notas |
|------|--------|-------|-------|
| Preparación / Preparación-2 / 2b | ✅ | 2026-10-11 | Documental, publicado en `359ac57` |
| **FASE-A** | ✅ **COMPLETADA (sin commit)** | 2026-10-11 | Contrato de cuatro estados en la API checked + utilidad compartida + cache versionada (mutation check AC2 con par rojo/verde) + recibo por extracción + prompt con frontera de dato. Delta R2.3 **+46** (5207→5253 con el grep canónico); quick 13/13 tras regenerar `wiring_report.json`. AC1 se **cierra en FASE-B** con AC15 (DEC-A1 conserva el wrapper). Evidencia en `evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-A/`. Decisión nueva DEC-A5 (techo `max_tokens` 2000→4000) y tres seguimientos con dueño en `10-analisis` |
| FASE-B | ✅ **COMPLETADA (sin commit)** | 2026-10-11 | Orden interno ejecutado **T3→T2→T1→T4**. AC8/9/10/15/17/18 legibles en `evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-B/` y **AC1 cerrado con AC15** (el wrapper `extract_verbal_promises` ya no existe: `grep -rn` = 0 ocurrencias en `modules/`). Delta R2.3 **+27** (5253→5280, verificado restando); suite del tribunal 277 passed / 9 skipped / 0 failed; quick 13/13 tras republishar `wiring_report.json` (718→719 por el archivo nuevo). Tres mutantes con par rojo/verde (M1 guard de contexto, M2 frontera del `%`, M3 estado del acta). La medición de AC10 deja **10 coincidencias matcheadas vs 2 emitidas** sobre la propuesta del run de referencia. `outcome.py` y `acta_writer.py` editados como obliga DEC-A2. Presupuesto EXCEDIDO: ~80 tool calls contra ~55 (≈45 %; unidad auto-reportada, sin instrumento que la mida) |
| FASE-C | ✅ **COMPLETADA (sin commit)** | 2026-10-12 | AC11/12/13 legibles en `evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-C/`. Nace `modules/quality_gates/tribunal/evidence_tier.py` (precedencia escenarios→MANIFEST, fallback `"C"` con `declarado=False`) y lo consumen Juez y Bot 4; `OVER_PRESENTATION_NO_EVALUABLE` sustituye el silencio bajo tier no declarado; el acta generada ya no niega a Bot 2; los cuatro sitios de captura del motor publican tri-estado. Delta R2.3 **+29** (5280→5309, cero re-anclajes); tribunal+data_validation 460 passed / 9 skipped; selección del motor 55 passed; quick 13/13 (wiring 719→723). Tres mutantes en par rojo/verde, con la declaración de que `M1` **no** lo discrimina la rama de coincidencia. Presupuesto EXCEDIDO: ~52 contra ~45. **Dos escalados al Operador**: la cura de «`INPUT_NOT_EVALUABLE` no suprime el ZIP» (sin AC que la cubra, decisión previa a FASE-E2E) y `_extract_precision_tier`, que conserva su regla local fuera de AC11 |
| FASE-C2 | ⬜ | — | **AC19, fase nueva por decisión del Operador (2026-10-12)**: el CRITICAL verificado bloquea aunque el insumo sea no-OK. Corre en sesión propia **antes de FASE-E2E** (`05-prompt-inicio-sesion-fase-C2.md`); abre sobre el árbol de FASE-C sin commitear (18 rutas) |
| FASE-E2E | ⬜ | — | Run único |
| FASE-VERIFY | ⬜ | — | |
| FASE-RELEASE-4.81.0 | ⬜ | — | |


## Riesgos y plan de recuperación

- **Credencial de proveedor ausente en FASE-E2E**: la extracción terminaría `FALLIDO` (estado honesto tras FASE-A) y el veredicto perdería la pata LLM. Pre-vuelo T0 verifica presencia de credencial por nombre de variable y lo publica; si falta, la fase se detiene y consulta antes de gastar el run.
- **Onboarding que entra mudo por `ONBOARDING_FRESHNESS_HOURS`** (medido en el loader): si la variable está seteada, el YAML cuya `fecha_captura` cae fuera del límite se **descarta en silencio**, y la rama del warehouse no casa con la URL del run (su `website` es otro dominio). El resultado es «Using defaults» sin aviso. El pre-vuelo publica el estado de la variable y la rama efectiva de la sonda.
- **El dato de 2026-07-22 vence el techo de frescura del arnés el 2026-10-20**: medido, hoy (2026-10-11) tiene **81 días** y `run_once.py` fija `EDAD_MAXIMA_DIAS = 90`. Si FASE-E2E corre después del 2026-10-20, el requisito de edad sale NO-FAVORABLE y la fase **para y consulta** (re-datado del consentimiento del operador o posposición del run). Nunca se rellena ni se re-fecha el dato a mano.
- **`v4complete` supera 15 min en el subagente**: timeout 900 s y `notify_on_complete`; protocolo de re-spawn del executor (Re-spawn con timeout mayor, sin re-ejecutar lo ya correcto — el run es ÚNICO, un re-spawn que dispare una segunda corrida exige consultar al operador).
- **Fase agotada**: marcar `⏳ INCOMPLETA` en `dependencias-fases.md` con checkpoint, guardar evidencia en `evidence/FASE-*/`, retomar en sesión nueva desde el checkpoint.
