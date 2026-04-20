# FASE-8: Validación E2E + Documentación Final
**Proyecto**: Amaziliahotel E2E Refactor v2
**Anterior**: FASE-1 a FASE-7 (TODAS deben estar completas)
**Siguiente**: Ninguna (última fase)

---

## Contexto

Esta es la fase final de validación. Después de ejecutar FASE-1 a FASE-7, debemos verificar que:
1. El score forense suba de 63.8 a >= 80
2. Todos los GAPs originales (G1-G14) estén resueltos
3. Los nuevos GAPs (NG1-NG5) estén resueltos
4. El veredicto E2E sea APROBADO

---

## Tareas de la Fase

### 1. Ejecutar v4complete E2E

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

# Ejecución completa
./venv/Scripts/python.exe main.py v4complete --url https://amaziliahotel.com/ 2>&1 | tee /tmp/v4complete_e2e.log

# Verificar score
grep -E "score|Score|forense|Forense" /tmp/v4complete_e2e.log | tail -10
```

### 2. Validar GAPs resueltos

| GAP | Verificación | Esperado |
|-----|-------------|---------|
| G2 hotel_schema | `cat outputs/amaziliahotel.com/assets/hotel_schema.json` | tel, addr, geo.lat con datos reales |
| G4 faq_page | `ls outputs/amaziliahotel.com/assets/faq_page.*` | `faq_page.json` existe, NO `.csv` |
| G7 monthly_report | `grep -c "_____" outputs/amaziliahotel.com/assets/monthly_report.md` | 0 blanks |
| G10 ROI | `grep -E "ROI\|[0-9]+X" outputs/amaziliahotel.com/propuesta.md` | Un solo ROI dinámico, sin "(24X)" |
| G13 "eje_cafetero" | `grep -c "eje_cafetero" outputs/amaziliahotel.com/propuesta.md` | 0 |
| G14 "COP COP" | `grep -c "COP COP" outputs/amaziliahotel.com/propuesta.md` | 0 |
| NG4 geo_score | `grep "geo_score" outputs/amaziliahotel.com/audit/diagnostic.md` | geo_score > 0 |
| NG5 scrubber | `grep -c "COP COP" outputs/amaziliahotel.com/diagnostic.md` | 0 (scrubber activo) |

### 3. Verificaciones post-forense específicas

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

# 3a. Content Scrubber está activo (no es dead code)
grep -c "ContentScrubber\|content_scrubber" modules/orchestration_v4/v4_complete_orchestrator.py
# Esperado: > 0 (FASE-3 lo integró)

# 3b. Template V6 sin ROI hardcodeado
grep "24X" modules/commercial_documents/templates/propuesta_v6_template.md || echo "OK"

# 3c. Voice/AEO no se promete
grep -i "búsqueda por voz" outputs/amaziliahotel.com/propuesta.md || echo "OK: Voice no aparece"

# 3d. WhatsApp sigue activo (NO eliminado)
grep -i "whatsapp" outputs/amaziliahotel.com/propuesta.md && echo "OK: WhatsApp activo"

# 3e. Query de Places API usa nombre parseado
grep -A5 "_build_search_queries" modules/auditors/v4_comprehensive.py | grep -c "split"
# Esperado: no usa domain.split('.')[0] como query directo
```

### 4. Validar score >= 80

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

# Ejecutar veredicto
./venv/Scripts/python.exe main.py v4audit --url https://amaziliahotel.com/ --full 2>&1 | grep -E "score|Score|veredicto|Veredicto|APROBADO|RECHAZADO"

