# Checklist de Implementación — Corrección Bugs Amazilia Hotel

**Proyecto:** AMAZILIA-BUGFIX  
**Fecha:** 2026-04-14  
**Versión inicial:** v4.30.0 → **Versión objetivo:** v4.30.1  

---

## Estado General

| Fase | ID | Estado | Completada | Dependencias | Prioridad |
|------|----|--------|------------|--------------|-----------|
|| 1 | FASE-DATASOURCE | ✅ Completada | 2026-04-14 | Ninguna | CRÍTICA |
| 2 | FASE-PERSONALIZATION | ✅ Completada | 2026-04-14 | FASE-DATASOURCE | ALTA |
| 3 | FASE-BUGFIXES | ⏳ Pendiente | — | FASE-DATASOURCE | ALTA |
| 4 | FASE-CONTENT-FIXES | ✅ Completada | 2026-04-14 | FASE-PERSONALIZATION | MEDIA |
| 5 | FASE-VALIDATION-GATE | ⏳ Pendiente | — | FASE-1..4 | ALTA |
| 6 | FASE-RELEASE | ⏳ Pendiente | — | FASE-5 | CRÍTICA |

---

## Detalle por Fase

### FASE-DATASOURCE (Fase 1) — CRÍTICA

**Objetivo:** Corrección de datos fuente — coordenadas GPS, región, teléfono, GBP inválido

**Hallazgos:** D1, D3, D9, D12

**Tareas:**
- [x] D1: Eliminar coordenadas hardcodeadas NYC (40.7128, -74.0060)
- [x] D1: Usar coordenadas de Pereira (~4.81°N, -75.69°W) o del GBP
- [x] D3: Fix región "nacional" → "Pereira" o "Eje Cafetero"
- [x] D9: Capturar teléfono tel:3104019049 del HTML
- [x] D12: Rechazar GBP que es resultado de búsqueda (no perfil real)

**Criterios de aceptación:**
- [x] `grep "40.7128" modules/` → 0 matches
- [x] Región en audit_report = "Pereira" o "Eje Cafetero"
- [x] phone_web = "+57 3104019049" (no null) — verificable con v4complete en FASE-RELEASE
- [x] GBP status = "unavailable" si es resultado de búsqueda

**Post-fase:**
- [x] dependencias-fases.md marcado ✅
- [x] 09-documentacion-post-proyecto.md actualizado
- [ ] REGISTRY.md actualizado con log_phase_completion.py — pendiente

---

### FASE-PERSONALIZATION (Fase 2) — ✅ Completada

**Objetivo:** Generators reciben audit_report como contexto

**Hallazgos:** D2 (causa raíz)

**Tareas:**
- [x] Diagnosticar flujo actual de datos hacia generators
- [x] Modificar v4_asset_orchestrator.py para pasar audit_report
- [x] Modificar conditional_generator.py para pasar audit_report
- [x] Modificar cada generator para usar audit_report["name"], ["region"], etc.

**Criterios de aceptación:**
- [x] Generators reciben audit_report dict
- [x] hotel_schema usa name del audit (no "Hotel")
- [x] llms_txt usa URL real amaziliahotel.com
- [x] geo_playbook usa región correcta

**Post-fase:**
- [x] REGISTRY.md actualizado
- [x] dependencias-fases.md marcado ✅
- [x] 09-documentacion-post-proyecto.md actualizado

---

### FASE-BUGFIXES (Fase 3)

**Objetivo:** Corrección de 4 bugs específicos

**Hallazgos:** D4, D5, D6, D7

**Tareas:**
- [ ] D4: Fix WhatsApp href="detected_via_html" → número real o PENDIENTE
- [ ] D5: Fix Review widget ★★★★★ falso → mostrar rating real (0 reviews)
- [ ] D6: Fix org_schema url="example.com" → amaziliahotel.com
- [ ] D7: Fix propuesta "No generado" vs assets reales

**Criterios de aceptación:**
- [ ] `grep "detected_via_html" modules/` → 0 matches
- [ ] `grep "Excelente servicio" modules/` → 0 matches
- [ ] `grep "example.com" modules/` → 0 matches
- [ ] Propuesta refleja estado real de assets

**Post-fase:**
- [ ] REGISTRY.md actualizado
- [ ] dependencias-fases.md marcado ✅
- [ ] 09-documentacion-post-proyecto.md actualizado

