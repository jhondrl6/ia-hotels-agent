# FASE-A — Contrato de extracción con cuatro estados, cache versionada y recibo

**ID**: FASE-A (plan CURA-COSTURA-TRIBUNAL-2026-10-11)
**Objetivo**: reemplazar el contrato colapsado `extract_verbal_promises → list` por un contrato de cuatro estados (`OK_CON_PROMESAS` / `OK_SIN_PROMESAS` / `NO_EVALUABLE` / `FALLIDO`), versionar la clave de cache, y producir el recibo mínimo por extracción. Cura las causas raíz 1 y 2 (§10.4 del contexto) y los defectos 1-6 + N1-N4 + N9-N10.
**Dependencias**: ninguna (primera fase de implementación).
**Duración estimada**: 1 sesión.
**Complejidad**: ALTA — cambio de contrato compartido por Bot 2, Bot 4 y el Juez; decisión arquitectónica cross-module (DEC-A1).
**Skill**: `.agents/workflows/phased_project_executor.md` (workflow canónico).

## Contexto

La costura de juicio semántico del Tribunal (`LLMPromiseExtractor`, instanciada una sola vez por corrida y consumida por Bot 2 y Bot 4) tiene dos causas raíz medidas en el contexto del plan: (1) el tipo de retorno `list` colapsa cuatro estados — de ahí el envenenamiento cacheable de `.cache/tribunal/` con `[]` ilegibles, el acta que se ve sana, y la self-confidence sin consumidor; (2) cero versionado del contrato — de ahí la cache que sobrevive a cambios de prompt y la ausencia de recibo. Esta fase cura el productor del contrato y su cache; los consumidores se migran en FASE-B.

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| Preparación (Paso 0 + maestro + prompts) | ✅ Completada (2026-10-11) |

### Base Técnica Disponible

- Módulos: `modules/quality_gates/tribunal/llm_extractor.py` (símbolos: `VerbalPromise`, `PromiseExtractor`, `LLMPromiseExtractor`, `extract_verbal_promises`, `_compute_cache_key`, `_cache_path`, `_load_from_cache`, `_save_to_cache`, `_parse_response`, `_is_valid_promise`, `MockPromiseExtractor`, `EXTRACTION_PROMPT`), `modules/providers/llm_provider.py` (símbolos: `ProviderAdapter`, `chat_completion`, `get_provider_name`, `_initialize_provider`).
- Tests base: `tests/quality_gates/tribunal/` (suite del tribunal; tomar la cifra con el método canónico `grep -rE "^\s*def test_" tests --include=*.py` y el par pre/post de esta fase).
- Cache de producción: `.cache/tribunal/` con 3 entradas de formato viejo — quedan inertes bajo la clave versionada (sin migración).

### Lecciones capitalizadas aplicables a esta fase

| ID | Lección (una línea) | Qué cambia en ESTA fase |
|----|---------------------|-------------------------|
| L-T4A.3 | Cache SHA256 de extracciones LLM con `cache_dir=tmp_path` en tests | T3: todos los tests de cache inyectan `tmp_path` al constructor; la cache de producción `.cache/tribunal/` queda como decisión declarada |
| L-T4A.1 | PromiseExtractor runtime_checkable para isinstance en tests | T1: la firma nueva conserva `@runtime_checkable`, pero eso **solo** prueba presencia de métodos y **no** certifica el contrato — la evidencia son los tests por causa sobre el objeto devuelto (AC1) |
| L-T4A.2 | El parsing de respuestas LLM debe manejar bloques markdown con indentación variable; su «aplicación futura» publicada dice «considerar extraer a utilidad compartida si hay terceros consumidores» (Archives/TRIBUNAL-OFFLINE-2026-09-09) | T1: el mapeo de estados y el des-cercado de fences viven en una **utilidad compartida**, no dentro de `LLMPromiseExtractor` — este plan deja el contrato listo para una tercera implementación, que sería ese tercer consumidor |
| DA-T4A | PromiseExtractor es la única interfaz; LLM real vs mock intercambiables | T1: el contrato de cuatro estados se define en `PromiseExtractor` y `MockPromiseExtractor` se actualiza; no se añaden implementaciones |
| S-H13 | Clave de cache con id() de objeto es reciclable tras GC | T3: la clave es contenido+contrato, nunca identidad de objetos (AC4) |

