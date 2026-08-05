# Evidencia N3-diff — Run 123637 (pre-bump)

> **Estado**: preservado 2026-08-05 (FASE-E, R3.3)
> **Nota de versión**: los artefactos E2E llevan la versión del código que corrió
> (4.69.0 + fixes aplicados en sesiones anteriores); el bump a 4.70.0 es posterior
> y no se re-ejecutó v4complete. Esto es correcto por diseño: la versión reflejada
> en los artefactos es la que estaba vigente al momento de la ejecución.

## Contexto

El run 123637 (2026-08-04 12:36:37) fue el primero de dos ejecuciones de
`v4complete` contra Zi One Luxury (https://zione.co/) en la sesión del 2026-08-04.
El segundo run (124443) sobrescribió los `.md` del primero, pero los JSON
metadata y archivos de auditoría del run 123637 sobrevivieron en el output.

## Diff de 97 líneas (N20)

La validación cruzada post-implementación identificó un diff de 97 líneas entre
los outputs de los runs 123637 y 124443. Este diff **NO es reproducible** porque
los `.md` del run 123637 fueron sobrescritos por el run 124443 en el mismo
directorio de output. Los JSON preservados aquí son la única evidencia restante
del run 123637.

## Archivos preservados

14 archivos JSON del run 123637/123636:
- `gate_report_20260804_123637.json` — report de gates del run 123637
- `commercial_gates_report_diagnostic_20260804_123637.json` — gates comerciales
- `hotel_schema_20260804_123636.json` + metadata — Schema hotel
- `ESTIMATED_faqs_20260804_123637.json` + metadata — FAQ page
- 8 archivos metadata adicionales (open_graph, llms_txt, optimization_guide, etc.)

## Nota de versión (pre-bump)

Los artefactos reflejan v4.69.0 + fixes aplicados durante las sesiones de
desarrollo previas al bump formal a v4.70.0. El bump NO implicó re-ejecución
de v4complete; por lo tanto, los outputs siguen siendo válidos para la
verificación de coherencia del plan.
