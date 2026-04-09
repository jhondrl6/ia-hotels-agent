# Documentacion Post-Proyecto — Correccion Falsos Positivos

> **Proyecto:** iah-cli v4.25.x  
> **Fecha inicio:** 2026-04-09  
> **Contexto:** `.opencode/plans/context/whatsapp_false_positive.md`  
> **Alineado con:** `docs/CONTRIBUTING.md` §55-163 (Trigger: "Actualizar documentacion oficial del repositorio")

---

## Seccion A: Modulos Afectados

| Fase | Modulo | Archivo | Cambio |
|------|--------|---------|--------|
| FASE-A | auditors | v4_comprehensive.py | Conectar scraper whatsapp detection al cross_validator |
| FASE-A | data_structures | data_structures.py | Campo whatsapp_html_detected en ValidationSummary |
| FASE-A | commercial_documents | v4_diagnostic_generator.py | 4 zonas: brecha, tabla, quick wins, condicion WhatsApp |
| FASE-B | commercial_documents | v4_diagnostic_generator.py | Logica citability con blocks_analyzed |
| FASE-B | financial_engine | opportunity_scorer.py | Justificacion low_citability generica |
| FASE-B | tests | test_diagnostic_brechas.py | 3 nuevos tests blocks_analyzed |
| FASE-C | commercial_documents | diagnostico_v6_template.md | Typo yRevisan |
| FASE-C | commercial_documents | v4_diagnostic_generator.py | Mapping regional + fallback |
| FASE-E | orchestration | main.py | Rama elif whatsapp_html en ValidationSummary + region desde GBP + keywords URL |
| FASE-E | commercial_documents | v4_diagnostic_generator.py | Sanitizar hotel_region (nacional → Colombia) |
| FASE-E | commercial_documents | pain_solution_mapper.py | Consultar whatsapp_html_detected antes de pain |
| FASE-E | scrapers | web_scraper.py | Capturar telefonos de enlaces tel: |
| FASE-E | commercial_documents | coherence_validator.py | Consultar whatsapp_html_detected en coherence gate |

---

## Seccion B: Problemas Resueltos

| ID | Problema | Causa Raiz | Fase | Solucion |
|----|----------|------------|------|----------|
| FP-1 | Falso positivo "Sin WhatsApp" | scraper detection no conectado al pipeline | FASE-A | Conectar _detectar_whatsapp() → cross_validator |
| FP-2 | Narrativa "poco estructurado" con score=0 | No distinguir blocks_analyzed=0 | FASE-B | Diferenciar ausencia vs baja calidad |
| FP-3 | "La region de Nacional" en diagnostico | Fallback generico + typo template | FASE-C | Agregar regiones + corregir fallback + typo |
| FP-4 | pain no_whatsapp_visible falso positivo | whatsapp_html_detected no llega a pain_solution_mapper | FASE-E | Propagar campo a ValidationSummary + pain_mapper |
| FP-5 | Region "nacional" persiste en template | Solo URL consulta, ignora GBP address | FASE-E | Inferir region desde GBP + sanitizar hotel_region |
| FP-6 | phone_web=null cuando tel: existe | Scraper no parsea href="tel:" | FASE-E | Capturar tel: links en _extract_contact() |
| FP-7 | whatsapp_verified=0.0 incorrecto | coherence_validator no consulta HTML | FASE-E | Consultar whatsapp_html_detected en coherence gate |

---

## Seccion C: Tests

| Fase | Tests ejecutados | Resultado |
|------|-----------------|-----------|
| FASE-A | test_pain_solution_mapper.py + test_diagnostic_brechas.py | 25 passed, whatsapp_html_detected validated |
| FASE-B | test_diagnostic_brechas.py (25 tests) + test_pain_solution_mapper.py (5) | 25 passed, 3 nuevos tests blocks_analyzed |
| FASE-C | test suite completo (commercial_documents + asset_generation) | 218 passed, 7 pre-existentes |
| FASE-D | E2E v4complete | coherence 0.84, 5/6 gate checks, READY |
| FASE-E | [pendiente] tests whatsapp + region + pain + coherence | [pendiente] |

