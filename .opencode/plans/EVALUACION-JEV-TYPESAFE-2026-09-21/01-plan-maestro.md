# Plan maestro — EVALUACION-JEV-TYPESAFE-2026-09-21

**Estado: PREPARACIÓN AJUSTADA el 2026-09-21; implementación e inferencias PENDIENTES.** La preparación offline puede avanzar con una instrucción de fase. La integración y la comparación siguen bloqueadas por las dependencias de §5. Ninguna fase se ejecutó durante este ajuste documental.

Base de la concepción y de la auditoría: HEAD `99a33d8`, medido con `git rev-parse --short HEAD`. Antes del ajuste, `git status --short` mostraba el plan y su contexto sin seguimiento; no se interpreta ese estado posterior como refutación de la limpieza anterior a su creación. El usuario pidió seguir preparando **sin commit**.

Objetivo: comparar la búsqueda fría, **DeepSeek** y Jev para proponer lecciones pertinentes que el Paso 0 pudo omitir. El resultado es consultivo y aditivo: ni filtra lecciones ancladas, ni decide permisos, ni sustituye verificaciones exactas. `triage_lesson_relevance.py` es el consumidor diseñado, todavía no implementado; no es el único componente semántico del repositorio.

## 1. Premisas y procedencia

| # | Premisa | Evidencia y fecha | Consecuencia |
|---|---|---|---|
| P1 | El verificador de capitalización excluye expresamente la pertinencia | `scripts/validate_lesson_capitalization.py`, docstring LÍMITE DECLARADO, leído el 2026-09-21 | Jev se evalúa para juicio semántico, no para validar forma |
| P2 | No existen `scripts/decision_client.py` ni `scripts/triage_lesson_relevance.py` | Existencia comprobada con `Path.exists()`; README del hermano con fases pendientes, 2026-09-21 | Integración bloqueada; la muestra y sus controles locales no necesitan esas implementaciones |
| P3 | D7 exige AC9 verde y un consumidor real que lo pida; D6 exige pertinencia aceptable y candidatos nuevos | Maestro y prompt C de VERIFICADOR-CONTEXTO-DE-FASE, leídos el 2026-09-21 | No exigir AC15 semántico verde para poder medirlo; tampoco exigir que gane Jev para evaluar D6 |
| P4 | **DeepSeek es el proveedor habilitado por defecto; Anthropic no tiene API habilitada** | Confirmación explícita del operador en esta sesión, 2026-09-21; no se inspeccionaron secretos ni se probó autenticación | Comparador único LLM: DeepSeek. Anthropic excluido; habilitarlo no es requisito ni fallback |
| P5 | El wrapper vigente devuelve solo texto y puede seleccionar otro proveedor disponible | `modules/providers/llm_provider.py`: `AnthropicProvider.chat_completion`, `DeepSeekProvider.chat_completion`, `ProviderAdapter._initialize_provider` y `unified_request`, leídos completos el 2026-09-21 | No usar su retorno como fuente de usage ni su modo auto en el benchmark. No modificar ese archivo en este plan |
| P6 | Jev tiene API propia, respuestas tipadas y usage de tokens; Noul no trae confidence separada | Documentación API, modelos, Noul y SDK, consultada el 2026-09-21; enlaces completos en el contexto | Contrato explícito de probabilidad, confianza disponible y abstención; no fabricar campos |
| P7 | SDK publicado `typesafe-sdk==0.7.0`, Python >=3.10; modelo versionado documentado `jev-1.13.0` | PyPI y docs de modelos, 2026-09-21 | Candidatos a pin, a revalidar antes de instalar; el alias `jev-latest` no es pin |
| P8 | Entorno local Python 3.13.3; SDK, httpx2 y tenacity ausentes | `venv/Scripts/python.exe`, `importlib.metadata`, 2026-09-21; pydantic 2.12.3, pydantic-core 2.41.4, typing-extensions 4.15.0 presentes | Probar resolución en entorno aislado; `httpx` instalado no satisface `httpx2` |
| P9 | Docs de modelos: 64k tokens para estado + todas las preguntas; 32k para estado + pregunta más larga; inglés ofrece mejor precisión | `https://docs.typesafe.ai/models`, 2026-09-21 | Rectifica «ventana no documentada». Corpus español sin traducción silenciosa; controlar tamaño y cuotas vigentes |
| P10 | Precio público Jev: USD 0.042/MTok de entrada, salida gratuita; benchmarks son demostraciones internas | Blog de anuncio y portada, 2026-09-21 | Precio no equivale a coste medido; no prometer ahorro ni latencia sin corrida |
| P11 | No entrenar con inputs no implica no retenerlos; ZDR se ofrece para enterprise | Política de privacidad y docs legales, 2026-09-21 | Corpus propio saneado, sin material del cliente; no presumir ZDR en esta cuenta |
| P12 | En la auditoría faltaba el Paso 0 y el índice estaba vencido | `scripts/validate_lesson_capitalization.py` produjo C1/AUSENTE; `scripts/build_lesson_index.py --check` produjo FAIL, 2026-09-21 | El ajuste incorpora `00-` y regeneración. Que los controles documentales pasen no demuestra calidad del modelo |

