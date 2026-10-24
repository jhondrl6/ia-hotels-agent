# Pre-vuelo de la corrida única — FASE-E2E (CURA-DEUDAS-PRODUCTO-Y-CONTRATO-TIER-2026-10-22)

> **Medido el 2026-10-24 (20:47 UTC) sobre el árbol vivo en `7182745`.** Precede a la única corrida
> `v4complete` del plan (1/1). Ninguno de estos checks gastó inferencia: son lectura de disco, sondas del loader y
> del código, y la letra del Operador.

## Checks

| # | Check | Criterio | Medido | Estado |
|---|-------|----------|--------|--------|
| 1 | Ensayo previo | `FASE-E2E-PRE` en `LISTO_PARA_E2E` | `pre-vuelo.md` del ensayo: veredicto `LISTO_PARA_E2E`, 15 checks, 2 condiciones abiertas con dueño Operador | ✅ |
| 2 | Onboarding materializado | el YAML versionado vive en `output/clientes/` | re-medido **en esta sesión**, no heredado del ensayo: sha256 `2990d768f0ae75f3…` idéntico entre `output/clientes/hotel_don_alfonso_onboarding.yaml` y `evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-E2E/hotel_don_alfonso_onboarding.yaml` (499 B, mtime 2026-10-12) | ✅ |
| 3 | El loader devuelve Don Alfonso | rama efectiva `YAML_DE_DIR_CLIENTES` | sonda por stdin (sin red, sin inferencia): `_load_latest_onboarding_data("https://www.donalfonsohotel.com/")` → `Hotel Don Alfonso`, `hotel.url = https://www.donalfonsohotel.com/`, `fecha_captura 2026-07-22`; `ONBOARDING_FRESHNESS_HOURS` **ausente** del entorno | ✅ |
| 4 | Cifras operativas con productor | rooms / adr_cop / occupancy / canal | rooms 11, `valor_reserva_cop` 330000, `canal_directo_pct` 30.0 del YAML; `occupancy_rate` 0.42424242424242425 = 140/(11×30), **coincide** con `financial_scenarios_20261012_165654.json → input_data` del baseline | ✅ |
| 5 | Dominio confirmado | `domain_confirmed: true` con letra del Operador | **`true`**: dictado del 2026-10-24 «Esta es la web de: https://donalfonsohotel.com/» (asiento `01-plan-maestro.md` §5). El run conserva la grafía `www` del baseline porque las dos cargan la misma rama y la misma identidad. **Descartada** `https://hoteldonalfonso.com/`: carga por el fallback del warehouse, no dispara alerta y estamparía en el documento del cliente una web que no es la del hotel (`evidence/…/FASE-E2E-PRE/confirmacion-dominio.txt`) | ✅ |
| 6 | Frescura vencida, declarada | `frescura_declarada_vencida: true` con la edad medida | `fecha_captura: 2026-07-22` → **94 días** al 2026-10-24 contra el techo de 90 del baseline (`vence_el: 2026-10-20`). Es la **opción (b)** del Operador (2026-10-24). No se fija `ONBOARDING_FRESHNESS_HOURS`: con el dato vencido eso pone el loader en fail-closed, el tribunal trueca `ANALYTICS_CEILING` por `ONBOARDING_INCOMPLETE` y AC7 se vuelve inalcanzable (`condicion-frescura-decision-b.txt`) | ✅ declarado, no curado |
| 7 | Consentimiento de **esta** corrida | documento propio en `evidence/…/FASE-E2E/`, con ruta, fecha y sha256 publicados en `preflight.json` | `consentimiento-corrida.md`, 4.136 B, sha256 `ba392cc9da17121e…`, acto del 2026-10-24. **No** se reutiliza el del 2026-10-12: ese ampara su corrida, declara que la ampara y su ventana venció el 2026-10-20 | ✅ |
| 8 | Aislamiento del análisis previo (`L-PF11`) | declarado, sin heredar premisa en silencio | `output/v4_complete/` conserva los artefactos del 2026-10-12 y la memoria **sí** tiene análisis para la URL canónica (`find_latest_analysis` devolvió no-`None`). Re-medido en el código: `run_v4_complete_mode` **solo imprime** el análisis descubierto y vuelve a ejecutar la auditoría (`V4ComprehensiveAuditor.audit` bajo `check_permission`); la reutilización efectiva (`find_latest_v4_analysis`) vive en `run_execution_mode`. `--force-new` no interviene en `v4complete`: su único consumidor vivo es `run_execution_mode` | ✅ |
| 9 | Destino del ZIP | `deliveries/` con `suppressed: false` | `deliveries_dir = output/v4_complete/deliveries` (main.py, construcción de `DeliveryPackager`). Antes de la corrida: **existe y tiene 0 entradas** — el ZIP del baseline fue suprimido | ⏳ lo decide la corrida |
| 10 | Baseline congelado, sin escribir | `evidence/CURA-COSTURA-TRIBUNAL-2026-10-11` intacto | `git status` de esa ruta: vacío. Sus cifras leídas en solo lectura: `verdict BLOQUEADO`, `evidence_tier B+`, `summary.over_presentations 2`, `scenarios.realistic 3.511.200,0 COP/mes` (conservative 6.176.940 / optimistic 582.120), `pain_ledger.entries 11` | ✅ |
| 11 | Fuentes que no se tocan | `observations.json` y el YAML | sin edición en esta fase; el ensayo ya los declaró intactos y la copia de trabajo sigue byte-idéntica al SHA versionado | ✅ |
| 12 | Credenciales | presencia por nombre de variable, nunca por valor | **no sondado en esta sesión**: la política de la herramienta bloquea leer `.env` sin autorización expresa y el consentimiento no la otorga. El baseline del 2026-10-12 corrió con extracción pagada y sus recibos están versionados. Riesgo declarado: si la key falta, la corrida falla y se declara `⏳ INCOMPLETA`, sin reintento | ⚠️ hallazgo del instrumento |
| 13 | Codificación del crudo | el stdout preservado tiene que sobrevivir a los emojis | sonda: sin flag, `sys.stdout.encoding` bajo redirect es **cp1252** y `main.py` imprime `📍/✅/🔍`. Se usa el mismo instrumento que el baseline: `PYTHONUTF8=1`, y su `stdout-corrida.txt` está versionado como UTF-8 válido. Desviación del comando literal: solo el entorno de codificación, ninguna variable de conducta del producto (`ONBOARDING_FRESHNESS_HOURS` sigue ausente) | ✅ |

