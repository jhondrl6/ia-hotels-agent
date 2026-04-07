# FASE-A: Canonical Metrics + Provider Registry + Permission Modes

**ID**: FASE-A
**Objetivo**: Implementar 3 patrones arquitectonicos de Goose en iah-cli: canonical_metrics.py (normalizacion de nombres entre fuentes), provider_registry.py (registro centralizado de proveedores), y permission_modes (control granular de aprobacion)
**Dependencias**: FASE-B completada (review response scraper integrado)
**Duración estimada**: 2-3 horas
**Skill**: `phased_project_executor` v2.1.0

---

## Contexto

El sistema iah-cli tiene 3 debilidades estructurales que agregan friccion al desarrollo y al runtime:

1. **Nombres dispersos entre fuentes**: GA4 dice `organic_traffic`, SerpAPI dice `organicClicks`, Places API dice `search_direct_views`. Cada modulo hace su propio mapeo ad-hoc. Cuando una API cambia un nombre, tocas 3-4 archivos.

2. **Config de proveedores dispersa**: Endpoints y auth estan en `.env`, `config/settings.yaml`, y hardcodeado en cada client. No hay un solo archivo donde ver TODOS los proveedores de un vistazo.

3. **Sin control granular de costo/API**: El sistema ejecuta todo y hace fallback si falla. No hay modo para pedir confirmacion antes de llamadas costosas.

Estos 3 problemas se resuelven con patrones de Goose (block/goose): canonical models, provider catalog, y goose modes. No se copia codigo de Goose -- se adaptan los patrones a Python y al dominio hotelero.

### Estado de Fases Anteriores

| Fase | Descripcion | Estado |
|------|------------|--------|
| FASE-A | Scraping de Review Response Rate + Pipeline Integration | ✅ Completada |
| FASE-B | Documentos Comerciales (Diagnostico + Propuesta con datos reales de reviews) | ✅ Completada |

### Base Tecnica Disponible

**Modulos existentes que necesitan refactor**:

1. `modules/analytics/google_analytics_client.py` — Campo `organic_total`, `organic_new`
2. `modules/analytics/profound_client.py` — Campo `organic_clicks`
3. `modules/scrapers/google_places_client.py` — Campo `search_direct_views`, `search_views`
4. `config/settings.yaml` — Config general de proveedores
5. `main.py` — Entry point, donde vive el routing de comandos
6. `modules/orchestration_v4/` — Flujo v4complete que coordina todo

**Archivos de referencia**:
- `data_models/canonical_assessment.py` — Ya existe el concepto de "canonical" para assessments
- `data_models/aeo_kpis.py` — Modelo de KPIs con campos de metricas
- `agent_harness/types.py` — Tipos compartidos del agent harness

**Tests base**: ~1800 tests pasando. Validacion: `python scripts/run_all_validations.py --quick`

---

## Tareas

### Tarea 1: Canonical Metrics

**Objetivo**: Crear `modules/utils/canonical_metrics.py` que defina un diccionario maestro de mapeo entre nombres de metricas de fuentes externas y nombres canonicos internos.

**Archivos nuevos**:
- `modules/utils/canonical_metrics.py`
- `tests/utils/test_canonical_metrics.py`

**Contenido del modulo**:

