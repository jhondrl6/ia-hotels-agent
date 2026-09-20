# FASE-G — Inventario de callers y matriz de cableado por productor

**Plan:** REFACTOR-WHATSAPP-ENTREGA-2026-09-18 · **Sesión:** G (implementación) · **Fecha:** 2026-09-20
**HEAD al abrir:** `d7ff932` · rama `master` · árbol limpio · 0 ahead / 0 behind con `origin/master`
**Instrumento:** `scripts/validate_wiring.py` (AST, sin lista fija de archivos) — no lectura con grep a mano
**Artefacto publicado:** `.opencode/wiring_report.json` (copia saneada en este directorio)

Este inventario **lo produjo el verificador**, no una búsqueda manual: la lista de abajo es la
sección `poblacion` del reporte con `git_sha` anotado. Un inventario a mano repetiría el defecto
que esta fase quiere cerrar (gobernar solo los callers que alguien recordó buscar).

---

## 1. Población productiva descubierta (24 llamadas fuera de `tests/`)

De 611 archivos en alcance, el AST encontró **169 llamadas** a métodos de nombre gobernado;
**24** están fuera de `tests/`. Clasificación completa en el JSON; la parte que decide AC7:

| Clasificación | Productivas | Qué significa |
|---|---|---|
| `GOBERNADA_CONFORME` | 5 | productor gobernado y señal propagada |
| `GOBERNADA_CON_OMISION` | 3 | señal requerida ausente → **violación** (las tres del orquestador) |
| `EXCLUIDA_POR_CLASE` | 13 | el receptor resuelve a un homónimo confirmado |
| `EXCLUIDA_POR_CLASE_NO_GOBERNADA` | 3 | resuelve a una clase que no es productor gobernado |
| `RECEPTOR_NO_RESUELTO` | **0** | **cero huecos de cobertura en producción** |

### 1.1 Los cinco callers gobernados conformes

