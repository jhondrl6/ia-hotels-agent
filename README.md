# IA Hoteles Agent CLI

**Plataforma agéntica de diagnóstico de visibilidad digital hotelera: audita presencia en Google, IAs y búsquedas locales; cuantifica la fuga de reservas directas; y genera assets técnicos (schema, FAQ, llms.txt, geo_playbook) para recuperar ingresos que hoy van a OTAs y competidores.**

**Version:** 4.26.0 | **Última actualización:** 10 Abril 2026

---

## 🧭 Índice de Navegación Rápida

| Si buscas... | Ir a... |
|--------------|---------|
| **Índice Completo de Documentación** | [INDICE_DOCUMENTACION.md](INDICE_DOCUMENTACION.md) |
| **Habilidades del Agente (Meta-Skills)** | `.agents/workflows/` - PhasedProjectExecutor (TDD Gate), AuditGuardian (ejecución paralela), Capability Contracts |
| **Estrategia y Roadmap 2026** | [ROADMAP.md](ROADMAP.md) |
| **Historial de Cambios** | [CHANGELOG.md](CHANGELOG.md) |
| **Guía Técnica (Arquitectura)** | [docs/GUIA_TECNICA.md](docs/GUIA_TECNICA.md) |
| **Dominio Hotelero-Digital** | [.agent/knowledge/DOMAIN_PRIMER.md](.agent/knowledge/DOMAIN_PRIMER.md) (Glosario y taxonomía) |
| **Contexto Global del Agente** | [AGENTS.md](AGENTS.md) (canónico) + [.cursorrules](.cursorrules) (puente) |

---

> **🛡️ AGENT PLATFORM STATUS (v4.24.0 - FASE-D: Google Search Console Integration)**:
> *   **Orthogonal Diagnostic Metrics (v4.22.0)**: Eliminada duplicacion entre "Google Maps (GEO)" y "Activity Score (GBP)". Nuevo sistema de 4 pilares independientes: GEO (completitud), Posicion Competitiva (ranking vs competidores), Web/SEO (credibilidad del sitio), AEO (legibilidad para IAs). Cada score usa datos no solapados.
> *   **AEO Re-Architecture**: Modulo AEO (Auditory Engine Optimization) alineado con voice assistants (Alexa, Siri, Google Assistant). SpeakableSpecification, FAQ TTS-ready (40-60 palabras), voice keywords Eje Cafetero.
> *   **Coherence Validator**: Detección de hard/soft conflicts entre fuentes de datos, score de coherencia ≥ 0.8 requerido.
> *   **Evidence Coverage Tracking**: Cobertura de evidence en documentos (≥ 95% coverage).
> *   **Quality Gates de Pre-publicación**: Gates técnico, comercial, financiero y de coherencia (score ≥ 0.8).
> *   **Estados de Publicación**: READY_FOR_CLIENT, DRAFT_INTERNAL, REQUIRES_REVIEW con validación estricta.
> *   **No Defaults in Money**: Validación financiera que bloquea cálculos con valores por defecto.
> *   **Voice Assistant Integration**: 3 blueprints (Google Assistant, Apple Business Connect, Alexa Skill) en delivery.

> *   **Controles de Coherencia**: Validación automática diagnosis↔propuesta↔assets con score ≥ 0.8.
> *   **Observabilidad y Dashboard**: Métricas de calidad en tiempo real y calibración de umbrales.
> *   **Suite de Regresión Permanente**: Test E2E automatizado con Hotel Vísperas como caso de referencia.
> *   **NEVER_BLOCK Architecture**: El sistema nunca se bloquea, siempre entrega algo con benchmark regional + disclaimers honestos.
> *   **Benchmark Resolver**: Fallback con datos regionales de Pereira/Santa Rosa de Cabal cuando faltan datos reales.
> *   **Autonomous Researcher**: Investiga automáticamente en GBP, Booking, TripAdvisor, Instagram cuando datos son insuficientes.
> *   **Disclaimer Generator**: Genera disclaimers honestos por nivel de confidence (≥0.9: sin disclaimer, <0.5: detallado).
> *   **Taxonomía de Confianza**: VERIFIED (≥0.9) / ESTIMATED (0.5-0.9) / CONFLICT (<0.5).
> *   **V4 Assessment Schema**: Estructura de datos unificada para diagnóstico (reemplaza schema v4.2).
> *   **Mejoras Recientes**: TDD Gate en workflows, ejecución paralela en auditorías

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

Sistema que responde a la pregunta: "¿Por qué este hotel pierde reservas que van a Booking, competidores o ChatGPT?". Audita 4 pilares (GEO, SEO, AEO, posición competitiva), asigna un costo en COP a cada brecha detectada, y genera un paquete de assets técnicos listos para deploy con validación cruzada de coherencia.

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

El sistema opera bajo el **Sistema de Confianza v4.5.x** con validación cruzada de datos y controles de coherencia automáticos entre diagnóstico, propuesta y assets.

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

Cada hotel recibe proyecciones personalizadas basadas en sus datos validados:

| Escenario | Probabilidad | Base de cálculo |
|-----------|--------------|-----------------|
| **Conservador** | 70% | Peor caso plausible |
| **Realista** | 20% | Meta esperada |
| **Optimista** | 10% | Mejor caso |

El valor esperado ponderado determina el ROI proyectado y la propuesta comercial personalizada.

---

## ⚠️ Troubleshooting

| Problema | Solución |
|----------|----------|
| Fallo Gate de Coherencia | Verifica que los datos tengan confianza suficiente (≥0.8) y no haya conflictos entre fuentes. |
| No LLM API key configured | Ejecuta `python main.py setup` para configurar de forma segura. |

---

## ✅ Calidad Garantizada

- **52 tests** de regresión pasando al 100% (suite NEVER_BLOCK)
- **TDD Gate**: Todo cambio comienza con un test que falla
- **Pre-commit hooks**: Validaciones automáticas en cada commit
- **Suite de regresión**: Hotel Vísperas como caso de referencia permanente
- **Coherence Score ≥ 0.8**: Validación cruzada documentos ↔ assets

---

**IA HOTELES AGENT © 2026**  
*Diagnosticando la invisibilidad digital hotelera y recuperando reservas que hoy van a OTAs.*

---

## Testing

**1700+ test functions** across unit, integration and E2E suites | **52/52 regression tests** in NEVER_BLOCK suite
