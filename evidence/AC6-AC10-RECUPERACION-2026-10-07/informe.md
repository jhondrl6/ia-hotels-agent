# Recuperación AC6 y AC10 — REFACTOR-WHATSAPP-ENTREGA-2026-09-18

**Fecha:** 2026-10-07 · **Régimen:** offline (tests, mutantes y writer real en harness)
**Corridas `v4complete` ejecutadas en esta sesión:** 0. El contador del contrato
(`04-contrato-ejecucion.md` §Corrida única) sigue en **1/1 consumido**, acreditado
por `evidence/…/FASE-E2E/run_control.json`, no por narración.

**Dictamen:** AC6 = `SUPERADO_OFFLINE`, AC10 = `SUPERADO_OFFLINE`. Ninguno asciende
a SUPERADO EN E2E (L-VUP-17). El producto deja de producir ambos defectos; **el ZIP
entregado el 2026-10-07 precede a esta corrección y conserva los dos defectos: no
está ejercitado por ninguna corrida y no se reescribió** (árbol certificado intocable).

---

## 1. Premisas re-medidas antes de editar

Ninguna se heredó de la lectura del mandato: todas se volvieron a medir en disco.

| Premisa | Medición | Coincide con la certificación |
|---|---|---|
| `LocalContentGenerator._conclusion` | `modules/asset_generation/local_content_generator.py:530` construía `https://wa.me/{phone_clean}` desde `hotel_data.get("phone")` | sí (citada :528-530) |
| `._build_internal_links` | `:559`, misma construcción | sí (citada :557-559) |
| Miembro certificado afectado | `contenido_local__20261007_093402.md`: **5** líneas `wa.me` en 73, 147, 221, 295, 369 con `wa.me/6063146139` | sí, número y líneas exactas |
| Evidencia del canal real | `audit_report_20261007_093348.json`: `whatsapp_status='estimated'`, `phone_web=null`, `whatsapp_href_number=null`; `site_presence_snapshot.json → whatsapp_button.presence_evidence_kind='plugin_fingerprint'` | sí |
| `CORE_TO_GEO_MAP` | `asset_responsibility_contract.py:94-98` casa 3 nombres canónicos; `get_implementation_order` comparaba por igualdad exacta | sí |
| `IMPLEMENTATION_ORDER.md` del ZIP | 2.586 chars, **0** cabeceras `### N.`, 13 rutas solo bajo ADICIONALES | sí |
| Población de nombres | `main.py:3380-3389` deriva `core_assets` de `Path(a.path).name` → basenames con `ESTIMATED_` y marca de tiempo; el reporte de la corrida trae **13** | sí (V-3) |
| Bloque CONTACTO | `propuesta_v6_template.md:253` publicaba `WhatsApp: ${hotel_phone}` con `gbp.phone` (`v4_proposal_generator.py:750-754`, clave de contexto `:1005`) | sí (V-5) |
| Número de la agencia en `config/` | **no existe**: ninguna clave de contacto en `config/*.yaml` (medido con grep sobre `config/`) | aplica la rama «en su defecto» del criterio 4 |
| `implementation_order_check` | `{status: 'OK', source: 'zip'}`: registraba fuente; `_is_template_stub` contaba contenido de OTRA sección y no lo declaraba stub | sí (V-2) |

Sin divergencias: ningún símbolo había cambiado desde la certificación.

## 2. AC6 — el destino solo sale del canal

**El guard vive en el contrato** (`modules/data_validation/whatsapp_contract.py`),
no en una lista propia del generador: `destino_whatsapp_verificado(canal, numero_en_uso)`
exige (a) `presence_evidence_kind == EVIDENCE_WA_ME_HREF`, (b) `whatsapp_status ==
ConfidenceLevel.VERIFIED.value` y (c) número del href utilizable por
`normalizar_numero_whatsapp`; si se informa un número en uso, debe normalizar al
mismo destino. Cualquier otro caso devuelve `None` y no hay enlace.

Cambios:

- `local_content_generator.py`: `_conclusion` y `_build_internal_links` reciben el
  **destino resuelto**, nunca `hotel_data["phone"]`; nuevo método `_destino_whatsapp`.
  Sin destino, la frase de reserva se omite (`_build_internal_links` conserva su
  fallback «Reservar: contactar al hotel»).