## Tareas

### Tarea 1 — Contrato de cuatro estados (AC1, AC6, AC7)

**Objetivo**: `PromiseExtractor` deja de colapsar cuatro estados en `list`.

**Archivos afectados**:
- `modules/quality_gates/tribunal/llm_extractor.py`
- `tests/quality_gates/tribunal/` (tests del extractor)

**Criterios de aceptación**:
- [ ] Nuevo tipo de resultado (dataclass) con estados `OK_CON_PROMESAS` / `OK_SIN_PROMESAS` / `NO_EVALUABLE` (respuesta ilegible) / `FALLIDO` (proveedor falló), con el motivo legible en el resultado. En artefactos publicados, el literal de la casa es `NO-EVALUABLE`. La **API checked** que lo devuelve lleva nombre nuevo (`extract_checked`), de modo que AC1 se enuncia sobre ella y no sobre el wrapper.
- [ ] `_parse_response` distingue las tres vías al no-OK hoy mapeadas a `[]`: JSON inválido, forma incorrecta (respuesta decodificada que no es lista), y prosa antes del JSON. Ninguna devuelve `[]` como si fuera «sin promesas».
- [ ] El mapeo de estados y el des-cercado de fences Markdown se extraen a una **utilidad compartida** dentro del módulo (L-T4A.2, con terceros consumidores declarados en DEC-A1): `LLMPromiseExtractor` los consume, no los contiene.
- [ ] `PromiseExtractor` conserva `@runtime_checkable`; `MockPromiseExtractor` implementa el contrato nuevo. **`@runtime_checkable` no es la evidencia del contrato**: solo comprueba presencia de métodos. La evidencia son los tests por causa sobre el objeto devuelto.
- [ ] El prompt deja de pedir self-confidence y el DTO `VerbalPromise` pierde el campo muerto (defecto 1 + N3): `grep -c confidence` sobre `EXTRACTION_PROMPT` y el DTO devuelve 0 tras el cambio.
- [ ] `EXTRACTION_PROMPT` delimita el texto de la propuesta como dato no-confiable (defecto 5): la instrucción prohíbe seguir instrucciones del contenido, y el test de forma verifica que el prompt compuesto contiene los delimitadores y la propuesta solo dentro de ellos.
- [ ] **DEC-A1**: la API nueva convive con `extract_verbal_promises` como wrapper transicional DEPRECADO que mapea no-OK → `[]` **sin cachear** el estado no-OK (con comentario de una línea que apunte a su eliminación en FASE-B). FASE-B lo elimina.

### Tarea 2 — Truncamiento detectado (AC3, cura N1)

**Objetivo**: una respuesta cortada deja de llegar como JSON inválido silencioso.

**Archivos afectados**:
- `modules/providers/llm_provider.py`
- `modules/quality_gates/tribunal/llm_extractor.py`

**Criterios de aceptación**:
- [ ] La capa de proveedor expone `finish_reason` de la respuesta (hoy ninguna ruta lo inspecciona).
- [ ] Respuesta con truncamiento (finish_reason de longitud) produce estado `NO_EVALUABLE` con motivo «respuesta truncada», nunca una lista parcial.
- [ ] Test con respuesta cortada sintética que antes producía `[]` envenenada.
- [ ] El techo `max_tokens=2000` del extractor sale de esta fase con **decisión registrada**: se sube con la medida que lo justifique, o se pide salida compacta al proveedor, o se mantiene con el riesgo declarado y su dueño. Motivo medido (AC14): las propuestas reales van de 13.334 a 14.690 caracteres, así que sin decisión la corrida única tiende a `NO_EVALUABLE` y el camino OK de la cura nunca se ejercitaría. La decisión se escribe en `10-analisis` (Decisiones Arquitectónicas o Seguimientos), no en un comentario del código.

