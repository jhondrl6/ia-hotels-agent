# Plan: WHATSAPP-CONFLICT-VISIBILITY

**Proyecto**: Refactorización de visibilidad del WhatsApp Conflict  
**Referencia**: L 123 de `.opencode/context/FASE-A-01c-whatsapp-conflict-analysis.md`  
**Objetivo**: Que el warning de WhatsApp conflict tenga visibilidad de impacto de negocio en la sección de contexto del diagnóstico, no diluido en "Validación de Calidad"

---

## Resumen del Problema

El warning de WhatsApp conflict aparece en la tabla "Validación de Calidad" donde compite visualmente con items menores (GBP sub-optimizado, fotos insuficientes). El hotelero que va directo a BRECHAS no lo ve. El impacto real — **reservas perdidas sin que el hotel lo sepa** — no está cuantificado ni destacado.

**Decisión**: NO tratarlo como BRECHA (no hay asset para resolverlo operativamente). SÍ debe ser visible como nota de impacto de negocio.

---

## Nota de Auditoría Pre-Ejecución (2026-05-24)

Este plan fue auditado contra código vivo. Se corrigieron 6 gaps:

| Gap | Severidad | Descripción | Corrección |
|-----|-----------|-------------|------------|
| G1 | CRÍTICO | `_generate_diagnostico_v6()` no existe | Wire en `_prepare_template_data()` L692 |
| G2 | CRÍTICO | Conflict dict no tiene phone_gbp separado | Usar `validation.phone_web` / `validation.phone_gbp` |
| G3 | ALTO | `pain_narratives` se carga de YAML, no del default Python | Modificar también `config/regional_benchmarks.yaml` (4 regiones) |
| G4 | ALTO | Ruta de tests `tests/unit/...` no existe | Corregido a `tests/commercial_documents/test_diagnostic_generator.py` |
| G5 | MEDIO | `{hotel_id}` literal en comando cp | Reemplazado por `hotelcastillareal` |
| G6 | MEDIO | `--regenerate-domain-primer` no existe | Reemplazado por `--doctor` |

Los archivos de fase fueron parcheados para reflejar estas correcciones.

---

## Fases

| Fase | Descripción | Estado | Tests |
|------|-------------|--------|-------|
| FASE-A-02a | Investigación de visibilidad | ✅ Completada | 0 |
| FASE-A-02b | Implementación nota en contexto | ✅ Completada | +2 |
| FASE-A-02c | Ajuste impacto y phrasing | ✅ Completada | 0 |
| FASE-RELEASE | v4complete Hotel Castilla Real | ⏳ Pendiente | 0 |

---

## Archivos del Plan

```
.opencode/plans/WHATSAPP-CONFLICT-VISIBILITY/
├── 05-prompt-inicio-sesion-fase-A-02a.md
├── 05-prompt-inicio-sesion-fase-A-02b.md
├── 05-prompt-inicio-sesion-fase-A-02c.md
├── 05-prompt-inicio-sesion-fase-RELEASE.md
├── 06-checklist-implementacion.md
├── 09-documentacion-post-proyecto.md
├── dependencias-fases.md
└── README.md (este archivo)
└── evidence/
    └── FASE-A-02a/
    └── FASE-RELEASE/
```

---

## Dependencias

```
FASE-A-02a → FASE-A-02b → FASE-A-02c → FASE-RELEASE
```

---

## Criterios de Éxito

- [ ] Nota de contexto con phrasing de impacto de negocio en sección contexto del diagnóstico
- [ ] Phrasing correcto: "Su Google Business muestra un número diferente al de su sitio — cada cliente que intenta reservar por WhatsApp desde Google podría estar escribiendo al número equivocado"
- [ ] Sin costo mensual (operativo, no tenemos activo para cuantificar)
- [ ] Condicional: solo aparece cuando hay conflicto whatsapp real
- [ ] v4complete Hotel Castilla Real completado con coherence >= 0.80

---

*Creado: 2026-05-24*