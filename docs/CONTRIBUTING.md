# Guia de Contribucion - IA Hoteles Agent

> **Version Actual:** v4.19.0 (Agent Ecosystem Integration)
> **Cooldown Score:** 0.84 (>= 0.8) - Publication Ready
> **Ultima fase completada:** (ver REGISTRY.md)
> **PLAN ANALYTICS-E2E-BRIDGE:** 100% COMPLETADO (01, 02, 03, 04)
> **GA4 MULTI-HOTEL:** Property ID por hotel via `--ga4-property-id` (no global)
> **Version del sistema de docs:** v2.4.0 (GA4 Multi-Hotel Architecture)
> **Consular REGISTRY para historial de fases:** docs/contributing/REGISTRY.md

---

## Indice de Secciones

| Seccion | Ubicacion | Contenido |
|---------|-----------|-----------|
| Procedimientos | [procedures.md](contributing/procedures.md) | Reglas de version, skills, modulo, TDD |
| Documentacion | [documentation_rules.md](contributing/documentation_rules.md) | Checklist obligatoria, archivos manuales |
| Validacion | [validation.md](contributing/validation.md) | Pre-commit, regression, troubleshooting |
| Capabilities | [capabilities.md](contributing/capabilities.md) | Capability contracts, matriz de capacidades |
| Registro de Fases | [REGISTRY.md](contributing/REGISTRY.md) | **Auto-generado** - historial de fases completadas |

---

## Flujo de Documentacion Post-Fase

Cuando ejecutes `.agents/workflows/phased_project_executor.md`:

```
FASE completada
    │
    ├── Paso 6: Documentacion Post-Fase
    │   ├── Leer docs/contributing/documentation_rules.md §5
    │   ├── Ejecutar: python scripts/log_phase_completion.py --fase N
    │   │   ├── Registra en REGISTRY.md (auto)
    │   │   └── Muestra POR_HACER para docs manuales
    │   └── Verificar capability contracts (capabilities.md §13)
    │
    └── Validar con:
        python main.py --doctor            # Ecosistema + contexto (NUEVO v4.19.0)
```

### Version Sync Gate (Release Final)

Cuando una fase marca un **release** (nueva version), usar el Version Sync Gate:

```bash
# Al completar fase final de un release
python scripts/log_phase_completion.py --fase FASE-X \
    --desc "Descripcion del release" \
    --archivos-mod "modules/foo.py" \
    --release 4.10.0 \
    --auto-sync

# O en dos pasos:
# Paso 1: Registrar sin gate
python scripts/log_phase_completion.py --fase FASE-X \
    --desc "Descripcion del release" \
    --archivos-mod "modules/foo.py"

# Paso 2: Verificar sincronizacion (BLOCKING si hay gap)
python scripts/log_phase_completion.py --fase FASE-X \
    --release 4.10.0 \
    --check-manual-docs
```

**El gate verifica:**
1. CHANGELOG.md tiene entrada `[X.Y.Z]`
2. CHANGELOG y VERSION.yaml coinciden en X.Y.Z
3. Documentacion manual (GUIA_TECNICA.md) menciona la fase

**Si hay desincronizacion:**
```
FAIL: Version desincronizada entre CHANGELOG y VERSION.yaml
Pasos:
  1. python scripts/version_consistency_checker.py  # Diagnosticar
  2. python scripts/sync_versions.py                # Sincronizar
  3. Reintentar con --release
```

**Consistency checker autonomo:**
```bash
python scripts/version_consistency_checker.py       # Verificar todo
python scripts/version_consistency_checker.py --fix # Auto-reparar si es posible
```

---

## Conexiones Clave

| Archivo | Proposito | Conexion |
|---------|-----------|----------|
| `AGENTS.md` | Contexto global canónico | §7 → CONTRIBUTING, executor |
| `phased_project_executor.md` | Motor de ejecucion por fases | Paso 6 → documentation_rules.md |
| `CONTRIBUTING.md` | Reglas de documentacion | Index → fragmentos + REGISTRY |
| `REGISTRY.md` | Registro auto de fases | Actualizado por log_phase_completion.py |