# Si hay script de veredicto específico
./venv/Scripts/python.exe scripts/generate_veredicto.py --url https://amaziliahotel.com/ --output /tmp/veredicto_v2.md
```

---

## Post-Ejecución — Documentación

### 2.1. Diagnóstico Inicial (CONTRIBUTING §60-67)

```bash
./venv/Scripts/python.exe scripts/version_consistency_checker.py
./venv/Scripts/python.exe main.py --doctor
```

### 2.2. Sincronización Automática (CONTRIBUTING §70-76)

```bash
./venv/Scripts/python.exe scripts/sync_versions.py
```

### 2.3. CHANGELOG.md (CONTRIBUTING §78-85)

Agregar entrada para el release de refactor:

```markdown
## [4.32.0] - Amaziliahotel E2E Refactor (Fecha)

### Objetivo
Resolver GAPs persistentes del veredicto forense E2E — score de 63.8 a >=80.

### Cambios Implementados
- Fix Google Maps query builder — nombre parseado + ubicación, no domain.split() (FASE-1)
- Fix hotel_schema con datos reales de geo_enriched (FASE-2)
- Activar Content Scrubber en pipeline — dead code → integrado en orquestador (FASE-3)
- Fix ROI — eliminar "24X" hardcodeado del template V6 (FASE-4)
- Fix faq_page JSON-LD + monthly_report blanks (FASE-5)
- Fix Voice/AEO deprecated — eliminado de template y alignment (FASE-6)
- Fix capitalización región .title() en proposal generator (FASE-7)

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| modules/auditors/v4_comprehensive.py | Query builder con nombre parseado |
| modules/asset_generation/conditional_generator.py | hotel_schema + faq_page |
| modules/postprocessors/content_scrubber.py | Integrado en pipeline |
| modules/orchestration_v4/v4_complete_orchestrator.py | Import ContentScrubber |
| modules/commercial_documents/templates/propuesta_v6_template.md | ROI + Voice eliminado |
| modules/commercial_documents/v4_proposal_generator.py | ROI dinámico + region .title() |
| modules/asset_generation/proposal_asset_alignment.py | Voice eliminado |

### Tests
- ~30 tests nuevos/modificados
```

### 2.4. GUIA_TECNICA.md (CONTRIBUTING §86-93)

Agregar notas de cambios v4.32.0 con:
- Módulos afectados
- Problema/solución
- Backwards compatibility

### 2.5. Skills/Workflows (CONTRIBUTING §94-106)

```bash
ls -la .agents/workflows/*.md
```

### 2.6. Regenerar SYSTEM_STATUS.md (CONTRIBUTING §107-111)

```bash
./venv/Scripts/python.exe scripts/doctor.py --status
```

### 2.7. Verificar DOMAIN_PRIMER.md (CONTRIBUTING §145-157)

```bash
./venv/Scripts/python.exe scripts/doctor.py --context
```

### 2.8. Symlink + Validación Final (CONTRIBUTING §113-128)

```bash
ls -la .agent/workflows
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
git diff --stat
```

---

## Checklist de Completitud

- [ ] v4complete ejecuta sin errores
- [ ] Score forense >= 80/100
- [ ] GAPs G2, G4, G7, G10, G13, G14 resueltos
- [ ] NG4 (geo_score > 0) resuelto
- [ ] NG5 (scrubber activo) resuelto
- [ ] publication_ready = true
- [ ] CHANGELOG.md actualizado
- [ ] GUIA_TECNICA.md con notas v4.32.0
- [ ] SYSTEM_STATUS.md regenerado
- [ ] Validaciones pasan (4/4)
- [ ] Tests pasando: 100%

---

## Criterios de Aprobación Final

| Criterio | Umbral | Estado |
|----------|--------|--------|
| Score forense | >= 80 | [ ] |
| GAPs pre-existentes resueltos | >= 11/14 (80%) | [ ] |
| Nuevos GAPs | <= 2 | [ ] |
| Tests pasando | 100% | [ ] |
| Publication ready | true | [ ] |
| CHANGELOG formato | Correcto | [ ] |
| Validaciones | 4/4 | [ ] |

**Si todos los criterios en [ ] = [x] → VEREDICTO: APROBADO**

**Si score < 80**: Re-diagnosticar. La hipótesis del plan era incorrecta. NO iterar el mismo plan.