```python
"""
Canonical Metrics — Normalizacion de nombres de metricas entre fuentes externas.

Patron inspirado en Goose (canonical models para LLM providers).
Cada fuente de datos usa su propio vocabulario. Este modulo mapea
todos los nombres a un vocabulario unico interno.
"""

from typing import Dict, Optional
from dataclasses import dataclass, field


@dataclass
class CanonicalMetric:
    """Definicion de una metrica canonica y sus aliases."""
    canonical_name: str       # nombre interno unico
    description: str          # que mide esta metrica
    unit: str                 # unidad (clicks, score, rate, cop, etc.)
    aliases: Dict[str, str] = field(default_factory=dict)  # {fuente: nombre_en_fuente}


# Registro central de metricas canonicas
CANONICAL_METRICS: Dict[str, CanonicalMetric] = {
    "organic_traffic": CanonicalMetric(
        canonical_name="organic_traffic",
        description="Visitas organicas desde motores de busqueda",
        unit="clicks",
        aliases={
            "ga4": "organic_total",
            "ga4_new": "organic_new",
            "profound": "organic_clicks",
            "serpapi": "organicClicks",
            "semrush": "Organic Traffic",
        }
    ),
    "geo_score": CanonicalMetric(
        canonical_name="geo_score",
        description="Completitud del perfil de Google Business",
        unit="score_0_100",
        aliases={
            "places_api": "geo_score",
            "gbp_auditor": "geo_score",
        }
    ),
    "review_rating": CanonicalMetric(
        canonical_name="review_rating",
        description="Calificacion promedio en Google Maps",
        unit="rating_1_5",
        aliases={
            "places_api": "rating",
            "gbp_auditor": "rating",
            "serpapi": "rating",
        }
    ),
    "review_count": CanonicalMetric(
        canonical_name="review_count",
        description="Numero total de reviews en Google Maps",
        unit="count",
        aliases={
            "places_api": "user_rating_count",
            "gbp_auditor": "reviews",
            "serpapi": "reviewsCount",
        }
    ),
    "photo_count": CanonicalMetric(
        canonical_name="photo_count",
        description="Numero de fotos en el perfil GBP",
        unit="count",
        aliases={
            "places_api": "photo_count",
            "gbp_auditor": "photos",
        }
    ),
    "adr": CanonicalMetric(
        canonical_name="adr",
        description="Average Daily Rate (tarifa promedio diaria)",
        unit="cop",
        aliases={
            "manual": "adr",
            "pms": "ADR",
            "benchmark": "adr_avg",
        }
    ),
    "occupancy_rate": CanonicalMetric(
        canonical_name="occupancy_rate",
        description="Tasa de ocupacion del hotel",
        unit="percentage",
        aliases={
            "manual": "occupancy_rate",
            "pms": "occupancy",
        }
    ),
}


def resolve_metric(source: str, source_name: str) -> Optional[str]:
    """
    Resuelve un nombre de metrica de una fuente externa a su nombre canonico.

    Args:
        source: identificador de la fuente (ga4, serpapi, places_api, etc.)
        source_name: nombre de la metrica en esa fuente

    Returns:
        canonical_name si existe, None si no se encuentra
    """
    for canonical, metric in CANONICAL_METRICS.items():
        if source in metric.aliases and metric.aliases[source] == source_name:
            return canonical
    return None


def get_all_names(canonical_name: str) -> Optional[Dict[str, str]]:
    """Devuelve {fuente: nombre_en_fuente} para una metrica canonica."""
    metric = CANONICAL_METRICS.get(canonical_name)
    return metric.aliases if metric else None


def metric_exists(canonical_name: str) -> bool:
    """Verifica si una metrica canonica existe en el registro."""
    return canonical_name in CANONICAL_METRICS


def list_sources() -> list:
    """Lista todas las fuentes registradas."""
    sources = set()
    for metric in CANONICAL_METRICS.values():
        sources.update(metric.aliases.keys())
    return sorted(sources)
```

**Criterios de aceptacion**:
- [ ] Modulo importa sin errores
- [ ] `resolve_metric("ga4", "organic_total")` retorna `"organic_traffic"`
- [ ] `resolve_metric("profound", "organic_clicks")` retorna `"organic_traffic"`
- [ ] `get_all_names("geo_score")` retorna dict con todas las fuentes
- [ ] `list_sources()` retorna lista con al menos: ga4, places_api, gbp_auditor, serpapi, profound, semrush
- [ ] Tests pasan 100%

---

### Tarea 2: Provider Registry

**Objetivo**: Crear `config/provider_registry.yaml` (datos) y `modules/utils/provider_registry.py` (logica) que centralice toda la configuracion de proveedores de datos/LLM.

**Archivos nuevos**:
- `config/provider_registry.yaml`
- `modules/utils/provider_registry.py`
- `tests/utils/test_provider_registry.py`

**Contenido del YAML** (`config/provider_registry.yaml`):

