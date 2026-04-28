# IA Hoteles Agent CLI

**Plataforma agéntica de diagnóstico de visibilidad digital hotelera: audita presencia en Google, IAs y búsquedas locales; cuantifica la fuga de reservas directas; y genera assets técnicos (schema, FAQ, llms.txt, geo_playbook) para recuperar ingresos que hoy van a OTAs y competidores.**

**Version:** 4.36.0 | **Última actualización:** 27 Abril 2026

---

## 🧭 Índice de Navegación Rápida

| Si buscas... | Ir a... |
|--------------|---------|
| **Índice Completo de Documentación** | [INDICE_DOCUMENTACION.md](INDICE_DOCUMENTACION.md) |
| **Habilidades del Agente (Meta-Skills)** | `.agents/workflows/` - PhasedProjectExecutor (TDD Gate), Capability Contracts, v4_regression_guardian (validación post-implementación) |
| **Estrategia y Roadmap 2026** | [ROADMAP.md](ROADMAP.md) |
| **Historial de Cambios** | [CHANGELOG.md](CHANGELOG.md) |
| **Guía Técnica (Arquitectura)** | [docs/GUIA_TECNICA.md](docs/GUIA_TECNICA.md) |
| **Dominio Hotelero-Digital** | [.agent/knowledge/DOMAIN_PRIMER.md](.agent/knowledge/DOMAIN_PRIMER.md) (Glosario y taxonomía) |
| **Contexto Global del Agente** | [AGENTS.md](AGENTS.md) (canónico) + [.cursorrules](.cursorrules) (puente) |

---

> **🛡️ AGENT PLATFORM STATUS (v4.35.1 - Propuesta Dinámica + Intervención Amazilia Hotel)**:
> *   **Propuesta Dinámica desde Pain Detection (v4.35.0)**: Tabla de servicios generada dinámicamente según los pains detectados (no diccionario estático). 7 servicios base + AEO condicional cuando score_aeo < 20.
> *   **Planes de Implementación Dinámicos (v4.35.0)**: _build_7/30/60/90_day_plan() reciben asset_plan y generan contenido por prioridad P1/P2/P3. Backward compatible si asset_plan=None.
> *   **Motor Financiero Verificable (v4.27.0)**: Escenarios conservador/realista/optimista con recovery_factor (0.15/0.20/0.25). ROI realista <= 5.0X. pain_ratio aplicado a projected_gain.
> *   **Evidence Tiers**: A (datos reales) → B (scraping) → C (estimación) con disclaimers honestos por tier.
> *   **2,224 test functions**, 0 regresiones.
> *   **Intervención post-4.35.0 (Amazilia Hotel)**: Fix test drift, escenarios financieros ordenados, BUG-8 ortografía "huéspedes", template V6, planes dinámicos, sección competidores. v4complete E2E validado — GO.
> *   **Coherence Validator**: Score ≥ 0.8 requerido. 6 gates de pre-publicación (contradictions, coverage, validity, coherence, recall, ethics).

---

## 🧠 Cómo Funciona el Sistema

IA Hoteles Agent opera como un **cerebro orquestador** (Agent Harness) que valida, analiza y protege:

1. **Datos** → Recolecta información de web, Google Business Profile y APIs
2. **Valida** → Compara fuentes para detectar inconsistencias
3. **Calcula** → Proyecciones financieras en 3 escenarios (70/20/10)
4. **Genera** → Diagnóstico + Propuesta + Assets condicionales
5. **Certifica** → Controles de coherencia antes de entregar

El **Agent Harness** es el núcleo que orchestra: memoria (recuerda análisis previos), auto-corrección (repara errores), y routing inteligente (dirige cada tarea al módulo correcto).

---

## Contexto Global del Agente

- `AGENTS.md` — Fuente canónica de contexto global, modulos activos y flujo de trabajo
- `.cursorrules` — Puente de compatibilidad legacy
- Procedimiento para actualizar documentacion: `docs/CONTRIBUTING.md`

## 🎯 ¿Qué es IA Hoteles Agent?

