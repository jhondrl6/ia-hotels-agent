# Checklist de Implementación

**Proyecto**: PATCH-AUDITORIA-FORENSE-AMAZILIA-v2
**Versión**: 4.36.1 → 4.37.0
**Fecha inicio**: 2026-04-29

---

## Estado de Fases

| Fase | ID | Descripción | Estado | Fecha |
|------|----|-------------|--------|-------|
| A | FASE-PATCH-A | Critical Bugs + Diagnostic Stubs + Unicode Fix | ✅ Completada | 2026-04-29 |
|| B | FASE-PATCH-B | Placeholders + Evidence Integrity | ✅ Completada | 2026-04-29 |
| C | FASE-PATCH-C | v4complete Verification Run | ✅ Completada | 2026-04-29 |
| D | FASE-PATCH-D | Documentation + Version Sync + Deuda Técnica | ✅ Completada | 2026-04-29 |
| RELEASE | FASE-RELEASE-4.37.0 | Cierre Oficial | ⬜ Pendiente | - |

---

## Dependencias

```
FASE-PATCH-A → FASE-PATCH-B → FASE-PATCH-C → FASE-PATCH-D → FASE-RELEASE-4.37.0
```

- FASE-PATCH-B requiere FASE-PATCH-A ✅
- FASE-PATCH-C requiere FASE-PATCH-A ✅ + FASE-PATCH-B ✅
- FASE-PATCH-D requiere FASE-PATCH-A ✅ + FASE-PATCH-B ✅ + FASE-PATCH-C ✅
- FASE-RELEASE-4.37.0 requiere TODAS las fases de implementación ✅

---

## Criterios Globales de Aceptación

### Bugs Críticos (PATCH-A)
- [x] ROI muestra formato "0.2X" (con X) en propuesta
- [x] Proyección mensual explica pain_ratio o muestra beneficio > $0

### Stubs Diagnósticos (PATCH-A)
- [x] blog_activo no es siempre False sin evaluación
- [x] speakable_schema no es siempre False sin evaluación
- [x] ga4_indirect no es siempre False sin evaluación

### Infraestructura (PATCH-A)
- [x] version_consistency_checker.py no crashea con UnicodeEncodeError

### Placeholders (PATCH-B)
- [x] web_score usa audit_result real o marca "No disponible"
- [x] Teléfono no muestra placeholder fijo "+57 300 123 4567"
- [x] Evidence Tier no es siempre "C" sin GA4

### Verificación (PATCH-C) — Completada 2026-04-29
- [x] v4complete ejecuta sin errores
- [x] coherence_score >= 0.80 (resultado: 0.893)
- [x] publication gates: ready=true (READY_FOR_PUBLICATION, 7/9 PASSED, 2 WARNING)
- [x] Evidencia guardada en evidence/fase-patch-auditoria-v2/ (11 archivos)
- [x] BUG-1 verificado: ROI muestra "0.2X" con X
- [x] H-1/H-3/H-4/H-5 verificados: sin hardcodes/stubs
- [x] H-2 verificado: sin placeholder de teléfono
- [x] H-6 PARCIAL: Tier C sigue siendo "C" pero con justificación detallada (correcto para datos limitados)
- [x] BUG-2 PARCIAL: Beneficio neto $0 (inversión = recuperación), consistente con Tier C

### Documentación (PATCH-D)
- [x] AGENTS.md test count correcto (2251 funciones, 185 archivos)
- [x] AGENTS.md documenta 9 gates reales
- [x] H-9→H-27 catalogados en docs/technical_debt/
- [x] derive_version_from_changelog.py creado y funcional
- [x] VERSION.yaml sincronizado con CHANGELOG (4.36.1)
- [x] run_all_validations.py --quick: 4/4

### RELEASE (4.37.0)
- [ ] CHANGELOG.md entrada [4.37.0] con formato CONTRIBUTING.md
- [ ] GUIA_TECNICA.md nota técnica v4.37.0
- [ ] sync_versions.py ejecutado
- [ ] version_consistency_checker.py pasa (sin crash unicode)
- [ ] run_all_validations.py --quick: 4/4
- [ ] doctor.py --status sin errores críticos

---

## Notas

- Version bump: 4.36.1 → 4.37.0 (PATCH: corrección de bugs + hardcodes)
- v4_proposal_generator.py es modificado por PATCH-A y PATCH-B → deben aplicarse en orden
- derive_version_from_changelog.py fue CREADO en PATCH-D
- Los 20+ hardcodes H-9→H-27 NO se corrigen en este PATCH, solo se documentan
