# FASE-D: Freshness, Procedencia y Pulido — D9, D10, D11, D12, N4, N3, N5-N8

**ID**: COHERENCIA-FASE-D
**Objetivo**: Cerrar los hallazgos P2: constantes duplicadas (D9), dedup de redes (D10), reportes stale (D11/N4), label de occupancy por origen real (D12) y pulido de texto (N5-N8); verificar N3.
**Dependencias**: FASE-A ✅, FASE-B ✅ (N8 requiere D4 resuelto), FASE-C-B ✅ (mismo archivo, rangos disjuntos).
**Duración estimada**: 1 sesión (~40 iteraciones de 60).
**Skill**: `phased_project_executor` v2.13.0 · skill de apoyo: `iah-cli-output-forensics` (patrón subdirectory path mismatch, D11).

## Contexto

- **D11+N4 (freshness)**: el ZIP del 08-01 contiene `commercial_gates_report.json` stale (07-30) con CG-ROI-NEGATIVE BLOCKING y 7 gate reports históricos. Causas: la propuesta no regenera el reporte (v4_proposal_generator.py:629) y el packager copia v4_audit COMPLETO sin filtrar por run.
- **D12 (procedencia)**: occupancy 0.7843 = 800/1020 viene del onboarding (main.py:1763) pero se etiqueta "regional" según feature flag (main.py:1878/1937), no según el origen real.
- **D9/D10/N5-N8 (pulido)**: target fotos 20 vs 40+; "Instagram, Instagram, Facebook" sin dedup; "acima" (portugués); "Por que importa" sin acento; truncamiento `[:80]` a mitad de palabra; "70% de confianza" mal atribuido.
- **N3 (verificación)**: tras todos los fixes de texto (A, B, C-B, D), los docs entre runs ya NO deben ser copias byte-idénticas.

Fuente completa: contexto §5 FASE-4.

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-A / B / C-A / C-B | ✅ Completadas |
| FASE-D | ▶️ EN CURSO (esta sesión) |

## Modo de ejecución (delegate_task)

**DELEGADO PARCIAL.** El track de pulido de texto (N5-N8) es mecánico, acotado y sin decisión de diseño → subagente. El track principal (D9-D12+N4) toca packager/main.py/proposal con criterio de freshness → agente principal DIRECTO.

### Track principal (agente principal) — D9, D10, D11, N4, D12

**D9**: constante compartida `TARGET_GBP_PHOTOS = 40` usada por v4_diagnostic_generator.py:1737 y las recomendaciones (hoy `20 - photos` local).
> ⚠️ Nota de fuente (2026-08-03): el "40+" del contexto (audit_report:101) NO se encontró como target en `audit_report_20260801_170528.json` (gbp.photos=10, sin campo target). El "40+ fotos" real vive en `modules/scrapers/gbp_leak_detector.py:133` (urgencia Booking). Fijar TARGET_GBP_PHOTOS=40 es decisión válida de estandarización, pero NO buscar "40+" en el audit_report para verificarlo; usar el valor de gbp_leak_detector o el estándar definido. Nota: con photos=10, "Subir al menos N" = 40−10 = 30.

**D10**: en v4_diagnostic_generator.py:1854-1862 — dedupe con `seen` set ANTES del tope; iterar TODA la lista, no `social[:3]`.

**D11**: el reporte `commercial_gates_report.json` SOLO se escribe en el branch de ERROR (`v4_proposal_generator.py:629` está dentro del `else` del `if not commercial_report.blocking_passed`, justo antes del `raise`) — por eso en runs exitosos NUNCA se regenera y queda stale.
- (a) v4_proposal_generator.py:629: mover el write FUERA del branch condicional → escribir `commercial_gates_report.json` SIEMPRE en cada generación de propuesta (pass, warning y blocking), ruta canónica `output_dir/hotel_id/v4_audit/`.
- (b) main.py:2898: si el archivo es más viejo que la propuesta → warning "reporte stale".

**N4**: el packager debe filtrar el directorio v4_audit: incluir SOLO artefactos del run actual (timestamp/run_id) o mover históricos a subdirectorio `historico/`.
- ⚠️ NO tocar la arquitectura single-write del packager (v4.69.0, contexto DELIVERY-ZIP-PACKAGING-BROKEN) — solo el criterio de selección de archivos.
- Riesgo §8 fila 4: verificar MANIFEST.json post-fix (referencias a históricos).

**D12**: main.py:1878/1937 — label occupancy desde el ORIGEN real: si `reservas_mes` existe → "onboarding"; solo "regional" cuando el valor vino de `resolver.resolve_occupancy`. NO cambiar `feature_flags.py`.

### Track delegado (subagente) — N5, N6, N7, N8

