# Documentacion Post-Proyecto

**Proyecto**: FASE-1-AMAZILIA-CORRECCION-ESTADO-ENTREGABLES
**Version**: 4.36.0 → 4.36.1

---

## Seccion A: Modulos Nuevos

> Ninguno. Este proyecto solo modifica modulos existentes.

---

## Seccion B: Modulos Modificados

| Modulo | Archivo | Cambio |
|--------|---------|--------|
| commercial_documents | v4_proposal_generator.py | Cierre de call chain site_presence_report (generate → _prepare_template_data → _generate_asset_quality_table → _confidence_to_nivel_significado) |
| main | main.py | Invocacion SitePresenceChecker antes de generar propuesta + pasar site_presence_report |
| tests | test_proposal_alignment.py | Fix tilde "Boton" → "Botón" + 2 tests nuevos de presencia verificada |
| postprocessors | document_quality_gate.py | Fix regex L245: lookbehind negativo `(?<!\d)` para evitar falso positivo "70% de confianza" |

---

## Seccion C: Tests

| Test | Archivo | Estado |
|------|---------|--------|
| test tilde WhatsApp | test_proposal_alignment.py | ✅ Agregado (FASE-1A) |
| test presence_verified=True | test_proposal_alignment.py | ✅ Agregado (FASE-1A) |
| test confidence sin presencia | test_proposal_alignment.py | ✅ Agregado (FASE-1A) |

---

## Seccion D: Metricas Acumulativas

| Metrica | Antes | Despues |
|---------|-------|---------|
| Tests totales | 2248 | 2250+ |
| Regresiones | 0 | 0 |
| coherence Amaziliahotel | 0.893 | 0.893 |
| WhatsApp en propuesta | "Incluido en su kit" (incorrecto) | "Verificado en sitio" ✅ |
| Schema en propuesta | "Completo" (incorrecto) | "Listo para implementar" ✅ |
| FAQ en propuesta | "Completo" (incorrecto) | "Listo para implementar" ✅ |
| content_quality gate | ❌ FALSO POSITIVO (regex) | ✅ PASSED |

---

## Seccion E: Archivos Afiliados

| Archivo | Actualizado | Fase |
|---------|------------|------|
| docs/CHANGELOG.md | ✅ (entrada [4.36.1]) | FASE-1C |
| docs/GUIA_TECNICA.md | ✅ (nota v4.36.1) | FASE-1C |
| docs/contributing/REGISTRY.md | ✅ | FASE-1B-PATCH (via log_phase_completion.py) |
| VERSION.yaml | ✅ | sincronizado (v4.36.0) |
| AGENTS.md | ✅ | sincronizado (v4.36.0) |
| README.md | ✅ | sincronizado (v4.36.0) |
| .opencode/plans/README.md | ✅ | FASE-1B-PATCH |
| .opencode/plans/dependencias-fases.md | ✅ | FASE-1B-PATCH |

---

## Historial de Actualizaciones

| Fecha | Seccion | Fase | Responsable |
|-------|---------|------|-------------|
| 2026-04-28 | Creacion | Preparacion | Hermes (orquestador) |
| 2026-04-28 | Seccion B, D, E | FASE-1A | Hermes |
| 2026-04-28 | Seccion B (regex fix), D (content_quality), E (REGISTRY) | FASE-1B-PATCH | Hermes |
| 2026-04-28 | Seccion E: CHANGELOG + GUIA_TECNICA | FASE-1C | Hermes |