Sistema que responde a la pregunta: "¿Por qué este hotel pierde reservas que van a Booking, competidores o ChatGPT?". Audita 4 pilares progresivos (SEO → AEO → IAO, con GEO como pilar lateral), asigna un costo en COP a cada brecha detectada, y genera un paquete de assets técnicos listos para deploy con validación cruzada de coherencia.

**Los 4 Pilares de Visibilidad Digital:**

| Pilar | Sigla | Propósito | Ejemplo |
|-------|-------|-----------|---------|
| SEO | Search Engine Optimization | **Para que te ENCUENTREN** | Apareces en top 10 de Google orgánico |
| GEO | Geographic Optimization | **Para que te UBICQUEN** | Sales en Google Maps con reseñas y fotos |
| AEO | Answer Engine Optimization | **Para que te CITEN** | Siri lee tu ficha: "Cierra a las 8:00 PM" |
| IAO | Intelligent Agent Optimization | **Para que te RECOMIENDEN** | ChatGPT te recomienda vs competidores |

El `score_global` fue reemplazado por `coherence_score` (0-1, umbral ≥ 0.8) como métrica principal de alineación. Los 4 pilares (SEO, GEO, AEO, IAO) contribute individualmente a la puntuación general de visibilidad, pero la validación cruzada entre diagnóstico, propuesta y assets usa coherence_score.

El diagnóstico siempre se entrega. La propuesta comercial solo se genera cuando los datos alcanzan score de coherencia ≥ 0.8. Los assets se etiquetan como VERIFIED o ESTIMATED según la fuente de datos disponible.

### Sistema de Evidencia y Confiabilidad v4.3.0

- **Validación cruzada**: Datos verificados entre web, Google Business Profile y APIs
- **Escenarios financieros**: Proyecciones con probabilidades (70%/20%/10%) en lugar de cifras únicas
- **Gate de coherencia**: Score automático que valida alineación entre diagnóstico, propuesta y assets

---

## 🚀 Inicio Rápido (5 minutos)

```bash
# 1. Clonar e instalar
git clone <repository-url>
cd iah-cli
python -m venv venv
.\venv\Scripts\Activate.ps1   # Windows PowerShell
pip install -r requirements.txt

# 2. Configuración Inicial (Umbrales v2.6)
python main.py setup
```

---

## 📊 Flujo Comercial y Técnico 2026

El sistema opera bajo el **Sistema v4.35.0** con validación cruzada de datos y controles de coherencia automáticos (score ≥ 0.8) entre diagnóstico, propuesta y assets.

```bash
python main.py v4complete --url https://hotel.com --nombre "Hotel Nombre"
```

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      FLUJO V4COMPLETE (5 Fases)                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  FASE 1        FASE 2           FASE 3          FASE 4       FASE 5     │
│  ───────       ───────          ───────         ───────      ───────    │
│                                                                         │
│  HOOK    →  VALIDACIÓN  →   MAPEO P→S   →   GATE COHERENCIA  → ASSETS   │
│  Automático   APIs Cruzada   PainSolution    Score ≥0.8       Validados │
│                              Mapper          (configurable)             │
│                                                                         │
│  Output: 01_DIAGNOSTICO_Y_OPORTUNIDAD.md (siempre)                      │
│          02_PROPUESTA_COMERCIAL.md (si coherence ≥ 0.8)                 │
│          delivery_assets/ (según confianza de cada asset)               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🔍 COMANDO V4COMPLETE - Protocolo de Verdad 4.0

**Propósito:** Ejecuta el flujo completo de certificación con validación cruzada, escenarios financieros y controles de coherencia automáticos.

**Características:**
- Validación cruzada de datos (Web + Google Business Profile + Input)
- Cálculo de escenarios financieros (Conservador 70% / Realista 20% / Optimista 10%)
- Gate de coherencia con score calculado vs umbral configurable (default ≥ 0.8)
- Generación condicional: diagnóstico siempre, propuesta solo si pasa coherencia
- PainSolutionMapper: mapeo automático problemas → assets con prioridades P1/P2/P3

### Comandos Disponibles

