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

## Sonda de instalación

El operador autorizó instalar el SDK el 2026-09-21; en ese momento no estaban autorizados FASE-B, inferencias ni push (el push se pidió y ejecutó después). La sonda corrió en un entorno aislado y **sin red**: `TYPESAFE_API_KEY` se eliminó del entorno del subproceso y se usó una clave literal sintética con `httpx2.MockTransport`, que intercepta la petición dentro del proceso. No se escribieron archivos de plan ni de evidencia: `requirements-pilot.txt` y `entorno.json` siguen siendo artefactos de FASE-B.

| Medición | Valor |
|---|---|
| Entorno | `tmp_test/venv-jev-sdk` (Python 3.13.3, ignorado por git, 28 MB); el SDK no se instaló en `venv/` del proyecto (su pydantic se alineó al pin más tarde ese día, ver §Alineación de pydantic en el venv) |
| SDK | `typesafe-sdk==0.7.0` |
| Resolución de dependencias | httpx2 2.13.0, httpcore2 2.13.0, anyio 4.15.1, pydantic 2.13.5, pydantic-core 2.46.5, tenacity 9.1.4, truststore 0.10.4, typing-extensions 4.16.0 |
| Conflicto que exige aislamiento | pydantic 2.13.5 resuelto contra el pin `pydantic==2.12.5` de `requirements.txt`; en el momento de la sonda el venv del producto tenía `2.12.3` (desajuste preexistente con el pin), alineado a `2.12.5` después — ver §Alineación de pydantic en el venv |
| Interfaz real | `TypeSafeClient(api_key, model, retry, timeout, headers, transport, http_client, base_url)`; `system_one(state, questions, model, retry, timeout, extra_headers, extra_body, response_model)` |
| Reintentos por defecto | `max_retries=2`, `backoff_initial=0.5`, `backoff_max=5.0`, `backoff_jitter=0.25`, `respect_retry_after=True`, `timeout=30.0` (presupuesto total de la llamada) |
| Intentos medidos ante 429 | 3 con defaults; 1 con `max_retries=0` |
| Sin API key | `TypeSafeError` antes de cualquier acceso de red |
| 401 / 429 | `TypeSafeAuthenticationError` / `TypeSafeRateLimitError`, ambos con `.status` |
| 200 sin `usage` | `TypeSafeAPIResponseValidationError`: `usage` es obligatorio en el modelo, no degrada a `null` |
| Noul | `NoulAnswer` expone solo `.noul` (sin confidence); respuestas indexadas por los IDs enviados; `resp.model` = `jev-1.13.0` |

Consecuencia en el diseño: AC8 fija `max_retries=0` como requisito y AC9 aserta clases de error y trata un 200 sin `usage` como fallo, no como coste cero. La reproducibilidad del pin `jev-1.13.0` queda corroborada en el SDK real, no solo en la documentación. La sonda **no** prueba autenticación, cuota, saldo ni calidad de decisiones: sigue vigente `NO-EJERCITADO` para esos aspectos.

## Alineación de pydantic en el venv (post-sonda, mismo día)

**Qué se corrigió:** desajuste preexistente entre `requirements.txt` y el `venv/` del producto, ajeno al SDK de Jev. `requirements.txt` pinea `pydantic==2.12.5` / `pydantic_core==2.41.5` / `pydantic-settings==2.10.1` (bump de seguridad, commit `967b13d`); el venv tenía `2.12.3` / `2.41.4` y `pydantic-settings` **sin instalar**.

**Dirección elegida:** sincronizar el venv **al pin**, no bajar el pin al venv. Bajarlo habría deshecho el parche de CVEs y habría dejado el venv por debajo de `pydantic>=2.12.0` que exige el SDK del hermano. Se verificó que `2.12.5` y `2.41.5` son versiones reales y coherentes (par `2.12.x`↔core `2.41.x`).

| paquete | antes (sonda) | después (alineado) | pin en `requirements.txt` |
|---|---|---|---|
| pydantic | 2.12.3 | 2.12.5 | 2.12.5 |
| pydantic_core | 2.41.4 | 2.41.5 | 2.41.5 |
| pydantic-settings | no instalado | 2.10.1 | 2.10.1 |

**Límites que esto NO cambia:**
- El SDK `typesafe-sdk` / `httpx2` / `tenacity` **sigue sin instalarse** en `venv/` del producto; vive aislado en `tmp_test/venv-jev-sdk`. Esta sonda y la prohibición de AC9/contrato de instalarlo en el entorno principal permanecen vigentes.
- `requirements.txt` **no se modificó**: el pin ya era correcto; lo que estaba desviado era el entorno.
- No se tocó el runtime de producción ni `modules/providers/llm_provider.py`.

**Efecto documental:** las afirmaciones "el venv quedó intacto / no se tocó" de esta preparación se leen ahora en dos sentidos: *SDK aislado* (SIGUE CIERTO) vs *venv sin tocar* (YA NO — se alineó su pydantic). Las citas antiguas quedan re-ancladas aquí y en README §Qué cambió / `09-documentacion-post-proyecto.md` §B.

**Verificación tras la alineación:** `pip freeze` coincide con las tres líneas de `requirements.txt`; `run_all_validations.py --quick` → 11/11 PASSED (sin regresión).

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

Sin inferencias, write-back ni archivado. La preparación quedó comiteada y **empujada** el 2026-09-21: base `99a33d8`, rango `2c966f6..99ac860` en `origin/master`, paridad `0/0` verificada con `git ls-remote` y 7/7 checks del hook en cada commit; la instalación del SDK quedó limitada a un entorno aislado. El cierre futuro exige la revisión de artefactos y los permisos del contrato; una decisión administrativa de no ejecutar debe conservar los AC no ejercitados.
