# T2 — Cruces de Integración Cross-Fase

> Fecha: 2026-09-15
> Artefacto base: `output/v4_complete/hoteldonalfonso/` (P4 real)
> Modo: DIRECTO (sin delegación)

## Tabla de 6 Cruces

| # | Cruce | Evidencia real | Dictamen | Hallazgo / Dueño |
|---|-------|----------------|----------|------------------|
| 1 | **P2 × P6** — NR7 alimenta tribunal | `evidence/FASE-P2/NR7-AC-E*.txt` (6 archivos) + `actaRevision.json` reviewer_reports | **coherente** | Tribunal consume 4 reportes de revisores; NR7 pares verde/rojo existen para AC-E1..E5. Sin hallazgos. |
| 2 | **P3-A × P2** — Baseline NR1 post-auditoría | `evidence/FASE-P2/NR1_baseline_post.txt` (corte c31422a) | **coherente** | Baseline registrado tras auditoría forense. Sin hallazgos. |
| 3 | **P3-A × P3-B** — NR7 mutation checks | `evidence/FASE-P2/NR7-AC-E3.txt`, `NR7-AC-E5-a.txt` | **coherente** | Pares verde/rojo documentados con comando literal y salida. Sin hallazgos. |
| 4 | **P3-B × P4** — Cuarentena delivery | `delivery_packager.py` L430-470 (write → .zip.tmp → publish/suppress) + `actaRevision.json` verdict=BLOQUEADO | **coherente** | ZIP queda en .tmp cuando verdict=BLOQUEADO. publish() solo si Juez=PUBLICAR. Sin hallazgos. |
| 5 | **P5 × todo** — Redacción de secretos en cachés | `gbp_auditor.py:_save_cache` L149 → `_redact_secrets_tree()` ✅ / `google_places_client.py:_save_cache` L136 → `json.dump()` sin redacción ❌ | **incoherente** | **Hallazgo**: `google_places_client.py` no redacta secretos antes de persistir caché. Dueño: FASE-RELEASE (AC-S4 prevención complementaria). |
| 6 | **P1 × P2 × P6** — Datos operativos y epistémicos | `main.py` L1847/L1875 `rooms=10` default ✅ / `epistemic_status` default='no_declarado' ✅ | **coherente** | Default de rooms presente (no inventa dato). epistemic_status no falsea 'verified'. Sin hallazgos. |

## Resumen

- **5/6 cruces coherentes** — integración cross-fase verificada sobre artefactos reales.
- **1/6 incoherente** — P5 × todo: `google_places_client.py` falta redacción en `_save_cache`. Va a T4 triaje como "va a plan sucesor" (AC-S4 prevención complementaria).

## Nota sobre el cruce P5 × todo

El hallazgo no invalida la certificación P5 (AC-S4 cerrada con rotación de key). Es una **prevención complementaria**: el fix de AC-S4 cubrió `_save_cache` en `memory.py` (cache de onboarding), pero no extendió la redacción a todos los `_save_cache` del sistema de scrapers. `gbp_auditor.py` ya redacta; `google_places_client.py` no. Esto es deuda técnica menor, no bloqueante para RELEASE.
