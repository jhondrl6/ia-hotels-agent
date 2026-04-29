# Checklist de Implementacion

**Proyecto**: FASE-1-AMAZILIA-CORRECCION-ESTADO-ENTREGABLES
**Version**: 4.36.0 → 4.37.0
**Fecha inicio**: 2026-04-28

---

## Estado de Fases

| Fase | ID | Descripcion | Estado | Fecha |
|------|----|-------------|--------|-------|
| 1A | FASE-1A | Implementar codigo (call chain + main.py + tests) | ⬜ Pendiente | - |
| 1B | FASE-1B | Ejecutar v4complete + verificar propuesta | ⬜ Pendiente | - |
| 1C | FASE-1C | Documentacion cascade + cierre | ⬜ Pendiente | - |

---

## Dependencias

```
FASE-1A → FASE-1B → FASE-1C
```

- FASE-1B requiere FASE-1A ✅
- FASE-1C requiere FASE-1A ✅ + FASE-1B ✅

---

## Criterios Globales de Aceptacion

- [ ] WhatsApp muestra "Verificado en sitio" en propuesta
- [ ] Datos Estructurados NO muestra "Completo" (schema_valid=false)
- [ ] FAQ NO muestra "Completo" (faq_schema_valid=false)
- [ ] coherence_score >= 0.80
- [ ] 2248+ tests sin regresiones
- [ ] CHANGELOG.md actualizado con [4.37.0]
- [ ] GUIA_TECNICA.md actualizado con nota v4.37.0
- [ ] run_all_validations.py --quick: 4/4

---

## Notas

- Version bump: 4.36.0 → 4.37.0 (PATCH: correccion de bug)
- No se requiere FASE-RELEASE separada — el cambio es un PATCH y FASE-1C cubre la documentacion
