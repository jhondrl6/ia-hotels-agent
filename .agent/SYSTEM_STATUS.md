# System Status Dashboard

> Auto-generado: 2026-09-25 23:14:06 UTC
> Fuente de verdad para version: VERSION.yaml en raiz del proyecto
> REGENERAR CON: python scripts/doctor.py --status
> NO EDITAR MANUALMENTE - Este archivo se regenera automaticamente

## Versiones

| Componente | Version | Fuente |
|------------|---------|--------|
| Proyecto | 4.78.0 | VERSION.yaml |
| Ecosystem Convention | 1.0.0 | .agent/CONVENTION.md |

## Skills Activas (1)

| Skill | Descripcion |
|-------|-------------|
| phased_project_executor.md | Ejecutor de proyectos por fases. Una fase por sesión. Sin excepciones. Iteraciones medidas con `evidence/FASE-D/measure_iterations.py`, cortadas en el commit de código —o, si el commit no está autorizado, en «listo para revisión» (ver *Cinco cortes* en «Proceso común»). El Paso 0 capitaliza lecciones en `00-lecciones-capitalizadas.md` consultando el índice generado del corpus, y ese artefacto lo verifica `scripts/validate_lesson_capitalization.py` (`[7/7]` del pre-commit). Ejecutado por agentes AI. |


## Estado de Datos

| Metrica | Valor |
|---------|-------|
| Shadow logs | 1218 archivos JSON |
| Sesiones activas | 10 |
| Sesiones archivadas | 6 |
| Ultimo shadow log | 20260923_003742_86a31470.json |
| Ultima sesion activa | 2026-09-19_dfa27c04.json |
| Ultimo contexto actualizado | 2026-09-19T19:58:31.332935+00:00 |
| Ultima URL procesada | https://www.donalfonsohotel.com/ |

## Config Files (11/11 healthy)

| Archivo | Estado |
|---------|--------|
| `certificates.yaml` | OK |
| `client_material_policy.yaml` | OK |
| `commercial.yaml` | OK |
| `fallbacks.yaml` | OK |
| `financial_defaults.yaml` | OK |
| `pricing.yaml` | OK |
| `provider_registry.yaml` | OK |
| `regional_benchmarks.yaml` | OK |
| `scenarios.yaml` | OK |
| `settings.yaml` | OK |
| `url_blocklist.yaml` | OK |

**Total:** 11/11 archivos con version+description

## Validaciones

Ejecuta `python main.py --doctor` para verificar el estado completo del ecosistema.

Scripts de validacion:
- `python scripts/validate_agent_ecosystem.py` -- Ecosistema de agentes
- `python scripts/validate_context_integrity.py` -- Integridad de contexto
- `python scripts/doctor.py --status` -- Regenerar este archivo
