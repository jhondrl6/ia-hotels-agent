# Documentación Post-Proyecto — VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20

> Acumulativo. Cada fase de implementación lo actualiza al cerrar; es la fuente de datos de
> FASE-RELEASE para generar CHANGELOG y `GUIA_TECNICA`. **Se crea vacío y se llena por fases.**

## Sección A: Módulos nuevos

| Módulo / archivo | Qué hace | Entra por | Estado |
|---|---|---|---|
| `scripts/validate_governance_numbers.py` | Compara cada aserción sobre un conteo en los documentos de gobierno contra la etiqueta `[N/M]` que el código imprime; publica denominador y tres estados | FASE-A | **Escrito y verificado offline el 2026-09-21** (914 líneas, stdlib-only, standalone; `--report` / `--json` / inyectables `--governance-doc`/`--source`/`--hook`) |
| `scripts/decision_client.py` | Única puerta del repo a un proveedor de decisiones estructuradas: contrato propio (`choice`/`score`/`noul` con su confidence), proveedor resuelto por entorno, fallo explícito sin decisión por defecto, escáner AST de su propio aislamiento y medidor de lo que cuesta añadir un proveedor | FASE-B | **Escrito y verificado offline el 2026-09-21** (≈800 líneas con su docstring de límites, stdlib-only —`argparse`/`ast`/`importlib`/`json`/`os`/`re`/`sys`/`pathlib`/`tempfile`/`hashlib`/`shutil`—; CLI `--provider-status` / `--scan-imports` / `--costura` / `--report`; **ningún módulo de red importado**, ver `evidence/…/FASE-B/cero-red.txt`) |
| `tests/quality_gates/decision_client/falsos_proveedores/falso_forma.py` | Proveedor **falso** que cumple la forma: determinista, sin red y sin credencial. Es la materia sobre la que AC8 fija la forma y AC9 mide la extensión | FASE-B | Escrito el 2026-09-21 |
| `tests/quality_gates/decision_client/falsos_proveedores/falso_ilegible.py` | Proveedor **falso** que contesta fuera de forma (`choice` sin `confidence` + una pregunta sin responder): provoca el estado `ILEGIBLE` desde el lado del proveedor, no desde un mock del test | FASE-B | Escrito el 2026-09-21 |
| `scripts/triage_lesson_relevance.py` | Capa de pertinencia **aditiva** sobre `.opencode/lecciones_index.json`: propone lo que el Paso 0 no ancló y nunca elimina una fila anclada | FASE-C | Pendiente de escribir |
| `scripts/build_phase_briefing.py` | Compone por cada fase un pack derivado con las secciones que su prompt **declara** leer, con proveniencia (HEAD + sha por fuente), `--check` de frescura y negativa a emitir un pack más corto en silencio | FASE-D | Pendiente de escribir |
| `…/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/briefing/` | Directorio de **artefactos generados** dentro del plan (no en `.agents/workflows/`, que tiene contadores de skills) | FASE-D | Pendiente de generar |

## Sección B: Funcionalidades nuevas

- (FASE-A, **cerrada el 2026-09-21**) Detección mecánica de aserciones vencidas sobre conteos, con
  su población y sus familias no cubiertas. Sobre el árbol vigente reproduce **A1–A4 y ninguna
  otra** (`findings[]` con `assertion_id`, `claimed`, `observed`, `occurrences[]`), clasifica las
  **24 instancias** de la población en viva-hallazgo (5) / viva-correcta (11) / histórica congelada
  (8) / no resuelta (0), y publica `coverage_basis` con las cuatro familias no cubiertas medidas en
  runtime. Tres estados sin colapso (`SIN-HALLAZGOS` / `AUSENTE` / `LECTOR-FALLIDO`), seis mutantes
  del guard real en `evidence/…/FASE-A/mutation/` y delta 0 en los conteos que otros planes pinean.
- (FASE-B, **cerrada el 2026-09-21**) Costura neutra de proveedor con contrato propio. Lo que
  quedó cerrado con medición: **AC6** `0` imports del SDK/adapter fuera de la puerta sobre **692** `.py`
  del árbol de trabajo (4.379 nodos de import; 21 menciones no-import publicadas aparte; exclusiones
  declaradas por directorio con su conteo) y **9 mutantes** que muestran que cada guard carga con lo
  suyo; **AC7** `provider_status` en sus tres estados, con 5 `motivo_clase` que no colapsan y con la
  conversión a tipos negativa a rellenar un campo ausente; **AC8** contract test verde (`exit 0`) y
  el **mismo test rojo** (`exit 1`) al quitarle `confidence` al proveedor falso, con el pin del modelo
  declarado y probado por AST como no-usado; **AC9** `files_changed_to_add_provider = 1` medido por
  sha256 sobre la frontera completa, con los dos proveedores despachados y contestando distinto.
  Sin llamadas de red —verificadas con guard de `socket` vivo, denegatoria AST de 19 módulos y SDK
  ausente del venv del producto— y sin credencial alguna en árbol, evidencia o logs. La comparación
  real entre proveedores **no** es de este plan: es la deuda **D7**.
- (FASE-C) Informe de candidatos de pertinencia por plan, con umbral publicado, sus términos de
  búsqueda y la **aceptabilidad** que dispara la deuda D6.
- (FASE-D) Unificación de la carga de lectura declarada por fase, y medición del delta con el mismo
  comando en los dos lados (AC20).

## Sección C: Correcciones

- (FASE-B, **2026-09-21**) Dos cifras del propio cierre estaban estimadas y se corrigieron midiendo:
  «10 archivos de código» → **11** y «13 de evidencia» → **25**, ambas con su comando en
  `evidence/…/FASE-B/baseline-pre-post.md` §Presupuesto. Es la medición A6 del maestro golpeando a
  esta fase: el número se escribió antes de terminar de escribir los archivos.