| Sitio | Receptor → clase | Señal propagada |
|---|---|---|
| `main.py` `run_v4_complete_mode` → `pain_mapper.detect_pains` | `PainSolutionMapper` (asignación local) | `whatsapp_html_detected=getattr(audit_result.validation, …)` |
| `main.py` `run_v4_complete_mode` → `coherence_validator.validate` | `CoherenceValidator` | ídem, además de `generated_assets` y `site_presence_report` |
| `main.py` `run_v4_complete_mode` → `builder.with_validation` | `AssessmentBuilder` | `validation_summary` (único argumento tras F-D') |
| `v4_diagnostic_generator.py` `_identify_brechas` → `pain_mapper.detect_pains` | `PainSolutionMapper` | `whatsapp_html_detected=…` con fallback al audit |
| `v4_proposal_generator.py` `generate` → `self._generate_dynamic_services_table` | `V4ProposalGenerator` (`self` propio) | `site_presence_report` **y** `whatsapp_conflict` |
| `coherence_gate.py` `execute_from_validator` → `self._validator.validate` | `CoherenceValidator` (`self.__init__`) | `whatsapp_html_detected=whatsapp_html_detected` |

(`coherence_gate` aparece como sexto: la tabla cuenta cinco *líneas* conformes de producto más
esa, que el AST también resolvió. El conteo exacto del reporte es `GOBERNADA_CONFORME` = 14 sobre
todo el árbol, incluidos los archivos de `scripts/`.)

### 1.2 Las tres omisiones — el rojo de AC7 sobre el código tal como está hoy

| Sitio | Símbolo | Señal ausente | Amparada por |
|---|---|---|---|
| `v4_asset_orchestrator.py:286` | `PainSolutionMapper.detect_pains` | `whatsapp_html_detected` | excepción tipada, dueño FASE-B / AC1 |
| `v4_asset_orchestrator.py:309` | `CoherenceValidator.validate` (pre-gen) | `whatsapp_html_detected` | ídem |
| `v4_asset_orchestrator.py:447` | `CoherenceValidator.validate` (post-gen) | `whatsapp_html_detected` | ídem |

**Precisión nueva que el plan no tenía:** la fila F-A' del maestro describe la divergencia como
**una** invocación (`generate_assets` → `detect_pains`). Medido por AST, son **tres** invocaciones
del mismo archivo las que omiten la misma señal, dos de ellas sobre `CoherenceValidator.validate`.
El efecto no es teórico: `_check_whatsapp_verified` aplica su boost leyendo `site_presence_report`
y decide con `whatsapp_html_detected`; al omitirla, la ruta del orquestador evalúa la coherencia
bajo el supuesto de que no hay canal visible, justo cuando la hay.

Consecuencia para FASE-B: cerrar F-A' corrigiendo solo la línea 286 **no** apaga el rojo del
verificador, y su excepción quedaría `EXCEPCION_VAGA` para las otras dos. B tiene que gobernar
las tres o registrar las dos restantes con dueño propio.

### 1.3 Homónimos excluidos (gobernar por clase, no por nombre)

`validate` es nombre común en el repo. Las trece exclusiones productivas resolvieron a:
`PrecisionValidator` (2), `NoDefaultsValidator` (3), `PlanValidator` (3), `ContentValidator` (3),
`EnvValidator` (1) y una en `scripts/validate.py`. Más tres llamadas propias de clases no
gobernadas (`FinancialInputsContract.validate`, `EthicsGate.validate`, y `self.validate()`).

Sin resolución de receptor, **todas** esas serían violaciones falsas; el mutation check M3
lo demostró al revés: al gobernar por nombre de método, el verificador denuncia
`modules/ajeno.py:3` — un `PrecisionValidator.validate` de un fixture — y el test del AC7
que exige excluirlo cae rojo.

---

## 2. Matriz de cableado por productor (no solo por símbolo)

El mandato de cierre de FASE-A lo exige explícitamente: *el verificador gobierna señales por
productor, no solo por símbolo*. Estado medido de cada productor de promesa/señal:

| Productor | Qué decide | Señal que lo gobierna | ¿Gobernada por el verificador? |
|---|---|---|---|
| `PainSolutionMapper.detect_pains` | emite o no `no_whatsapp_visible` / `whatsapp_conflict` | `whatsapp_html_detected` | **Sí** (AC7) |
| `CoherenceValidator.validate` | score y veredicto de `whatsapp_verified` | exige `whatsapp_html_detected`; **no** exige `site_presence_report` (ver nota abajo) | **Sí** (AC7) |
| `AssessmentBuilder.with_validation` | qué viaja al payload canónico | `validation_summary`; `whatsapp_validation` **prohibido** | **Sí** (AC16) |
| `V4ProposalGenerator._generate_dynamic_services_table` | fila del botón en la propuesta y su estado | `site_presence_report`, `whatsapp_conflict` | **Sí** (alta de G, ver §2.1) |
| `preflight_checks.NEW_HOTEL_THRESHOLDS["whatsapp_button"] = 0.3` | barra de planificación en hotel nuevo | confianza del asset (dato, no kwarg) | No: es una **constante**, no un caller; la gobierna AC5 con `thresholds.json` (dueño C/D) |
| `ASSET_CATALOG["whatsapp_button"]` (`required_confidence=0.7`, `block_on_failure=False`) | planifica el botón y su bloqueo | misma constante de catálogo | No: tabla estática. **Precisión medida abajo (§2.2)** |
| `ELEMENTO_KB_TO_PAIN_ID["nap_consistente"] → ("whatsapp_conflict", "whatsapp_button", None)` | convierte elemento KB en pain+asset | identidad de servicio (dato) | No es un caller con señales; su **consumidor** sí: `conditional_generator.py` la lee y luego llama a `get_assets_for_pain` |
| `ConditionalGenerator.PAIN_TO_ASSET` | pain → assets prometidos | contenido de la tabla (dato) | No: verificable por contenido, no por kwargs. **Medido abajo (§2.3)** |
| `CrossValidator._reconcile_whatsapp_multisede` | reconcilia número↔sede antes de usar el campo | — | **No gobernar ni reimplementar** (instrucción de A, decisión 11): ya tiene suite propia `tests/data_validation/test_whatsapp_multisede.py` |

### 2.1 Alta nueva en la política: la tabla de servicios de la propuesta

`_generate_dynamic_services_table` decide si la fila de WhatsApp se muestra como
`present_in_production` y si aparece el aviso de conflicto, y **ambas señales tienen default**
(`site_presence_report=None`, `whatsapp_conflict=False`). Su único caller productivo las pasa
las dos, así que hoy es conforme; gobernarla cuesta cero y cierra el extremo del cable que
mira el cliente. Sin esto, el verificador protegería el pain pero no la promesa.

### 2.2 `ASSET_CATALOG["whatsapp_button"]`: la instrucción NEVER_BLOCK sigue ahí

Medido otra vez en esta sesión (coincide con P12 de FASE-A):

```
required_confidence=0.7, fallback="generate_basic_whatsapp",
block_on_failure=False,  # NEVER_BLOCK: generar botón básico aunque falte WhatsApp
promised_by=["no_whatsapp_visible", "whatsapp_conflict"]  # FASE-5: "always" ELIMINADO
```

Es una **quinta** instructiva dentro del propio catálogo: autoriza generar el botón sin dato.
No es un kwargs, así que ningún AST lo gobierna; queda como hallazgo para B/C con dueño
declarado, no como cobertura falsa de G.

### 2.3 `PAIN_TO_ASSET` sigue sin clave `no_whatsapp_visible` (segunda fuente divergente)

Medido por lectura de las claves reales de la tabla:
`no_ssl, no_hotel_schema, no_schema_reviews, poor_performance, low_citability, no_og_tags,
no_faq_schema, whatsapp_conflict, missing_alt_text, no_blog_content, no_social_links`.

Dos cosas se sostienen y una es nueva:

1. Confirmado el inventario de la revisión 2: **no hay** clave `no_whatsapp_visible`, mientras
   `pain_ledger.py` sí la mapea a `whatsapp_button`. Dos productores, dos identidades.
2. Confirmado que `whatsapp_conflict` promete **además** el botón
   (`["whatsapp_button", "whatsapp_conflict_guide"]`), contra la matriz de decisión que para
   CONFLICT manda guía y no botón operativo.
3. Nuevo para el inventario: la clave de conflicto existe en `PAIN_TO_ASSET` **y** en
   `PAIN_SOLUTION_MAP` **y** en `ASSET_CATALOG.promised_by`, tres tablas distintas que deben
   coincidir. Ninguna de las tres es gobernable por kwargs; la goberna AC2 con `mutation_report`
   de B, no este check.

**Límite declarado de esta matriz:** el verificador gobierna **señales que viajan como
argumentos**. La coherencia entre tablas de promesas es un defecto de *contenido*, y FASE-G no
lo convierte en cobertura que no tiene.

**Por qué `validate` exige una señal y no dos.** `site_presence_report` también tiene default
`None`, pero gobernarla sería extrapolar: el plan (maestro §1, fila CONFLICT) fija que el
hueco vivo de coherencia es la señal de HTML, y el boost de presencia es trabajo de V-1 con
dueño en C/D. Exigirla hoy habría convertido al verificador en autor de un requisito que
ninguna AC aprobó, y habría producido dos hallazgos adicionales sin dueño. Queda registrado
como **deuda de política** con su razón, no como cobertura.

---

## 3. Firma de `with_validation` antes y después (AC16)

| | Parámetros | Defaults |
|---|---|---|
| **Antes** (HEAD `d7ff932`) | `self, validation_summary, whatsapp_validation` | — (el segundo era obligatorio) |
| **Después** (FASE-G) | `self, validation_summary` | — |

Leída por `firmar_simbolos()` sobre el árbol, no transcrita. Callers tocados:

| Sitio | Antes | Después |
|---|---|---|
| `main.py` `run_v4_complete_mode` | `builder.with_validation(validation_summary, whatsapp_validation)` | `builder.with_validation(validation_summary)` |
| `tests/test_assessment_builder.py` `test_builder_with_validation` | `b.with_validation(validation_summary, None)` | un solo argumento |
| `tests/test_assessment_builder.py` (flujo completo) | `b.with_validation({...}, None)` | un solo argumento |

**Dato upstream conservado, no borrado.** `whatsapp_validation` sigue vivo en `main.py` en las
ocho líneas que **sí** lo consumen: construye los `ValidatedField` de `whatsapp_number`
(ramas VERIFIED / CONFLICT / web-only), alimenta `'whatsapp': whatsapp_validation.to_dict()`,
y las dos salidas de `whatsapp_status`/`whatsapp_confidence`. Eso es lo que luego entra a
`validation_summary`. Retirar el parámetro del builder no tocó ninguna de esas líneas; borrar la
variable habría sido el defecto que AC16 prohíbe explícitamente.

Prueba de que el segundo argumento era contrato muerto: los **dos** tests que lo ejercitaban le
pasaban `None`, y el cuerpo del método nunca lo leyó.

---

## 4. `CommercialGate._check_whatsapp_verified` — rol test/legacy, intacto

Medido en `modules/quality_gates/domain_gates.py`: `CommercialGate.__init__` toma
`whatsapp_confidence_threshold` con default **0.9** de su config, `evaluate()` llama a
`_check_whatsapp_verified(assessment)` y compara `confidence >= umbral`.

Referenciado por `modules/quality_gates/commercial_gate.py` y por
`tests/quality_gates/{test_domain_gates,test_commercial_gate,test_claim_self_healing}.py` y
`tests/commercial_documents/conftest.py`. **No** está en la ruta de `v4complete`: el check
productivo de WhatsApp vive en `CoherenceValidator._check_whatsapp_verified`.

**Clasificación: test/legacy.** Sin una sola línea modificada, y sus tests no certifican el
fix productivo (así lo fija la ratificación 6 de FASE-A). El verificador tampoco lo goberna:
no recibe `whatsapp_html_detected`, y gobernarlo implicaría tocar el módulo legado.