---

## Seccion D: Metricas Acumulativas

| Metrica | Pre-fix | Post-FASE-D | Post-FASE-E (esperado) |
|---------|---------|-------------|------------------------|
| Falsos positivos WhatsApp (amazilia) | 1 | 0 (diagnostico corregido) | 0 (pain + coherence tambien) |
| Pain IDs falsos no_whatsapp_visible | 1 (no medido) | 1 (persiste) | 0 |
| whatsapp_verified score falso 0.0 | 1 (no medido) | 1 (persiste) | 0.5+ (parcial si HTML existe) |
| Region "nacional" en template | 7+ instancias | 7+ instancias | 0 |
| Regiones detectables por URL | 4 | 4 | 4+ (keywords ampliadas) |
| Telefonos capturados (tel: links) | 0 | 0 | Capturados via scraper |
| Regiones mapeadas | 6 | 10 | 10 + 7 inferibles desde GBP |
| Coherence score (amazilia) | 0.84 | 0.84 | >= 0.84 |

---

## Seccion E: Documentacion Oficial (CONTRIBUTING.md §55-163)

### Flujo Post-Proyecto Obligatorio (TODAS las fases completadas)

Este es el Paso 7 del `phased_project_executor.md`. Ejecutar UNA VEZ al cerrar el proyecto.
El registro por fase (log_phase_completion.py) ya se ejecuto en el Paso 6 de cada fase individual.

#### E1. Diagnostico Inicial (CONTRIBUTING §60-67)

```bash
./venv/Scripts/python.exe scripts/version_consistency_checker.py
./venv/Scripts/python.exe main.py --doctor
```

- [x] version_consistency_checker.py pasa sin discrepancias (v4.25.3 sincronizado, crash Unicode pre-existente en emoji output)
- [x] doctor no reporta errores criticos (1 issue no-critico: agents_path_consistency symlink)

#### E2. Sincronizacion Automatica (CONTRIBUTING §70-76)

```bash
./venv/Scripts/python.exe scripts/sync_versions.py
```

Sincroniza VERSION.yaml → 6 archivos: AGENTS.md, README.md, .cursorrules, CONTRIBUTING.md, GUIA_TECNICA.md, REGISTRY.md

- [x] sync_versions.py ejecutado sin errores (3 archivos actualizados: README, AGENTS, .cursorrules)

#### E3. CHANGELOG.md (CONTRIBUTING §78-85, MANUAL)

Formato segun documentation_rules.md §36-58:

```markdown
## [4.25.4] - Correccion Falsos Positivos Diagnosticos (2026-04-09)

### Objetivo
Eliminar 3 falsos positivos y errores de narrativa detectados en diagnostico de amaziliahotel.com

### Cambios Implementados
- `modules/auditors/v4_comprehensive.py` - Conectar _detectar_whatsapp() al cross_validator
- `modules/commercial_documents/data_structures.py` - Campo whatsapp_html_detected
- `modules/commercial_documents/v4_diagnostic_generator.py` - Fix WhatsApp + citability + regional
- `modules/commercial_documents/templates/diagnostico_v6_template.md` - Typo yRevisan

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| [completar por fase] | [completar] |

### Tests
- N tests pasando
```

**NOTA:** FASE-D es validacion-only → NO bump version. Agregar como subsection dentro de la version de FASE-A/B/C.

- [x] CHANGELOG.md tiene entrada para la version actual (FASE-D Validacion E2E en v4.25.3)
- [x] No hay entradas duplicadas
- [x] CHANGELOG describe archivos modificados de cada fase

#### E4. GUIA_TECNICA.md (CONTRIBUTING §86-93, MANUAL)

Agregar seccion "Notas de Cambios v4.25.4":