- Cableado: `v4_asset_orchestrator.py` expone `whatsapp_presence_evidence_kind`
  (nuevo lector `site_presence_adapter.presencia_evidencia_whatsapp`, que solo
  publica lo que el lector ya observó) y `whatsapp_status`;
  `conditional_generator.py` arma el registro `canal_whatsapp` que recibe el
  generador de contenido local. `phone` sigue viajando para otros consumidores;
  ya no decide el enlace.
- Plantilla: se retiró la línea `WhatsApp:` del bloque CONTACTO y se conservó el
  email. Con la línea fuera, el contexto `hotel_phone` y su extracción de
  `gbp.phone` (PATCH-6) quedaron sin lector y se retiraron también; un campo de
  contexto sin lector caduca en silencio.

**Contrafactual medido, no afirmado** — comando
`python -X utf8 evidence/AC6-AC10-RECUPERACION-2026-10-07/contrafactual_wa_me.py`
(crudo: `crudos/contrafactual_wa_me.txt`, EXIT 0):

```
lineas wa.me PRE : 5  -> numeros de linea [73, 147, 221, 295, 369]
ejemplo PRE      : Para reservar: [Hotel Don Alfonso - WhatsApp](https://wa.me/6063146139)
lineas wa.me POST: 0  -> []
CONTRAFACTUAL: 5 -> 0
```

El lado POST es el mismo handler de producción
(`ConditionalGenerator._generate_content("local_content_page", …)`) con las mismas
entradas de la corrida del 2026-10-07.

## 3. AC10 — el orden tiene tareas y el revisor las mide

**Emparejamiento** (`asset_responsibility_contract.py`): `despojer_nombre_real` quita
`ESTIMATED_` y la marca `_YYYYMMDD_HHMMSS`; `resolver_nombre_real` solo devuelve un
catálogo si el resultado es **exactamente** uno de los seis nombres canónicos, y el
tipo (CORE/GEO) lo fija el catálogo, no la lista donde llegó el nombre. `
get_implementation_order`, `generate_delivery_template`, la guía de relaciones y el
checklist usan ese emparejamiento; `get_replacement_rule` también, para que
`ASSET_RESPONSIBILITY.json` no contradiga al `IMPLEMENTATION_ORDER.md`.

Medido con los 13 nombres reales de la corrida: **casa 1**
(`hotel_schema_20261007_093402.json` → `hotel_schema.json`, CORE) y **12 siguen en
ADICIONALES**. `ESTIMATED_faqs_…json` **no** se empareja con `faq_schema.json`: sería
fabricar el par. `None` sigue significando «todos» y `[]` «nada».

**Writer real**: `tests/geo_enrichment/test_orden_implementacion_nombres_reales_ac10.py`
(19 tests) materializa los 13 archivos con su ruta real y llama a
`DeliveryPackager.write`. El ZIP resultante tiene `IMPLEMENTATION_ORDER.md` con una
tarea numerada cuya ruta existe como miembro, manifiesto contra `namelist()` con 0
ausencias y 0 discrepancias de tamaño, y el caso sin assets planificados **no** emite
el archivo (se declara, no se inventa).

**El revisor** (`asset_reviewer.py`): `implementation_order_check` deja de ser un
registro de fuente y publica `contenido` ∈ {`OK`, `ORDEN_VACIA`, `NO-EVALUABLE`},
`tareas` y `seccion_orden`. El corte es **por sección** —una `###` de la guía de
relaciones no cuenta como tarea del orden—, que es exactamente cómo el documento
certificado engañó al criterio estructural viejo.

**Contrato declarado del rojo:** con cero tareas emite `WARNING` con tipo propio
(`IMPLEMENTATION_ORDER_SIN_TAREAS`). No es `CRITICAL` porque el veredicto bloqueante
de Bot 3 exige CRITICAL y esta sesión no reabre la política de enforcement del
Tribunal (V-7 y el primer piso tienen su dueño). Con lectura fallida declara
`NO-EVALUABLE`: abstinencia, no verde.

## 4. Verificación externa, citada textualmente

Comando `python -X utf8 evidence/AC6-AC10-RECUPERACION-2026-10-07/verificacion_externa.py`
(crudo: `crudos/verificacion_externa.txt`, EXIT 0):

