# System Status Dashboard

> Auto-generado: 2026-09-04 23:11:52 UTC
> Fuente de verdad para version: VERSION.yaml en raiz del proyecto
> REGENERAR CON: python scripts/doctor.py --status
> NO EDITAR MANUALMENTE - Este archivo se regenera automaticamente

## Versiones

| Componente | Version | Fuente |
|------------|---------|--------|
| Proyecto | 4.75.0 | VERSION.yaml |
| Ecosystem Convention | 1.0.0 | .agent/CONVENTION.md |

## Skills Activas (1)

| Skill | Descripcion |
|-------|-------------|
| phased_project_executor.md | Ejecutor de proyectos por fases. Una fase por sesión. Sin excepciones. Iteraciones medidas con `evidence/FASE-D/measure_iterations.py`, cortadas en el commit de código. Ejecutado por agentes AI. |


## Estado de Datos

| Metrica | Valor |
|---------|-------|
| Shadow logs | 1201 archivos JSON |
| Sesiones activas | 18 |
| Sesiones archivadas | 6 |
| Ultimo shadow log | 20260903_212834_9d212284.json |
| Ultima sesion activa | 2026-09-04_9d9b4f36.json |
| Ultimo contexto actualizado | 2026-09-04T17:01:34.765883+00:00 |
| Ultima URL procesada | https://www.hotelsalentoreal.com/ |

## Config Files (10/10 healthy)

| Archivo | Estado |
|---------|--------|
| `certificates.yaml` | OK |
| `commercial.yaml` | OK |
| `fallbacks.yaml` | OK |
| `financial_defaults.yaml` | OK |
| `pricing.yaml` | OK |
| `provider_registry.yaml` | OK |
| `regional_benchmarks.yaml` | OK |
| `scenarios.yaml` | OK |
| `settings.yaml` | OK |
| `url_blocklist.yaml` | OK |

**Total:** 10/10 archivos con version+description

## Validaciones

Ejecuta `python main.py --doctor` para verificar el estado completo del ecosistema.

Scripts de validacion:
- `python scripts/validate_agent_ecosystem.py` -- Ecosistema de agentes
- `python scripts/validate_context_integrity.py` -- Integridad de contexto
- `python scripts/doctor.py --status` -- Regenerar este archivo
