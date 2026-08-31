# IA Hoteles Agent CLI

**Plataforma agéntica de diagnóstico de visibilidad digital hotelera: audita presencia en Google, IAs y búsquedas locales; cuantifica la fuga de reservas directas; y genera assets técnicos (schema, FAQ, llms.txt) para recuperar ingresos que hoy van a OTAs y competidores.**

**v4.74.1** -- Blocklist-v2 | Actualizado 31 Agosto 2026

---

## Indice de Navegacion Rapida

| Si buscas... | Ir a... |
|--------------|---------|
| **Indice Completo de Documentacion** | [INDICE_DOCUMENTACION.md](INDICE_DOCUMENTACION.md) |
| **Guia Tecnica (Arquitectura)** | [docs/GUIA_TECNICA.md](docs/GUIA_TECNICA.md) |
| **Historial de Cambios** | [CHANGELOG.md](CHANGELOG.md) |
| **Estrategia y Roadmap 2026** | [ROADMAP.md](ROADMAP.md) |
| **Estado Interno del Proyecto** | [AGENTS.md](AGENTS.md) (canonico) + [.cursorrules](.cursorrules) (puente) |
| **Convenciones de Contribucion** | [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) |
| **Dominio Hotelero-Digital** | [.agent/knowledge/DOMAIN_PRIMER.md](.agent/knowledge/DOMAIN_PRIMER.md) |
| **Habilidades del Agente (Skills)** | `.agents/workflows/` — phased_project_executor |

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

Desde v4.74.0 incluye un **guard de URL propia**: las URLs de OTAs, redes sociales y buscadores (Booking, Instagram, etc.) se rechazan antes de cualquier llamada de red/API, evitando analisis sobre paginas de terceros. El bypass explicito existe via `--force`.

---

## Que Produce

Cada corrida de `v4complete` entrega un paquete completo de diagnostico comercial y assets tecnicos:

```
output/<corrida>/v4_complete/
├── 01_DIAGNOSTICO_Y_OPORTUNIDAD_<fecha>.md   # Diagnostico con brechas cuantificadas en COP
├── 02_PROPUESTA_COMERCIAL_<fecha>.md         # Propuesta (solo si coherence >= 0.8)
├── v4_complete_report.json                   # Reporte maquina-legible completo
├── <hotel>/                                  # Assets tecnicos generados
│   ├── llms_txt/                             #   llms.txt estandar para IAs
│   ├── geo_enriched/                         #   Enriquecimiento geografico
│   ├── analytics_setup_guide/                #   Guia GA4 + trafico indirecto
│   └── ...                                   #   Segun brechas detectadas (P1/P2/P3)
├── deliveries/<hotel>_<fecha>.zip            # Paquete de entrega final
└── health_dashboard/                         # Dashboard de observabilidad
```

Adicionalmente, `hook-pdf` genera un **PDF gancho de 2 paginas** (A4) con la cifra de fuga mensual, brechas principales y precios — pensado para el primer contacto comercial.

---

## Como Funciona el Sistema

IA Hoteles Agent opera como un **cerebro orquestador** (Agent Harness) que valida, analiza y protege:

1. **Datos** -> Recolecta informacion de web, Google Business Profile y APIs
2. **Valida** -> Compara fuentes para detectar inconsistencias (validacion cruzada)
3. **Calcula** -> Proyecciones financieras en 3 escenarios (70/20/10)
4. **Genera** -> Diagnostico + Propuesta + Assets condicionales
5. **Certifica** -> Controles de coherencia (gates) antes de entregar

Todos los parametros financieros, umbrales de scoring, fallbacks y narrativas de impacto son configurables via YAML sin tocar codigo. Sin YAML, el sistema usa defaults documentados.

---

## Inicio Rapido

**Requisitos:**

- Python 3.13+ y un entorno virtual
- API keys de Google (ver tabla abajo). Sin keys el sistema funciona con benchmarks regionales (arquitectura NeverBlock), pero las validaciones externas quedan marcadas como ESTIMATED en vez de VERIFIED

```bash
# 1. Clonar e instalar
git clone https://github.com/jhondrl6/ia-hotels-agent.git
cd iah-cli
python -m venv venv
.\venv\Scripts\Activate.ps1   # Windows PowerShell (bash: source venv/bin/activate)
pip install -r requirements.txt

# 2. Configuracion de API keys (asistente interactivo)
python main.py setup

# 3. Primer analisis (URL del sitio PROPIO del hotel)
python main.py v4complete --url https://hoteldomino.com
```

**API keys (`python main.py setup` o editar `.env` directamente):**

