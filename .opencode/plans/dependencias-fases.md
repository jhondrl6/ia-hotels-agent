# Dependencias entre Fases

## Diagrama de Dependencias

```
FASE-A (WhatsApp Detection Fix)
  │
  ├─→ FASE-B (Citability Narrative Fix)     [independiente de A]
  │
  ├─→ FASE-C (Regional Template Fixes)      [independiente de A]
  │
  └───────┬─────────────┘
          │
     FASE-D (Validacion E2E)    [depende de A+B+C]
```

FASE-A, FASE-B y FASE-C son **independientes entre si** (modifican archivos distintos o secciones distintas del mismo archivo sin overlap).

FASE-D (validacion E2E) requiere que A+B+C esten completas.

---

## Tabla de Conflictos de Archivos

| Archivo | FASE-A | FASE-B | FASE-C | Conflicto? |
|---------|--------|--------|--------|------------|
| v4_diagnostic_generator.py | Lineas 750-776, 941-944, 1005-1009, 1786-1794 | Lineas 1850-1860, narrativa citability | Lineas 413, 1608-1627 | BAJO (zonas distintas) |
| v4_comprehensive.py | Lineas 1021-1070 (cross_validation) | - | - | NINGUNO |
| data_structures.py | Linea 184 (whatsapp_status) | - | - | NINGUNO |
| diagnostico_v6_template.md | - | - | Lineas 21, 27 | NINGUNO |
| pain_solution_mapper.py | Solo lectura | - | - | NINGUNO |
| asset_catalog.py | Solo lectura | - | - | NINGUNO |

### Analisis de Riesgo: v4_diagnostic_generator.py

Unico archivo compartido. Las zonas de cada fase NO se superponen:

- **FASE-A**: Lineas 750-776 (phone_web/phone_gbp), 941-944 (tabla brechas), 1005-1009 (quick wins), 1786-1794 (brecha WhatsApp)
- **FASE-B**: Lineas 1850-1860 (low_citability brecha) y narrativa alrededor de 1044-1061
- **FASE-C**: Lineas 413 (hotel_region fallback) y 1608-1627 (_build_regional_context)

**Riesgo: BAJO**. Las zonas estan claramente separadas. Si FASE-A y FASE-B se ejecutan en sesiones distintas (como dicta el workflow), no hay colision.

---

## Orden de Ejecucion Recomendado

1. **FASE-A** — Mayor impacto comercial (falso positivo WhatsApp = brecha falsa en diagnostico entregado al cliente)
2. **FASE-B** — Impacto narrativo (explicacion incorrecta al cliente)
3. **FASE-C** — Impacto visual/template (errores de texto)
4. **FASE-D** — Validacion E2E completa con amaziliahotel.com
