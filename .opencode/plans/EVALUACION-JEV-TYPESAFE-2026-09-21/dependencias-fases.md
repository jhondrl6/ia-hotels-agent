# Dependencias — EVALUACION-JEV-TYPESAFE-2026-09-21

Estado al ajustar el 2026-09-21: solo preparación documental. No se ejecutan fases por la existencia de sus prompts.

## Cadena

```text
Preparación documental ajustada
    |
FASE-A propia: corpus / protocolo / checker offline
    |
    +-- B del hermano: AC6–AC9 verificados, interfaz disponible
    +-- C del hermano: consumidor implementado, AC10–AC14 mecánicos verificados
    |                 AC15 mecánico verificado; aceptación real NO-EJERCITADO admitida
    |
FASE-B propia: adaptadores / SDK real con transporte falso / runner offline
    |
    +-- corpus y protocolo inicial versionados + aprobación humana
    +-- autorización literal de conectividad/ajuste con límites propios
    |
FASE-C propia (sin código)
    +-- conectividad y ajuste permitido, solo sobre desarrollo
    +-- checkpoint: congelación final + autorización literal de evaluación
    +-- evaluación / comparación / decisión
    |
FASE-RELEASE propia: revisión / transferencia autorizada / cierre
```

El hermano es `VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20`. Su cadena A→B→C→D→RELEASE y su prohibición de inferencias permanecen intactas. El piloto real corre en este plan, no dentro de sus fases.

## Hitos y evidencia de entrada

| Hito | Evidencia requerida | Estado inicial |
|---|---|---|
| Interfaz de decisiones | AC6–AC9 del hermano, scanner/contract/costura y tests reales en disco | PENDIENTE; archivo ausente |
| Consumidor de pertinencia | AC10–AC14 y mecánica AC15; test real no filtrador y su par verde/rojo | PENDIENTE; archivo ausente |
| Aceptabilidad del consumidor | Se mide en la FASE-C propia; no se exige antes para evitar circularidad | NO-EJERCITADA |
| Comparador LLM | DeepSeek habilitado por defecto según operador, modelo efectivo y credencial utilizable por verificar en preflight autorizado | Declaración del operador, no autenticación medida |
| Anthropic | No tiene API habilitada; no es dependencia ni alternativa automática | EXCLUIDO |
| Cuenta Jev | Acceso declarado; autenticación, cuota y saldo aún sin comprobar | NO-EJERCITADO |
| Muestra/protocolo | Validación, revisión humana y commit autorizado anterior a cualquier inferencia | PENDIENTE |

El maestro original de D7 pide AC9 verde y un consumidor real solicitante, **no todos los AC10–AC15 verdes**. Este plan exige el consumidor C implementado para su integración, pero admite el cierre offline de su aceptabilidad. No se cambia una deuda ajena para aparentar desbloqueo.

## Conflictos de archivos

| Superficie | Regla |
|---|---|
| `scripts/decision_client.py` | Propiedad inicial de B del hermano; este plan no lo crea antes. Integración solo tras su entrega, sin sesiones concurrentes sobre el archivo |
| `scripts/triage_lesson_relevance.py` | Se consume y prueba su guard real; no se modifica para acomodar silenciosamente el piloto |
| `modules/providers/llm_provider.py` | Solo lectura; DeepSeek se integra como comparador por la costura, sin modificar runtime ni su retorno de texto |
| Índice generado `.opencode/LECCIONES-INDEX.md` y `.opencode/lecciones_index.json` | Compartido con otros planes; regenerar desde todo el árbol, revisar delta y no revertir trabajo ajeno |
| `evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/` | Directorio propio; no reutilizar carpetas FASE-A/B/C de otros planes ni sobrescribir corridas |
| Documentos de planes hermanos | Solo lectura. Excepción futura exclusivamente para D7/D6, con instrucción literal que nombre archivos y alcance |
| Configuración central, VERSION, hooks y gates | Fuera de alcance; no modificar para hacer pasar una validación |

## Decisiones pendientes con dueño y condición

| Decisión | Dueño | Momento / condición | Si falta |
|---|---|---|---|
| Etiquetas humanas y validación del saneamiento | Operador o persona designada | A, antes de congelar | Muestra BORRADOR; no inferir |
| Umbrales de calidad/suficiencia y política de ajuste | Operador con propuesta razonada de A | Antes de llamadas; cierre final de umbrales operativos antes de evaluación | No ejecutar; nunca escoger el corte mirando evaluación |
| Modelo DeepSeek y primitiva Jev | Ejecutor B + operador si cambia el diseño | Docs actuales, interfaz efectiva y pruebas offline | Checkpoint; no cambiar a Anthropic |
| Entorno aislado e instalación | Operador | B, una vez resueltas dependencias del SDK y exclusión Git del entorno | No instalar en el entorno principal |
| Presupuesto de solicitudes, tokens, USD, tiempo y reintentos | Operador | Antes de cada etapa con inferencias, ligado a hashes | COSTE-NO-PAGADO si no se autoriza financiar/ejecutar |
| Commit de muestra/protocolo | Operador | Antes de primera inferencia y de cada nuevo congelado usado | No inferir; el usuario ha diferido commits en la preparación |
| Transferencia de D7/D6 | Operador | Tras decisión y lectura del estado vigente del hermano | `transfer_status = PENDIENTE`; sin cierre ajeno |
| Registro oficial, write-back y archivado | Operador | RELEASE, interfaz vigente verificada y alcance autorizado | Checkpoint documental; no cierre final ficticio |

## Alternativas consideradas

| Opción | Base disponible | Decisión de diseño |
|---|---|---|
| Preparar ahora; integrar tras B/C offline | Dos scripts externos aún ausentes; corpus local existente | ELEGIDA para este ajuste. Evita duplicar la interfaz y no exige calidad semántica antes de medirla |
| Piloto independiente antes de B/C | Técnicamente posible llamar la API directa; no hay runner medido ni ventaja cuantificada | NO elegida: cambia la arquitectura acordada y duplicaría parte del trabajo. Requiere nueva decisión |
| Solo mejorar búsqueda fría | Índice de 320 IDs en la medición de entrada, sin inferencias necesarias | Se conserva como línea base, no demuestra por sí sola el juicio semántico |
| Comparador Anthropic | Código existe, API no habilitada según operador | EXCLUIDA, no pendiente de conseguir credenciales |

No se adjudican a estas opciones costes o rendimientos que no se midieron. Una demora por gobernanza no se presenta como imposibilidad técnica.
