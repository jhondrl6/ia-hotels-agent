# IA Hoteles Agent CLI

**Plataforma agéntica de diagnóstico de visibilidad digital hotelera: audita presencia en Google, IAs y búsquedas locales; cuantifica la fuga de reservas directas; y genera assets técnicos (schema, FAQ, llms.txt) para recuperar ingresos que hoy van a OTAs y competidores.**

**v4.73.0** -- Reparacion-Pipeline-Salento-Real | Actualizado 29 Agosto 2026 | 3,631 pruebas automatizadas | 0 errores conocidos

---

## Indice de Navegacion Rapida

| Si buscas... | Ir a... |
|--------------|---------|
| **Indice Completo de Documentacion** | [INDICE_DOCUMENTACION.md](INDICE_DOCUMENTACION.md) |
| **Habilidades del Agente (Skills)** | `.agents/workflows/` — phased_project_executor (skills v4_* archivados en v4.72.2) |
| **Estrategia y Roadmap 2026** | [ROADMAP.md](ROADMAP.md) |
| **Historial de Cambios** | [CHANGELOG.md](CHANGELOG.md) |
| **Guia Tecnica (Arquitectura)** | [docs/GUIA_TECNICA.md](docs/GUIA_TECNICA.md) |
| **Dominio Hotelero-Digital** | [.agent/knowledge/DOMAIN_PRIMER.md](.agent/knowledge/DOMAIN_PRIMER.md) |
| **Contexto Global del Agente** | [AGENTS.md](AGENTS.md) (canonico) + [.cursorrules](.cursorrules) (puente) |
| **Convenciones de Contribucion** | [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) |

---

## Estado del Proyecto (v4.73.0 -- Reparacion-Pipeline-Salento-Real)