Las cifras del corpus previo al ajuste y las consultas están en `00-lecciones-capitalizadas.md`. Acceso habilitado, SDK instalable y proveedor ejercitado son tres hechos distintos. No hay medición de autenticación, cuota de cuenta ni saldo de Jev/DeepSeek en esta sesión.

## 2. Criterios de aceptación

Los AC1–AC7 conservan sus IDs; se precisan sus contratos y se añaden AC8–AC12. Todas las rutas de evidencia de esta tabla son **artefactos futuros**, bajo `evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/`. Los instrumentos del piloto todavía no existen; sus dueños son las fases indicadas.

| AC | Criterio | Fase / instrumento y evidencia |
|---|---|---|
| AC1 | Integración detrás de `decision_client.py`, sin SDK ni adaptadores importados por consumidores. Añadir cada proveedor afecta una sola frontera de producción; tests, runner y manifiesto de dependencias se contabilizan aparte, no se esconden para afirmar «un archivo» | B; `FASE-B/import_scanner.txt` con población y coincidencias, `FASE-B/integracion.json` con archivos y API pública consumida |
| AC2 | Sin proveedor, respuesta ilegible o modelo inesperado: error explícito, nunca decisión por defecto. Jev versionado; Noul conserva `p_yes` y `confidence = null`. DeepSeek explícito, sin auto ni fallback a Anthropic | B; tests causales en `FASE-B/contract.txt`, `FASE-B/modelos.json` |
| AC3 | Muestra objetivo de 60–100 pares, humana, saneada, con originales rastreables por sha y partición por plan. Inputs, etiquetas y manifiesto quedan versionados antes de la primera inferencia, incluida conectividad | A/B; `muestra.json`, `etiquetas.json`, `protocolo.json`; productor y checker `scripts/evaluate_jev_pilot.py` previstos |
| AC4 | Comparación sobre los mismos pares y contenido semántico: capa fría, DeepSeek y Jev. Publica proveedor/modelo efectivos, recuperación, precisión, recall importante, abstenciones, errores, revisión humana, latencia, tokens y contabilidad de coste separada | C; `FASE-C/respuestas.jsonl`, `FASE-C/informe_comparativa.json`, regenerables desde registros |
| AC5 | Regla de adopción pre-registrada; decisión entre ACTIVAR, RECHAZAR, MUESTRA-INSUFICIENTE y COSTE-NO-PAGADO. Fallo operativo usa `run_status = FALLIDO`, `decision = null`, no RECHAZAR | C; `FASE-C/decision.json` + `FASE-C/decision.md`, producidos por el runner y revisados por el operador |
| AC6 | Ningún proveedor elimina filas ancladas. Test sobre el guard real del consumidor y mutación causal verde/rojo; en C se repite offline con respuestas reales persistidas, sin nuevas inferencias | B/C; `FASE-B/mutation.json`, `FASE-C/aditividad.json` con `anchored_before`, `anchored_after`, `removed: []` |
| AC7 | Publicar decisiones separadas sobre Jev/D7 y sobre elegibilidad de D6. Actualizar la deuda del hermano solo con instrucción literal y estado re-leído; sin ella queda transferencia PENDIENTE, nunca deuda cerrada | C/RELEASE; `FASE-C/decision.json` con `jev_recommendation`, `d6_eligibility`, `transfer_status` y, si se autoriza, diff delimitado |
| AC8 | Antes de cada intento real comprobar permiso con alcance exacto, hashes, saneamiento y presupuesto finito de llamadas/tokens/USD/tiempo/reintentos. Falta o agotamiento impide la siguiente llamada | B/C; `FASE-B/budget_tests.txt`, `FASE-C/preflight.json`, `FASE-C/consumo.json`; mutation check del guard real |
| AC9 | SDK real instalado en entorno aislado, con transporte falso y cero red; prueba éxito, IDs incompletos, esquema inválido, 401, 422, 429, 5xx y timeout. Los tests prueban que alcanzaron cada ruta, no solo el mock de nuestra interfaz | B; `FASE-B/entorno.json`, `FASE-B/requirements-pilot.txt`, `FASE-B/sdk_contract.txt`, `FASE-B/mutation.json` |
| AC10 | Instrumentos de muestra/métricas/coste auto-verificados con casos de resultado conocido. Recuperación y clasificación tienen denominadores separados; ausencias y fallos no se computan como ceros favorables | A/B; `FASE-A/selftest.txt`, `FASE-B/metrics_tests.txt`, reporte con población y exclusiones |
| AC11 | Preparación con Paso 0, dependencias, contrato, prompts y checklist coherentes; índices frescos y validaciones documentales sin nuevas infracciones. Estado de cada AC respaldado por su artefacto, no por prosa | Preparación y cada fase; salidas de validadores en el registro de preparación/ejecución |
| AC12 | Preflight distingue habilitación declarada, SDK instalado, autenticación real y cuota/saldo comprobados. DeepSeek obligatorio, Anthropic excluido; indisponibilidad detiene o aplaza, no elimina un brazo de la comparación | B/C; `FASE-C/preflight.json` por proveedor, sin credenciales ni headers de autorización |

