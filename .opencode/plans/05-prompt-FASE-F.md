# FASE-F: Documentation & Validation — Cierre del Ciclo

**ID**: FASE-F
**Objetivo**: Documentar todos los cambios del refactor 4 pilares en la documentación oficial del repositorio (CHANGELOG, GUIA_TECNICA, REGISTRY, CONTRIBUTING), ejecutar la suite completa de validaciones, y marcar el proyecto como completado.
**Dependencias**: TODAS las fases anteriores completadas (A-E)
**Duración estimada**: 2-3 horas
**Skill**: `iah-cli-docs-update`, `iah-cli-phased-execution`

---

## Contexto

### Estado post-FASE-A/B/C/D/E
- CHECKLIST_IAO redistribuido a 4 pilares (SEO/GEO/AEO/IAO)
- AEO mide resultado (snippets) no solo infraestructura
- IAO restaurado con LLM Mention Checker
- Paquetes, templates, gap analyzer, report builder alineados
- Voice Readiness Proxy implementado
- 4 scores funcionando: SEO, GEO, AEO, IAO + score_global

### Esta fase es documentación y validación
- NO se modifica código de producción (solo docs y configs)
- Se ejecutan todas las validaciones del repositorio
- Se actualiza documentación oficial según CONTRIBUTING.md §55-163

---

## Tareas

### Tarea 1: Ejecutar diagnóstico inicial

**Comandos**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe scripts/version_consistency_checker.py
./venv/Scripts/python.exe main.py --doctor
```

**Criterios de aceptación**:
- [ ] version_consistency_checker.py pasa sin discrepancias
- [ ] doctor no reporta errores críticos

### Tarea 2: Actualizar CHANGELOG.md

**Objetivo**: Crear entrada de versión con todos los cambios del refactor.

**Formato** (según docs/contributing/documentation_rules.md §36-58):
```markdown
## [4.28.0] - Refactor 4 Pilares SEO/GEO/AEO/IAO (2026-04-XX)

### Objetivo
Corregir la arquitectura de scores de visibilidad: redistribuir CHECKLIST_IAO a 4 pilares 
coherentes (SEO→AEO→IAO con GEO lateral), restaurar IAO score eliminado incorrectamente 
en v4.21.0, y añadir medición real de AEO (SerpAPI) e IAO (LLM Mention Checker).

### Cambios Implementados

#### FASE-A: Score Redistribution
- `modules/commercial_documents/v4_diagnostic_generator.py` - CHECKLIST_IAO redistribuido a 4 checklists (SEO/GEO/AEO/IAO), calcular_cumplimiento deprecated en favor de calcular_score_{pilar}, _extraer_elementos_de_audit refactorizado a 4 funciones
- `modules/commercial_documents/data_structures.py` - DiagnosticSummary ampliado con score_seo/geo/aeo/iao/global

#### FASE-B: AEO Real Measurement
- `modules/auditors/aeo_snippet_tracker.py` - NUEVO: Verificación de featured snippets via SerpAPI
- `modules/commercial_documents/v4_diagnostic_generator.py` - _calculate_aeo_score refactorizado para medir resultado (snippets) no solo infraestructura, citabilidad movida de AEO a IAO

#### FASE-C: IAO Restoration + LLM Checker
- `modules/auditors/llm_mention_checker.py` - NUEVO: Detección de menciones en LLMs via OpenRouter/Gemini/Perplexity
- `modules/commercial_documents/v4_diagnostic_generator.py` - _calculate_iao_score restaurado (eliminado en v4.21.0)

#### FASE-D: Package & Template Alignment
- `modules/analyzers/gap_analyzer.py` - 2 gaps → 4 gaps (seo + geo + aeo + iao)
- `modules/financial_engine/opportunity_scorer.py` - Brechas IAO/SEO añadidas
- `modules/generators/report_builder.py` - Sección 4-Pilares completa
- `modules/commercial_documents/templates/diagnostico_v6_template.md` - Fila IAO + Score Global
- `scripts/update_benchmarks.py` - 3 → 4 benchmarks con IAO

#### FASE-E: Voice Readiness Proxy
- `modules/auditors/voice_readiness_proxy.py` - NUEVO: Score proxy basado en inputs (no medición directa Siri/Alexa)

### Archivos Nuevos
| Archivo | Descripción |
|---------|-------------|
| `modules/auditors/aeo_snippet_tracker.py` | Featured snippets tracking via SerpAPI |
| `modules/auditors/llm_mention_checker.py` | LLM mention detection via OpenRouter/Gemini/Perplexity |
| `modules/auditors/voice_readiness_proxy.py` | Voice readiness proxy score |
| `tests/auditors/test_aeo_snippet_tracker.py` | Tests AEO snippet tracker |
| `tests/auditors/test_llm_mention_checker.py` | Tests LLM mention checker |
| `tests/auditors/test_voice_readiness_proxy.py` | Tests voice readiness proxy |
| `tests/commercial_documents/test_iao_score.py` | Tests IAO score restaurado |

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| `modules/commercial_documents/v4_diagnostic_generator.py` | CHECKLIST redistribution, 4 scores, IAO restaurado, AEO refactorizado |
| `modules/commercial_documents/data_structures.py` | DiagnosticSummary con 4 pilares |
| `modules/commercial_documents/v4_proposal_generator.py` | score_tecnico → score_global |
| `modules/analyzers/gap_analyzer.py` | 4 gaps |
| `modules/financial_engine/opportunity_scorer.py` | Brechas IAO/SEO |
| `modules/generators/report_builder.py` | 4 pilares completos |
| `modules/utils/benchmarks.py` | 4 benchmarks con IAO |
| `scripts/update_benchmarks.py` | calculate_iao_score + 4 benchmarks |
| `modules/commercial_documents/templates/diagnostico_v6_template.md` | Fila IAO |

