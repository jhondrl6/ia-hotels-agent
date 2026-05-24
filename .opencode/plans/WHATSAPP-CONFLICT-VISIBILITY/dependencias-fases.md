# Dependencias y Estado de Fases — WHATSAPP-CONFLICT-VISIBILITY

**Proyecto**: WhatsApp Conflict Visibility Refactor  
**Bloque**: L 123 de FASE-A-01c-whatsapp-conflict-analysis.md  
** Objetivo**: Hacer visible el warning de WhatsApp conflict con phrasing de impacto de negocio, no diluido en "Validación de Calidad"

---

## Estado de Fases

|| Fase | Estado | Inicio | Fin | Notas |
|------|-------|--------|------|-----|-------|
| FASE-A-02a | ✅ Completada | 2026-05-24 | 2026-05-24 | Investigación de visibilidad |
| FASE-A-02b | ✅ Completada | 2026-05-24 | 2026-05-24 | Implementación nota en contexto |
| FASE-A-02c | ✅ Completada | 2026-05-24 | 2026-05-24 | Impacto 0.10→0.20, phrasing mejorado |
| FASE-RELEASE | ✅ Completada | 2026-05-24 | 2026-05-24 | v4complete Hotel Castilla Real (coherence 0.8261) |

---

## Dependencias

```
FASE-A-02a (investigación)
    └── FASE-A-02b (implementación nota contexto)
            └── FASE-A-02c (ajustar narratives)
                    └── FASE-RELEASE (v4complete)
```

---

## Diagnóstico del Problema (L 123)

**Situación actual**:
- `whatsapp_conflict` aparece en `_build_manual_attention_table()` (línea 1477) como fila en tabla "Validación de Calidad"
- Compite visualmente con: Perfil GBP, Fotos GBP, Core Web Vitals
- No tiene cuantificación de impacto financiero
- No aparece en sección de contexto del diagnóstico

**Impacto real (no documentado)**:
> Su Google Business muestra un número diferente al de su sitio — cada cliente que intenta reservar por WhatsApp desde Google podría estar escribiendo al número equivocado

**Decisión documentada**: NO tratarlo como BRECHA (no tenemos asset para resolverlo — requiere decisión del hotelero). Sí debe ser visible como nota de impacto de negocio.

---

## Métricas del Proyecto

| Métrica | Valor |
|---------|-------|
| Archivos a modificar | 5 |
| Tests esperados | +2 |
| Líneas de código impactadas | ~50 |
| Comandos largos | 1 (v4complete en RELEASE) |

---

## Resumen de Cambios por Fase

| Fase | Archivos | Descripción |
|------|----------|-------------|
| A-02a | v4_diagnostic_generator.py, diagnostico_v6_template.md | Mapear flujo actual |
| A-02b | v4_diagnostic_generator.py, diagnostico_v6_template.md | Agregar nota contexto |
| A-02c | v4_diagnostic_generator.py, config/regional_benchmarks.yaml | Ajustar impacto + phrasing |
| RELEASE | - | v4complete Hotel Castilla Real |

---

*Creado: 2026-05-24*
*Plan: WHATSAPP-CONFLICT-VISIBILITY*