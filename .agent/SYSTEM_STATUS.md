# System Status Dashboard

> Auto-generado: 2026-10-24 23:53:35 UTC
> Fuente de verdad para version: VERSION.yaml en raiz del proyecto
> REGENERAR CON: python scripts/doctor.py --status
> NO EDITAR MANUALMENTE - Este archivo se regenera automaticamente

## Versiones

| Componente | Version | Fuente |
|------------|---------|--------|
| Proyecto | 4.82.0 | VERSION.yaml |
| Ecosystem Convention | 1.0.0 | .agent/CONVENTION.md |

## Skills Activas (1)

| Skill | Descripcion |
|-------|-------------|
| phased_project_executor.md | Ejecutor de proyectos por fases. Una fase por sesión. Sin excepciones. Iteraciones medidas con `evidence/FASE-D/measure_iterations.py`, cortadas en el commit de código —o, si el commit no está autorizado, en «listo para revisión» (ver *Cinco cortes* en «Proceso común»). El Paso 0 capitaliza lecciones en `00-lecciones-capitalizadas.md` consultando el índice generado del corpus, y ese artefacto lo verifica `scripts/validate_lesson_capitalization.py` (`[7/8]` del pre-commit). Ejecutado por agentes AI. |


## Estado de Datos

| Metrica | Valor |
|---------|-------|
| Shadow logs | 1364 archivos JSON |
| Sesiones activas | 6 |
| Sesiones archivadas | 6 |
| Ultimo shadow log | 20261024_142416_b1ca5447.json |
| Ultima sesion activa | 2026-10-24_460dbdba.json |
| Ultimo contexto actualizado | 2026-10-24T23:02:11.255589+00:00 |
| Ultima URL procesada | https://example.com/hotel-fixture |

## Config Files (11/12 healthy)

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
| `secret_fragment_policy.yaml` | MISSING FIELDS |
| `settings.yaml` | OK |
| `url_blocklist.yaml` | OK |

**Total:** 11/12 archivos con version+description

## Validaciones

Ejecuta `python main.py --doctor` para verificar el estado completo del ecosistema.

Scripts de validacion:
- `python scripts/validate_agent_ecosystem.py` -- Ecosistema de agentes
- `python scripts/validate_context_integrity.py` -- Integridad de contexto
- `python scripts/doctor.py --status` -- Regenerar este archivo