| Key | Uso | Nivel |
|-----|-----|-------|
| `PAGESPEED_API_KEY` | Core Web Vitals reales | Recomendada |
| `GOOGLE_MAPS_API_KEY` | Places API (datos del hotel, fotos) | Recomendada |
| `GA4_PROPERTY_ID` + service account | Trafico real del sitio | Opcional (advisory) |
| Google Search Console | Keywords, posiciones, CTR | Opcional (advisory) |
| `DEEPSEEK_API_KEY` / `ANTHROPIC_API_KEY` | Generacion narrativa | Opcional |

---

## Flujo v4complete

```bash
python main.py v4complete --url https://hoteldomino.com --nombre "Hotel Domino"
```

```
FASE 1        FASE 2           FASE 3          FASE 4          FASE 5
HOOK     ->   VALIDACION  ->   MAPEO P->S  ->  GATE COHERENCIA -> ASSETS
Auto          APIs Cruzada     PainSolution    Score >=0.8       Validados
                               Mapper          (configurable)

Output: 01_DIAGNOSTICO_Y_OPORTUNIDAD.md (siempre)
        02_PROPUESTA_COMERCIAL.md (si coherence >= 0.8)
        Assets (segun confianza de cada asset: PASSED / WARNING / BLOCKED)
```

**Caracteristicas clave:**
- Guard de URL propia: rechaza OTAs/redes sociales antes de red/API (blocklist versionada en `config/url_blocklist.yaml`, `--force` para bypass auditado)
- Validacion cruzada de datos (Web + Google Business Profile + Input)
- Escenarios financieros: Conservador 70% / Realista 20% / Optimista 10%
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
| `execute` | Activo | Implementacion de paquete usando analisis previo | Assets segun paquete seleccionado |
| `stage` | Activo | Ejecuta etapas individuales (geo, ia, seo, outputs) | Resultado de fase especifica |
| `onboard` | Activo | Captura datos operativos reales del hotel | Mejora precision del analisis |
| `deploy` | Activo | Despliegue remoto via FTP/WP-API | Archivos subidos al servidor |
| `validate-guarantee` | Activo | Valida garantia Dia 55 contra datos reales | Reporte de estado de garantia |
| `setup` | Activo | Configuracion interactiva de API keys | Credenciales configuradas |
| `--doctor` | Activo | Diagnostico del ecosistema de agentes | Reporte de salud completo |
| `spark` | Deprecado | Legacy v3.x | Usar `v4complete` |
| `audit` | Deprecado | Legacy v3.x | Usar `v4audit` |

### Opciones de v4complete

| Flag | Uso |
|------|-----|
| `--url` | URL del sitio propio del hotel (requerida; OTAs/redes se rechazan salvo `--force`) |
| `--nombre` | Nombre del hotel (opcional, extraido de URL) |
| `--output` | Directorio de salida (default: ./output) |
| `--debug` | Modo verbose con informacion detallada |
| `--force` | Bypass del guard de URL propia / sobrescribir PDF existente (evento auditado) |

### onboard - Datos Operativos Reales

Captura datos reales del hotel (habitaciones, reservas/mes, ADR, % canal directo, % ocupacion) para subir la confianza del analisis: ESTIMATED -> VERIFIED, assets WARNING -> PASSED.

```bash
python main.py onboard --url https://hoteldomino.com --nombre "Hotel Domino"
```

### hook-pdf - PDF Gancho Comercial

```bash
python main.py hook-pdf --output-dir output/v4_complete/   # desde una corrida v4complete
```

Valida que el reporte apunte a un sitio propio (misma proteccion que v4complete); `--force` omite el guard y/o sobrescribe el PDF existente.

### Doctor - Diagnostico del Ecosistema

```bash
python main.py --doctor              # Check completo
python scripts/doctor.py --status    # Regenerar SYSTEM_STATUS.md
python scripts/doctor.py --json      # Output maquina-legible
```

Verifica symlink de workflows, skills, memoria del agente, gitignore, DOMAIN_PRIMER e integridad de los YAML de config.

---

## Estado del Proyecto (v4.74.1 -- Blocklist-v2) vive en **[AGENTS.md](AGENTS.md)** — fuente unica del estado interno. Historial de cambios: [CHANGELOG.md](CHANGELOG.md). Registro de fases: [docs/contributing/REGISTRY.md](docs/contributing/REGISTRY.md).

---

## Escenarios Financieros

Cada hotel recibe proyecciones personalizadas basadas en sus datos validados. Cada cifra tiene origen trazable (ADR regional, occupancy validada), etiqueta honesta (VERIFIED/ESTIMATED) y base verificable (comision OTA).

| Escenario | Probabilidad | Base de calculo |
|-----------|--------------|-----------------|
| **Conservador** | 70% | Peor caso plausible |
| **Realista** | 20% | Meta esperada |
| **Optimista** | 10% | Mejor caso |

