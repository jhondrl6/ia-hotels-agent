# Contexto: Módulo Hook PDF Generator para iah-cli

**Archivo:** `/.opencode/context/Historico/MODULO-HOOK-PDF.md`
**Fecha:** 2026-07-09
**Propósito:** Insumo completo para planificar la implementación del módulo `hook_pdf_generator` como parte de `modules/commercial_documents/`, resolviendo el gap #2 "Empaquetado no técnico" del plan de negocio.
**Origen:** Conversación analítica entre el usuario y Hermes Agent sobre coherencia arquitectónica del diseño actual en `PROPUESTA_EMPAQUETADO_NO_TECNICO.md`.

---

## 1. Archivos fuente (output/Recomendaciones/)

Cuatro archivos forman el dossier completo de monetización. Todos residen en `output/Recomendaciones/` y constituyen la justificación de negocio para este módulo:

| Archivo | Rol en esta decisión |
|---------|---------------------|
| `Resultados.ini` | Plan de negocio maestro. Define los 5 gaps, el modelo escalera (Express→Impl→Retainer), el roadmap F1-F5, y el pricing. El gap #2 "Empaquetado no técnico" (línea 8-11) es el que este módulo resuelve. |
| `PROPUESTA_EMPAQUETADO_NO_TECNICO.md` | Especificación funcional completa del PDF gancho: catálogo de datos (3 fuentes), estructura 2 páginas, placeholders, validaciones, pipeline pre-Express/Post-Express, y diseño de script `generate_hook_pdf.py`. |
| `PROMPT_INGRESOS.md` | Prompt que generó el Resultados.ini. Contiene el contexto de negocio calibrado con datos reales del piloto Luxorhotel. Sirve para entender el "por qué" de cada decisión en el plan. |
| `PROMPT_INGRESOS_README.md` | Guía de uso del prompt. Meta-documento sobre la estrategia de cacheo y costos. |

### Lo que Resultados.ini exige (extraído literal)

**Gap #2** (línea 8-11):
```
Gap: Empaquetado no técnico
Estado hoy: Output .md técnico; hotelero no lee JSON-LD
Yo solo puedo: Sí: 1 PDF de 2 páginas "Cuánto pierde su hotel" con datos del propio hotel
               (generado por v4_complete). Plantilla única reutilizable, datos dinámicos por cliente
```

**F2 — Roadmap** (línea 60):
```
F2 | Validar willingness-to-pay | Vender 3-5 Express ($120K) con PDF de 2 páginas | 3 pagos recibidos
```

**Acción 2 — Top 3 esta semana** (línea 81-84):
```
PDF gancho de 2 páginas: datos del propio prospecto (v4_complete + generate_hook_pdf).
Requiere correr v4_complete por cada prospecto (~5 min c/u).
20 prospectos = ~100 min de procesamiento antes de enviar el primer WhatsApp.
```

**P3 — Pricing** (línea 97):
```
Express | $120K único | Diagnóstico v4complete resumido: fuga en COP, 3 escenarios,
top 5 acciones, PDF 5 pág (distinto del PDF gancho de 2 pág pre-venta). Entrega 72h
```

### Distinción crítica: PDF gancho (2 pág) ≠ Diagnóstico Express (5 pág)

| Artefacto | Páginas | Momento en ciclo de venta | Tier | Datos |
|-----------|---------|--------------------------|------|-------|
| **PDF gancho** | 2 | Pre-venta (segundo contacto) | B/C (estimados) | v4_complete con datos públicos |
| **Diagnóstico Express** | 5 | Post-pago $120K | A (exactos) | v4_complete con datos reales del hotel |

El módulo `hook_pdf_generator` implementa el **PDF gancho de 2 páginas**. El Diagnóstico Express de 5 páginas es un deliverable futuro (post-pago) que podría reutilizar el mismo módulo con otro template, pero NO es el alcance de esta implementación.

---

## 2. Análisis de ubicación en la arquitectura del repositorio

### 2.1 Ubicación actual (diseño de la propuesta) — RECHAZADA

```
output/v4_complete/
├── scripts/generate_hook_pdf.py    ← CÓDIGO FUENTE dentro de directorio de output
├── templates/hook_template.md      ← CÓDIGO FUENTE dentro de directorio de output
└── templates/hook_styles.css       ← CÓDIGO FUENTE dentro de directorio de output
```