```yaml
# Provider Registry — Configuracion centralizada de todas las fuentes de datos
# Patron inspirado en Goose (provider catalog / provider_metadata.json)
# Un solo lugar donde agregar/quitar/ver proveedores.

providers:
  # === ANALYTICS ===
  ga4:
    type: analytics
    description: Google Analytics 4 - Trafico organico y comportamiento
    auth_type: service_account
    credentials_file: config/google-analytics-key.json
    env_vars:
      - GA4_PROPERTY_ID
    enabled: true
    cost_per_call: 0.00  # service account, gratis
    retry_count: 3
    timeout_seconds: 30

  profound:
    type: analytics
    description: Profound - Search visibility y keyword tracking
    auth_type: api_key
    env_vars:
      - PROFOUND_API_KEY
    enabled: false  # requiere key del usuario
    cost_per_call: 0.01  # estimado
    retry_count: 2
    timeout_seconds: 15

  semrush:
    type: analytics
    description: Semrush - Analisis SEO competitivo
    auth_type: api_key
    env_vars:
      - SEMRUSH_API_KEY
    enabled: false  # requiere key del usuario
    cost_per_call: 0.01  # estimado
    retry_count: 2
    timeout_seconds: 15

  # === SEARCH / PLACES ===
  places_api:
    type: search
    description: Google Places API (New) - Datos de perfil GBP
    auth_type: api_key
    env_vars:
      - GOOGLE_API_KEY
    enabled: true
    cost_per_call: 0.008  # $0.005-0.010 por request
    retry_count: 3
    timeout_seconds: 10

  serpapi:
    type: search
    description: SerpAPI - Busqueda en Google Maps alternativo
    auth_type: api_key
    env_vars:
      - SERPAPI_API_KEY
    enabled: false  # 250 searches/mes (free tier)
    cost_per_call: 0.01
    retry_count: 2
    timeout_seconds: 15

  # === PERFORMANCE ===
  pagespeed:
    type: performance
    description: Google PageSpeed Insights
    auth_type: api_key
    env_vars:
      - GOOGLE_API_KEY
    enabled: true
    cost_per_call: 0.00  # gratis dentro de quota
    retry_count: 2
    timeout_seconds: 30

  rich_results:
    type: performance
    description: Google Rich Results Test
    auth_type: none
    env_vars: []
    enabled: true
    cost_per_call: 0.00
    retry_count: 2
    timeout_seconds: 15

  # === LLM (para diagnostico/propuesta/assets) ===
  openrouter:
    type: llm
    description: OpenRouter - Gateway multi-modelo
    endpoint: https://openrouter.ai/api/v1
    auth_type: api_key
    env_vars:
      - OPENROUTER_API_KEY
    default_model: qwen/qwen3.6-plus:free
    enabled: true
    cost_per_call: variable
    retry_count: 2
    timeout_seconds: 120
```

**Contenido del modulo** (`modules/utils/provider_registry.py`):

```python
"""
Provider Registry — Registro centralizado de proveedores de datos y LLM.

Patron inspirado en Goose (provider catalog). Un solo archivo YAML
donde se configuran TODOS los proveedores: endpoint, auth, costo, retry.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

import yaml


@dataclass
class ProviderConfig:
    id: str
    type: str
    description: str
    auth_type: str
    env_vars: List[str] = field(default_factory=list)
    endpoint: Optional[str] = None
    enabled: bool = True
    cost_per_call: float = 0.0
    retry_count: int = 2
    timeout_seconds: int = 15
    credentials_file: Optional[str] = None
    default_model: Optional[str] = None


class ProviderRegistry:
    _instance = None
    _providers: Dict[str, ProviderConfig] = {}
    _loaded: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load(self, config_path: Optional[str] = None) -> None:
        if self._loaded:
            return
        if config_path is None:
            project_root = Path(__file__).resolve().parent.parent.parent
            config_path = str(project_root / "config" / "provider_registry.yaml")
        with open(config_path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f)
        for pid, pdata in raw.get("providers", {}).items():
            self._providers[pid] = ProviderConfig(
                id=pid,
                type=pdata.get("type", "unknown"),
                description=pdata.get("description", ""),
                auth_type=pdata.get("auth_type", "none"),
                env_vars=pdata.get("env_vars", []),
                endpoint=pdata.get("endpoint"),
                enabled=pdata.get("enabled", True),
                cost_per_call=pdata.get("cost_per_call", 0.0),
                retry_count=pdata.get("retry_count", 2),
                timeout_seconds=pdata.get("timeout_seconds", 15),
                credentials_file=pdata.get("credentials_file"),
                default_model=pdata.get("default_model"),
            )
        self._loaded = True

    def get(self, provider_id: str) -> Optional[ProviderConfig]:
        return self._providers.get(provider_id)

    def list_by_type(self, type_: str) -> List[ProviderConfig]:
        return [p for p in self._providers.values() if p.type == type_]

    def list_enabled(self) -> List[ProviderConfig]:
        return [p for p in self._providers.values() if p.enabled]

    def is_configured(self, provider_id: str) -> bool:
        """Verifica si un proveedor tiene sus credenciales disponibles."""
        p = self._providers.get(provider_id)
        if not p or not p.enabled:
            return False
        if p.auth_type == "none":
            return True
        if p.credentials_file:
            return os.path.exists(p.credentials_file)
        for env_var in p.env_vars:
            if not os.environ.get(env_var):
                return False
        return True

    def estimated_cost_per_run(self) -> float:
        """Costo estimado por corrida v4complete (solo enabled + configurado)."""
        total = 0.0
        for p in self._providers.values():
            if p.enabled and self.is_configured(p.id) and p.cost_per_call:
                total += p.cost_per_call
        return total
```