Formulas y parametros exactos (recovery_factor, ROI cap, degradacion): [docs/GUIA_TECNICA.md](docs/GUIA_TECNICA.md) y `config/scenarios.yaml`.

---

## Configuracion YAML

**10 archivos YAML** con schema validado; todos los parametros configurables sin tocar codigo. Sin YAML, el sistema usa defaults documentados (backwards compatible).

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
| `config/url_blocklist.yaml` | Blocklist versionada de plataformas OTA/red social/buscador (v4.74.0+) |

---

## Metricas Advisory (no bloqueantes)

Ademas de los gates de publicacion, cada corrida reporta metricas orientativas:

- **Voice Readiness Proxy** — preparacion para asistentes de voz (GBP 30%, Schema 25%, Snippets 25%, Factual 20%); mide inputs, no consulta Siri/Alexa
- **Citability Score / IA-Readiness / AI Crawler Score** — calidad de contenido para citacion por IAs y accesibilidad de crawlers

Se reportan para orientar mejoras pero nunca bloquean la publicacion.

---

## Calidad

Publicacion protegida por gates de calidad automaticos (coherencia documental, cobertura de evidencia, validez financiera, etica) y un QA bloqueante pre-entrega. La suite de pruebas, la lista completa de gates y sus umbrales se documentan en [AGENTS.md](AGENTS.md); las convenciones de contribucion y validacion en [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md).

---

## Troubleshooting

| Problema | Solucion |
|----------|----------|
| URL rechazada por el guard ("agregador de reservas / red social") | Es el comportamiento esperado (v4.74.0+): usa la URL del sitio propio del hotel; `--force` solo para casos excepcionales auditados |
| Fallo Gate de Coherencia | Verifica que los datos tengan confianza suficiente y no haya conflictos entre fuentes; `onboard` sube la confianza |
| No LLM API key configured | Ejecuta `python main.py setup` para configurar de forma segura |
| Symlink `.agent/workflows` roto en Windows | Windows requiere terminal con permisos de admin para crear symlinks (ver AGENTS.md §Diagnostico Rapido) |
| sync_versions.py desincronizado | Ejecuta `python scripts/sync_versions.py` para resincronizar headers de version |

---

## Arquitectura del Repositorio

```
iah-cli/
  main.py                     # CLI entry point (v4complete, hook-pdf, deploy, etc.)
  VERSION.yaml                # Fuente unica de verdad (version)
  config/                     # Configuracion YAML (10 archivos)
  templates/                  # Templates HTML/CSS/MD para generacion
    hook_template.md            #   Template PDF gancho (HTML, 34 placeholders)
    hook_styles.css             #   Estilos A4, 2 paginas, hook figure 28pt
    delivery_readme_template.md #   Template README de entrega
    diagnostico_ejecutivo.md    #   Template diagnostico ejecutivo
    local_content/              #   Templates de contenido local
  modules/                    # Modulos funcionales (24 directorios)
    data_validation/          #   Validacion cruzada + guard de URL propia (own_site_guard)
    commercial_documents/     #   Diagnostico + Propuesta v4 + PDF gancho (hook-pdf)
    financial_engine/         #   Pricing, scenarios, loss projector
    asset_generation/         #   Generacion condicional de assets
    quality_gates/            #   Publication gates, commercial gate, ethics
    orchestration_v4/         #   Two-phase flow, auditor
    auditors/                 #   APIs externas (Rich Results, Places, PageSpeed)
    analytics/                #   GA4, GSC, agregacion de datos
    scrapers/                 #   Places API, Google Travel, SerpAPI
    geo_enrichment/           #   Enriquecimiento geografico (GEO)
    delivery/                 #   Empaquetado y entrega de assets
    deployer/                 #   FTP/WP-API deployment
    onboarding/               #   Captura de datos operativos del hotel
    providers/                #   Providers LLM y API
    common/                   #   yaml_loader, fallback_loader
    ...                       #   analyzers, generators, monitoring, utils, validation
  agent_harness/              # Core del agente (memoria, routing, self-healing)
  tests/                      # Suite de pruebas (25 directorios por modulo)
  scripts/                    # Scripts de automatizacion y validacion
    sync_versions.py          #   Sincronizacion versiones
    doctor.py                 #   Diagnostico ecosistema
    log_phase_completion.py   #   Registro de fases en REGISTRY.md
    run_all_validations.py    #   Suite de validaciones
  .agents/workflows/          # Agent skills (phased_project_executor + README)
  .opencode/plans/            # Planes de fases (phased execution)
  evidence/                   # Evidencia de fases ejecutadas
  docs/                       # Documentacion detallada (GUIA_TECNICA, CONTRIBUTING)
```

---

**IA HOTELES AGENT (c) 2026**
*Diagnosticando la invisibilidad digital hotelera y recuperando reservas que hoy van a OTAs.*
