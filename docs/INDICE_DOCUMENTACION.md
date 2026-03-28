# Índice de Documentación - IA Hoteles Agent CLI

**Versión:** 4.10.0  
**Última actualización:** 27 Marzo 2026

---

## 📚 Documentación General

| Documento | Descripción | Actualizado |
|-----------|-------------|-------------|
| `README.md` | Guía de uso general | sync_versions.py |
| `AGENTS.md` | Contexto global canónico | Manual |
| `CHANGELOG.md` | Historial de cambios | Manual |
| `VERSION.yaml` | Fuente de verdad de versiones | Manual |

---

## 📖 Guías

| Documento | Descripción | Actualizado |
|-----------|-------------|-------------|
| `docs/GUIA_TECNICA.md` | Guía técnica y arquitectura | Manual |
| `docs/CONTRIBUTING.md` | Guía de contribución | Manual |
| `docs/PRECIOS_PAQUETES.md` | Precios y paquetes comerciales | Manual |

---

## 🔧 Módulos del Sistema

### Core

| Módulo | Descripción | Ubicación |
|--------|-------------|-----------|
| `main.py` | Punto de entrada CLI | Raíz |
| `orchestration_v4/` | Flujo dos fases | `modules/` |
| `agent_harness/` | Memoria y routing | Raíz |

### Validación

| Módulo | Descripción | Ubicación |
|--------|-------------|-----------|
| `data_validation/` | Validación cruzada | `modules/` |
| `evidence_ledger.py` | Almacén de evidencia | `data_validation/` |
| `contradiction_engine.py` | Detección de conflictos | `data_validation/` |
| `consistency_checker.py` | Validación inter-documento | `data_validation/` |
| `metadata_validator.py` | Detección CMS defaults | `data_validation/` |

### Financiera

| Módulo | Descripción | Ubicación |
|--------|-------------|-----------|
| `financial_engine/` | Motor financiero | `modules/` |
| `calculator_v2.py` | Calculadora v2 | `modules/financial_engine/` |
| `no_defaults_validator.py` | Validación sin defaults | `modules/financial_engine/` |

### Commercial Documents

|| Módulo | Descripción | Ubicación |
|--------|-------------|-----------|
| `commercial_documents/` | Documentos comerciales | `modules/` |
| `v4_diagnostic_generator.py` | Generador diagnóstico V6 | `modules/commercial_documents/` |
| `v4_proposal_generator.py` | Generador propuesta V6 | `modules/commercial_documents/` |
| `composer.py` | Generación determinística | `modules/commercial_documents/` |
| `coherence_validator.py` | Validador de coherencia | `modules/commercial_documents/` |
| `pain_solution_mapper.py` | Mapeo problemas→assets | `modules/commercial_documents/` |

### Assets

|| Módulo | Descripción | Ubicación |
|--------|-------------|-----------|
| `asset_generation/` | Generación condicional | `modules/` |
| `asset_catalog.py` | Catálogo centralizado | `modules/asset_generation/` |
| `asset_diagnostic_linker.py` | Link assets a diagnóstico | `modules/asset_generation/` |
| `conditional_generator.py` | Generador condicional | `modules/asset_generation/` |
| `preflight_checks.py` | Gates de calidad | `modules/asset_generation/` |
| `v4_asset_orchestrator.py` | Orchestrator de assets V4 | `modules/asset_generation/` |

### Quality Gates

| Módulo | Descripción | Ubicación |
|--------|-------------|-----------|
| `quality_gates/` | Gates de publicación | `modules/` |
| `domain_gates.py` | Gates por dominio | `modules/quality_gates/` |
| `coherence_gate.py` | Gate de coherencia | `modules/quality_gates/` |
| `publication_gates.py` | Gates de publicación | `modules/quality_gates/` |

### Auditors

|| Módulo | Descripción | Ubicación |
|--------|-------------|-----------|
| `auditors/` | APIs externas | `modules/` |
| `v4_comprehensive_auditor.py` | Auditor comprehensivo V4 | `modules/auditors/` |

### Observabilidad

| Módulo | Descripción | Ubicación |
|--------|-------------|-----------|
| `observability/` | Dashboard y calibración | Raíz |
| `dashboard.py` | Métricas | `observability/` |
| `calibration.py` | Calibración de umbrales | `observability/` |

### Data Models

| Módulo | Descripción | Ubicación |
|--------|-------------|-----------|
| `data_models/` | Modelos Pydantic | Raíz |
| `canonical_assessment.py` | Assessment unificado | `data_models/` |
| `claim.py` | Claims con evidencia | `data_models/` |
| `evidence.py` | Evidencia con hash | `data_models/` |

### Enums

| Módulo | Descripción | Ubicación |
|--------|-------------|-----------|
| `enums/` | Enumeraciones | Raíz |
| `severity.py` | Niveles de severidad | `enums/` |
| `confidence_level.py` | Niveles de confianza | `enums/` |

---

## 🧪 Testing

| Directorio | Descripción |
|------------|-------------|
| `tests/` | Suite completa de tests |
| `tests/regression/` | Suite de regresión permanente |
| `tests/data_validation/` | Tests de validación |
| `tests/financial_engine/` | Tests financieros |
| `tests/asset_generation/` | Tests de assets |

---

## 📜 Scripts

| Script | Descripción |
|--------|-------------|
| `scripts/sync_versions.py` | Sincroniza versiones |
| `scripts/run_all_validations.py` | Validaciones completas |
| `scripts/validate_context_integrity.py` | Valida referencias |
| `scripts/generate_domain_primer.py` | Genera DOMAIN_PRIMER |

---

## 🔗 Referencias

- **Versión actual:** `VERSION.yaml`
- **Contexto global:** `AGENTS.md`
- **Contribución:** `docs/CONTRIBUTING.md`
- **Changelog:** `CHANGELOG.md`