```
1) zipfile.testzip() sobre donalfonso_20261007.zip.tmp -> None
2) IMPLEMENTATION_ORDER.md del ZIP de prueba: 1 tarea(s) numerada(s)
   tarea 1: ASSETS/hotel_schema/hotel_schema_20261007_093402.json | existe como miembro del ZIP: True
3) contenido local producido tras el fix: 0 linea(s) con `wa.me`
```

## 5. PRE / POST, mutantes y bajas

| Concepto | Valor |
|---|---|
| Selección (misma en PRE y POST, mismo entorno) | `tests/asset_generation/test_local_content_generator.py`, `tests/asset_generation/test_conditional_generator.py`, `tests/geo_enrichment/test_asset_responsibility.py`, `tests/test_ac_g1_implementation_order.py`, `tests/quality_gates/tribunal`, `tests/delivery`, `tests/commercial_documents` |
| PRE (antes de editar producto) | 780 passed, 9 skipped, EXIT 0 — `crudos/pre_seleccion.txt` |
| POST (misma selección) | 789 passed, 9 skipped, EXIT 0 — `crudos/post_seleccion.txt` |
| Delta | **+9**, 0 bajas. Se explica: 4 tests nuevos en `tests/commercial_documents` y 5 en `tests/quality_gates/tribunal`, ambos directorios dentro de la selección. Skipped sin cambios (9→9) |
| Tests nuevos fuera de la selección | 42 = 23 (`test_reserva_whatsapp_desde_canal_ac6.py`) + 19 (`test_orden_implementacion_nombres_reales_ac10.py`) |
| Mutantes | 10/10 rojos **por su causa** (nodo nombrado en la salida, EXIT≠0), 10/10 restaurados, árbol intacto por sha256 — `mutation_report.json`, instrumento `run_mutations.py` |
| Regresión completa (por tocar un test de producto) | `python -m pytest tests/ -q` → **3 failed, 5182 passed, 42 skipped, 4 xfailed, EXIT 1** en 428 s — crudo `crudos/post_regresion_completa.txt`. Los 3 rojos están desglosados abajo; tras curar el único propio, la corrida queda en **2 rojos ajenos** |

### Los tres rojos de la regresión completa, desglosados por firma

| Rojo | En aislado | Atribución |
|---|---|---|
| `tests/test_validate_wiring_check_derivado_versionado.py::test_el_derivado_versionado_del_repo_pasa_su_propio_check` | FALLA (EXIT 3) | **propio y curado**: `exclusiones_por_rol.evidence.cantidad_versionada` publicado 150 vs fresco 154 — la carpeta de evidencia que exige el mandato mete `.py` en el alcance del verificador. Cura: regenerar el derivado con su escritor (`python scripts/validate_wiring.py --write-report`, 712 archivos) y borrar un scratch propio (`crudos/probe_orden_writer.py`). No se rebajó la aserción ni se tocó el artefacto certificado del plan: el derivado vencido es `.opencode/wiring_report.json`, que viaja pendiente de commit. Verificado verde después (`1 failed → 0`) |
| `tests/quality_gates/jev_pilot/test_jev_pilot_deepseek_brazo.py::test_la_falta_de_deepseek_falla_antes_de_enviar…` | **PASA** | rojo ajeno por interferencia de corrida (patrón conocido del piloto JEV) |
| `tests/quality_gates/jev_pilot/test_jev_pilot_sdk_ac9.py::test_cargar_sdk_anade_al_final_y_conserva_el_pydantic_del_product` | FALLA | rojo ajeno **y** ambiental: `sys.path.index(sitio) > sys.path.index(venv_paquete)` se mide `14 > 14` porque la ruta durable del SDK resuelve al mismo `tmp_test/venv-jev-sdk/Lib/site-packages` (directorio ignorado por `.gitignore:28`) que el test usa como «el venv». El archivo no importa nada de `modules.*` (medido por AST: 0 imports del producto), así que ninguno de los 9 archivos tocados interviene. Dueño: piloto JEV / entorno de medición. Procedencia: pasaba el 2026-10-04 (`evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/FASE-B/metrics_tests.txt:91`) |

### Cierre documental y validaciones rápidas (último paso)

- Índice de lecciones regenerado con su escritor y verificado fresco:
  `python scripts/build_lesson_index.py --check` → `[OK] Índice de lecciones fresco (344 IDs)`, EXIT 0.
