# FASE-F (AC13) — inventario de salidas y estado real

Fecha: 2026-10-06. HEAD de partida: `9127735` (FASE-E commiteada, sellada y empujada; paridad con `origin/master`
verificada por la sesion de E). Instrumento: lectura directa del arbol + dos inventarios read-only delegados
(`Agent`/Explore), cuyas rutas se re-verificaron en disco antes de citarlas: el informe delegado ubicaba
`v4_comprehensive.py` en `modules/commercial_documents/` y la ruta real es `modules/auditors/v4_comprehensive.py`.

Que NO se hizo: no se abrio `.env`, ni valores del entorno, ni caches, ni logs crudos historicos para buscar una
key; no se imprimio un valor ni una linea coincidente en todo el faseo (los unicos numeros que se publican son
conteos); no se ejecuto `v4complete` (contador del plan: 0/1); no se roto nada; no se contacto servicios.

## 1. Estado antes de F, por canal

| Canal | Mecanismo existente | Brecha demostrada (leida, no inferida) |
|---|---|---|
| consola del auditor LLM | `LLMMentionChecker._sanitize_text` + `_sanitize_error` sobre las ramas de error | noop si la instancia no tenia keys; solo enmascaraba `?key=`/`&key=` |
| consola de `PageSpeed` | `sanitize_pagespeed_message` para el **documento** | el `logger.warning` de la misma linea imprimia `mobile_result.message` crudo |
| consola de `HttpClient` | ninguna en `_log_ssl_bypass` | `print` del texto tal cual |
| disco bajo `logs/` | `SSLLogger._sanitize_for_log` = quitar saltos + recorte 200 | unica escritura real bajo `logs/` (linea 18 de `.gitignore`) sin redaccion |
| excepciones de PageSpeed | `params` con la key en la query | `raise Exception(... {response.text})` y `RequestException` crudos |
| excepciones de Places | `X-Goog-Api-Key` en header | `error_message=f"...{str(e)}"` en 6 ramas, persistidas por `scripts/preload_prospects_gbp.py` |
| artefacto nuevo de D | enmascarado de telefono en `failed_error_checks` | el mismo JSON guardaba `report.to_dict()` con `checks[].message`/`errors`/`warnings` crudos |
| print nuevo de E | ninguno en la rama `never-block` | `print(... {e})` del fallo del snapshot |
| snapshot interno de E | exclusion del ZIP (`delivery_packager`) | no es fuga: es el limite interno/cliente definido por E |
| verificador de secretos | `git ls-files` + staged | `output/**` y `logs/**` nunca leidos; `sk-or-v1-`/`sk-ant-` fuera del patron; NameError en la rama >5 MB |

## 2. Medicion de la pata nueva del verificador, antes de activarla

Con los patrones reales de `_secret_patterns` sobre el arbol de trabajo (grueso en `temp/fase_f_scan_precheck_out.txt`):

```
archivos_examinados 1041
no_texto_omitidos 0
demasiado_grandes 0
archivos_con_hallazgos 0
```

Consecuencia: activar el escaneo de `output/` y `logs/` no hered6 ningun rojo historico. Se midio **antes** de
editar, porque un rojo de exposures previas habria puesto el quick en rojo sin que F lo produjera.

Complemento medido: ningun archivo versionado supera `_MAX_SCAN_BYTES` (el mayor es `archives/scraped_sites.json`,
780.700 bytes), asi que la rama del NameError estaba inexecutable en el repo de hoy; tiene diente propio con un
archivo >5 MB en `tmp_repo` (`test_archivo_grande_versionado_es_no_cubierto_sin_name_error`).

## 3. Consumidor futuro de H (no construido aqui)

H integra el runner con captura y snapshot. Lo que F define para que H consuma, sin construir su runner:

- el sumidero es `modules/utils/redaction.py`; cualquier salida nueva del runner pasa por `redact_secrets` (texto),
  `redact_payload` (estructuras serializables) o `redact_and_clip` (limites fijos), **antes** de consola o disco;
- `assert_redacted(texto, channel=...)` es el guard fail-closed para informes: falla sin repetir el valor;
- los estados del lector nuevo del verificador son tres y distinguibles: salidas presentes leidas (verde con
  conteo), `output/`+`logs/` ausentes (`0 salidas en output/ y logs/`, NO "sin secretos"), y archivo que no se
  pudo leer (`NO_LEGIBLE`, rojo).

## 4. Lo que no se pudo determinar

- si el stderr de los loggers sin handler se redirige a un archivo por wrappers de shell o CI (no hay
  `basicConfig`/`FileHandler` configurado en `main.py`; la redaccion ahora ocurre antes de que exista el texto).
- que ninguna de las 3 ramas de `logger.exception` de auditeras externas pueda reconstruir una credencial a partir
  del traceback una vez redactada la fuente: se razona por la fuente, no por observacion de una corrida real.
- el inventario gobernable de credenciales del repo no tiene artefacto propio ni script que lo genere (buscado y
  no encontrado); `credential_status.json` es el primer registro y es evidencia de fase, no producto de runtime.

## 5. Deuda declarada por F

- **S-F1** `scripts/preload_prospects_gbp.py` persiste `PlaceData.error_message` en markdown y JSON. Llega ya
  redactado desde el cliente, pero el script no esta en la allowlist de F y no se toco. Dueño: H/VERIFY.
- **S-F2** `_query_perplexity` no tiene `try/except` propio: depende del que le da `_query_provider`. La rama
  sobrevive redactada por el sumidero, pero no tiene diente propio de consola. Dueño: VERIFY.
- **S-F3** la pata nueva del verificador lee lo que existe al momento de la validacion; un archivo que aparezca
  despues queda fuera hasta la siguiente corrida. No hay watch ni hook que la cubra (los 8 checks del pre-commit
  leen HEAD, y `output/`/`logs/` nunca entran al index). Dueño: RELEASE o deuda declarada.
- **S-F4** `archives/gbp_profiles.json` y `evidence/`/`.opencode`/`archives` siguen excluidos del escaneo por la
  allowlist de cuarentena que venia de P5; F no la amplió ni la redujo. Dueño: operador.