| Comando | Estado | Propósito | Output |
|---------|--------|-----------|--------|
| `v4complete` | ✅ | **Flujo completo con controles de coherencia** | Diagnóstico + Propuesta condicional + Assets |
| `v4audit` | ✅ | Auditoría técnica rápida con APIs | JSON con validación cruzada |
| `spark` | ⚠️ | Legacy v3.x (deprecado, usar `v4complete`) | - |
| `execute` | ✅ | Implementación de paquete usando análisis previo | Assets según paquete seleccionado |
| `stage` | ✅ | Ejecuta etapas individuales (geo, ia, seo, outputs) | Resultado de fase específica |
| `deploy` | ✅ | Despliegue remoto vía FTP/WP-API | Archivos subidos al servidor |
| `setup` | ✅ | Configuración interactiva de API keys | Credenciales configuradas |
| `onboard` | ✅ | Captura datos operativos reales del hotel | Mejora precisión del análisis |
| `--doctor` | ✅ | Diagnóstico del ecosistema de agentes | Reporte de salud completo |
| `audit` | ⚠️ | Legacy v3.x (deprecado) | - |

### Opciones de v4complete

| Flag | Uso |
|------|-----|
| `--url` | URL del hotel a analizar (requerido) |
| `--nombre` | Nombre del hotel (opcional, extraído de URL) |
| `--output` | Directorio de salida (default: ./output) |
| `--debug` | Modo verbose con información detallada |

**Ejemplos:**
```bash
# Análisis completo nuevo
python main.py v4complete --url https://hotel.com

# Análisis completo nuevo (recomendado)
python main.py v4complete --url https://hotel.com

# Implementar paquete (usa análisis previo si existe)
python main.py execute --url https://hotel.com --package starter_geo
```

---

## 📋 COMANDO ONBOARD - Datos Operativos Reales

**Propósito:** Capturar datos operativos reales del hotel para mejorar la precisión del análisis v4complete.

**Diferencia con v4complete:**
- `v4complete`: Usa datos estimados (benchmark regional, scraping)
- `onboard`: Usa datos reales proporcionados por el hotel

**Cuándo usar:**
- Después de `v4complete` para mejorar coherence score (de 0.55 → 0.8+)
- Cuando se requieren proyecciones financieras precisas
- Para convertir assets de WARNING a PASSED

### Opciones de onboard

| Flag | Uso |
|------|-----|
| `--url` | URL del hotel (opcional) |
| `--nombre` | Nombre del hotel |
| `--run-audit` | Ejecuta auditoría después de capturar datos |

**Ejemplo:**
```bash
python main.py onboard --url https://hotelvisperas.com --nombre "Hotel Vísperas"
python main.py onboard --url https://hotelvisperas.com --run-audit
```

**Datos que captura:**
- Número de habitaciones
- Reservas por mes
- Valor promedio de reserva (ADR real)
- % Canal directo
- % Ocupación
- Tarifa promedio

**Resultado:**
- Confidence: ESTIMATED → VERIFIED
- Coherence: Potencialmente ≥ 0.8
- Assets: WARNING → PASSED

---

## 🩺 Doctor - Diagnostico del Ecosistema de Agentes

**Propósito:** Verificar la salud completa del ecosistema de agentes (skills, validaciones, contexto).

**Comando:**
```bash
# Desde main.py (integrado al CLI)
python main.py --doctor

# O directo desde scripts
python scripts/doctor.py           # Check completo
python scripts/doctor.py --agent   # Solo ecosistema de agentes
python scripts/doctor.py --context # Solo integridad de contexto
python scripts/doctor.py --status  # Regenerar SYSTEM_STATUS.md
python scripts/doctor.py --json    # Output maquina-legible
```

**Que verifica:**
| Check | Descripción |
|-------|-------------|
| Symlink integrity | `.agent/workflows` -> `.agents/workflows` |
| README dead references | Skills referenciados pero inexistentes |
| Skills tracked | Todos los archivos .md en workflows reflejados en README |
| Shadow logs health | JSON validos y estructura correcta |
| Memory structure | current_state.json, error_catalog, sesiones |
| Gitignore patterns | Datos runtime excluidos de version control |
| Knowledge base | DOMAIN_PRIMER.md existe |
| Agents directory | Contenido consistente |

---

## 💵 Escenarios Financieros

