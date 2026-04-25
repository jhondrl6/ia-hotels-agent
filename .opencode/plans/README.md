# Planes de Implementación - Trazabilidad "Calidad Garantizada" + Reconección Módulos→Diagnóstico

**Creado**: 2026-04-24
**Actualizado**: 2026-04-25 (v3 — auditoría profundizada: 10→18 hallazgos)
**Workflow**: `phased_project_executor.md` v2.4.0
**Total fases**: 3

---

## Archivos en este directorio

| Archivo | Descripción |
|---------|-------------|
| `README.md` | Este índice |
| `00-decisiones-deprecacion.md` | **NUEVO** — Decisiones de qué deprecar y por qué (DEP-01/02/03, RES-01/02/03, BUG-01/02) |
| `dependencias-fases.md` | Diagrama de dependencias y conflictos entre fases |
| `05-prompt-inicio-sesion-fase-trazabilidad-docs.md` | Prompt para FASE 1: Correcciones documentales |
| `05-prompt-inicio-sesion-fase-trazabilidad-raiz.md` | **AMPLIADO** — Prompt para FASE 2: Unificación + Cableado + Reconección Template + Deprecaciones |
| `05-prompt-inicio-sesion-fase-trazabilidad-validate.md` | **AMPLIADO** — Prompt para FASE 3: Validación con v4complete (incluye nuevos criterios) |
| `06-checklist-implementacion.md` | **AMPLIADO** — Checklist maestro (18 hallazgos, 16 tests) |
| `09-documentacion-post-proyecto.md` | Plan de documentación post-proyecto |

---

## Origen

Auditoría original en `.opencode/context/auditoria_calidad_garantizada_20260424.md` que detectó 10 desconexiones. **Auditoría profundizada** el 2026-04-25 identificó 8 hallazgos adicionales al comparar el diagnóstico generado contra lo que los módulos realmente producen:

### Hallazgos Originales (contexto)
1. PublicationGatesOrchestrator nunca se ejecuta en producción
2. Dos detectores paralelos con umbrales divergentes
3. financial_validity gate pasa con datos default/hardcode
4. SEO dual (10 vs 25 para el mismo concepto)
5. IAO vs ia_readiness (17 vs 33.2)
6-10. README gates, ghost command, bug escala, geo dual, coherence múltiple, benchmarks sin trace

### Hallazgos Nuevos (auditoría profundizada 2026-04-25)
11. **CRÍTICA**: IA metrics (14 crawlers bloqueados, IA-Readiness Critical) computadas pero V6 template las descarta
12. **ALTA**: geo_flow_result (23, "critical") contradice GEO (62) sin explicación
13. **ALTA**: 14 crawlers IA bloqueados NUNCA mencionados en diagnóstico
14. Código muerto: `_build_geo_problems_table()` en path V6
15. Sin sección de hallazgos positivos (WhatsApp, HTTPS, redes sociales detectados pero no mostrados)
16. Contexto regional es diccionario hardcoded (narrativa — aceptable)
17. Competidores son stub/placeholder
18. Matiz en clasificación financial sources

---

## Resumen Ejecutivo

3 fases secuenciales. Optimización de costos: validación con 1 sola ejecución v4complete al final.

**Principio rector**: Los módulos producen datos valiosos que NO pueden ser ignorados. Es capacidad instalada desaprovechada. Se depreca lo redundante, se reconecta lo desconectado.

```
FASE 1 (DOCS) ──→ FASE 2 (RAIZ) ──→ FASE 3 (VALIDATE)
     │                  │                    │
     │  README gates    │  Unificar detectores│  1 solo v4complete
     │  Workflow ghost  │  Cablear 9 gates   │  Hotel: Amazilia
     │  Docstrings      │  DEP-01/02/03      │  Verificar 18 criterios
     │                  │  RES-01/02/03      │
     │                  │  BUG-01/02         │
     │                  │  16 tests          │
```

---

## Decisiones Clave de Deprecación

| DEP # | Qué se depreca | Por qué | Reemplazo |
|-------|---------------|---------|-----------|
| DEP-01 | `_calculate_web_score()` algoritmo custom | Inconsistente con patrón CHECKLIST_* de otros pilares | `calcular_score_seo()` via CHECKLIST_SEO |
| DEP-02 | CHECKLIST_IAO como fuente primaria | `ia_readiness` es más granular (5 componentes) | `ia_readiness.overall_score` |
| DEP-03 | Umbrales duplicados en `_identify_brechas()` | Dos fuentes de verdad = divergencia | `detect_pains()` como única fuente |

Ver `00-decisiones-deprecacion.md` para detalle completo.

---

## Reglas

- **1 fase por sesión** (sin excepciones)
- Cada fase usa su propio prompt de inicio de sesión
- Post-ejecución: `log_phase_completion.py` obligatorio
- Validación final: 1 solo `v4complete` para optimizar costos API
- Cualquier hallazgo nuevo durante implementación → actualizar `00-decisiones-deprecacion.md`