### Tarea 3 — Cache versionada y sin envenenamiento (AC2, AC4)

**Objetivo**: la cache deja de sobrevivir a cambios de contrato y de dejar de cachear fallos.

**Archivos afectados**:
- `modules/quality_gates/tribunal/llm_extractor.py`

**Criterios de aceptación**:
- [ ] `_compute_cache_key` = `VERSION_PROMPT` (constante `VERSION_PROMPT` del módulo, bump en cada cambio semántico del prompt) + sha256 del **prompt compuesto** + sha256 del texto + **proveedor configurado** resuelto por **lectura pura de configuración sin construir cliente**: `LLM_PROVIDER` si está declarada; si no `deepseek` si hay `DEEPSEEK_API_KEY`, `anthropic` si hay `ANTHROPIC_API_KEY`, `sin-credencial` si ninguna — **nunca el literal `auto`**, que `_initialize_provider` resuelve a dos proveedores servidos distintos según qué clave exista (medido el 2026-10-11: `.env` declara `LLM_PROVIDER` y trae solo `DEEPSEEK_API_KEY`). El **modelo NO entra en la clave** — el extractor no puede conocerlo antes de llamar; entra en el recibo (AC5, AC4).
- [ ] `_save_to_cache` rechaza estados no-OK; `_load_from_cache` solo devuelve entradas OK. **Mutation check**: revertir el guard → los tests de envenenamiento quedan rojos → reactivar → verdes; las DOS salidas se guardan en `evidence/FASE-A/`.
- [ ] Escritura atómica del artefacto de cache (cura N10) y sin techo de crecimiento declarado como seguimiento (no feature nueva).
- [ ] El default de `cache_dir` queda **anclado a la raíz del repo**, no al CWD del proceso. Motivo medido: el constructor hace `cache_dir or Path(".cache/tribunal")` — ruta relativa, así que un run lanzado desde otro directorio lee y escribe **otra** cache (y con ella, otros recibos). Si se decide no anclarlo, el residuo se registra como seguimiento con dueño; ninguna de las dos salidas es «no declarado».
- [ ] Prompt distinto → clave distinta (test N4: si Bot 4 recibiera prompt propio mañana, no le sirven respuestas de Bot 2). **Este test es el que demuestra que una constante de módulo no basta**: con solo `VERSION_PROMPT`, dos prompts distintos de la misma versión casan la misma clave.
- [ ] Test de que **un hit de cache no construye proveedor**: la ruta del hit corre **sin credencial** en el entorno y no levanta `ProviderAdapter()`. Medido: hoy ningún test de `test_llm_extractor.py` ejercita la rama `self.provider is None`, que solo en miss construye el adapter — y ese constructor lee `SecureConfigManager`, imprime `[INFO] Using…` y **lanza `ValueError` sin credencial**.
- [ ] Sin migración: las entradas viejas quedan inalcanzables (declarado en maestro §4).

### Tarea 4 — Recibo mínimo (AC5, curan defectos 4, 6 y N9)

**Objetivo**: cada extracción deja un recibo reproducible y atribuible.

**Archivos afectados**:
- `modules/quality_gates/tribunal/llm_extractor.py`
- `modules/providers/llm_provider.py`

