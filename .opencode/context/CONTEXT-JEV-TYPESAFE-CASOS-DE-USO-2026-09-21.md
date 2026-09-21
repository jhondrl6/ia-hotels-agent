# CONTEXT-JEV-TYPESAFE-CASOS-DE-USO-2026-09-21

Evaluación de aplicabilidad de Jev/TypeSafe a `iah-cli`, concebida y revisada el 2026-09-21 a partir de https://typesafe.ai/blog/introducing-system-one-models-and-jev y del documento público "thoughts on a typesafe coding agent" (https://docs.google.com/document/d/1G61uUB0FifUnmmrPzFQojZ3KpczYKmXGpgEXDJ2l_Zg/preview).

La ruta inicialmente evaluada fue `.opencode/plans/VERIFICADOR-ESCRITURA-QMIND-2026-09-20`. El plan derivado vive en `.opencode/plans/EVALUACION-JEV-TYPESAFE-2026-09-21`: allí se fijan ACs, fases y permisos; aquí se conserva evidencia, límites y alternativas.

**Estado:** evaluación documental y comprobaciones locales, sin inferencias. Acceso Jev habilitado desde 2026-09-20 y credencial existente según información del operador, no autenticación medida por este piloto. Confirmación adicional del operador el 2026-09-21: **DeepSeek es el proveedor habilitado por defecto; Anthropic no tiene API habilitada**. El comparador LLM es DeepSeek; Anthropic no es requisito ni fallback. No se leyeron ni imprimieron credenciales y no se cambia `llm_provider.py`.

## 1. Jev: interfaz y límites verificados en documentación

Documentación pública consultada el 2026-09-21, sujeta a cambios de early access; no equivale a contrato probado contra la cuenta del operador.

- Modelo de decisiones estructuradas sobre un `state`, no generador de texto libre. API `POST https://api.typesafe.ai/v1/systemone`, Bearer y variable `TYPESAFE_API_KEY` en el SDK.
- Paquete Python `typesafe-sdk`, versión publicada consultada **0.7.0**, Python >=3.10. Clientes `TypeSafeClient` y `AsyncTypeSafeClient`; método `system_one`.
- Dependencias publicadas por PyPI: `httpx2>=2.0.0`, `pydantic>=2.12.0`, `pydantic-core>=2.41.1`, `tenacity>=9.0.0`, `typing-extensions>=4.13.0`. No confundir httpx2 con httpx.
- Modelo fijo documentado **`jev-1.13.0`**. `jev-latest` y `jev-preview` son aliases móviles; request y response deben conservar sus IDs para reproducibilidad. Revalidar disponibilidad el día del piloto.
- `Choice`: hasta 255 opciones, probabilidades y confidence. `Score`: hasta 10 niveles. `Noul`: probabilidad de sí, sin confidence separada. Probabilidad baja no significa incertidumbre: puede ser un no claro.
- Cada Noul evalúa una condición; las preguntas del mismo request se procesan en paralelo. El piloto empieza serial entre requests para controlar intentos y coste.
- Respuesta API con `model`, `answers` y `usage.input_tokens` / `usage.output_tokens`. No se documenta ahí un importe monetario facturado. Request ID se preserva cuando lo exponga el SDK/error; no se inventa cuando falta.
- **Corrección de la primera evaluación:** la página de modelos sí documenta **64k tokens** para estado + todas las preguntas y **32k tokens** para estado + pregunta más larga. También publica límites de tasa sujetos a cambio; la cuota efectiva de esta cuenta sigue pendiente. No afirmar que estos límites no están documentados.
- Inglés es el idioma primario de entrenamiento y de mayor precisión declarada; otros idiomas funcionan sin paridad garantizada. La evaluación debe usar español real, sin traducir para favorecer al proveedor.
- SDK admite transporte/cliente HTTP inyectable, útil para probar su código real sin red. `RetryPolicy` documenta dos reintentos por defecto, hasta tres intentos; presupuesto total de reintentos distinto del timeout HTTP. El runner deberá controlar los intentos y desactivar reintentos ocultos.
- Errores API documentados incluyen 401, 422, 429 y 529. En SDK se distinguen error HTTP, conexión y validación de respuesta. Un fallo nunca equivale a «no hay lecciones pertinentes».