- `python scripts/run_all_validations.py --quick` → **`TOTAL: 13/13 validations passed`**,
  `STATUS: ALL VALIDATIONS PASSED`, **EXIT 0** (crudo `crudos/quick_final.txt`, con la
  `[GUARDA]` que casa las 13 etiquetas impresas con el TOTAL dinámico).

### El derivado que mis propios artefactos vencieron

La carpeta de evidencia que exige el mandato mete `.py` en el alcance del verificador de
cableado: `exclusiones_por_rol.evidence.cantidad_versionada` pasó de 150 publicado a 154
fresco y `test_el_derivado_versionado_del_repo_pasa_su_propio_check` salió EXIT 3. La cura
es la que publica el propio verificador — regenerar el derivado con su escritor
(`python scripts/validate_wiring.py --write-report`, 712 archivos en alcance) — más borrar
un scratch propio de esta sesión (`crudos/probe_orden_writer.py`). No se rebajó la aserción
y no se tocó `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/**`. `.opencode/wiring_report.json`
queda regenerado y **pendiente de commit** (no autorizado en esta sesión).

**Test de producto re-ancado y declarado:**
`tests/asset_generation/test_local_content_generator.py::test_whatsapp_link_in_conclusion`
asertaba `if "Para reservar:" in …: assert "wa.me" in …` sobre un fixture alimentado
solo con `phone`. Con el fix ese verde ya no podía perder. Se re-ancló dando el canal
verificado y exigiendo el destino del canal — no se afeitó la aserción.

**Enseñanza del instrumento (no se promociona como verde):** los mutantes M1 y M2
apagaban, respectivamente, el filtro de clase de evidencia y el de estado, y
**sobrevivieron** en el fixture del caso real porque la capa siguiente (contraste de
número) cortaba el mismo caso. Hubo que añadir dos tests discriminantes
(`test_estado_estimated_con_numero_casado_rechaza_por_estado`,
`test_plugin_fingerprint_con_numero_casado_rechaza_por_clase_de_evidencia`) para que
cada guard tenga oportunidad individual de perder.

## 6. Límites

1. El ZIP del 2026-10-07 conserva ambos defectos y ninguna corrida lo ejerce.
2. `SUPERADO_OFFLINE` ≠ E2E.
3. El rojo del revisor es WARNING: no bloquea publicación por sí solo (dueño: Tribunal).
4. El par CORE↔GEO de `hotel_schema` se declara «No generado» aunque
   `ASSETS/geo_enriched/hotel_schema_rich.json` viaje en el paquete: la población de
   entrada son los `generated_assets` del reporte (`main.py` NF-6) y los artefactos de
   `geo_flow` no están en ella. Dueño: delivery/main.py.
5. Un asset proveído que no queda empaquetado se lista con nombre crudo (sin
   `ASSETS/`): medido con fixture plano, `llms_*.txt` en la raíz no enruta por la lista
   de extensiones de `_collect_files`. En la ruta real vive en subdirectorio y sí
   empaqueta; el test se fixtureó con las rutas reales.
6. Sin lección nueva que capitalizar: los mecanismos (guard en el límite, re-anclaje de
   un verde vacío, mutante enmascarado por capa siguiente) ya están en el índice. Se
   declara en lugar de fabricar cuota.
7. Sin commit, push, L3 ni tag: termina en «listo para revisión».

## 7. Archivos tocados

Producto: `modules/data_validation/whatsapp_contract.py`,
`modules/asset_generation/local_content_generator.py`,
`modules/asset_generation/conditional_generator.py`,
`modules/asset_generation/v4_asset_orchestrator.py`,
`modules/asset_generation/site_presence_adapter.py`,
`modules/geo_enrichment/asset_responsibility_contract.py`,
`modules/quality_gates/tribunal/asset_reviewer.py`,
`modules/commercial_documents/v4_proposal_generator.py`,
`modules/commercial_documents/templates/propuesta_v6_template.md`.

Tests: 4 archivos nuevos + 1 re-ancado.

Plan: filas V-1 y V-2 de `10-analisis-post-implementacion.md` con anotación `⟦…⟧`
(medido, corregido, sin corrida). Índice de lecciones regenerado con su escritor y
verificado fresco con `--check`.