- **3,631 test functions** — suite completa, 0 regresiones
- **207 archivos Python en modules/** (~78K lineas, 24 directorios) + **30 scripts** (~7.6K lineas) + **57 directorios de test**
- **9 config YAML** con schema validado
- **1 agent skill** en `.agents/workflows/` (phased_project_executor) + README.md
- **13 Publication Gates** — hard_contradictions, evidence_coverage, financial_validity, coherence, critical_recall, ethics, tier_c_onboarding_required, coverage_no_silent_drop, doc_audit_consistency (modo WARNING), pricing_compliance (blocking); content_quality, asset_confidence, proposal_asset_alignment (advisory)
- **Coherence Score >= 0.8** requerido para publicacion
- **25 assets** en catalogo (22 IMPLEMENTED + 2 DEPRECATED + 1 MANUAL_ONLY)
- **Financial Evidence Engine** — metadata epistemica, benchmarks regionales 2026, channel-aware scoring, rendering condicional

---

## Como Funciona el Sistema

IA Hoteles Agent opera como un **cerebro orquestador** (Agent Harness) que valida, analiza y protege:

1. **Datos** -> Recolecta informacion de web, Google Business Profile y APIs
2. **Valida** -> Compara fuentes para detectar inconsistencias (cruzada)
3. **Calcula** -> Proyecciones financieras en 3 escenarios (70/20/10) con recovery_factor
4. **Genera** -> Diagnostico + Propuesta + Assets condicionales
5. **Certifica** -> Controles de coherencia antes de entregar

Todos los parametros financieros, umbrales de scoring, fallbacks y narrativas de impacto son configurables via YAML sin tocar codigo. Backwards compatible: sin YAML, usa defaults documentados.

---

## Que es IA Hoteles Agent?

Sistema que responde a la pregunta: "Por que este hotel pierde reservas que van a Booking, competidores o ChatGPT?". Audita 4 pilares progresivos (SEO -> AEO -> IAO, con GEO como pilar lateral), asigna un costo en COP a cada brecha detectada, y genera un paquete de assets tecnicos listos para deploy con validacion cruzada de coherencia.

**Los 4 Pilares de Visibilidad Digital:**

| Pilar | Sigla | Proposito | Ejemplo |
|-------|-------|-----------|---------|
| SEO | Search Engine Optimization | **Para que te ENCUENTREN** | Apareces en top 10 de Google organico |
| GEO | Geographic Optimization | **Para que te UBIQUEN** | Sales en Google Maps con resenas y fotos |
| AEO | Answer Engine Optimization | **Para que te CITEN** | Siri lee tu ficha: "Cierra a las 8:00 PM" |
| IAO | Intelligent Agent Optimization | **Para que te RECOMIENDEN** | ChatGPT te recomienda vs competidores |

---

## Inicio Rapido (5 minutos)

```bash
# 1. Clonar e instalar
git clone https://github.com/jhondrl6/ia-hotels-agent.git
cd iah-cli
python -m venv venv
.\venv\Scripts\Activate.ps1   # Windows PowerShell
pip install -r requirements.txt

# 2. Configuracion Inicial
python main.py setup

# 3. Primer analisis
python main.py v4complete --url https://hotel.com
```

---

## Flujo v4complete (5 Fases)

```bash
python main.py v4complete --url https://hotel.com --nombre "Hotel Nombre"
```

```
FASE 1        FASE 2           FASE 3          FASE 4          FASE 5
HOOK     ->   VALIDACION  ->   MAPEO P->S  ->  GATE COHERENCIA -> ASSETS
Auto          APIs Cruzada     PainSolution    Score >=0.8       Validados
                               Mapper          (configurable)

Output: 01_DIAGNOSTICO_Y_OPORTUNIDAD.md (siempre)
        02_PROPUESTA_COMERCIAL.md (si coherence >= 0.8)
        delivery_assets/ (segun confianza de cada asset)
```

**Caracteristicas clave:**
- Validacion cruzada de datos (Web + Google Business Profile + Input)
- Calculo de escenarios financieros (Conservador 70% / Realista 20% / Optimista 10%)
- Gate de coherencia con score calculado vs umbral configurable (default >= 0.8)
- Generacion condicional: diagnostico siempre, propuesta solo si pasa coherencia
- PainSolutionMapper: mapeo automatico problemas -> assets con prioridades P1/P2/P3

---

## Comandos Disponibles

| Comando | Estado | Proposito | Output |
|---------|--------|-----------|--------|
| `v4complete` | Activo | **Flujo completo con controles de coherencia** | Diagnostico + Propuesta condicional + Assets |
| `v4audit` | Activo | Auditoria tecnica rapida con APIs | JSON con validacion cruzada |
| `hook-pdf` | Activo | **PDF gancho de 2 paginas** desde output v4complete | PDF A4 con cifra fuga, brechas, precios |
| `validate-guarantee` | Activo | Valida garantia Dia 55 contra datos reales | Reporte de estado de garantia |
| `execute` | Activo | Implementacion de paquete usando analisis previo | Assets segun paquete seleccionado |
| `stage` | Activo | Ejecuta etapas individuales (geo, ia, seo, outputs) | Resultado de fase especifica |
| `deploy` | Activo | Despliegue remoto via FTP/WP-API | Archivos subidos al servidor |
| `setup` | Activo | Configuracion interactiva de API keys | Credenciales configuradas |
| `onboard` | Activo | Captura datos operativos reales del hotel | Mejora precision del analisis |
| `--doctor` | Activo | Diagnostico del ecosistema de agentes | Reporte de salud completo |
| `spark` | Deprecado | Legacy v3.x | Usar `v4complete` |
| `audit` | Deprecado | Legacy v3.x | Usar `v4audit` |

### Opciones de v4complete

| Flag | Uso |
|------|-----|
| `--url` | URL del hotel a analizar (requerido) |
| `--nombre` | Nombre del hotel (opcional, extraido de URL) |
| `--output` | Directorio de salida (default: ./output) |
| `--debug` | Modo verbose con informacion detallada |

---

## Comando onboard - Datos Operativos Reales

Captura datos operativos reales del hotel para mejorar la precision del analisis v4complete.

**Cuando usar:** Despues de `v4complete` para mejorar coherence score, cuando se requieren proyecciones financieras precisas, o para convertir assets de WARNING a PASSED.

```bash
python main.py onboard --url https://hotel.com --nombre "Hotel Nombre"
python main.py onboard --url https://hotel.com --run-audit
```

**Datos que captura:** Habitaciones, reservas/mes, ADR real, % canal directo, % ocupacion, tarifa promedio.

**Resultado:** Confidence ESTIMATED -> VERIFIED | Coherence potencialmente >= 0.8 | Assets WARNING -> PASSED

---

## Doctor - Diagnostico del Ecosistema

```bash
python main.py --doctor              # Check completo
python scripts/doctor.py             # Directo
python scripts/doctor.py --status    # Regenerar SYSTEM_STATUS.md
python scripts/doctor.py --regenerate-domain-primer  # Regenerar DOMAIN_PRIMER.md
python scripts/doctor.py --agent     # Diagnostico ecosistema agentes
python scripts/doctor.py --context   # Solo integridad de contexto
python scripts/doctor.py --json      # Output maquina-legible
```

**Que verifica:**

| Check | Descripcion |
|-------|-------------|
| Symlink integrity | `.agent/workflows` -> `.agents/workflows` |
| README dead references | Skills referenciados pero inexistentes |
| Skills tracked | Todos los .md en workflows reflejados en README |
| Shadow logs health | JSON validos y estructura correcta |
| Memory structure | current_state.json, error_catalog, sesiones |
| Gitignore patterns | Datos runtime excluidos de version control |
| Knowledge base | DOMAIN_PRIMER.md existe |
| Config files integrity | 9 YAML con estructura valida |

---

## Escenarios Financieros

Cada hotel recibe proyecciones personalizadas basadas en sus datos validados. Parametros configurables via `config/scenarios.yaml`, `config/pricing.yaml` y `config/financial_defaults.yaml`.

| Escenario | Probabilidad | recovery_factor | Base de calculo |
|-----------|--------------|-----------------|-----------------|
| **Conservador** | 70% | 0.15 | Peor caso plausible (recupera 15% de la perdida) |
| **Realista** | 20% | 0.35 | Meta esperada (recupera 35% de la perdida) |
| **Optimista** | 10% | 0.25 | Mejor caso (recupera 25% de la perdida) |

**Formula**: `projected_gain = monthly_loss_cop x pain_ratio x recovery_factor`
**ROI**: `roi = (projected_gain x 6) / (precio_mensual x 6)` — cap en 5.0X (configurable en `config/commercial.yaml`)

**Motor Financiero Verificable**: Cada COP tiene origen trazable (ADR regional, occupancy validada), peso proporcional, etiqueta honesta (VERIFIED/ESTIMATED) y base verificable (comision OTA). El escenario optimista con valor negativo se presenta como "ganancia neta".

---

## Configuracion YAML (v4.38.0+)

31 hardcoded values migrados originalmente a 6 archivos YAML; hoy **9 archivos YAML** con schema validado. Todos los parametros son configurables sin tocar codigo.

| Archivo | Contenido |
|---------|-----------|
| `config/pricing.yaml` | TIER_CONFIG, GATE ratios, floor_price unificado |
| `config/scenarios.yaml` | Recovery factors, scenario weights, degradation, OTA shifts, ia_boost |
| `config/financial_defaults.yaml` | DEFAULTS financieros (12 valores) |
| `config/fallbacks.yaml` | Fallbacks de scores con flags estimated |
| `config/commercial.yaml` | ROI cap, break_even, descuentos, garantias, planes |
| `config/regional_benchmarks.yaml` | Pain narratives (16) + umbrales de scoring multi-region |
| `config/certificates.yaml` | Certificados SSL/TLS y configuracion de seguridad |
| `config/provider_registry.yaml` | Registro de providers LLM (modelos, endpoints, fallbacks) |
| `config/settings.yaml` | Configuracion general de la aplicacion |

**Backwards compatible:** Sin YAML, el sistema funciona identicamente con defaults documentados. Con YAML, todos los valores son configurables.

---

## Voice Readiness Proxy (v4.28.0+)

Evalua que tan preparado esta un hotel para que asistentes de voz (Siri, Google Assistant, Alexa) lo mencionen como respuesta directa. PROXY — mide los INPUTS que alimentan los asistentes de voz, NO consulta Siri/Alexa directamente.

| Componente | Peso | Que evalua |
|------------|------|------------|
| GBP Completeness | 30% | NAP, categorias, horarios, fotos, atributos |
| Schema for Voice | 25% | Hotel/LocalBusiness, FAQ, Speakable markup |
| Featured Snippets | 25% | Optimizacion para posicion cero en Google |
| Factual Coverage | 20% | Datos factuales accesibles (horarios, precios, direccion) |

| Nivel | Rango | Significado |
|-------|-------|-------------|
| Critical | 0-25 | Sin presencia detectable por asistentes de voz |
| Basic | 26-50 | Presencia minima, datos parciales |
| Good | 51-75 | Optimizacion solida, capturable por voz |
| Excellent | 76-100 | Presencia completa y consistente para voz |

---

## Calidad Garantizada

- **3,631 test functions** — suite completa, 0 regresiones
- **61 config tests** — migracion YAML, fallback, schema, integracion
- **Pre-commit hooks** — Validaciones automaticas en cada commit (version-sync, agent-ecosystem, secrets, residual files, referencias .opencode con auto-fix)
- **Phased Workflow** — `.agents/workflows/phased_project_executor.md` v2.17.0 (1 fase/sesion, max 60 iteraciones)
- **Capitalizacion de Lecciones** — cada plan recupera la experiencia de planes anteriores (memoria del agente + QMind `iah-cli-lecciones`) antes de planificar y escribe sus lecciones nuevas al cerrar cada fase
- **Coherence Score >= 0.8** — Validacion cruzada documentos <-> assets
- **13 Publication Gates** — hard_contradictions, evidence_coverage, financial_validity, coherence, critical_recall, ethics, tier_c_onboarding_required, coverage_no_silent_drop, doc_audit_consistency (modo WARNING), pricing_compliance (blocking); content_quality, asset_confidence, proposal_asset_alignment (advisory)
- **Delivery Quality Report** — QA bloqueante pre-ZIP, advisory warnings para IA-Readiness Critical

---

## Troubleshooting

| Problema | Solucion |
|----------|----------|
| Fallo Gate de Coherencia | Verifica que los datos tengan confianza suficiente (>=0.8) y no haya conflictos entre fuentes |
| No LLM API key configured | Ejecuta `python main.py setup` para configurar de forma segura |
| sync_versions.py desincronizado | Ejecuta `python scripts/sync_versions.py` para resincronizar headers de version |

---

## Arquitectura del Repositorio

```
iah-cli/
  main.py                     # CLI entry point (v4complete, hook-pdf, deploy, etc.)
  VERSION.yaml                # Fuente unica de verdad (version)
  config/                     # Configuracion YAML (9 archivos)
  templates/                  # Templates HTML/CSS/MD para generacion
    hook_template.md            #   Template PDF gancho (HTML, 34 placeholders)
    hook_styles.css             #   Estilos A4, 2 paginas, hook figure 28pt
    delivery_readme_template.md #   Template README de entrega
    diagnostico_ejecutivo.md    #   Template diagnostico ejecutivo
    local_content/              #   Templates de contenido local
  modules/                    # 207 archivos Python (~78K lineas) en 24 directorios
    asset_generation/         #   Generacion condicional de assets
    commercial_documents/     #   Diagnostico + Propuesta v4 + PDF gancho (hook-pdf)
    financial_engine/         #   Pricing, scenarios, loss projector
    orchestration_v4/         #   Two-phase flow, auditor
    quality/                  #   Coherence validator, asset semantics
    quality_gates/            #   Publication gates (13), commercial gate, ethics
    scrapers/                 #   Places API, Google Travel, SerpAPI
    common/                   #   yaml_loader, fallback_loader
    analytics/                #   GA4, GSC (Profound/Semrush deprecados)
    deployer/                 #   FTP/WP-API deployment
    analyzers/                #   Analisis de datos y metricas
    auditors/                 #   Auditoria de componentes
    data_validation/          #   Validacion cruzada de fuentes
    delivery/                 #   Empaquetado y entrega de assets
    generators/               #   Generadores de contenido
    geo_enrichment/           #   Enriquecimiento geografico (GEO)
    monitoring/               #   Monitoreo de pipelines
    onboarding/               #   Captura de datos operativos del hotel
    orchestration/            #   Orquestacion de flujos
    postprocessors/           #   Post-procesamiento de outputs
    providers/                #   Providers LLM y API
    utils/                    #   Utilidades compartidas
    validation/               #   Validacion de outputs
  tests/                      # ~74K lineas de test (281 archivos, 57 directorios)
    config/                   #   61 tests de migracion YAML
    financial_engine/         #   Tests de motor financiero
    commercial_documents/     #   Tests de documentos comerciales
  scripts/                    # 30 scripts de automatizacion
    sync_versions.py          #   Sincronizacion versiones
    doctor.py                 #   Diagnostico ecosistema
    log_phase_completion.py   #   Registro de fases en REGISTRY.md
    run_all_validations.py    #   Suite de validaciones
    validate_opencode_refs.py #   Referencias .opencode validas (auto-fix)
  .agents/workflows/          # Agent skills (phased_project_executor + README)
  .opencode/plans/            # Planes de fases (phased execution)
  evidence/                   # Evidencia de fases ejecutadas
```

---

**IA HOTELES AGENT (c) 2026**
*Diagnosticando la invisibilidad digital hotelera y recuperando reservas que hoy van a OTAs.*