## 3. Arquitectura, APIs y límites

### Frontera de proveedores

`decision_client.py` es la frontera prevista para Jev y DeepSeek. No se instancia `ProviderAdapter` en modo auto, ni se recupera telemetría a partir de su cadena de texto. La integración de evaluación llama al proveedor seleccionado a través de la costura y captura la respuesta externa antes de perder sus metadatos. No cambia `modules/providers/llm_provider.py`, ni las prioridades globales del producto, ni habilita Anthropic.

Al llegar B se lee la interfaz **real** entregada por el hermano. Si ya preserva uso y modelo, se reutiliza; si necesita evolución, se documenta el delta y se exige compatibilidad con sus consumidores y tests. No inventar una segunda costura ni cambiar el triaje ajeno para ocultar una incompatibilidad. Si el contrato vigente impide AC1/AC2, dejar checkpoint y pedir decisión.

Contrato requerido para el piloto: `provider_requested`, `provider_effective`, `model_requested`, `model_effective`, `answers`, `usage_raw`, `usage_normalized`, `elapsed_ms`, `attempts`, `error_kind`, `request_id` cuando lo ofrezca el proveedor. Ausente se conserva como null con motivo. Telemetría no es una decisión semántica; se preserva sin alterar la forma que consume C del hermano.

DeepSeek usa la credencial `DEEPSEEK_API_KEY` por el mecanismo seguro disponible y el endpoint vigente de su servicio. El código actual usa `https://api.deepseek.com/v1/chat/completions` y `deepseek-chat`. Ese nombre es candidato de configuración, **no garantía de versión inmutable**: B verifica la interfaz oficial y registra modelo solicitado/devuelto, fecha y fingerprint si existe. Sin versión fija disponible, declarar reproducibilidad acotada; no fabricar un pin ni afirmar identidad entre corridas. No se requiere `ANTHROPIC_API_KEY`.

### Jev