### Tests
- N tests nuevos en `tests/auditors/test_aeo_snippet_tracker.py`
- N tests nuevos en `tests/auditors/test_llm_mention_checker.py`
- N tests nuevos en `tests/commercial_documents/test_iao_score.py`
- N tests nuevos en `tests/auditors/test_voice_readiness_proxy.py`
- Total: N+ tests, 0 regresiones

### Decisión de Diseño
- Modelo: OPCION A (scores independientes 0-100, sin gate booleano)
- Score global = promedio ponderado SEO(25%) + GEO(25%) + AEO(25%) + IAO(25%)
- AEO mide RESULTADO (snippets capturados), no solo infraestructura
- IAO restaurado como pilar independiente con LLM Mention Checker
- Voice Readiness = score proxy derivado de AEO, NO 5to pilar
- OpenAI SIEMPRE via OpenRouter (nunca SDK directo)
```

**Criterios de aceptación**:
- [ ] CHANGELOG.md tiene entrada [4.28.0] completa
- [ ] Todos los archivos nuevos y modificados listados
- [ ] Tests documentados con conteo

### Tarea 3: Actualizar GUIA_TECNICA.md

**Objetivo**: Añadir nota técnica de la versión 4.28.0.

**Formato**:
```markdown
## Notas de Cambios v4.28.0

### Módulos Afectados
- `modules/commercial_documents/` (diagnostic_generator, data_structures, proposal_generator)
- `modules/analyzers/gap_analyzer.py`
- `modules/financial_engine/opportunity_scorer.py`
- `modules/generators/report_builder.py`
- `modules/auditors/` (aeo_snippet_tracker, llm_mention_checker, voice_readiness_proxy)
- `modules/utils/benchmarks.py`
- `scripts/update_benchmarks.py`
- Templates de diagnóstico y propuesta

### Problema
El código trataba GEO, AEO, SEO e IAO como pilares paralelos independientes. CHECKLIST_IAO mezclaba 
elementos de los 4 pilares sin distinguir capas. AEO medía infraestructura en lugar de resultado. 
IAO fue eliminado incorrectamente en v4.21.0. Existía un sistema dual de scoring (CHECKLIST + 4-Pilar).

### Solución
- Redistribución de CHECKLIST_IAO a 4 checklists independientes (SEO/GEO/AEO/IAO)
- Progresión SEO→AEO→IAO con GEO como pilar lateral
- AEO refactorizado para medir featured snippets (resultado), no solo schema (infraestructura)
- IAO restaurado con LLM Mention Checker (OpenRouter/Gemini/Perplexity)
- Sistema dual unificado: un solo scoring basado en 4 pilares
- Voice Readiness Proxy (inputs, no medición directa)

### Backwards Compatibility
- `calcular_cumplimiento()` mantenida como deprecated pero funcional
- `score_tecnico` en DiagnosticSummary mantenida como alias de `score_global`
- `schema_infra_score` mantenida como alias de `aeo_score`
- Templates existentes siguen funcionando con variables legacy
- Outputs existentes NO se regeneran