Precio público: **USD 0.042/MTok de entrada**, salida gratuita. Las grandes cifras de aceleración del anuncio son demostraciones internas, con sesgo de evaluación declarado; no se heredan como objetivo del piloto. «Zero Hallucinations» se refiere a forma/esquema, no garantiza exactitud semántica.

Privacidad: política de 2025-11-19, no entrenamiento con inputs y alojamiento en EE. UU.; no promete retención cero por defecto. La documentación legal ofrece ZDR a enterprise, no acredita que esta cuenta lo tenga. No exportar material del cliente ni el repositorio completo: solo una copia saneada del corpus propio aprobada por una persona.

## 2. Por qué no reemplaza el verificador de escritura QMind

| Necesidad del mini-plan | Instrumento adecuado | Por qué no Jev |
|---|---|---|
| Writer con título/archivo explícitos | Parser y contrato del writer | Sintaxis exacta, no juicio |
| Frescura de contenido | Descarga y sha256 frente a snapshot | Igualdad de bytes |
| Fin de PASS cuando falta el CLI | Estados explícitos y modo estricto | Error de instrumentación, no semántica |
| Una sola fuente vigente | Relación de reemplazo verificable | No delegar borrado/publicación a una probabilidad |
| Detección por mutación | Par verde/rojo del guard real | Propiedad determinista |
| Prompt de cierre que mande el writer | Revisión del contrato y del diff | Instrucción textual |

«¿El análisis recoge las decisiones importantes?» o «¿estas fuentes se contradicen?» son preguntas de calidad de contenido. No prueban una escritura correcta ni autorizan eliminación o publicación.

## 3. Casos de uso priorizados

Evidencia de código revisada sobre HEAD `99a33d8`; revalidar antes de implementar.

1. **Pertinencia aditiva de lecciones.** `validate_lesson_capitalization.py` declara que no verifica pertinencia. La medición A5 del hermano documenta una búsqueda de «verificador mec» sin coincidencias sobre un corpus con verificadores expresados de otra forma. Es evidencia del límite de esa consulta, no medición del recall total de la capa fría. `triage_lesson_relevance.py` está diseñado pero todavía no existe. Ninguna fila anclada de un `00-` puede desaparecer.
2. **Lint semántico de contradicciones, deuda D6.** Requiere que el triaje entregue candidatos nuevos con aceptabilidad medida. Puede justificarse aunque el proveedor ganador sea DeepSeek; no depende lógicamente de adoptar Jev.
3. **Menciones hoteleras.** `LLMMentionChecker._parse_mentions` usa subcadena del nombre y regex de competidores. Un clasificador podría distinguir recomendación, mención y rechazo sobre respuestas ya obtenidas, sin sustituir las consultas de visibilidad. Fuera de este piloto: necesitaría muestra propia.
4. **Promesa frente a servicio del Tribunal.** `AlignmentReviewer` usa hints y coincidencias de palabras. Jev podría seleccionar entre candidatos, pero no reemplaza `LLMPromiseExtractor`, que devuelve citas/localizaciones libres. Habría que recuperar las citas desde fragmentos originales identificados. El parseo que transforma JSON inválido en lista vacía muestra un colapso de estados que el adaptador no debe repetir. Fuera del alcance actual.
5. **Priorización de contexto por fase.** Exploratorio: ordenar información opcional, nunca retirar reglas, lecturas contractuales o evidencia obligatoria. El documento de arquitectura propone ideas, no funcionalidades entregadas, y advierte del coste de recargar contexto.

Descartados: permisos/comandos, autorización de publicación y sustituir verificaciones exactas por clasificaciones probabilísticas.

## 4. Comparación y requisitos medibles

### DeepSeek: habilitado no significa instrumentado

El operador confirma DeepSeek como proveedor habilitado por defecto y Anthropic sin API. En el código actual, `DeepSeekProvider.chat_completion` extrae `choices[0].message.content` y devuelve solo texto; `AnthropicProvider.chat_completion` hace lo mismo con su contenido. `ProviderAdapter.unified_request` propaga ese retorno. `ProviderAdapter._initialize_provider` puede seleccionar otro proveedor disponible si el solicitado no tiene clave.