- API `POST https://api.typesafe.ai/v1/systemone`; Bearer mediante `TYPESAFE_API_KEY` gestionada fuera de la evidencia. No es un reemplazo OpenAI-compatible supuesto.
- SDK candidato `typesafe-sdk==0.7.0`, modelo candidato `jev-1.13.0`, revalidados en B y antes de C. `jev-latest` puede moverse.
- Dependencias publicadas: httpx2 >=2.0.0, pydantic >=2.12.0, pydantic-core >=2.41.1, tenacity >=9.0.0, typing-extensions >=4.13.0. No instalar en el entorno principal durante la preparación; B usa entorno aislado y deja su lock/manifiesto reproducible.
- Noul es la opción inicial para una pregunta binaria por candidato. `p_yes` bajo es evidencia negativa, no baja confianza por definición. Banda intermedia deriva a revisión; los cortes se calibran según §4. No fabricar `confidence` a partir de Noul.
- Choice con categorías pertinente/no pertinente/insuficiente es alternativa de diseño, no un cuarto brazo obligatorio. Si se elige en lugar de Noul, se fija antes de la evaluación. Sus probabilidades/confidence no se comparan como si fueran la misma escala que un score autorreportado de DeepSeek.
- DeepSeek entrega etiquetas estructuradas con abstención explícita. Un score autorreportado, si se usa, se etiqueta como tal y se calibra por separado; no se presenta como probabilidad calibrada del proveedor. Si el consumidor exige confianza numérica obligatoria, resolver el contrato antes de inferir, no rellenar null con 0 o 1.
- Los límites de tokens son sobre estado y preguntas, no sobre el número de lecciones del índice. No enviar todo el repo ni truncar silenciosamente. El contador/tokenizador o cota conservadora utilizada debe verificarse antes de permitir red; no se usa bytes/4 como garantía de presupuesto.
- Configurar timeout y reintentos explícitos. El SDK documenta dos reintentos por defecto; para el piloto se desactivan los ocultos y el runner controla cada intento autorizado. La concurrencia inicial es serial y cualquier cambio se pre-registra.

### No-alcance

El write-back de QMind se verifica por título/contenido/sha/estados y no se sustituye por Jev. Fuera: Tribunal, gates de publicación, `run_all_validations.py`, hooks, `.agents/`, AGENTS.md, `.cursorrules`, VERSION.yaml, prioridades LLM globales, producto hotelero, material del cliente y routing de permisos. No se ejecuta `v4complete` ni `v4audit`.

## 4. Protocolo experimental y contabilidad

### Corpus y etiqueta

A construye una muestra candidata de 60–100 pares plan–lección desde corpus propio. El tamaño final y el número de planes/clases se publican: no se presume suficiencia estadística por alcanzar un número. La rúbrica distingue pertinente/no pertinente/insuficiente y marca importancia por separado. El operador o una persona designada etiqueta sin ver las respuestas de los proveedores; el agente puede preparar candidatos, pero no atribuirse una etiqueta humana.

Separar por **plan** el ajuste y la evaluación; deduplicar pares y fragmentos, declarar lecciones compartidas y controlar dependencias. El contexto de un plan no incluye su cierre posterior ni metadatos que revelen la etiqueta (`planes_que_lo_citan`, aceptación posterior, etc.). Un aprendizaje posterior puede ayudar a etiquetar una omisión, pero solo entra como candidato histórico si se prueba que la lección ya estaba disponible en el corte de ese plan; de otro modo pertenece a otro experimento, no a recall histórico.

Versionar inputs saneados, etiquetas separadas, SHA del original, SHA del saneado, cortes temporales, rúbrica, splits, exclusiones y revisión humana del saneamiento. Nunca versionar secretos ni texto del cliente. Las etiquetas no viajan a las APIs. El índice reducido sirve para recuperar candidatos, no sustituye por defecto al fragmento completo que requiere el juicio; el contexto semántico aportado debe ser equivalente para los tres brazos.

### Línea base y métricas

Congelar consultas, campos y reglas de la capa fría, sin afinarlas mirando el conjunto de evaluación. DeepSeek y Jev clasifican el mismo conjunto de candidatos elegibles. Medir por separado:

1. Recuperación: pertinentes importantes presentes entre candidatos / pertinentes importantes del conjunto humano elegible.
2. Clasificación: precisión entre propuestas, recall importante dentro de candidatos, abstenciones e insuficiencia.
3. Extremo a extremo: propuestas importantes correctas / conjunto importante elegible, incluyendo omisiones de recuperación.
4. Coste operativo: tiempo de revisión humana, latencia total y por solicitud, errores, reintentos y consumo.

Cada cociente publica numerador/denominador e intervalo o motivo de no estimación. Denominador cero no equivale a 100 %. Reportar fallos por separado y su impacto en cobertura, sin excluirlos para mejorar artificialmente el score. Las distribuciones agrupadas por plan no se presentan como pares independientes. A define el cálculo de incertidumbre y la suficiencia mínima antes de observar evaluación.

### Pre-registro y decisión