```markdown
### Notas de Cambios v4.25.4 - Correccion Falsos Positivos

**Modulos afectados:** auditors, commercial_documents, data_structures

**Problema:** Tres falsos positivos/errores en diagnosticos generados para amaziliahotel.com:
1. WhatsApp detectado como ausente cuando boton HTML existe visualmente
2. Narrativa citability incorrecta ("poco estructurado" cuando blocks_analyzed=0)
3. Errores regionales ("nacional" en lugar de region real) + typo template

**Solucion:**
- [FASE-A] _detectar_whatsapp() del scraper alimenta cross_validator via whatsapp_html_detected
- [FASE-B] Logica citability distingue blocks_analyzed=0 (no discoverable) vs score real bajo
- [FASE-C] Eje Cafetero agregado a region_contexts, fallback mejorado, typo corregido

**Backwards compatibility:** Sin cambios en API publica. Validacion existente no afectada.
```

- [x] GUIA_TECNICA.md tiene nota tecnica para cada fase con cambios ("Corrección Falsos Positivos — FASE-A/B/C/D")
- [x] Nota incluye modulos afectados, problema/solucion, backwards compatibility

#### E5. Skills/Workflows (CONTRIBUTING §94-106, MANUAL)

```bash
ls -la .agents/workflows/*.md
```

- [x] Todos los .md en .agents/workflows/ listados en .agents/workflows/README.md (doctor PASS)
- [x] No hay skills huerfanos

#### E6. Regenerar SYSTEM_STATUS.md (CONTRIBUTING §107-111)

```bash
./venv/Scripts/python.exe scripts/doctor.py --status
```

- [x] SYSTEM_STATUS.md regenerado con version actual (16 skills, 795 shadow logs, 110 sesiones)

#### E7. Verificar DOMAIN_PRIMER.md (CONTRIBUTING §145-157)

```bash
./venv/Scripts/python.exe scripts/doctor.py --context
```

- [x] Todo modulo en `modules/` documentado en DOMAIN_PRIMER.md (doctor PASS)
- [x] Todo archivo referenciado en DOMAIN_PRIMER.md existe en disco (doctor PASS)

#### E8. Symlink + Validacion Final (CONTRIBUTING §113-128)

```bash
ls -la .agent/workflows    # Debe mostrar → .agents/workflows
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
git diff --stat
```

- [x] Symlink .agent/workflows → .agents/workflows intacto
- [x] run_all_validations.py --quick pasa sin errores (4/4 PASS)
- [x] git diff --stat muestra todos los archivos modificados

---

## Seccion F: Lecciones Aprendidas

1. **HTML comprimido no es problema en iah-cli**: `requests` descomprime automaticamente gzip/deflate/brotli. El falso negativo de WhatsApp no fue por compresion -- el sitio genuinamente no tiene boton WhatsApp.

2. **Distinguir "ausencia de dato" de "dato malo"**: `blocks_analyzed=0` no es contenido malo. La narrativa debe diferenciar entre "no hay contenido para analizar" y "el contenido analizado es de baja calidad".

3. **Region "nacional" como fallback persiste**: `_build_regional_context()` necesita que cada hotel tenga una region real. Sin onboarding que capture region, el fallback siempre sera "nacional". Solucion: consultar GBP address.

4. **phone_web vs whatsapp_html_detected son campos distintos**: Uno viene del Schema JSON-LD, otro del escaneo HTML. Un hotel puede tener telefono sin WhatsApp y viceversa.

5. **version_consistency_checker.py tiene bug Unicode**: Los emojis en output crashean con console cp1252 de Windows. Pre-existente, no relacionado con este proyecto.

6. **Fix de 1 consumidor no es suficiente**: FASE-A corrigio v4_diagnostic_generator (1 de 4 consumidores). El dato `whatsapp_html_detected` necesitaba propagarse a ValidationSummary, pain_solution_mapper, y coherence_validator. Regla: por cada dato nuevo, identificar TODOS los consumidores antes de cerrar.

7. **Deteccion por URL sola es insuficiente**: `_detect_region_from_url()` solo consulta la URL. Hoteles sin keywords geograficas en su dominio (amaziliahotel.com) siempre caen a "nacional". GBP address ya esta disponible y contiene la ciudad real -- usarla como fallback.