**Criterios de aceptacion**:
- [ ] YAML parsea sin errores
- [ ] `ProviderRegistry().get("ga4")` retorna ProviderConfig correcto
- [ ] `list_by_type("analytics")` retorna ga4, profound, semrush
- [ ] `is_configured("ga4")` retorna True si el archivo de credentials existe
- [ ] `estimated_cost_per_run()` retorna numero > 0 con providers activos
- [ ] Tests pasan 100%

---

### Tarea 3: Permission Modes

**Objetivo**: Agregar modo de permiso `--mode` al CLI que controle granularidad de aprobacion de tool calls, inspirado en GooseMode de Goose.

**Archivos modificados**:
- `main.py` — Agregar argumento `--mode` con parsing
- `modules/orchestration_v4/orchestrator.py` (o donde viva el flujo principal) — Respetar modo

**Archivos nuevos**:
- `modules/utils/permission_mode.py`
- `tests/utils/test_permission_mode.py`

**Contenido del modulo** (`modules/utils/permission_mode.py`):

```python
"""
Permission Mode — Control granular de aprobacion de operaciones con costo.

Patron inspirado en Goose (GooseMode: auto, approve, smart_approve, chat).
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional


class PermissionMode(str, Enum):
    AUTO = "auto"              # Ejecutar todo sin preguntar
    SMART_APPROVE = "smart_approve"  # Preguntar solo si costo > umbral
    APPROVE = "approve"        # Preguntar antes de cada operacion externa
    CHAT = "chat"              # Solo diagnostico, sin llamadas externas


DEFAULT_MODE = PermissionMode.AUTO
COST_THRESHOLD = 0.05  # USD — arriba de este valor, preguntar en smart_approve


@dataclass
class OperationPermission:
    name: str
    estimated_cost: float
    is_external: bool  # llamada a API externa


def check_permission(
    op: OperationPermission,
    mode: PermissionMode = DEFAULT_MODE,
    on_ask: Optional[callable] = None,
) -> bool:
    """
    Decide si una operacion debe ejecutarse segun el modo de permiso.

    Args:
        op: la operacion a evaluar
        mode: el modo activo
        on_ask: callback para pedir confirmacion (recibe nombre y costo, retorna bool)

    Returns:
        True si se debe ejecutar, False si se debe saltar
    """
    if mode == PermissionMode.AUTO:
        return True
    if mode == PermissionMode.CHAT:
        return False  # sin llamadas externas
    if mode == PermissionMode.APPROVE:
        if op.is_external and on_ask:
            return on_ask(op.name, op.estimated_cost)
        return True  # operaciones internas siempre pasan
    if mode == PermissionMode.SMART_APPROVE:
        if op.is_external and op.estimated_cost > COST_THRESHOLD:
            if on_ask:
                return on_ask(op.name, op.estimated_cost)
            return False  # sin callback, no ejecutar por seguridad
        return True  # bajo umbral o interno = ejecutar
    return True
```

**Integracion en main.py**: Agregar en el argparse:

```python
parser.add_argument(
    "--mode",
    type=str,
    choices=["auto", "smart_approve", "approve", "chat"],
    default="auto",
    help="Modo de permisos: auto (todo), smart_approve (preguntar si caro), "
         "approve (preguntar siempre), chat (sin llamadas externas)"
)
```

**Criterios de aceptacion**:
- [ ] `--mode auto` ejecuta como siempre (comportamiento actual)
- [ ] `--mode chat` no hace ninguna llamada externa a APIs
- [ ] `--mode smart_approve` permite calls < $0.05 sin preguntar
- [ ] `--mode approve` pregunta (o retorna False) para cada call externa
- [ ] Tests: check_permission para los 4 modos con operaciones de distinto costo
- [ ] Tests: 100% pasados

---

## Tests Obligatorios

| Test | Archivo | Criterio de Exito |
|------|---------|-------------------|
| `test_canonical_metrics.py` | `tests/utils/test_canonical_metrics.py` | 8/8 tests, resolve_metric, get_all_names, list_sources |
| `test_provider_registry.py` | `tests/utils/test_provider_registry.py` | 6/6 tests, load, get, list_by_type, is_configured, cost |
| `test_permission_mode.py` | `tests/utils/test_permission_mode.py` | 8/8 tests, 4 modos x 2 escenarios |
| Validacion del proyecto | `scripts/run_all_validations.py --quick` | 4/4 gates pasan |

**Comando de validacion**:
```bash
python -m pytest tests/utils/test_canonical_metrics.py tests/utils/test_provider_registry.py tests/utils/test_permission_mode.py -v
python scripts/run_all_validations.py --quick
```

---

## Conflictos y Riesgos

| Riesgo | Nivel | Mitigacion |
|--------|-------|------------|
| Tests existentes break por import faltante | Bajo | Modulos nuevos, no modifican existentes |
| argparse conflict con otro argumento | Bajo | `--mode` no existe actualmente en main.py |
| YAML de providers sin sintaxis correcta | Bajo | Test de carga del YAML incluido |
| `main.py` modificacion rompe parseo de args | Medio | Test manual con `python main.py --help` |

## Restricciones

- NO modificar ningun modulo de analytics, scrapers, o commercial_documents en esta fase
- Los 3 modulos nuevos son independientes y auto-contenidos
- Backward compatible: si `--mode` no se especifica, comportamiento = `auto` (como hoy)
- NO usar codigo de Goose ni GitNexus — solo patrones arquitectonicos

---

## Post-Ejecucion (OBLIGATORIO)

NO OMITIR. Al finalizar esta fase, ejecutar INMEDIATAMENTE (antes de cerrar la sesion):

1. **`scripts/log_phase_completion.py`**:
```bash
python scripts/log_phase_completion.py \
    --fase FASE-A \
    --desc "Canonical Metrics + Provider Registry + Permission Modes (patrones Goose)" \
    --archivos-nuevos "modules/utils/canonical_metrics.py,modules/utils/provider_registry.py,modules/utils/permission_mode.py,config/provider_registry.yaml,tests/utils/test_canonical_metrics.py,tests/utils/test_provider_registry.py,tests/utils/test_permission_mode.py" \
    --archivos-mod "main.py" \
    --tests "22" \
    --check-manual-docs
```

2. **Actualizar `.opencode/plans/06-checklist-implementacion.md`**: Marcar FASE-A como completada
3. **Verificar dependencias-fases.md**: Actualizar estado

---

## Criterios de Completitud (CHECKLIST)

Verificar ANTES de marcar como COMPLETADA:

- [ ] `test_canonical_metrics.py`: 8/8 tests passing
- [ ] `test_provider_registry.py`: 6/6 tests passing
- [ ] `test_permission_mode.py`: 8/8 tests passing
- [ ] `python scripts/run_all_validations.py --quick` pasa 4/4
- [ ] `python main.py --help` muestra `--mode` sin errores
- [ ] `modules/utils/canonical_metrics.py` importa sin errores desde cualquier contexto
- [ ] `config/provider_registry.yaml` parsea correctamente
- [ ] `log_phase_completion.py` ejecutado con exito
- [ ] Checklist maestro actualizado

NO marcar la fase como completada si algun criterio falla.