`protocolo.json` contiene reglas de recuperación, rúbrica, modelos, parámetros, política de caché, splits, límites de gasto y criterios de adopción con valores explícitos: mínimos de calidad/cobertura, margen frente a DeepSeek, tratamiento de abstenciones, coste, latencia y revisión humana. **Los valores aún no están elegidos**; A los propone con su base y el operador los acuerda antes de las llamadas. Null, «a decidir» o falta de aprobación impiden inferencias.

La muestra se congela/versiona antes de cualquier inferencia. La política y el presupuesto permiten, si se aprueba, conectividad y ajuste únicamente sobre el split de desarrollo. Tras ese ajuste se congelan prompt y umbrales operativos definitivos **antes de abrir la evaluación**; los criterios de adopción y suficiencia no se retocan según resultados. Toda nueva versión tiene hashes y autorización propios. La conectividad, el ajuste y la evaluación tienen contabilidad separada. Un cambio inducido por resultados de evaluación exige otra muestra de evaluación y nuevo protocolo, no reetiquetar el mismo resultado como confirmatorio.

`run_status` usa los literales NO-EJERCITADO, COMPLETO, INCOMPLETO o FALLIDO. Un fallo de autenticación, esquema, datos o contabilidad produce `decision = null`; se corrige o se declara impedimento operativo, nunca se usa para afirmar que Jev no sirve. Si no hay autorización/financiación, COSTE-NO-PAGADO describe la decisión de no ejecutar, no un rechazo del modelo. Con datos válidos pero potencia insuficiente, MUESTRA-INSUFICIENTE. ACTIVAR y RECHAZAR requieren los criterios pre-registrados evaluables.

ACTIVAR es una recomendación de adopción, **no un cambio de default ni un permiso de escritura**. Que estructurar mejor a DeepSeek cierre el hueco puede sostener RECHAZAR Jev; también puede habilitar la evaluación de D6 si satisface su disparador.

### Consumo y dinero

No confundir tres magnitudes:

- `usage_observed`: tokens reales devueltos, con `usage_raw` y categorías de caché/entrada/salida disponibles.
- `cost_calculated`: consumo observado multiplicado por tarifa fechada y moneda. Es un cálculo sobre uso real, no una extrapolación de un benchmark comercial.
- `cost_billed`: cargo verificable por consola/factura, si está disponible; en otro caso null con motivo. No se exige acceso a datos financieros sensibles para fingir una cifra.

Jev documenta tokens, no importe facturado. DeepSeek requiere su propia tarifa vigente, incluidas categorías de caché si existen; su importe todavía no se midió. La capa fría tiene 0 tokens y 0 cargos de API porque no llama a proveedores, pero su tiempo local/humano no se presenta como gratuito.

El manifiesto fija techos de solicitudes/intentos, tokens de entrada y salida, USD y tiempo total por proveedor y por etapa. Antes de cada intento reservar una cota conservadora; no confiar solo en el usage posterior para frenar gasto. Si un timeout deja cargo desconocido, conservar la reserva y el estado desconocido: no liberar presupuesto como si el coste fuera cero. Si no puede acotarse o conciliarse para decidir, detener la corrida. No repetir por cuenta propia una llamada sin respuesta ni ocultar reintentos del SDK.

## 5. Dependencias y fases

Disparador original de D7: AC9 de B del hermano verde y solicitud de un consumidor real. Este piloto conserva ese disparador; **no afirma que D7 exigiera todos los AC de C verdes**.

Para integrarse se requiere además que el consumidor C esté implementado y verificado offline: AC10–AC14 y parte mecánica de AC15 con evidencia. `acceptance = NO-EJERCITADO` y AC15 parcial por falta de proveedor real **son la entrada esperada**, no un bloqueo circular. El resultado semántico se mide aquí. El contrato de cero inferencias del hermano y su orden A→B→C→D→RELEASE permanecen intactos.

| Fase propia | Trabajo | Entrada | Estado al ajustar |
|---|---|---|---|
| FASE-A | Corpus, rúbrica, checker y protocolo offline | Instrucción de fase y participación humana para etiquetas/criterios; no depende de B/C | PENDIENTE |
| FASE-B | Adaptadores y runner integrado; SDK real con transporte falso; controles de presupuesto y métricas | A y B/C offline del hermano; archivo compartido liberado, sin ejecución concurrente | BLOQUEADA POR DEPENDENCIA |
| FASE-C | Conectividad, ajuste permitido, comparación real y decisión; **sin escribir código** | A/B verificadas, snapshots versionados y autorizaciones literales con presupuesto | BLOQUEADA POR DEPENDENCIA Y AUTORIZACIÓN |
| FASE-RELEASE | Revisión de evidencia, transferencia D7/D6 y cierre documental | C con resultado válido o decisión explícita de cierre sin inferencias; deuda visible y permisos separados | PENDIENTE |