- (FASE-B, **2026-09-21**) El `--quick` cayó a 10/11 al registrar la fase, por el mismo conflicto de
  los **dos escritores de la fecha** en `REGISTRY.md` que documentó FASE-A. Corregido con su writer
  (`sync_versions.py --rule registry_last_update`) y no a mano; el conflicto sigue sin dueño de
  reconciliación y esta es la segunda fase que lo paga.



- Las aserciones A1–A4 medidas en `01-plan-maestro.md` §1 **no se corrigen** en este plan
  (AC17). Quedan como deuda D1 con su disparador.

## Sección D: Métricas acumulativas

| Métrica | Pre (a medir por cada fase) | Post | Notas |
|---|---|---|---|
| Checks de `run_all_validations.py --quick` | 11 | **11** (delta **0**, 2026-09-21) | Delta esperado **0** en las cuatro fases de implementación (AC16) — cumplido por FASE-A **y por FASE-B** |
| Checks del hook `scripts/git_hooks/pre-commit` | 7 | **7** (delta **0**) | Delta esperado **0** — cumplido. Quién lo afirma en `tests/`: `test_validate_plan_closure.py` (`[5/7]`) |
| `def test_` en `tests/` | **4.330** (PRE de FASE-B) | **4.378** (resta **+48**, verificada: 4.378 − 4.330 = 48) | FASE-B: `tests/quality_gates/decision_client/` = 48 funciones / **53 casos** (parametrización de los 6 guards). La cifra canónica que publica `AGENTS.md` (4.246) sigue vencida por tráfico ajeno y su edición pide instrucción literal |
| IDs definidos en `.opencode/LECCIONES-INDEX.md` | 320 (re-medido el 2026-09-20) | re-medido al cerrar cada fase: lo publica `build_lesson_index.py` y FASE-A cerró con **325** | Cambia al archivar; lo regenera RELEASE. A6 documentó que esta cifra vence al escribir cualquier `.md` del corpus — **y FASE-B la vuelve a reproducir**: esta fase escribe IDs reales (L-V2.3, L-PF6, L-R.3…) en seis `.md` de plan, así que el índice se regenera en el cierre |
| Imports del SDK/adapter fuera de la puerta (AC6) | **0** sobre 678 `.py` rastreados / **692** del árbol de trabajo (690 en el primer escaneo: +2 por los instrumentos propios) (medido al abrir FASE-B con el AST de la propia puerta) | **0** re-medido al cerrar (misma población) y **0 otra vez el 2026-09-22**, ya con **691** rastreados (el commit de la fase sumó sus 13 `.py`) sobre los mismos **692** del árbol | El SDK sí existe en el entorno, pero **aislado en `tmp_test/venv-jev-sdk`** y no instalado en el venv del producto; esa exclusión está publicada con su conteo en `import_scanner.txt`, no callada. **Y hay una exclusión que faltaba**: el residuo 692−691 es `.venv-wsl/bin/activate_this.py` (deuda **S11**, lección **L-VCF-11**), que no importa el SDK y por eso no mueve el 0 |
| Coste de añadir un proveedor (AC9) | sin instrumento (no existía la costura) | **1** archivo, medido por sha256 sobre la frontera copia+door (`costura.json`) | Tests paralelos: 1, declarado aparte y no escondido para inflar el «1». Con un proveedor **real** (D7) habría además manifiesto de dependencias: eso no está medido aquí porque ningún proveedor se activa |
| **Carga de lectura declarada por fase (bytes / ~tokens)** | **263.973 / ≈65.993** re-medidos el 2026-09-20 sobre las siete lecturas que suma A7 en el plan de referencia (al concebir: 254.010 / ≈63.502; maestro §1, A7 y A6) | **263.973 / ≈65.993** re-medidos el 2026-09-21 con `stat -c %s` sobre los siete archivos: **sin cambio** (las fases de `REFACTOR-WHATSAPP` no volvieron a escribirlos). FASE-A no reduce lectura: es FASE-D quien debe mover esta fila | **AC20 lo mide con el mismo comando en los dos lados**, sobre las fases de este plan; delta cero o negativo es resultado válido y se explica |
| Población bajo el patrón de conteo (A8) | **22 instancias `[N/M]` en 17 líneas** + 2 formas «check N» en `.agents/` (medido el 2026-09-20) | **22 / 17 / 2, re-medido el 2026-09-21: idéntico** (el verificador las agrupa en 24 instancias auditables = 22 + 2) | El verificador las clasifica en viva / histórica congelada / vigente-correcta y publica las dos últimas con su conteo; sin esa regla AC1 no es verificable |

## Sección E: Archivos afiliados

- [ ] `CHANGELOG.md` (RELEASE)
- [ ] `GUIA_TECNICA.md` (RELEASE)
- [ ] `docs/contributing/REGISTRY.md` (RELEASE — los tres módulos nuevos)
- [ ] `VERSION.yaml` → sync a los seis archivos que lista el executor (RELEASE)
- [x] `.opencode/LECCIONES-INDEX.md` y `.opencode/lecciones_index.json` (regenerados en cada commit que escribe `.md` de plan con IDs) — **FASE-B regeneró el par el 2026-09-21** al escribir sus seis documentos de cierre, y el commit que los llevaba dentro llegó con su instrucción literal: **`647f436`, el 2026-09-22** (`--numstat`: 24+/17− y 100+/14−), con `[6/7]` del hook verde en esa corrida
- (FASE-B, **sin tocar**) `AGENTS.md`: su cifra canónica de funciones de test está vencida contra disk (4.246 publicados / 4.378 medidos) y es configuración central: se edita con instrucción literal, no a mitad de fase