Cada hotel recibe proyecciones personalizadas basadas en sus datos validados. El ROI se calcula con `pain_ratio` (porcentaje de la pérdida que se recupera al implementar los cambios) y `recovery_factor` (factor de recuperación por escenario):

|| Escenario | Probabilidad | recovery_factor | Base de cálculo |
|-----------|--------------|-----------------|-----------------|
| **Conservador** | 70% | 0.15 | Peor caso plausible (recupera 15% de la pérdida) |
| **Realista** | 20% | 0.20 | Meta esperada (recupera 20% de la pérdida) |
| **Optimista** | 10% | 0.25 | Mejor caso (recupera 25% de la pérdida, puede ser ganancia neta) |

**Fórmula**: `projected_gain = monthly_loss_cop × pain_ratio × recovery_factor`
**ROI**: `roi = (projected_gain × 6) / (precio_mensual × 6)` — cap en 5.0X

**Motor Financiero Verificable**: Cada COP tiene origen trazable (ADR regional, occupancy validada), peso proporcional, etiqueta honesta (VERIFIED/ESTIMATED) y base verificable (comisión OTA). El escenario optimista con valor negativo se presenta como "ganancia neta".

---

## 🎤 Voice Readiness Proxy (v4.28.0)

**Propósito:** Evaluar qué tan preparado está un hotel para que asistentes de voz (Siri, Google Assistant, Alexa) lo mencionen como respuesta directa.

**Enfoque:** PROXY — mide los INPUTS que alimentan los asistentes de voz, NO consulta Siri/Alexa directamente (no existe API para ello).

| Componente | Peso | Qué evalúa |
|------------|------|------------|
| GBP Completeness | 30% | NAP, categorías, horarios, fotos, atributos |
| Schema for Voice | 25% | Hotel/LocalBusiness, FAQ, Speakable markup |
| Featured Snippets | 25% | Optimización para posición cero en Google |
| Factual Coverage | 20% | Datos factuales accesibles (horarios, precios, dirección) |

| Nivel | Rango | Significado |
|-------|-------|-------------|
| Critical | 0-25 | Sin presencia detectable por asistentes de voz |
| Basic | 26-50 | Presencia mínima, datos parciales |
| Good | 51-75 | Optimización sólida, capturable por voz |
| Excellent | 76-100 | Presencia completa y consistente para voz |

**Restricciones (por diseño):**
- NO consulta APIs de Siri, Alexa, Google Assistant directamente
- NO simula queries de voz con TTS/STT
- Voice Readiness es sub-score de AEO, no un 5to pilar independiente

---

## ⚠️ Troubleshooting

| Problema | Solución |
|----------|----------|
| Fallo Gate de Coherencia | Verifica que los datos tengan confianza suficiente (≥0.8) y no haya conflictos entre fuentes. |
| No LLM API key configured | Ejecuta `python main.py setup` para configurar de forma segura. |

---

## ✅ Calidad Garantizada

- **2,224 tests** de regresión pasando al 100% (suite completa)
- **TDD Gate**: Todo cambio comienza con un test que falla
- **Pre-commit hooks**: Validaciones automáticas en cada commit (version-sync, secrets, residual files)
- **Suite de regresión**: Amaziliahotel + Hotel Vísperas como casos de referencia
- **Coherence Score ≥ 0.8**: Validación cruzada documentos ↔ assets
- **9 Publication Gates** (6 blocking + 3 advisory): hard_contradictions, evidence_coverage, financial_validity, coherence, critical_recall, ethics *(blocking)* + content_quality, asset_confidence, proposal_asset_alignment *(advisory/warning)*
- **183 tests postprocessors + commercial_documents + delivery**: 0 regresiones post-intervención Amazilia Hotel

---

**IA HOTELES AGENT © 2026**  
*Diagnosticando la invisibilidad digital hotelera y recuperando reservas que hoy van a OTAs.*

---

## Testing

**2,224+ test functions** across unit, integration and E2E suites | **30/30 financial_engine tests** | **183 postprocessors + commercial + delivery tests** | **4 tests test_proposal_generator_dict (hotfix validation)** | **Motor Financiero Verificable con recovery_factor y pain_ratio**