**Problemas:**
1. `output/` es efímero por definición — se regenera, se limpia, no se versiona igual que `src/`
2. Un `rm -rf output/` o una limpieza de outputs viejos borraría el código fuente
3. Sin cobertura de tests (el suite de 2743 tests no escanea `output/`)
4. Sin integración con el CLI (`python main.py v4complete` pero no `python main.py hook-pdf`)
5. Rompe el principio de separación código/datos del proyecto

### 2.2 Ubicación propuesta — MÓDULO en commercial_documents

```
iah-cli/
├── modules/commercial_documents/
│   ├── __init__.py                    (MODIFICAR — exportar HookPDFGenerator)
│   ├── coherence_validator.py         (existe — referencia de patrón)
│   ├── coherence_config.py            (existe — NO relevante para hook PDF)
│   ├── v4_diagnostic_generator.py     (existe — referencia de patrón, fuente de datos)
│   ├── v4_proposal_generator.py       (existe — referencia de patrón, fuente de datos)
│   ├── pain_solution_mapper.py        (existe — verificar si hook_pdf necesita mapear pain_ids a texto humano para brechas)
│   ├── service_catalog.py             (existe — verificar si hook_pdf necesita resolver nombres de servicio)
│   ├── data_structures.py             (MODIFICAR — agregar dataclass HookPDFData: ver §5 tarea #7)
│   └── hook_pdf_generator.py          (NUEVO — ~200 líneas)
├── templates/
│   ├── hook_template.md               (NUEVO — ~100 líneas, placeholders, en raíz templates/ junto a delivery_readme_template.md)
│   └── hook_styles.css                (NUEVO — ~50 líneas, diseño 2 pág, en raíz templates/)
├── tests/commercial_documents/
│   └── test_hook_pdf_generator.py     (NUEVO — 8+ tests unitarios)
└── main.py                            (MODIFICAR — agregar comando 'hook-pdf')
```

**Nota sobre archivos existentes no mencionados:** El módulo `commercial_documents/` contiene 8 archivos `.py`. Además de los 4 citados como referencia de patrón (`v4_diagnostic_generator`, `v4_proposal_generator`, `coherence_validator`, `data_structures`), existen `service_catalog.py`, `pain_solution_mapper.py`, y `coherence_config.py`. Aunque no son fuentes de datos del PDF, el plan debe verificar si `hook_pdf_generator` necesita importar `PainSolutionMapper` para resolver nombres de brechas (pain_ids → texto humano legible para el PDF) o `ServiceCatalog` para resolver nombres de servicios. Si la extracción de brechas desde `opportunity_scores` del JSON ya trae el nombre legible, estas importaciones no son necesarias.

### 2.3 Justificación: por qué commercial_documents/

`modules/commercial_documents/` ya contiene los generadores de los documentos que alimentan el PDF:

| Archivo existente | Función | Relación con hook_pdf |
|-------------------|---------|----------------------|
| `v4_diagnostic_generator.py` | Genera `01_DIAGNOSTICO_Y_OPORTUNIDAD_{ts}.md` | Fuente primaria de datos para el PDF |
| `v4_proposal_generator.py` | Genera `02_PROPUESTA_COMERCIAL_{ts}.md` | Fuente primaria de datos para el PDF |
| `coherence_validator.py` | Valida coherencia entre diagnóstico y propuesta | Mismo patrón: validar → generar → entregar |
| `data_structures.py` | Define `DiagnosticDocument`, `ProposalDocument`, `Scenario` | El hook PDF reutiliza/lee estas estructuras |

El hook PDF es literalmente un "documento comercial" — un PDF derivado de los mismos datos que alimentan el diagnóstico y la propuesta. Su lugar natural es este módulo, no un directorio de output.

### 2.4 Relación con agent_harness/

`agent_harness/` es el orquestador de tareas, NO el lugar para lógica de negocio:

| Componente | Rol | NO debe contener |
|------------|-----|-----------------|
| `agent_harness/core.py` | `AgentHarness.run_task()` — ejecuta handlers registrados | Lógica de generación de PDFs |
| `agent_harness/memory.py` | `MemoryManager` — persistencia de estado | Templates o placeholders |
| `agent_harness/skill_router.py` | Ruteo semántico de Meta-Skills | Datos de hotel o parseo de frontmatter |

