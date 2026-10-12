# Recibo de extracción — tabla de claves (AC5, R2.4)

**Quién lo escribe**: `LLMPromiseExtractor._write_receipt` en
`modules/quality_gates/tribunal/llm_extractor.py`.

**Dónde vive un humano**: un archivo JSON por extracción bajo
`<cache_dir>/recibos/<cache_key[:16]>-<origen>-<secuencia>.json`. En producción
`cache_dir` es `.cache/tribunal/` (directorio **gitignored**, `.gitignore:47`), así que el recibo
no viaja con el ZIP: es el rastro del corredor, no del cliente. La copia de ejemplo versionada es
`evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-A/recibo-ejemplo.json`, escrita por el mismo writer
con un proveedor de muestra (cero red, cero gasto).

| Clave | Qué registra | Productor |
|-------|--------------|-----------|
| `generado` | Timestamp UTC `YYYY-MM-DDThh:mm:ssZ` | `_write_receipt` |
| `origen` | `llamada` (respondió el proveedor) o `cache` (se sirvió del artefacto versionado) | `_write_receipt` |
| `cache_key` | Clave versionada con la que se indexó la entrada | `_compute_cache_key` |
| `digest_texto` | sha256 del texto de la propuesta tal como entró | `_write_receipt` |
| `digest_prompt_compuesto` | sha256 del prompt ya con los delimitadores y el dato neutralizado | `_write_receipt` |
| `version_prompt` | `VERSION_PROMPT` del módulo; la bumps quien cambia el prompt en sentido semántico | constante de módulo |
| `proveedor_configurado` | `deepseek` / `anthropic` / el valor declarado de `LLM_PROVIDER` / `sin-credencial` — **nunca `auto`** | `configured_provider()` |
| `proveedor_servido` | Nombre real del proveedor del cliente (`get_provider_name()`); `null` en un hit de cache | `_nombre_proveedor_inyectado` |
| `modelo_pedido` | Modelo que se le pasó al servicio (default resuelto por el proveedor) | `ChatCompletionDetail.model_requested` |
| `modelo_firmado` | Modelo que **firmó** el servicio. Medido en esta casa: DeepSeek firma `deepseek-flash` cuando se le pide `deepseek-chat`, por eso van en claves separadas | `ChatCompletionDetail.model_served` |
| `finish_reason` | Razón de cierre del servicio (`stop`, `length`, `max_tokens`, `null` si el proveedor no la reporta) | `ChatCompletionDetail.finish_reason` |
| `latencia_ms` | Milisegundos de la llamada (no la mide un hit de cache) | `extract_checked` |
| `usage` | Tokens reportados, o `null` si el proveedor no los da | `_usage_a_dict` |
| `digest_respuesta_cruda` | sha256 del texto crudo del LLM, antes de parsear | `_write_receipt` |
| `estado` | `OK_CON_PROMESAS` / `OK_SIN_PROMESAS` / `NO-EVALUABLE` / `FALLIDO` — el literal de la casa para el ilegible es `NO-EVALUABLE` | `ExtractionOutcome.estado_publicado` |
| `motivo` | Cadena legible de la causa, obligatoria en los dos estados no-OK | `llm_extractor.RAZON_*` |
| `num_promesas` | Promesas del resultado | `_write_receipt` |

**Regla que gobierna el artefacto**: un estado no-OK **deja recibo y no deja entrada de cache**
(AC2 + AC5). El recibo es el único lugar donde el fallo de una extracción es legible después de la
corrida; la cache nunca guarda un `NO-EVALUABLE` ni un `FALLIDO`.

**Lo que este archivo no puede sostener**: que el recibo de la corrida única de Don Alfonso exista.
Eso lo certifica FASE-E2E (AC14) leyendo `evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-E2E/`;
aquí solo se certifica que el writer produce el JSON con estas claves.