### API Cost
- SerpAPI: $0/mes (free tier 100 queries) para AEO
- OpenRouter: ~$0.05-0.15/hotel para IAO
- Gemini: GRATIS para IAO
- Perplexity: ~$0.10-0.25/hotel para IAO (opcional)
- Total estimado: $0.20-0.50 USD/hotel/mes
```

**Criterios de aceptación**:
- [ ] GUIA_TECNICA.md tiene nota técnica v4.28.0
- [ ] Incluye: módulos afectados, problema, solución, backwards compatibility, costo API

### Tarea 4: Verificar Skills/Workflows

**Comandos**:
```bash
ls -la .agents/workflows/*.md
```

**Criterios de aceptación**:
- [ ] Todos los .md en .agents/workflows/ listados en .agents/workflows/README.md
- [ ] No hay skills huérfanos

### Tarea 5: Regenerar SYSTEM_STATUS.md

**Comando**:
```bash
./venv/Scripts/python.exe scripts/doctor.py --status
```

**Criterios de aceptación**:
- [ ] SYSTEM_STATUS.md regenerado con versión actual

### Tarea 6: Sincronización de versiones

**Comando**:
```bash
./venv/Scripts/python.exe scripts/sync_versions.py
```

**Criterios de aceptación**:
- [ ] 6 archivos sincronizados: AGENTS.md, README.md, .cursorrules, CONTRIBUTING.md, GUIA_TECNICA.md, REGISTRY.md

### Tarea 7: Verificar DOMAIN_PRIMER.md

**Comando**:
```bash
./venv/Scripts/python.exe scripts/doctor.py --context
```

**Criterios de aceptación**:
- [ ] Todo módulo nuevo documentado en DOMAIN_PRIMER.md
- [ ] aeo_snippet_tracker, llm_mention_checker, voice_readiness_proxy documentados

### Tarea 8: Validación final

**Comandos**:
```bash
ls -la .agent/workflows    # Debe mostrar → .agents/workflows
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
./venv/Scripts/python.exe scripts/version_consistency_checker.py
git diff --stat
```

**Criterios de aceptación**:
- [ ] Symlink intacto
- [ ] run_all_validations.py pasa
- [ ] version_consistency_checker.py pasa
- [ ] git diff --stat muestra todos los archivos modificados

### Tarea 9: Validación end-to-end — v4complete contra hotel real

**Objetivo**: Ejecutar el pipeline `v4complete` completo contra `https://amaziliahotel.com/` para verificar que los 4 pilares (SEO/GEO/AEO/IAO), el motor financiero, la generación de assets y los documentos comerciales funcionan integrados después del refactor.

**Comando**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe main.py v4complete --url https://amaziliahotel.com/
```

**Qué verificar en la salida**:
1. **Diagnóstico**: Los 4 scores aparecen (SEO, GEO, AEO, IAO) + score_global
2. **Motor financiero**: Escenarios (conservador/realista/optimista) generan valores COP positivos y coherentes
3. **Data sources**: No deben aparecer `legacy_hardcode` ni `default` como fuentes de ADR/occupancy/direct_channel
4. **Coherencia**: `coherence_validator` pasa sin contradicciones entre diagnóstico y propuesta
5. **Assets**: Generación condicional ejecuta gates y genera assets aplicables
6. **Sin errores**: No tracebacks, no warnings críticos en consola

**Criterios de aceptación**:
- [ ] v4complete ejecuta sin errores (exit code 0)
- [ ] Salida contiene score_seo, score_geo, score_aeo, score_iao, score_global
- [ ] Escenarios financieros en COP con data_sources verificables (no legacy_hardcode)
- [ ] Documentos generados en directorio de salida (diagnóstico + propuesta)
- [ ] Coherence score ≥ 0.8

**Si falla**: Crear issue con el error y NO continuar a Tarea 10. El refactor no puede cerrarse con el pipeline roto en producción.

---

### Tarea 10: Registrar fase F + Release marker

**Comandos**:
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-F \
    --desc "Documentation & Validation: CHANGELOG, GUIA_TECNICA, REGISTRY, version sync" \
    --archivos-mod "CHANGELOG.md,docs/GUIA_TECNICA.md,REGISTRY.md" \
    --check-manual-docs

# Release marker (si es release)
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-RELEASE-4.28.0 \
    --desc "Release 4.28.0: Refactor 4 Pilares SEO/GEO/AEO/IAO" \
    --check-manual-docs
```

**Criterios de aceptación**:
- [ ] REGISTRY.md actualizado
- [ ] Si fue release: VERSION SYNC GATE pasó
- [ ] Checklist final en pantalla verificado

### Tarea 11: Git commit

**Comando**:
```bash
git add -A
git commit -m "feat: refactor 4 pilares SEO/GEO/AEO/IAO (FASE-A..F)

- CHECKLIST_IAO redistribuido a 4 pilares coherentes
- AEO refactorizado para medir resultado (SerpAPI)
- IAO restaurado con LLM Mention Checker
- Gap analyzer expandido a 4 gaps
- Voice Readiness Proxy implementado
- Paquetes, templates y report builder alineados
- N tests nuevos, 0 regresiones"
```

---

## Criterios de Completitud (CHECKLIST)

- [ ] version_consistency_checker.py pasa
- [ ] doctor.py pasa sin errores críticos
- [ ] CHANGELOG.md tiene entrada [4.28.0]
- [ ] GUIA_TECNICA.md tiene nota técnica v4.28.0
- [ ] Skills/workflows verificados
- [ ] SYSTEM_STATUS.md regenerado
- [ ] sync_versions.py ejecutado
- [ ] DOMAIN_PRIMER.md actualizado con módulos nuevos
- [ ] run_all_validations.py --quick pasa
- [ ] v4complete --url https://amaziliahotel.com/ ejecuta sin errores (Tarea 9)
- [ ] REGISTRY.md actualizado (FASE-F + RELEASE)
- [ ] Git commit realizado
- [ ] `dependencias-fases.md` → Todas las fases marcadas como completadas
- [ ] `06-checklist-implementacion.md` → Todas las fases con ✅

---

## Restricciones

- NO modificar código de producción en esta fase
- NO crear nuevos módulos Python
- NO ejecutar tests nuevos (ya validados en fases anteriores)
- Si se encuentran errores en validación, crear issue y NO intentar arreglar en esta fase
- Python: `./venv/Scripts/python.exe`
- Working directory: `/mnt/c/Users/Jhond/Github/iah-cli`
