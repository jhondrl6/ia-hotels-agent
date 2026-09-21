# EVALUACION-JEV-TYPESAFE-2026-09-21

**Estado: FASE-A EJECUTADA offline el 2026-09-21 (instrumento `scripts/evaluate_jev_pilot.py` + suite auto-verificada en verde; muestra en **BORRADOR**). Sin inferencias ejecutadas. Los artefactos de A quedaron **commiteados en `71b85b7`** y pendientes de push. La preparación documental sigue publicada en `origin/master` (push `03b9929..60cce03`, verificado con `git ls-remote`; 7/7 checks del hook).** Autorizado y hecho: ajustar el plan, commitear/empujar la preparación, instalar el SDK en entorno aislado para una sonda sin red, y ejecutar/commitear FASE-A offline. Sigue sin autorización: ejecutar FASE-B o posteriores, llamar a APIs de inferencia, empujar los artefactos de FASE-A, write-back a QMind y archivado.

Objetivo: medir si Jev mejora el triaje aditivo de pertinencia frente a la búsqueda fría y **DeepSeek**, con corpus propio saneado y coste acotado. DeepSeek es el proveedor habilitado por defecto según confirmación del operador del 2026-09-21. **Anthropic no tiene API habilitada, queda fuera del piloto y no es un fallback.** No se modifica `modules/providers/llm_provider.py`.

## Qué cambió en la preparación

- Se distingue preparación offline de integración: A puede preparar la muestra; B requiere la costura del hermano y C implementada/verificada offline. No se exige aceptabilidad real para comenzar a medirla.
- El cierre offline de C del hermano puede conservar AC15 parcial y `acceptance = NO-EJERCITADO`. No se levanta su prohibición de inferencias ni se cambia su orden de fases.
- El comparador queda fijado en DeepSeek, con captura de usage/modelo efectivo detrás de la costura. El wrapper actual devuelve solo texto; no sirve como instrumento de coste y no se usa su selección automática.
- Se concretan muestra, saneamiento, aislamiento por plan, métricas, presupuesto, errores y los instrumentos que los producirán. Todos siguen sin implementar.
- La documentación actual de Jev sí publica límites de contexto; Noul no ofrece confidence separada y la calidad en español se debe medir, no heredar del inglés.
- Sonda ejecutada en el SDK real 0.7.0 (entorno aislado, `httpx2.MockTransport`, cero red): el transporte es inyectable, los reintentos por defecto dan **3 intentos** ante un 429 y un 200 sin `usage` lanza error de validación. Por eso AC8 exige `RetryPolicy(max_retries=0)` y AC9 aserta clases de error en lugar de `usage = null`. El SDK **no** se instaló en el `venv` del producto (resuelve pydantic 2.13.5 por encima del pin `2.12.5`). Corrección posterior del mismo día: el `venv` ya no está "intacto" en el sentido estricto — se alineó su pydantic al pin (`2.12.3`→`2.12.5`, core `2.41.4`→`2.41.5`, +`pydantic-settings 2.10.1`) para cerrar un desajuste preexistente entre `requirements.txt` y el entorno. `requirements.txt` y el aislamiento del SDK no se tocaron. Ver `10-analisis-post-implementacion.md` §Alineación de pydantic en el venv.
- D6 se evalúa por aceptabilidad y candidatos nuevos, aunque gane DeepSeek; adoptar Jev y modificar la deuda del hermano son decisiones distintas.
- Se subsana el Paso 0 ausente y se incorpora la preparación ejecutora. No se atribuye a la concepción original una consulta realizada después.

## Estados y dependencias

| Fase | Objetivo | Estado |
|---|---|---|
| FASE-A | Muestra humana/saneada, protocolo y checker offline | **EJECITADA offline 2026-09-21**: checker+métricas en verde (AC10); muestra **BORRADOR** con etiquetas y umbrales pendientes de humano (AC3 parcial) |
| FASE-B | Jev/DeepSeek detrás de la costura, SDK y controles probados sin red | BLOQUEADA POR DEPENDENCIA: A y B/C offline del hermano |
| FASE-C | Comparación autorizada y decisión, sin cambios de código | BLOQUEADA POR DEPENDENCIA Y AUTORIZACIÓN |
| FASE-RELEASE | Revisión de evidencia y cierre documental | PENDIENTE |

Dependencia externa: `VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20`. Al ajustar, `scripts/decision_client.py` y `scripts/triage_lesson_relevance.py` no existen. Re-medir al abrir cada fase; un estado escrito no sustituye evidencia de tests y artefactos.

Dos fases de implementación (A/B) y una de medición (C): no aplica una FASE-VERIFY adicional por el criterio de número de implementaciones del executor. C y RELEASE sí revisan la evidencia cruzada.

## Pendientes priorizados (orden de ejecución)

Cada ítem conserva su puerta de autorización propia: "ejecutar" solo lo inmediatamente siguiente, nunca la cola. Re-medir HEAD/dependencias al abrir cada uno.

