# Checklist de Implementación — WHATSAPP-CONFLICT-VISIBILITY

**Proyecto**: WhatsApp Conflict Visibility Refactor  
**Referencia**: L 123 de FASE-A-01c-whatsapp-conflict-analysis.md  
**Total de fases**: 4 (A-02a, A-02b, A-02c, RELEASE)

---

## Progreso

|| Fase | Estado | Inicio | Fin | Tests | Notes |
|------|--------|--------|------|-------|-------|
| FASE-A-02a | ⏳ Pendiente | - | - | 0 | Investigación |
| FASE-A-02b | ⏳ Pendiente | - | - | +2 | Nota contexto |
| FASE-A-02c | ⏳ Pendiente | - | - | 0 | Impacto ajuste |
| FASE-RELEASE | ⏳ Pendiente | - | - | 0 | v4complete |

---

## Criterios de Éxito Final

Para que el proyecto se considere exitoso:

- [ ] FASE-A-02a: Hallazgos documentados en `evidence/FASE-A-02a/hallazgos_02a.md`
- [ ] FASE-A-02b: `${whatsapp_conflict_business_note}` visible en sección contexto del template
- [ ] FASE-A-02b: Nota CONDICIONAL (solo aparece con conflicto real)
- [ ] FASE-A-02c: `impacto` whatsapp_conflict ajustado de 0.10 a 0.20
- [ ] FASE-RELEASE: v4complete Hotel Castilla Real genera diagnóstico con nota de impacto de negocio visible
- [ ] FASE-RELEASE: Phrasing correcto: "Su Google Business muestra un número diferente al de su sitio — cada cliente que intenta reservar por WhatsApp desde Google podría estar escribiendo al número equivocado"
- [ ] FASE-RELEASE: Sin costo mensual en la nota

---

## Validaciones Acumulativas

| Validación | FASE-A-02a | FASE-A-02b | FASE-A-02c | RELEASE |
|------------|------------|------------|------------|---------|
| Tests pasan | N/A | +2 | +0 | +0 |
| run_all_validations --quick | - | ✅ | ✅ | ✅ |
| doctor.py --status | - | ✅ | ✅ | ✅ |
| dependencias-fases.md | ✅ | ✅ | ✅ | ✅ |
| 09-doc-post-proyecto.md | ✅ | ✅ | ✅ | ✅ |

---

*Creado: 2026-05-24*  
*Plan: WHATSAPP-CONFLICT-VISIBILITY*