Por ello la comparación no debe usar el wrapper como fuente de usage ni su selección automática. El plan **no modifica ese módulo**: integra DeepSeek explícito detrás de la costura y conserva respuesta externa, modelo efectivo, usage y tiempos antes de reducirlos a una decisión. No exige habilitar Anthropic ni introduce un fallback hacia él.

El código usa `deepseek-chat` y `https://api.deepseek.com/v1/chat/completions`; son la referencia de integración existente, no una promesa de versión inmutable. Antes de inferir hay que verificar API, modelo y tarifa actuales de DeepSeek. Si no existe un pin estable, declarar el límite de reproducibilidad con fecha/modelo efectivo y fingerprint cuando esté disponible.

### Corpus y protocolo

- Objetivo inicial de 60–100 pares plan–lección: tamaño exploratorio, no cifra suficiente por definición. Etiqueta humana ciega a resultados, rúbrica pertinente/no pertinente/insuficiente e importancia separada.
- Separación ajuste/evaluación por plan, deduplicación y corte temporal. No enviar cierres posteriores ni metadatos que revelen qué lección se aceptó. La lección debía existir en el corte del plan para contar como omisión histórica.
- Mismos candidatos y contenido semántico en búsqueda fría, DeepSeek y Jev. Consultas/reglas de recuperación congeladas; clasificación no puede recuperar una lección que nunca recibió.
- SHA del original y del saneado; etiquetas separadas de los payloads. El índice puede recortar enunciados y no es automáticamente contexto suficiente. Revisión humana del saneamiento: un detector de patrones no garantiza ausencia de datos sensibles.
- Medir recuperación, clasificación y resultado extremo a extremo separadamente, con numerador/denominador, errores, abstenciones, intervalos y carga de revisión humana. No tratar pares del mismo plan como observaciones independientes sin declararlo.
- Acordar criterios de adopción/suficiencia antes de inferir. La muestra y el protocolo inicial se versionan antes de conectividad; ajuste solo en desarrollo y bajo presupuesto propio. Congelar umbrales/prompt finales antes de abrir evaluación, nunca calibrar sobre sus resultados.

### Dinero, errores y adopción

Distinguir tokens observados, coste calculado desde esos tokens y tarifa fechada, y cargo efectivamente facturado. No llamar «factura» al cálculo ni reportar como cero el usage desconocido tras un timeout. Incluir caché/categorías de DeepSeek si existen, intentos y gastos de conectividad/ajuste, no solo la evaluación final.

El presupuesto tiene límites finitos por proveedor/etapa: intentos, tokens, USD y tiempo. Se reserva una cota antes de enviar; el usage posterior por sí solo no limita el coste. Credencial/configuración presente no prueba autenticación ni saldo. Sin autorización literal con hashes/alcance, no hay llamadas.

Las cuatro decisiones son ACTIVAR, RECHAZAR, MUESTRA-INSUFICIENTE y COSTE-NO-PAGADO. Fallos operativos llevan estado de ejecución fallido y `decision = null`, no una quinta opinión sobre calidad. ACTIVAR recomienda adopción: no habilita un proveedor global ni autoriza escribir D7/D6.

## 5. Fuentes consultadas

Consultadas el 2026-09-21 salvo la fecha propia de la política; las páginas son documentación, no resultados del piloto.