| # | Pendiente | Estado hoy | Puerta (qué lo desbloquea) | Tipo |
|---|---|---|---|---|
| P0 | Commitear la corrección del punto 4 + re-anclajes (README, `04-contrato`, `09-documentacion`, `10-analisis`) | **Completado** — corrección del punto 4 + pendientes publicados en `origin/master` (push `03b9929..60cce03`, hook 7/7) | Sin puerta pendiente | Higiene documental |
| P1 | FASE-A: muestra humana/saneada, protocolo y checker **offline** | **Parcialmente hecho**: checker+métricas en verde; muestra **BORRADOR** (4 pares), etiquetas `sin_revisar` y umbrales nulos; **commiteado en `71b85b7`** | Falta: designar revisor humano que etiquete, acordar umbrales del protocolo, y **push** de `71b85b7` (autorización aparte). No bloquea B/C para preparar, pero sí para congelar | Ejecución (offline) |
| P2 | Re-medir la dependencia externa `VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20` (B/C offline, AC15 parcial) | Escrita, no evidenciada | Al abrir B; un estado escrito no sustituye tests | Verificación |
| P3 | FASE-B: Jev/DeepSeek tras la costura, SDK y controles probados **sin red** | BLOQUEADA (por P1 y P2) | A con muestra/protocolo + P2 verde; entorno aislado e instalación autorizados; `requirements-pilot.txt` y `entorno.json` se congelan aquí | Ejecución (offline) |
| P4 (portón de P5) | Preflight de autenticación/cuota/saldo de Jev (AC12/AC8, etiquetadas `B/C`) | **NO-EJERCITADO** (sonda con clave sintética y cero red) | No es fase propia: es el primer paso de FASE-C. Exige el cliente con `RetryPolicy(max_retries=0)` de B antes de llamar (defaults = 3 intentos ante 429, gastarían cuota sin contabilidad) + autorización literal y presupuesto | Medición (con red) |
| P5 | FASE-C: comparación autorizada fría/DeepSeek/Jev y decisión, sin cambios de código | BLOQUEADA (por P3, P4 y autorización) | Runner offline verificado; muestra/protocolo versionados; hashes y límites finitos | Medición (inferencias) |
| P6 | Write-back a QMind | SIN PERMISO | Tras evidencia de C; re-leer la interfaz del writer antes de publicar | Publicación |
| P7 | Archivado del plan + regeneración fresca del índice | SIN PERMISO | Después del write-back; nunca antes | Cierre |

Hecho fuera de git y sin puerta pendiente: la alineación del pydantic del `venv/` al pin (`2.12.3`→`2.12.5`, core `2.41.4`→`2.41.5`, +`pydantic-settings 2.10.1`); `requirements.txt` y `llm_provider.py` intactos, SDK sigue aislado en `tmp_test/venv-jev-sdk`.

## Índice

- [Lecciones capitalizadas](00-lecciones-capitalizadas.md): consultas, ocho lecciones aplicadas al diseño, tres descartes y límites.
- [Plan maestro](01-plan-maestro.md): premisas, AC1–AC12, APIs, protocolo y contabilidad.
- [Contrato](04-contrato-ejecucion.md): permisos, errores, presupuesto y post-fase.
- [Dependencias](dependencias-fases.md): hitos, decisiones pendientes y conflictos.
- [Checklist](06-checklist-implementacion.md): AC, fase, artefacto y estado.
- Prompts: [A](05-prompt-inicio-sesion-fase-A.md), [B](05-prompt-inicio-sesion-fase-B.md), [C](05-prompt-inicio-sesion-fase-C.md), [RELEASE](05-prompt-inicio-sesion-fase-RELEASE.md).
- [Documentación acumulativa](09-documentacion-post-proyecto.md) y [análisis de ejecución](10-analisis-post-implementacion.md).
- [Contexto de evaluación](../../context/CONTEXT-JEV-TYPESAFE-CASOS-DE-USO-2026-09-21.md): fuentes, alternativas y revisión de viabilidad.

## Límites

Fuera de alcance: Tribunal, gates, hooks, `run_all_validations.py`, VERSION.yaml, `.agents/`, configuración central, pipeline hotelera, material del cliente y cambios al proveedor LLM de producción. La exactitud del write-back de QMind no se evalúa con Jev.

No se edita ningún plan vivo ajeno. AC7 solo contempla una transferencia futura, con instrucción literal y alcance delimitado para D7/D6. Sin permiso, permanece PENDIENTE aquí.

No se imprimen ni persisten credenciales. Tener acceso a una API no autoriza llamadas. Instalación, inferencias, commit, push, write-back y archivado se solicitan por separado. No hay presupuesto de inferencias aprobado ni muestra versionada en esta preparación.

## Inicio de la siguiente sesión

Texto para usar **solo cuando el operador decida ejecutar A**; no constituye una orden emitida en esta sesión:

```text
Ejecuta únicamente FASE-A de EVALUACION-JEV-TYPESAFE-2026-09-21.
Lee el README, 05-prompt-inicio-sesion-fase-A.md, 01-plan-maestro.md,
04-contrato-ejecucion.md, dependencias-fases.md, 00-lecciones-capitalizadas.md
y el workflow canónico. Re-mide HEAD/status y el estado de las dependencias.
Prepara corpus y checker offline; no crees anticipadamente decision_client.py.
DeepSeek es el comparador habilitado; Anthropic está excluido y no es fallback.
No consultes credenciales, instales SDKs, llames APIs de inferencia ni hagas commit.
Las etiquetas, el saneamiento y los criterios requieren revisión humana:
si faltan, deja la muestra como borrador, no como congelada o aprobada.
```
