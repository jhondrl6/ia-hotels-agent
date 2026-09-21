# Análisis de ejecución — EVALUACION-JEV-TYPESAFE-2026-09-21

**Estado de ejecución: PENDIENTE.** Este archivo acumula evidencia desde la preparación; no afirma que el piloto se haya implementado.

## Resumen de ejecución

| Fase | Estado | Evidencia / iteraciones |
|---|---|---|
| Preparación documental | AJUSTADA el 2026-09-21 | Lecturas, consultas QMind y validación documental; no es fase de código |
| FASE-A | PENDIENTE | Sin ejecución |
| FASE-B | BLOQUEADA POR DEPENDENCIA | Sin ejecución |
| FASE-C | BLOQUEADA POR DEPENDENCIA Y AUTORIZACIÓN | Sin ejecución |
| FASE-RELEASE | PENDIENTE | Sin ejecución |

## Registro de preparación

La auditoría encontró disparadores B/B+C inconsistentes, circularidad potencial con AC15, comparador textual sin usage, coste sin distinción contable, Paso 0 ausente e índice vencido. El operador ordenó ajustar documentos y confirmó DeepSeek habilitado por defecto / Anthropic sin API. En ese momento no autorizó inferencias ni commits; después pidió explícitamente commitear la preparación antes de ejecutar nada, y entró como `2c966f6`.

Correcciones de diseño:

- A prepara localmente; B propia requiere costura y consumidor verificados offline, admitiendo AC15 semántico parcial. No se modifica el contrato de cero inferencias del hermano.
- DeepSeek queda fijado como comparador efectivo sin fallback. `llm_provider.py` no se modifica; telemetría por la frontera de decisiones.
- AC1–AC7 precisados y AC8–AC12 añadidos para presupuesto, SDK, instrumentos, preparación y estado operativo.
- Corpus humano/saneado, separación por plan, controles de fuga, preregistro, reproducción y costes observados/calculados/facturados diferenciados.
- D6 no exige que gane Jev; cambios de deuda requieren autorización adicional.
- Paso 0 realizado después de la concepción y antes de implementación; no atribuido retroactivamente. Dos consultas MCP a QMind funcionaron y se contrastaron con el corpus local.

## Validaciones de preparación

Ejecutados el 2026-09-21 con el Python del proyecto y `PYTHONDONTWRITEBYTECODE=1`. No se ejecutó pytest ni el quick de runtime en este ajuste exclusivamente documental; se aplicaron los controles focalizados siguientes.

| Comando | Estado de auditoría anterior al ajuste | Resultado después del ajuste |
|---|---|---|
| `venv/Scripts/python.exe scripts/validate_lesson_capitalization.py` | FAIL: C1/AUSENTE del propio plan | OK: cuatro planes en alcance; este plan acredita cinco fuentes; forma y trazabilidad, no pertinencia |
| `venv/Scripts/python.exe scripts/build_lesson_index.py --check` | FAIL: par de índices vencido | OK: índice fresco, 320 IDs definidos |
| `venv/Scripts/python.exe scripts/validate_plan_citations.py` | No ejecutado en la auditoría anterior | OK: 743 citas históricas, cero nuevas y cero crecimientos; 79 archivos en inventario |
| `venv/Scripts/python.exe scripts/validate_opencode_refs.py` | No ejecutado en la auditoría anterior | PASS: referencias existentes |
| `venv/Scripts/python.exe scripts/validate_plan_closure.py` | No ejecutado en la auditoría anterior | OK: sin declaraciones de cierre contradictorias |

La regeneración mediante `venv/Scripts/python.exe scripts/build_lesson_index.py` produjo 320 IDs definidos, 50 sin definición, 16 análisis y 415 Markdown. Son cifras de este cierre de preparación, no un pin de tests futuros. Una comparación de conjuntos con el JSON de HEAD descartó introducir IDs sin definición: la primera escritura del regex de Q2 generó citas parciales falsas; se reagrupó/re-ejecutó el patrón antes de regenerar, sin editar el índice a mano.

También se comprobó por aserciones locales la igualdad exacta del conjunto AC1–AC12 en maestro/checklist, ausencia de duplicados, existencia de enlaces locales y post-fase/checklist en los cuatro prompts. La revisión cruzada adicional corrigió el literal FALLIDO, situó la congelación final dentro de C antes de evaluar y dejó el modelo efectivo real pendiente hasta las llamadas autorizadas.

Estos checks no verifican pertinencia, saldo, autenticación, exactitud de etiquetas ni que los controles futuros ya existan. La verificación de estructura de ACs/prompts complementa su cobertura limitada.

## Decisiones de diseño y alternativas

| Tema | Decisión | Alternativa no elegida / motivo |
|---|---|---|
| Secuencia | Preparar offline y respetar B/C offline para integrar | API directa anticipada: posible, pero duplica integración y altera el alcance |
| Comparador LLM | DeepSeek explícito | Anthropic: API no habilitada; auto/fallback: contamina la comparación |
| Telemetría | Capturar por la costura la respuesta externa antes de reducirla a texto/decisión | Refactor del wrapper global: innecesario para este experimento y fuera de alcance |
| Calidad | Muestra humana, incertidumbre y salida insuficiente | Mock verde como calidad: solo prueba mecánica |
| Coste | Uso observado, cálculo tarifario y cargo facturado distintos | Precio de lista como coste de corrida: no es consumo medido |
| Semántica de errores | Ejecución fallida con decisión null | RECHAZAR por un 401/timeout: confunde disponibilidad con calidad |
| D6 | Elegibilidad independiente de victoria Jev | Exigir ACTIVAR Jev: no es el disparador original de D6 |

## Lecciones capitalizadas y límites

El efecto sobre el diseño y sus fuentes está en `00-lecciones-capitalizadas.md`. Todavía no hay lecciones de una implementación ejecutada ni cambios medidos en calidad del triaje. No inventar aprendizajes por fase pendiente.

La revisión separó tres contratos: proveedor habilitado, proveedor instrumentado y proveedor ejercitado. La confirmación del operador satisface el primero para DeepSeek, no los otros dos. El reporte de uso solo es fiable cuando sobrevive desde el response hasta el informe y queda atribuido al proveedor realmente usado.

## Seguimientos

Etiquetas/saneamiento humanos, criterios/umbrales, presupuesto, entorno aislado, versiones actuales y permisos: dueños y disparadores en `dependencias-fases.md`. Transferencia D7/D6 no ejecutada. No se dispone todavía de evidencia para adoptar o rechazar Jev.

## Cierre del plan — PENDIENTE

Sin inferencias, write-back ni archivado. La preparación quedó comiteada el 2026-09-21 en `2c966f6` (base `99a33d8`, par de índices en el mismo commit, 7/7 checks del hook en verde); el **push no está ejecutado ni autorizado**. El cierre futuro exige la revisión de artefactos y los permisos del contrato; una decisión administrativa de no ejecutar debe conservar los AC no ejercitados.
