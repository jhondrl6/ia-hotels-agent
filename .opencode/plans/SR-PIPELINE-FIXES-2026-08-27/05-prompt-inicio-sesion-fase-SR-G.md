# FASE-SR-G — Fixes de Display y Jerga: CG-TIER-CONSISTENCY + CG-TECH-JARGON

**ID**: FASE-SR-G
**Objetivo**: Cerrar los dos hallazgos restantes de H6: (6.3) `CG-TIER-CONSISTENCY` falló comparando "Tier B" vs "D" — display string vs valor canónico (L30: comparar SIEMPRE la fuente de verdad, nunca strings de presentación); (6.4) `CG-TECH-JARGON` detectó jerga técnica "sin costo (fallback)" visible al cliente en la propuesta (L27: reemplazo sin hardcodear — texto derivado de fuente única compartida entre generador y gate).
**Dependencias**: FASE-SR-C ✅ (mismo archivo `commercial_gate.py` — SR-C antes que SR-G) y FASE-SR-F ✅ (orden del plan).
**Complejidad**: Baja-Media · **Delegación**: ❌ DIRECTO (código + tests; decisiones ya pre-tomadas)
**Duración estimada**: 45 min · **Presupuesto**: ~15 iteraciones trabajo + ~15 verificación/docs (R2: máx. 60)

## Reglas de Sesión (MANDATORIO)

- R1: Una fase por sesión. R2: máx. 60 iteraciones (checkpoint + evidencia si se agota). R3: 4 tareas + 0 comandos largos.
- Python: `./venv/Scripts/python.exe`.
- ⚠️ NUNCA la suite completa de `tests/commercial_documents` en un proceso (memoria 2026-08-03: `test_proposal_generator.py` fuga ~8GB). Usar `-k` específico SIEMPRE.

## Contexto

**Lectura previa obligatoria**: CONTEXT-SALENTOREAL §7.3-7.4 (H6.3, H6.4), §8.2 (L30, L27), §9 #3 y #7 + plan maestro §8.

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-SR-A…SR-F | ✅ Completadas |

### Base Técnica Disponible (verificado contra código vivo)
- `modules/quality_gates/commercial_gate.py`: L81-82 (ids de gates), L665-709 (lógica `CG-TIER-CONSISTENCY`), L786-812 (lógica `CG-TECH-JARGON`).
- Corrida C: reporte de gates comerciales con `CG-TIER-CONSISTENCY` FAILED ("Tier B" vs "D") y `CG-TECH-JARGON` WARNING detectando la jerga en documentos cliente.
- `modules/commercial_documents/v4_proposal_generator.py`: L1189-1728 (clave L1248) — el texto literal `"sin costo (fallback)"` que llega a `02_PROPUESTA_COMERCIAL.md`.
- Fuente canónica de tiers: `config/pricing.yaml`. L30: display strings nunca se comparan; L27: el texto de negocio se deriva de una única fuente consumida por generador Y gate (no duplicado).

## Tareas

### T1: Investigar el mismatch de tier (B vs D)
**Archivos**: `commercial_gate.py` (L665-709), `config/pricing.yaml` (tiers canónicos), punto de asignación del tier al documento comercial.
**Criterios**:
- [ ] Determinar cuál lado está mal: ¿el documento prometió "B" desde una fuente/display equivocado, o el gate compara un display string contra el valor crudo?
- [ ] Localizar dónde se asigna el tier al documento (y de qué tipo de campo lo toma: canónico vs display)

### T2: Fix CG-TIER-CONSISTENCY (L30)
**Criterios**:
- [ ] Comparación normalizada a valores canónicos: ambos lados desde `config/pricing.yaml` (fuente única)
- [ ] Si el documento toma el tier de un display string: corregir la asignación para consumir la fuente canónica
- [ ] El gate sigue detectando mismatches REALES (test negativo obligatorio — no enmascarar)

### T3: Fix CG-TECH-JARGON (L27)
**Criterios**:
- [ ] Reemplazar "sin costo (fallback)" (L1248 y residuos en L1189-1728) por lenguaje de negocio comprensible para el hotel
- [ ] Sin hardcodear el nuevo texto en dos sitios: un mapeo/glosario único consumido por generador y gate
- [ ] Grep: 0 residuos de "sin costo (fallback)" en el repo

### T4: Tests + greps + docs
**Criterios**:
- [ ] Test TIER: mismatch real detectado; igualdad canónica (aunque los display strings difieran) NO dispara el gate
- [ ] Test JARGON: documento regenerado sin jerga; el patrón queda cubierto por el glosario
- [ ] Greps de residuos + docs post-fase (sección Post-Ejecución)

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| TIER canónico | tests de `commercial_gate` (específicos, `-k tier`) | solo mismatches reales disparan |
| JARGON cubierto | ídem (`-k jargon`) | 0 jerga en documentos regenerados |

**Comandos** (procesos aislados, salida a archivo):
```bash
./venv/Scripts/python.exe -m pytest tests/quality_gates -k "commercial or tier or jargon" -v > temp/fase_sr_g_tests1.txt 2>&1
./venv/Scripts/python.exe -m pytest tests/commercial_documents -k "tier or jargon" -v > temp/fase_sr_g_tests2.txt 2>&1
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

## Post-Ejecución (OBLIGATORIO — antes de cerrar la sesión)

1. `dependencias-fases.md` §2 → ✅. 2. `README.md` → ✅. 3. `06-checklist` → SR-G. 4. `09-documentacion` → B/D/E + Notas. 5. `10-analisis` → Resumen + lecciones (L30/L27 aplicadas). 6. `evidence/FASE-SR-G/` → diff + tests. 7. Registro (SIN `--release`):
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-SR-G --desc "Fix display CG-TIER-CONSISTENCY (comparacion canonica desde pricing.yaml) + CG-TECH-JARGON (glosario unico, sin hardcodeo)" --archivos-mod "modules/quality_gates/commercial_gate.py" --tests "<N reales>" --check-manual-docs
```
8. `./venv/Scripts/python.exe scripts/doctor.py --regenerate-domain-primer`

## Criterios de Completitud (CHECKLIST)

- [ ] Tests TIER/JARGON pasan; regresiones = 0
- [ ] `run_all_validations.py --quick` TOTAL PASS
- [ ] 0 residuos de "sin costo (fallback)" (grep verificado)
- [ ] Docs post-fase completos (1-8)
- [ ] Evidencia en `evidence/FASE-SR-G/`

## Restricciones

- Máx. 60 iteraciones; NO ejecutar v4complete/v4audit.
- NO cambiar la semántica de severidad de los gates (solo corregir la comparación y el texto).
- NO hardcodear el texto de negocio en el gate Y en el generador (una sola fuente).
- NO tocar `config/pricing.yaml` más allá de lectura (la fuente canónica no se reescribe para que pase el test — L3: tests de contrato contra la fuente dinámica).
- NO delegar a subagente; NO usar `--release` en log_phase_completion.
- AC10: capa financiera intacta.