El hook PDF **no es un skill ni un handler del harness**. Es un módulo de negocio que:
1. Lee output de v4_complete (3 archivos: 2 .md + 1 JSON)
2. Extrae datos con placeholders
3. Genera PDF vía weasyprint

El harness simplemente lo invoca como cualquier otro módulo cuando se registra el comando `hook-pdf`.

### 2.5 Relación con AGENTS.md

AGENTS.md (línea 196) ya lista `modules/commercial_documents/` como módulo activo:

```
| modules/commercial_documents/ | Diagnóstico, propuesta, coherencia | v4complete |
```

El hook PDF extiende esta fila:

```
| modules/commercial_documents/ | Diagnóstico, propuesta, coherencia, PDF gancho | v4complete, hook-pdf |
```

**Workflows table** (línea 42-59): El workflow `v4_complete.md` (trigger: "diagnostico", "analiza este hotel") es el que genera los datos que el hook PDF consume. No se necesita un nuevo workflow — el hook PDF es post-procesamiento del output de `v4complete`.

**Comandos CLI table** (línea 131-145): Se agregaría una fila:

```
| hook-pdf | ✅ Nuevo | Genera PDF gancho de 2 páginas desde output de v4complete |
```

### 2.6 Relación con DOMAIN_PRIMER.md

DOMAIN_PRIMER.md es auto-generado por `scripts/doctor.py --regenerate-domain-primer`. NO se edita manualmente. Una vez implementado el módulo:

1. El script `doctor.py` detectará automáticamente `hook_pdf_generator.py` en `modules/commercial_documents/`
2. Lo agregará a la tabla "GENERACION DE CONTENIDO Y ASSETS" (línea 38)
3. El `__init__.py` actualizado exportará `HookPDFGenerator`

No se requiere acción manual sobre DOMAIN_PRIMER.md.

---

## 3. Especificación técnica (extraída de PROPUESTA_EMPAQUETADO_NO_TECNICO.md)

> **⚠ FUENTE DE AUTORIDAD VISUAL:** `output/Recomendaciones/PROPUESTA_EMPAQUETADO_NO_TECNICO.md` (31KB, modificado 2026-07-09) es la fuente de autoridad para la especificación visual del PDF: catálogo de datos, estructura de 2 páginas, placeholders, validaciones, y diseño del script. Los §3.1-3.7 de este contexto son un extracto verificado al momento de esta auditoría (2026-07-09). **La sesión de planificación DEBE re-leer PROPUESTA_EMPAQUETADO_NO_TECNICO.md antes de implementar** para confirmar que los placeholders, la estructura visual, y las validaciones no hayan cambiado. Si hay divergencia entre este contexto y la propuesta, la propuesta gana para todo lo visual/estructural; este contexto gana para todo lo arquitectónico (ubicación de código, patrón CLI, integración con modules/).

### 3.1 Fuentes de datos (3 archivos por hotel)

```
output/v4_complete/
├── 01_DIAGNOSTICO_Y_OPORTUNIDAD_{timestamp}.md   ← frontmatter YAML + scores + brechas + GBP
├── 02_PROPUESTA_COMERCIAL_{timestamp}.md         ← frontmatter YAML + fuga + proyección + ROI + pricing
└── v4_complete_report.json                       ← opportunity_scores, gates, pricing
```

**Precedencia:** .md > .json para datos de presentación. JSON para datos estructurados (opportunity_scores ordenados por rank).

### 3.2 Placeholders del template (catálogo completo)

#### Datos del hotel
| Placeholder | Fuente | Obligatorio |
|-------------|--------|-------------|
| `{{HOTEL_NOMBRE}}` | JSON `hotel_name` | SÍ |
| `{{HOTEL_URL}}` | JSON `url` | SÍ |
| `{{HOTEL_REGION}}` | JSON `region` | SÍ |
| `{{HOTEL_DIRECCION}}` | 01_DIAGNOSTICO § título H2 | SÍ |
| `{{GBP_RESENAS}}` | 01_DIAGNOSTICO § GBP status | SÍ |
| `{{GBP_RATING}}` | 01_DIAGNOSTICO § GBP status | SÍ |