Dos fases de implementación (A/B) y una de medición sin código (C): no se cumple el requisito de tres implementaciones para FASE-VERIFY del executor §4.6. La revisión cruzada de artefactos se hace en C y RELEASE; no se omite. Ningún resultado certifica la pipeline hotelera.

Mientras se completa A, no se toca la costura inexistente. Tras B/C del hermano se re-lee el contrato efectivo: este plan se adapta a él, no ordena reescribir las fases ajenas. El permiso de ajustar documentos del 2026-09-21 no autoriza ejecutar A.

## 6. Archivos e instrumentos previstos

| Archivo / superficie | Dueño y propósito | Estado |
|---|---|---|
| `scripts/evaluate_jev_pilot.py` | A: preparar/checkear muestra y calcular métricas deterministas; B: ejecutar por la costura y emitir comparación/decisión | NUEVO, no implementado |
| `scripts/decision_client.py` | Lo crea B del hermano; B de este plan integra proveedores dentro de su frontera y preserva metadatos | Ausente al ajustar; no crearlo anticipadamente |
| `tests/quality_gates/jev_pilot/` | A/B: corpus, protocolo, contabilidad, ausencia de red, SDK y guard real de aditividad | NUEVO, no implementado |
| `evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/` | Muestra saneada y protocolo en raíz; subdirectorios FASE-A/B/C/RELEASE para evidencia propia | No existe al ajustar; ninguna evidencia se declara producida |
| Índice generado del corpus | Regenerado mediante `scripts/build_lesson_index.py`, nunca a mano | Se revalida al cerrar cada edición documental |

Interfaces previstas del runner: `prepare`, `check`, `run`, `report`, con rutas explícitas de muestra/protocolo/evidencia. A/B deben fijar y probar su `--help`; estos nombres describen trabajo pendiente, no comandos ya disponibles. `check` y `report` no instancian clientes ni cargan credenciales; `run` es el único modo que podría hacer inferencias, después del preflight. `report` reproduce resultados desde los registros, sin red.

No crear un framework de proveedores ni un buscador nuevo. Los consumidores solo importan el contrato público. El SDK y los adaptadores se mantienen en la frontera acordada; cualquier incompatibilidad con el aislamiento del hermano bloquea B hasta una decisión explícita.

## 7. Permisos, decisiones pendientes y cierre

La matriz operativa está en `04-contrato-ejecucion.md`; dependencias y conflictos en `dependencias-fases.md`.

Pendientes antes de gastar: designar quien etiqueta/revisa saneamiento, fijar umbrales y suficiencia, elegir configuración exacta DeepSeek y primitiva Jev, aprobar presupuesto finito y acceso al entorno aislado. No se solicitan valores de credenciales. El acceso habilitado no acredita cuota, saldo ni permiso de consumo.

Commit, push, write-back, archivado, instalación de dependencias e inferencias requieren sus instrucciones de alcance. Hoy solo están autorizados estos documentos y la regeneración derivada del índice. La muestra necesita un commit aprobado **más adelante**, antes de la primera inferencia; no se ejecuta ahora.

Por defecto no se edita ningún plan hermano. Única excepción futura: actualizar D7/D6 con instrucción literal que nombre archivos y alcance, tras re-leer su estado; si ya fue archivado, registrar el destino vigente en vez de inventar una ruta. Sin permiso, se deja transferencia PENDIENTE en este plan. No declarar la deuda cerrada ni activar D6 automáticamente.

RELEASE no aumenta VERSION ni cambia configuración central. Su registro oficial, write-back y archivado se realizan únicamente tras resolver los permisos del flujo documental; si faltan, dejar checkpoint y no presentar el plan como cerrado. Una conclusión RECHAZAR es un resultado válido; una ejecución fallida no cierra los AC de comparación. Cualquier cierre administrativo sin inferencias conserva todos los AC no ejercitados y su motivo.