---

## Scripts de Mantenimiento

| Script | Uso |
|--------|-----|
| `main.py --doctor` | Diagnóstico completo (ecosistema + contexto + versión) |
| `scripts/doctor.py --status` | Regenerar SYSTEM_STATUS.md |
| `log_phase_completion.py` | Registrar fase completada → REGISTRY.md |
| `sync_versions.py` | Sincronizar VERSION.yaml → archivos de contexto |
| `validate_agent_ecosystem.py` | 8 checks automatizados del ecosistema de agentes |
| `validate_context_integrity.py` | Validar referencias cruzadas en AGENTS.md |
| `.agents/workflows/v4_regression_guardian.py --quick` | Validación post-cambios v4 |

**Pre-commit hooks automáticos** (se ejecutan en cada commit):
- `agent-ecosystem` → Ejecuta `doctor.py --agent`
- `version-sync` → Ejecuta `sync_versions.py`

---

## Comandos CLI Activos

| Comando | Descripción |
|---------|-------------|
| `v4complete` | Flujo completo con coherencia ≥0.8 |
| `v4audit` | Auditoría con APIs externas |
| `execute` | Implementa paquete recuperado |
| `deploy` | Despliegue remoto FTP/WP-API |
| `setup` | Configuración interactiva de API keys |
| `onboard` | Captura datos operativos del hotel |
| `--doctor` | Diagnóstico del ecosistema de agentes |
| `spark` | ⚠️ Legacy (usar `v4complete`) |
| `stage` | Ejecuta etapas individuales |

---

## GA4 Analytics Integration: Escenarios y Flujo

### Arquitectura

```
GA4_CREDENTIALS_PATH  → GLOBAL en .env (service account compartido)
GA4_PROPERTY_ID       → POR HOTEL via --ga4-property-id (NO global)
```

El service account (`config@dian-467401.iam.gserviceaccount.com`) es fijo y compartido.
El Property ID varia por cada hotel y se pasa por CLI.

### Los 3 Escenarios

#### Escenario 1: Hotel SIN Google Analytics

```bash
python main.py v4complete --url https://hotel.com --nombre "Hotel X"
```

- No se pasa `--ga4-property-id`
- `GoogleAnalyticsClient(property_id=None)` → `is_available() = False`
- Sistema detecta pains: `no_analytics_configured` + `low_organic_visibility`
- Genera assets: `analytics_setup_guide` (guia paso a paso GA4) + `indirect_traffic_optimization`
- Diagnostico muestra: "No configurado (use --ga4-property-id para conectar)"
- Propuesta incluye argumento de valor: "sin analytics no puede medir"

**Resultado:** El cliente recibe guias para implementar GA4. 100% operativo.

#### Escenario 2: Hotel CON GA4 pero SIN acceso para ti

```bash
python main.py v4complete --url https://hotel.com --nombre "Hotel X"
```

- Igual que Escenario 1: no tienes su Property ID
- Sistema funciona en modo fallback honesto
- Diagnostico dice "no tenemos datos" sin mostrar informacion falsa
- El hotel recibe guias de configuracion

**Resultado:** Sin distorsion. El sistema no inventa metricas.

#### Escenario 3: Hotel CON GA4 y TE DA acceso

**Requisitos previos (una sola vez por hotel):**

1. Pregunta al cliente: "Tiene Google Analytics?"
2. Si si: "Agregue este email como Lector en su GA4:"
   ```
   config@dian-467401.iam.gserviceaccount.com
   ```
3. El cliente va a GA4 > Admin > Acceso a la propiedad > Agregar usuario > pega el email con rol **Lector**
4. El cliente te da su Property ID (lo encuentra en GA4 > Admin > Configuracion de la propiedad > ID de propiedad)
5. Ejecutas:

```bash
python main.py v4complete \
    --url https://hotel.com \
    --nombre "Hotel X" \
    --ga4-property-id 531121699
```

- `GoogleAnalyticsClient(property_id='531121699')` → `is_available() = True`
- Sistema trae metricas reales: sesiones, trafico indirecto, fuentes
- Diagnostico muestra datos reales con "Conectado (Property: 531121699)"
- No se generan pains de analytics faltante
- Propuesta basada en datos reales, no en estimaciones

**Resultado:** Diagnostico preciso con datos del hotel. Sin distorsion.

### Verificacion Rapida

```bash
# Probar conexion GA4 con un Property ID especifico:
venv/Scripts/python.exe -c "
from dotenv import load_dotenv; load_dotenv()
from modules.analytics.google_analytics_client import GoogleAnalyticsClient
c = GoogleAnalyticsClient(property_id='PROPERTY_ID_AQUI')
print('Available:', c.is_available())
if c.is_available():
    data = c.get_indirect_traffic()
    print('Source:', data.get('data_source'))
    print('Sessions indirect:', data.get('sessions_indirect'))
"

# Verificar que SIN property_id entra en fallback:
venv/Scripts/python.exe -c "
from dotenv import load_dotenv; load_dotenv()
from modules.analytics.google_analytics_client import GoogleAnalyticsClient
c = GoogleAnalyticsClient(property_id=None)
print('Available:', c.is_available())  # Debe ser False
"
```

### Archivos de Configuracion

| Archivo | Variable | Tipo | Descripcion |
|---------|----------|------|-------------|
| `.env` | `GA4_CREDENTIALS_PATH` | Global | Ruta al JSON del service account |
| `.env` | `GA4_PROPERTY_ID` | **Comentado** | No usar como global |
| CLI | `--ga4-property-id` | Por hotel | Property ID del cliente |
| `config/` | `google-analytics-key.json` | Infraestructura | Clave del service account |

### Archivos de Codigo que Consumen GA4

| Archivo | Metodo | Recibe property_id via |
|---------|--------|----------------------|
| `main.py` | `run_v4_complete_mode()` | `args.ga4_property_id` |
| `main.py` | `analytics_data` dict | `ga4_property_id` key |
| `v4_diagnostic_generator.py` | `_calculate_score_ia()` | Parametro `ga4_property_id` |
| `v4_diagnostic_generator.py` | `_check_analytics_status()` | Parametro `ga4_property_id` |
| `v4_diagnostic_generator.py` | `_get_analytics_summary()` | Parametro `ga4_property_id` |
| `v4_diagnostic_generator.py` | `_inject_analytics()` | `analytics_data["ga4_property_id"]` |

---

## Version y Sincronizacion

**Version:** v4.19.0

### Sincronizacion Automatica (pre-commit)

Estos archivos se sincronizan automaticamente en cada commit:
- `AGENTS.md`, `README.md`, `.cursorrules`
- `docs/CONTRIBUTING.md`, `docs/GUIA_TECNICA.md`
- `docs/contributing/REGISTRY.md`

### Regenerable (1 comando)

- `.agent/SYSTEM_STATUS.md` → `python main.py --doctor --status`

### Actualizacion Manual Requerida

- `CHANGELOG.md` -- Historico de cambios por release
- `GUIA_TECNICA.md` -- Notas tecnicas de arquitectura
- `ROADMAP.md` -- Estrategia de monetizacion
- `INDICE_DOCUMENTACION.md` -- Indice de modulos y scripts
- `.agents/workflows/README.md` -- Skills del agente
- `docs/contributing/documentation_rules.md` -- Reglas de documentacion

### Prompt para IA

Para actualizar toda la documentacion oficial, usar:
> "Actualizar documentacion oficial del repositorio"