---

### FASE-CONTENT-FIXES (Fase 4) — ✅ Completada

**Objetivo:** Corrección de contenido en assets

**Hallazgos:** D8, GAP-2, GAP-3

**Tareas:**
- [x] D8: Fix optimization_guide contradicciones (title tag, meta description)
- [x] GAP-2: Fix monthly_report "Hotel" → "Amazilia"
- [x] GAP-3: Fix llms_txt genérico → incluir Pereira, spa, Eje Cafetero

**Criterios de aceptación:**
- [x] optimization_guide sin contradicciones internas
- [x] `grep "**Hotel**: Hotel$" monthly_report/` → 0 matches
- [x] `grep -i "pereira\|spa" llms_txt/` → > 0 matches

**Post-fase:**
- [x] REGISTRY.md actualizado
- [x] dependencias-fases.md marcado ✅
- [x] 09-documentacion-post-proyecto.md actualizado

---

### FASE-VALIDATION-GATE (Fase 5)

**Objetivo:** Validación pre-release (tests + validaciones internas)

**Tareas:**
- [ ] Ejecutar suite completa de tests
- [ ] Ejecutar run_all_validations.py --quick
- [ ] Verificar fixes aplicados (grep en código)
- [ ] Verificar publication gates = 9+

**Criterios de aceptación:**
- [ ] 385+ tests pasando
- [ ] 4/4 validaciones pasando
- [ ] doctor.py --status sin errores
- [ ] D1-D6: 0 matches de problemas en código

**Post-fase:**
- [ ] REGISTRY.md actualizado
- [ ] Listo para FASE-RELEASE

---

### FASE-RELEASE (Fase 6) — ÚNICA PRUEBA v4complete

**⚠️ IMPORTANTE:** Esta es la ÚNICA ejecución de v4complete en todo el proyecto.

**Tareas:**
- [ ] Actualizar CHANGELOG.md con entrada v4.30.1
- [ ] Ejecutar sync_versions.py
- [ ] Ejecutar version_consistency_checker.py
- [ ] **Ejecutar v4complete --url https://amaziliahotel.com/** ← ÚNICA PRUEBA
- [ ] Verificar todos los criterios de datos reales
- [ ] Verificar OpenRouter fallback NO se activó
- [ ] Git commit

**Validación FINAL — Datos Reales:**
- [ ] D1: hotel_schema coordenadas Pereira (NO 40.7128)
- [ ] D3: región Pereira/Eje Cafetero (NO "nacional")
- [ ] D4: WhatsApp funcional (NO "detected_via_html")
- [ ] D5: review_widget honesto (NO ★★★★★ falso)
- [ ] D6: org_schema URL real (NO example.com)
- [ ] D7: propuesta refleja estado real
- [ ] GAP-2: monthly_report "Amazilia" (NO "Hotel")
- [ ] GAP-3: llms_txt menciona Pereira/spa/Eje Cafetero
- [ ] Cadena financiera intacta
- [ ] Tests pasando post-ejecución
- [ ] OpenRouter fallback = 0

---

## Métricas Acumulativas

| Métrica | Inicio (v4.30.0) | Fin (v4.30.1) |
|---------|------------------|----------------|
| Tests | 385+ | TBD |
| Coordenadas GPS correctas | NO (NYC) | TBD |
| Región correcta | NO ("nacional") | TBD |
| Teléfono capturado | NO (null) | TBD |
| WhatsApp funcional | NO (roto) | TBD |
| org_schema real | NO (example.com) | TBD |
| review_widget honesto | NO (falso) | TBD |
| llms_txt específico | NO (genérico) | TBD |
| monthly_report nombre real | NO ("Hotel") | TBD |
| GBP query correcta | NO ("amaziliahotel") | TBD ("Amazilia Hotel") |

---

## Checklist de Cierre

| Verificación | Estado |
|-------------|--------|
| CHANGELOG.md actualizado | [ ] |
| REGISTRY.md actualizado | [ ] |
| VERSION.yaml sincronizado | [ ] |
| sync_versions.py ejecutado | [ ] |
| version_consistency_checker.py pasado | [ ] |
| git commit realizado | [ ] |
| FASE-RELEASE ✅ completada | [ ] |

*Checklist creado: 2026-04-14*
