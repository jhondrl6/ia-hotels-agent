# Dependencias de Fases: Amaziliahotel Refactorizacion

**Proyecto**: Refactorizacion Amaziliahotel v4complete  
**Basado en**: `AMAZILIAHOTEL_FORENSIC_AUDIT_RESULTS.md` (2026-04-19)  
**Score Forense**: 16/100 → Objetivo: 80/100

---

## DIAGRAMA DE DEPENDENCIAS

```
[FASE-1] BookingScraper Real (BLOQUEANTE)
    │
    ├──╸ [FASE-2A] Regenerar hotel_schema con datos reales
    ├──╸ [FASE-2B] Regenerar monthly_report con datos reales
    ├──╸ [FASE-2C] Regenerar optimization_guide (datos entrada corregidos)
    │
[FASE-3] Correccion Bugs Generadores
    │
    ├── H3: faq_page ext .csv (bug formato)
    ├── H4: duplicados llms.txt y hotel_schema
    ├── H10: coherence metric duplicada
    └── H12: paths Windows (WSL)
    │
[FASE-4] Generar Asset B4 Open Graph (INDEPENDIENTE)
    │
[FASE-5] Decisiones de Producto + Quality Gates
    │
    ├── D1: WhatsApp ELIMINAR (hotel YA tiene, bug promised_by "always")
    ├── D2: Voice ELIMINAR de pipeline automatico (sin brecha real)
    ├── D3: Informe Mensual MANTENER reclasificado como servicio
    ├── H9: delivery_ready 25% → se resuelve con FASE-1
    └── H11: delivery_ready gates → se resuelve con FASE-1
    │
[FASE-6] Correccion Documentos Comerciales (A4, A5, M4)
    │
    ├── A4: ROI 20X sin base → corregir a 3X Tier C / 20X con GA4
    ├── A5: WhatsApp ELIMINADO (claim falso), Voice ELIMINADO, Informe reclasificado
    └── M4: WhatsApp numero verificado (573104019049 = GBP) → CERRADO
```

---

## TABLA DE CONFLICTOS DE ARCHIVOS

| Fase | Archivos Modificados | Conflictos |
|------|---------------------|------------|
| FASE-1 | `modules/scrapers/booking_scraper.py` | Ninguno (modulo isolated) |
| FASE-2A | `modules/asset_generation/conditional_generator.py` (schema) | Con FASE-3 H4 |
| FASE-2B | `modules/asset_generation/monthly_report_generator.py` | Ninguno |
| FASE-2C | `modules/asset_generation/optimization_guide_generator.py` | Ninguno |
| FASE-3 | `faq_generator`, `llmstxt_generator.py`, `coherence_gate.py`, `asset_report` | Con FASE-2A |
| FASE-4 | `modules/asset_generation/open_graph_generator.py` (NUEVO) | Ninguno |
| FASE-5 | `modules/asset_generation/asset_catalog.py` (promised_by), output dirs | Ninguno |
| FASE-6 | `01_DIAGNOSTICO_*.md`, `02_PROPUESTA_*.md` | Con FASE-5 (decisiones) |

---

## MATRIZ DE HALLAZGOS POR FASE

| ID | Hallazgo | Tipo | Fase | Decision |
|----|----------|------|------|----------|
| H1 | research.json vacio | SISTEMICO | FASE-1 | Resolver (cascada) |
| H2 | hotel_schema generico | CASCADA | FASE-2A | Resolver |
| H3 | faq_page ext .csv | BUG | FASE-3 | Resolver |
| H4 | llms.txt duplicado | ARQ | FASE-3 | Resolver |
| H5 | optimization_guide contradiccion | DATOS | FASE-2C | Resolver |
| H6 | monthly_report vacio | CASCADA | FASE-2B | Resolver |
| H7 | whatsapp_button sin brecha | PRODUCTO | FASE-5 | **ELIMINAR** (hotel ya tiene WhatsApp) |
| H8 | voice_assistant sin brecha | PRODUCTO | FASE-5 | **ELIMINAR** de pipeline (sin brecha real) |
| H9 | 75% assets ESTIMATED | CASCADA | FASE-1 | Resolver (cascada) |
| H10 | Coherence duplicada | BUG | FASE-3 | Resolver |
| H11 | delivery_ready 25% | CASCADA | FASE-1 | Resolver (cascada) |
| H12 | Paths Windows | BUG | FASE-3 | Resolver |
| A4 | ROI 20X sin base Tier C | INFLACION | FASE-6 | Corregir a 3X Tier C |
| A5 | 3 servicios sin brecha | DESALINEACION | FASE-6 | WhatsApp/Voice eliminados, Informe reclasificado |
| M4 | WhatsApp numero no verificado | VERIFICACION | FASE-6 | CERRADO (numero verificado = GBP) |

**Total**: 15 hallazgos → 6 fases

---

## CORRECCIONES APLICADAS AL PLAN ORIGINAL

| Cambio | Razon | Impacto |
|--------|-------|---------|
| H7: MANTENER → **ELIMINAR** | Hotel YA tiene WhatsApp. Claim "No hay boton" es FALSO | Bug sistemico `promised_by=["always"]` corregido |
| H8: MANTENER anticipatory → **ELIMINAR pipeline** | Sin brecha real. Hotel Tier C no necesita Alexa Skill | `promised_by=["always_aeo"]` corregido |
| Informe Mensual: sin decision → **MANTENER reclasificado** | Servicio legitimo como valor agregado | A5 completamente resuelto |
| A4: "ajustar ROI" → **3X Tier C / 20X con GA4** | Sin calculo explicito era insuficiente | ROI honesto y escalable |
| Nombres archivo: corregidos | `report_generator.py` → `monthly_report_generator.py`, etc. | Evitar friccion en ejecucion |

---

## PROGRESO

|||| Fase | Estado | Fecha Inicio | Fecha Fin |
||||------|--------|--------------|-----------|
|||| FASE-1 | ✅ COMPLETADA | 2026-04-19 | 2026-04-19 |
|||| FASE-2A | ✅ COMPLETADA | 2026-04-19 | 2026-04-19 |
|||| FASE-2B | ✅ COMPLETADA | 2026-04-19 | 2026-04-19 |
|||| FASE-2C | ✅ COMPLETADA | 2026-04-19 | 2026-04-19 |
|||| FASE-3 | ✅ COMPLETADA | 2026-04-19 | 2026-04-19 |
|||| FASE-4 | ✅ COMPLETADA | 2026-04-19 | 2026-04-19 |
|||| FASE-5 | ✅ COMPLETADA | 2026-04-20 | 2026-04-20 |
|||| FASE-6 | PENDIENTE | - | - |

---

## RECURSOS COMPARTIDOS

- **GBP verificado**: Amazilia Hotel Campestre, rating 4.5, reviews 202, phone 310 4019049
- **Address**: mts a la derecha, Via Pereira a #Entrada 8 Cafelia, 600, CERRITOS, Pereira, Risaralda
- **WhatsApp verificado**: 573104019049 (mismo que GBP) → hotel YA tiene WhatsApp
- **Geo score**: 62/100

---

*Generado: 2026-04-19 por Hermes Agent*
*Actualizado: 2026-04-19 -- FASE-3 completada (2026-04-19), FASE-4 docs completadas*
*Workflow: phased_project_executor.md*