Contexto para el subagente:
- **N5**: `modules/commercial_documents/templates/diagnostico_v6_template.md:57` — "La cifra acima" → "La cifra arriba".
- **N6**: `v4_diagnostic_generator.py:2458` — "Por que importa" → "Por qué importa".
- **N7**: `v4_diagnostic_generator.py:2471` — truncamiento `[:80]` a corte por palabra (no cortar a mitad de palabra; usar rsplit sobre espacio).
- **N8**: texto "Esta estimación está con 70% de confianza" (doc:231) — el 70% es la probabilidad del escenario conservative; corregir el label para que refleje la semántica aprobada en FASE-B (DEC-B3).
- Tests: render/golden de las 4 correcciones.

### Verificación N3 (se completa en FASE-E)
- En esta fase: confirmar vía greps que TODOS los hardcodes conocidos fueron eliminados o parametrizados (`203 reseñas`, `7 brechas`, `algoritmo propio de Google`, `acima`, `Por que importa`, `[:80]` crudo).
- La prueba definitiva (diff entre el doc baseline 2026-08-01 y el doc del run E2E > 3 líneas de diferencia) se ejecuta en FASE-E y se registra en `10-analisis-post-implementacion.md`.

## Criterios de aceptación

- [ ] D9: doc muestra target 40 fotos ("subir al menos N fotos adicionales" con N = 40 − fotos actuales).
- [ ] D10: redes listadas sin duplicados; TikTok/YouTube presentes si el audit los detecta.
- [ ] D11: `commercial_gates_report.json` con timestamp del run actual en `output_dir/hotel_id/v4_audit/`.
- [ ] N4: el empaquetado excluye históricos (0 artefactos con timestamp anterior al run) o los mueve a `historico/`; MANIFEST íntegro.
- [ ] D12: `financial_scenarios.json` con `occupancy: "onboarding"` cuando el valor viene de reservas_mes.
- [ ] N5-N8: greps en 0 hits.
- [ ] N3: verificación registrada (diff > 3 líneas).

## Tests Obligatorios

| Test | Comando | Criterio |
|------|---------|----------|
| Suites afectadas | Ver nota de seguridad ⬇️ | 0 regresiones |
| Validaciones | `./venv/Scripts/python.exe scripts/run_all_validations.py --quick` | 4/4 |

> ⚠️ **Seguridad de ejecución (L11)**: NUNCA ejecutar múltiples directorios de tests en un solo comando.
> Ejecutar por módulo individualmente con timeout de 60s:
> ```bash
> ./venv/Scripts/python.exe -m pytest tests/commercial_documents -q --tb=line  # conftest excluye patológicos
> ./venv/Scripts/python.exe -m pytest tests/delivery -q --tb=line
> ./venv/Scripts/python.exe -m pytest tests/financial_engine -q --tb=line
> ```
> Si algún módulo individual cuelga, matar INMEDIATAMENTE con `taskkill /F /IM python.exe /T`.

**Verificación estática**:
```bash
grep -rn "acima" modules/            # → 0 hits (N5)
grep -rn "Por que importa" modules/  # → 0 hits (N6)
```

## Post-Ejecución (OBLIGATORIO)

1. Marcar FASE-D ✅ en `dependencias-fases.md`, `09-checklist-implementacion.md`, `README.md`.
2. Actualizar `11-documentacion-post-proyecto.md` (B, D, E) y anotar verificación N3 en `10-analisis-post-implementacion.md`.
3. Ejecutar:
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-D \
    --desc "D9-D12 + N4 freshness ZIP + N3/N5-N8 pulido de texto" \
    --archivos-mod "modules/commercial_documents/v4_diagnostic_generator.py,modules/commercial_documents/v4_proposal_generator.py,modules/commercial_documents/templates/diagnostico_v6_template.md,modules/delivery/delivery_packager.py,main.py" \
    --tests "<N nuevos>" --check-manual-docs
```

## Criterios de Completitud (CHECKLIST)

- [ ] D9, D10, D11, D12, N4 cerrados (track principal)
- [ ] N5-N8 cerrados (track subagente) + verificación N3 registrada
- [ ] Tests pasan + 0 regresiones
- [ ] `log_phase_completion.py` ejecutado

## Restricciones

- Máximo 60 iteraciones (R2).
- NO ejecutar v4complete (la verificación E2E completa es FASE-E).
- NO modificar la arquitectura single-write del packager (solo criterio de selección).
- NO modificar `feature_flags.py` ni fórmulas financieras.
- Si el subagente del track N5-N8 falla → ejecutar directamente (es el track de menor prioridad, puede diferirse N8 si D4 dejó el texto ya corregido).