**Criterios de aceptación**:
- [ ] Recibo JSON por extracción (junto a la cache o en su propio directorio bajo `cache_dir`) con: digest del texto, digest del **prompt compuesto**, `VERSION_PROMPT`, proveedor servido (via `get_provider_name()` — el dato está a un método de distancia; el extractor deja de descartarlo), modelo **pedido** y modelo **firmado** por el servicio cuando difieran, latencia, usage cuando el proveedor lo dé, digest de la respuesta cruda, estado resultante y motivo si es no-OK. Medido en esta casa: DeepSeek **firma `deepseek-flash`** cuando se le pide `deepseek-chat` (etiqueta de serving), por eso los dos campos van separados.
- [ ] `llm_provider` deja de descartar el `usage` antes de que el extractor pueda verlo, **por vía aditiva** (DEC-A3): `chat_completion_detailed` o metadatos en el adapter, **sin cambiar el tipo de retorno de `chat_completion`**. Medido: 6 sitios de producción delegan en él fuera del tribunal (`gap_analyzer`, `ia_tester`, `content_gen`, `faq_gen`, `seo_accelerator_pro` dos veces) y 1 solo archivo de test ejercita la ruta.
- [ ] Un estado no-OK **no se cachea pero sí deja recibo** (el recibo registra el fallo, la cache no lo envenena).
- [ ] Tabla de claves del recibo publicada en `evidence/FASE-A/recibo-claves.md` (R2.4: dónde lo lee un humano).

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| Tres estados no-OK, uno por causa (R2.9) | `tests/quality_gates/tribunal/` | JSON inválido / forma incorrecta / prosa antes del JSON producen `NO_EVALUABLE` distinguible, no `[]` |
| Truncamiento | ídem | finish_reason length → `NO_EVALUABLE` |
| Cache no-OK + mutation check | ídem | con guard → no persiste; sin guard → rojo (ambas salidas en `evidence/FASE-A/`) |
| Clave versionada + N4 | ídem | `VERSION_PROMPT`, sha del prompt compuesto, sha del texto y proveedor configurado cambian la clave; prompt distinto → clave distinta; el modelo **no** entra |
| Hit de cache sin proveedor | ídem | el hit corre en entorno **sin credencial** y no construye `ProviderAdapter` (rama hoy no ejercitada por ningún test) |
| Recibo | ídem | claves del recibo presentes y serializadas (test lee el JSON del writer real, no el objeto en memoria) |
| Forma del prompt compuesto | ídem | delimitadores presentes, propuesta solo dentro |

**Comando de validación**:
```bash
./venv/Scripts/python.exe -m pytest tests/quality_gates/tribunal/ -v
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** — ver template §5. Al cerrar:

1. `dependencias-fases.md`: marcar FASE-A ✅ con fecha y notas.
2. README del plan: tabla de progreso; métricas por **referencia** a `09` §D.
3. `09-documentacion-post-proyecto.md`: secciones A/B/D/E con los datos de esta fase (aquí vive el número).
4. `10-analisis-post-implementacion.md`: fila de Resumen de Ejecución + lecciones (o «sin lecciones nuevas») + seguimientos (techo de cache sin dueño si aplica).
5. `00-lecciones-capitalizadas.md` §2: anotar qué pasó realmente en la columna «Qué cambia».
6. `evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-A/`: pares `*_baseline_pre/post.txt` (R2.3, con la suma y la resta publicadas), mutantes y par rojo/verde de AC2, `recibo-claves.md`.
7. **Registro de fase** (la fase se registra a sí misma, §2.5 del executor):
   ```bash
   ./venv/Scripts/python.exe scripts/log_phase_completion.py \
       --fase FASE-A --fecha <FECHA_DE_CIERRE_DE_ESTA_FASE> \
       --desc "Contrato 4 estados + cache versionada + recibo en LLMPromiseExtractor" \
       --archivos-mod "modules/quality_gates/tribunal/llm_extractor.py,modules/providers/llm_provider.py" \
       --tests <TESTS_NUEVOS_DE_ESTA_FASE> --check-manual-docs
   ```
8. DOMAIN_PRIMER: `./venv/Scripts/python.exe scripts/doctor.py --regenerate-domain-primer` (fase de implementación).
9. Pregunta de aporte durable de cualquier `CONTEXT-*.md` escrito en la sesión (criterio del Cierre Obligatorio).

## Criterios de Completitud (CHECKLIST)

⚠️ **Verificar ANTES de marcar como ✅ COMPLETADA** — ver template §6. Resumen:

- [ ] AC2..7 legibles en sus artefactos (no solo «el string está en el código») + **AC1 en su forma checked**: su cierre se certifica en FASE-B junto con AC15, porque DEC-A1 deja el wrapper devolviendo `[]` hasta entonces
- [ ] Mutation check de AC2 con par rojo/verde en `evidence/FASE-A/`
- [ ] Delta R2.3 verificado restando (`suma_post − suma_pre == tests_nuevos`); resta 0 con tests nuevos = baseline contaminado = fase no cierra
- [ ] `run_all_validations.py --quick` pasa (el número lo imprime la corrida)
- [ ] `log_phase_completion.py` ejecutado; REGISTRY con la entrada
- [ ] Cinco cortes declarados; sin commit (el commit requiere autorización del operador y pathspec)
- [ ] Post-ejecución 1-9 completa

## Restricciones

- **Presupuesto (R2.1)**: ~55 tool calls; instrumento: auto-reporte en unidad `tool calls`; corte: **hasta listo para revisión** (este prompt NO autoriza commit). Si la corrida excede el presupuesto, marcar ⏳ INCOMPLETA con checkpoint.
- **No tocar** en esta fase: `alignment_reviewer.py`, `honesty_reviewer.py`, `judge.py`, `outcome.py`, `main.py` (consumidores = FASE-B; Juez = FASE-C). El wrapper transicional de DEC-A1 es la única costura entre ambos.
- Citas por símbolo, nunca `archivo:línea` (R2.2).
- `git commit` prohibido sin autorización explícita; si algún día hay commit, **con pathspec** (trabajo ajeno staged en el índice).
- Rojo deliberado de mutation check = prueba que se conserva y atribuye, no error que se lima.

## Prompt de Ejecución

```
Actúa como agente de implementación del plan CURA-COSTURA-TRIBUNAL-2026-10-11.