## Instrumento de la corrida

```bash
PYTHONUTF8=1 ./venv/Scripts/python.exe main.py v4complete --url https://www.donalfonsohotel.com/ --force-new
```

Un solo intento (1/1), lanzado en `Bash` en segundo plano desde el hilo principal, stdout a
`stdout-corrida.txt` con `INICIO_UTC`, `EXIT=` y `FIN_UTC` estampados por el propio envoltorio. El término se
afirma por **exit code y presencia de artefactos**, no por la notificación de la herramienta.

## Veredicto del pre-vuelo

**`AUTORIZA_LA_CORRIDA`** — los siete criterios de la Tarea 1 están observados sobre medición propia de esta
sesión (no heredados del ensayo), con la frescura vencida declarada y el consentimiento de esta corrida asentado.

## Lo que este pre-vuelo NO prueba

- No ejecuta el pipeline: AC7 (ZIP real, `0 OVER_PRESENTATION`, pérdida honesta, brechas re-medidas) se certifica
  con los artefactos que escriba la corrida.
- No re-certifica el render determinista ni el juez: eso es mérito del ensayo E2E-PRE, sobre árbol sin cambios de
  código (`git diff d457986..HEAD -- main.py modules/ scripts/ config/ data/` vacío).
- No cierra la divulgación al cliente de la edad del dato (dueño: Operador, sede FASE-VERIFY o fase propia) ni el
  hueco del fallback de `observations.json` (cambio de producto sin fase dueña en este plan).