#### Datos financieros
| Placeholder | Fuente | Notas |
|-------------|--------|-------|
| `{{FUGA_MENSUAL}}` | JSON `expected_monthly` + 02_PROPUESTA | **Cifra gancho principal** |
| `{{FUGA_MINIMA}}` | 01_DIAGNOSTICO § escenarios | Rango inferior (70%) |
| `{{FUGA_MAXIMA}}` | 01_DIAGNOSTICO § escenarios | Rango superior (10%) |
| `{{COMISION_OTA_REAL}}` | 01_DIAGNOSTICO | Lo que paga al año en comisiones |
| `{{RECUPERACION_6M}}` | 02_PROPUESTA | Curva de maduración × 35% |
| `{{ROI}}` | 02_PROPUESTA | Calculado sobre OPEX |
| `{{FUGA_6M}}` | 02_PROPUESTA | Fuga bruta acumulada |

#### Scores de visibilidad (4 pilares)
| Placeholder | Fuente |
|-------------|--------|
| `{{SEO_SCORE}}` / `{{SEO_REGIONAL}}` | 01_DIAGNOSTICO § tabla de scores |
| `{{GEO_SCORE}}` / `{{GEO_REGIONAL}}` | 01_DIAGNOSTICO § tabla de scores |
| `{{AEO_SCORE}}` / `{{AEO_REGIONAL}}` | 01_DIAGNOSTICO § tabla de scores |
| `{{IAO_SCORE}}` / `{{IAO_REGIONAL}}` | 01_DIAGNOSTICO § tabla de scores |

#### Brechas (top 3)
| Placeholder | Fuente |
|-------------|--------|
| `{{BRECHA_1_NOMBRE}}`, `{{BRECHA_1_COP}}`, `{{BRECHA_1_JUSTIFICACION}}` | JSON `opportunity_scores[0]` |
| `{{BRECHA_2_NOMBRE}}`, `{{BRECHA_2_COP}}`, `{{BRECHA_2_JUSTIFICACION}}` | JSON `opportunity_scores[1]` |
| `{{BRECHA_3_NOMBRE}}`, `{{BRECHA_3_COP}}`, `{{BRECHA_3_JUSTIFICACION}}` | JSON `opportunity_scores[2]` |

#### Pricing (constantes del plan de negocio)
| Placeholder | Valor | Fuente |
|-------------|-------|--------|
| `{{PRECIO_EXPRESS}}` | $120.000 COP | Resultados.ini § P3 (NO viene de v4_complete) |
| `{{PRECIO_MENSUAL}}` | $400.000 COP/mes | 02_PROPUESTA línea 46 |
| `{{SETUP_FEE}}` | $2.500.000 COP | 02_PROPUESTA línea 164 |

### 3.3 Estructura del PDF (2 páginas)

**Página 1 — "¿Cuánto pierde su hotel?"**
1. Header: nombre, dirección, reseñas GBP, rating
2. Cifra gancho: FUGA_MENSUAL en COP, tamaño ≥24pt
3. Disclaimer: "(Estimación basada en datos de la región y perfil de su hotel.)"
4. Top 3 brechas con COP estimado cada una
5. Tabla 4 pilares: "Su hotel vs. promedio regional"

**Página 2 — "Cómo se resuelve"**
1. Explicación en español llano (sin jerga técnica)
2. Proyección: recuperación 6M, ROI, fuga acumulada
3. CTA: Diagnóstico Express con precio, garantía, y contacto

### 3.4 Validaciones obligatorias (8 checks)

1. **Placeholders sin llenar:** verificar que el HTML final no contiene `{{...}}`
2. **Campos obligatorios:** abortar si falta `hotel_name`, `FUGA_MENSUAL`, `BRECHA_1..3_NOMBRE`, `SEO_SCORE`, `PRECIO_MENSUAL`
3. **Resolución de timestamps:** glob pattern para `01_DIAGNOSTICO_*.md` y `02_PROPUESTA_*.md`
4. **Formato COP:** separador de miles (.) sin decimales: `3.741.696`
5. **Slug del hotel:** desde `hotel_name` → minúsculas, sin acentos, sin especiales
6. **No-sobrescritura:** si el PDF existe, preguntar o usar `--force`
7. **Dry-run:** `--dry-run` muestra datos sin generar archivo
8. **Detección de Tier:** leer `financial_evidence_tier` del frontmatter YAML; si B/C → incluir disclaimer de estimación

### 3.5 Pipeline de dos pasadas (pre-Express / post-Express)