Ejecuta únicamente FASE-A del plan .opencode/plans/Archives/CURA-COSTURA-TRIBUNAL-2026-10-11/
Lee 01-plan-maestro.md (§1 tabla de ACs y §4 restricciones), 00-lecciones-capitalizadas.md (§2 y §4), dependencias-fases.md, ../../context/CONTEXT-JEV-COSTURA-V4COMPLETE-2026-10-10.md (§3 defectos, §10.2 hallazgos N y §10.4 causas raíz) y el workflow canónico.

OBJETIVO: Contrato de extracción con cuatro estados (OK_CON_PROMESAS / OK_SIN_PROMESAS / NO_EVALUABLE / FALLIDO), cache con clave versionada que nunca persista no-OK, y recibo mínimo por extracción.

CONTEXTO:
- Fases previas completadas: Preparación
- Base técnica: llm_extractor.py y llm_provider.py (símbolos en este prompt), tests del tribunal en tests/quality_gates/tribunal/
- No delegates a subagente: decisión arquitectónica cross-module (DEC-A1)

TAREAS:
1. T1 Contrato de cuatro estados en la API checked + utilidad compartida del parsing (L-T4A.2) + fin de self-confidence + frontera de contenido (AC1/6/7, DEC-A1)
2. T2 Truncamiento: finish_reason expuesto, respuesta cortada → NO_EVALUABLE (AC3)
3. T3 Cache versionada (prompt compuesto + proveedor configurado, modelo fuera), nunca cachear no-OK, escritura atómica, hit sin construir proveedor (AC2/4, mutation check)
4. T4 Recibo JSON con proveedor servido, modelo pedido y firmado, usage y digest de respuesta cruda, por vía aditiva en el proveedor (AC5, DEC-A3)

CRITERIOS:
- AC2..7 legibles en sus artefactos + AC1 en su forma checked (cierre en FASE-B con AC15); tests por causa (R2.9); tmp_path en cache de tests
- Delta R2.3 con pares pre/post en evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-A/

VALIDACIONES:
- pytest tests/quality_gates/tribunal/ -v
- run_all_validations.py --quick
- log_phase_completion.py --fase FASE-A --fecha <fecha de cierre> (la fase se registra a sí misma)
```