- https://typesafe.ai/blog/introducing-system-one-models-and-jev — precio, formato y cautelas de benchmarks.
- https://docs.typesafe.ai/api — payload, respuesta, usage y errores.
- https://docs.typesafe.ai/models — IDs versionados, aliases, contexto, idioma y tasa.
- https://docs.typesafe.ai/primitives/noul y https://docs.typesafe.ai/confidence — probabilidad y confianza distintas.
- https://docs.typesafe.ai/introduction/quickstart y https://docs.typesafe.ai/sdk/python/ — instalación e interfaz.
- https://docs.typesafe.ai/sdk/python/api/clients/sync y https://docs.typesafe.ai/sdk/python/api/retries — transporte inyectable y política de reintentos.
- https://pypi.org/pypi/typesafe-sdk/json — versión y dependencias del SDK.
- https://typesafe.ai/ — tarifa pública de entrada.
- https://typesafe.ai/legal/privacy-policy, https://typesafe.ai/legal/terms y https://docs.typesafe.ai/legal — privacidad y ZDR enterprise.
- https://docs.google.com/document/d/1G61uUB0FifUnmmrPzFQojZ3KpczYKmXGpgEXDJ2l_Zg/preview — propuestas de arquitectura, no funciones entregadas.
- Repo: `scripts/validate_lesson_capitalization.py`, `scripts/build_lesson_index.py`, `scripts/validate_qmind_writeback.py`, `scripts/run_all_validations.py`, `modules/providers/llm_provider.py`, `modules/auditors/llm_mention_checker.py`, `modules/quality_gates/tribunal/`, y contratos de los planes hermanos.
- Operador, 2026-09-21: DeepSeek habilitado por defecto, Anthropic sin API. No se sustituye esa declaración por una inspección de secretos.
- QMind y fuentes locales: consultas literales y resultados en `00-lecciones-capitalizadas.md` del plan; sin write-back.

## 6. Revisión de viabilidad y correcciones de preparación

| Hallazgo de la auditoría | Ajuste incorporado al plan |
|---|---|
| README exigía B y §5 exigía B+C con todos los AC cerrados | A local independiente; B propia requiere costura y consumidor verificados offline; AC15 semántico parcial admitido |
| D7 se describía como si exigiera todos los AC de C | Se conserva su disparador original AC9 + consumidor y se explica el requisito técnico adicional de integración |
| Wrapper textual presentado como comparador listo con usage | DeepSeek explícito e instrumentado por la costura; Anthropic excluido; runtime de producción intacto |
| Límite de contexto declarado desconocido | Se incorpora lo publicado actualmente y se mantiene pendiente la cuota efectiva de la cuenta |
| Coste real confundido con un campo usage | Tres magnitudes separadas y límites antes de cada intento, con estados desconocidos visibles |
| Muestra y `--check` nombrados sin productor | A/B reciben checker/runner/tests concretos, con interfaces previstas y controles aún PENDIENTES |
| Falta de Paso 0 e índice vencido | Se incorpora Paso 0 posterior a la concepción, se consultan las fuentes y se regenera el índice; no se simula una fase ejecutada |
| Activación D6 ligada a victoria de Jev | Decisión independiente de aceptabilidad y novedad; transferencia al hermano exige permiso propio |

Medición previa al ajuste: Python 3.13.3; SDK/httpx2/tenacity no instalados; `decision_client.py`, `triage_lesson_relevance.py` y evidencia del piloto ausentes. El índice recalculado tenía 320 IDs definidos y 50 sin definición sobre 405 Markdown, 15 análisis y 37 contextos. El conteo es histórico y lo produce `scripts/build_lesson_index.py::build`; no se congela como tamaño futuro del corpus.

Ruta elegida: preparar offline y ejecutar después de B/C offline. Un piloto independiente sería técnicamente posible, pero duplicaría integración y cambiaría el alcance acordado. Mejorar solo la búsqueda fría no necesita API y se conserva como comparación, sin fingir que ya resuelve pertinencia. No se han medido ventajas numéricas entre estas alternativas.

## Lección durable: juicio, instrumentación y proveedor efectivo

Un verificador de propiedades exactas no mejora por añadir un clasificador probabilístico: red y errores de juicio no aportan información a una igualdad de sha. El modelo entra donde falta juicio, no donde falta un estado explícito o un writer.

Tampoco basta con que el proveedor esté habilitado o con que su SDK declare usage: el dato debe sobrevivir hasta el instrumento que compara. La habilitación de DeepSeek no convierte un wrapper que devuelve texto en un medidor de coste; y un fallback puede cambiar sin avisar el tratamiento experimental. Conservar proveedor/modelo efectivos, consumo observado y errores por petición es parte de la validez del experimento, no solo observabilidad.