```
PASADA 1 (pre-venta, SIN datos del hotel):
  v4_complete con datos públicos → Tier B o C → fuga ESTIMADA
  → hook_pdf_generator → PDF gancho 2 pág con disclaimer

PASADA 2 (post-Express, CON datos reales):
  Hotel paga $120K → entrega datos reales → v4_complete → Tier A
  → cifra EXACTA → Diagnóstico Express PDF 5 pág (otro template, futuro)
```

El `hook_pdf_generator` **siempre opera en PASADA 1** (Tier B/C). Si en el futuro se reutiliza para PASADA 2, el disclaimer se ajusta según `financial_evidence_tier == "A"`.

### 3.6 Firma del script (versión módulo)

```python
# modules/commercial_documents/hook_pdf_generator.py

class HookPDFGenerator:
    def __init__(self, output_dir: Path, template_path: Path = None, style_path: Path = None):
        ...

    def extract_data(self) -> HookPDFData:
        """Parsea frontmatter YAML + JSON, devuelve dataclass con todos los placeholders."""
        ...

    def validate_data(self, data: HookPDFData) -> list[str]:
        """Ejecuta 8 validaciones, devuelve lista de warnings/errores."""
        ...

    def render_html(self, data: HookPDFData) -> str:
        """Reemplaza placeholders en el template, devuelve HTML completo."""
        ...

    def generate(self, force: bool = False, dry_run: bool = False) -> Path:
        """Orquesta extract → validate → render → PDF (weasyprint)."""
        ...
```

### 3.7 Stack técnico decidido

**weasyprint** (50MB + ~100MB dependencias de sistema: libpango, libcairo).
- Ventaja sobre pandoc: 7× más liviano, CSS nativo, Python nativo (sin subproceso)
- El template es HTML+CSS, más fácil de iterar que LaTeX
- Dependencias de sistema en WSL: `sudo apt install libpango-1.0-0 libcairo2 libgdk-pixbuf2.0-0`

---

## 4. Integración con el CLI existente

### 4.1 Patrón de comandos en main.py

El patrón es simple (líneas 17-60 de `main.py`):

```python
# 1. Agregar choice en build_parser()
parser.add_argument("command", ..., choices=[..., "hook-pdf"])

# 2. Agregar dispatch en main()
if args.command == "hook-pdf":
    run_hook_pdf_mode(args)
    sys.exit(0)

# 3. Implementar handler
def run_hook_pdf_mode(args):
    from modules.commercial_documents.hook_pdf_generator import HookPDFGenerator
    ...
```

### 4.2 Argumentos CLI necesarios

```
python main.py hook-pdf --output-dir output/v4_complete/   ← obligatorio
                        --template templates/hook_template.md  ← opcional (default)
                        --style templates/hook_styles.css      ← opcional (default)
                        --dry-run                              ← opcional
                        --force                                ← opcional
                        --verbose                              ← opcional
```

### 4.3 Workflow típico

```bash
# 1. Ejecutar v4_complete sobre el hotel (genera los 3 archivos fuente)
python main.py v4complete --url https://hotel.com

# 2. Generar PDF gancho desde el output
python main.py hook-pdf --output-dir output/v4_complete/

# 3. Entregar
# → output/v4_complete/deliveries/{slug}_gancho.pdf
```

---

## 5. Artefactos a crear (resumen para el plan)

| # | Archivo | Tipo | Líneas estimadas | Dependencia |
|---|---------|------|-----------------|-------------|
| 1 | `modules/commercial_documents/hook_pdf_generator.py` | NUEVO | ~200 | Ninguna (puro stdlib + weasyprint + pyyaml) |
| 2 | `templates/hook_template.md` | NUEVO | ~100 | Ninguna |
| 3 | `templates/hook_styles.css` | NUEVO | ~50 | Ninguna |
| 4 | `tests/commercial_documents/test_hook_pdf_generator.py` | NUEVO | ~150 | pytest |
| 5 | `modules/commercial_documents/__init__.py` | MODIFICAR | +5 líneas | hook_pdf_generator.py |
| 6 | `main.py` | MODIFICAR | +30 líneas | hook_pdf_generator.py |
| 7 | `modules/commercial_documents/data_structures.py` | MODIFICAR | +15 líneas | hook_pdf_generator.py (HookPDFGenerator lo usa como return type de `extract_data()`) |

**Total:** 3 archivos nuevos, 3 modificados, ~550 líneas.

**Tarea #7 — HookPDFData dataclass (explícita):** §3.6 muestra `extract_data() -> HookPDFData` como return type. Este dataclass NO existe aún en `data_structures.py` (verificado: el archivo define `DiagnosticDocument`, `ProposalDocument`, `Scenario`, `V4AuditResult`, etc., pero no `HookPDFData`). El plan debe incluir la creación de `HookPDFData` como un dataclass con campos para todos los placeholders del catálogo §3.2 (datos del hotel, financieros, scores, brechas, pricing), más `evidence_tier: str` para el disclaimer condicional. Sin este dataclass, `extract_data()` no tiene tipo de retorno y `validate_data()` no puede operar tipadamente.

### Instalación previa (WSL)

```bash
# Dependencia de sistema para weasyprint
sudo apt install -y libpango-1.0-0 libcairo2 libgdk-pixbuf2.0-0 libffi-dev

# Dependencia Python (en el venv del proyecto)
uv pip install weasyprint pyyaml
```

---

## 6. Validación de coherencia con AGENTS.md

| Claim en AGENTS.md | Cómo hook-pdf se alinea |
|--------------------|------------------------|
| `v4complete` = flujo canónico de diagnóstico | El hook PDF consume output de v4complete, no lo reemplaza |
| `modules/commercial_documents/` = "Diagnóstico, propuesta, coherencia" | hook PDF extiende a "Diagnóstico, propuesta, coherencia, PDF gancho" |
| Workflow `v4_complete.md` = trigger "diagnostico", "analiza este hotel" | No se necesita nuevo workflow; hook-pdf es post-procesamiento |
| No existe "diagnóstico Express" como comando | El hook-pdf NO inventa un comando `express`; es un generador de PDF pre-venta |
| `financial_evidence_tier` = A/B/C | El hook PDF lo lee del frontmatter YAML y ajusta el disclaimer |
| 11 publication gates (6 blocking + 3 advisory + 2 quality) | El hook PDF no modifica los gates; el output ya pasó por ellos |

---

## 7. Lo que el plan NO debe hacer (anti-patrones detectados)

1. ❌ NO crear `output/v4_complete/scripts/` — código fuente en directorio de output
2. ❌ NO crear `output/v4_complete/templates/` — templates en directorio de output
3. ❌ NO crear un comando `express` — "Express" es un tier de pricing, no un comando
4. ❌ NO hardcodear `$120.000` en el código Python — va en el template como `{{PRECIO_EXPRESS}}` con comentario
5. ❌ NO generar PDF sin v4_complete previo — el script debe abortar si no encuentra los 3 archivos fuente
6. ❌ NO usar datos de un hotel para otro — cada ejecución de hook-pdf lee el output del hotel actual
7. ❌ NO modificar DOMAIN_PRIMER.md manualmente — se regenera con `doctor.py`

---

## 8. Criterios de aceptación (para el DoD del plan)

- [ ] `hook_pdf_generator.py` en `modules/commercial_documents/` con clase `HookPDFGenerator`
- [ ] `HookPDFGenerator` exportado en `modules/commercial_documents/__init__.py`
- [ ] `HookPDFData` dataclass creado en `modules/commercial_documents/data_structures.py` con campos para todos los placeholders §3.2 + `evidence_tier`
- [ ] `HookPDFData` exportado en `modules/commercial_documents/__init__.py`
- [ ] Sesión de planificación re-leyó `PROPUESTA_EMPAQUETADO_NO_TECNICO.md` antes de implementar y confirmó que placeholders/estructura no cambiaron
- [ ] Template `templates/hook_template.md` con todos los placeholders del catálogo (§3.2)
- [ ] Estilos `templates/hook_styles.css` con diseño 2 páginas exactas
- [ ] Comando `hook-pdf` registrado en `main.py` con argumentos: `--output-dir`, `--template`, `--style`, `--dry-run`, `--force`, `--verbose`
- [ ] 8 tests unitarios en `tests/commercial_documents/test_hook_pdf_generator.py`
- [ ] `luxorhotel_gancho.pdf` generado exitosamente desde output real del piloto
- [ ] PDF ocupa exactamente 2 páginas
- [ ] Cero placeholders `{{...}}` sin reemplazar en el PDF final
- [ ] Cifra de fuga ≥24pt en página 1
- [ ] Disclaimer de estimación visible (Tier B/C)
- [ ] Funciona con un segundo hotel de prueba
- [ ] Tiempo de generación <30 segundos por hotel
