# FASE-VERIFY — greps residuales con población declarada

**Población común**: árboles **versionados** de `modules/`, `scripts/`, `main.py` y `tests/`, con extensiones de fuente `.py`/`.md`/`.yaml`/`.json`, excluyendo `venv/` y `__pycache__/` (bytecode gitignorado por `.gitignore:4`). §4.10 del plan fija la regla: (a) atributos de código por **AST**, no por grep de menciones; (b) literales por rutas declaradas con allowlist de históricos.

## 1. Literal viejo del veredicto: `APROBADO-CONDICIONAL-PENDING-ONBOARDING`

| Paso | Comando (población) | Resultado |
|------|---------------------|-----------|
| Población de fuente | `grep -rn --include=*.py --include=*.md --include=*.yaml --include=*.json "APROBADO-CONDICIONAL-PENDING-ONBOARDING" modules tests main.py scripts \| wc -l` | **0** |
| Población ampliada sin filtro de extensión | `grep -rn "…" modules tests main.py scripts \| wc -l` | 6 |
| Naturaleza de los 6 | `grep` + `git check-ignore -v` | **los 6 son `.pyc`** bajo `tests/**/__pycache__/` (`test_acta_serialization`, `test_acta_version_desde_yaml`, `test_conditional_reason`, `test_judge`, `test_ac_g4_g5_multi_hotel_matrix`, `test_fase_0_ac20_evidencia_veredicto`) — huella del renombre de FASE-C en bytecode compilado antes de la cura. No versionados, no ejecutados como fuente |

**Allowlist de históricos** (§4.10b): `.opencode/` (27), `evidence/` (25), `archives/` (2), `docs/` (2), `CHANGELOG.md` (1), `VERSION.yaml` (1), `ROADMAP.md` (1), `.qoder/` (1), `temp/` (2), `output/` (2). `ROADMAP.md` y `GUIA_TECNICA.md` son prosa narrativa vencida ya declarada con dueño **FASE-RELEASE-4.82.0** (fila `H8` de §Seguimientos) y no entran en la población del AC2.

**Veredicto**: 0 en la población declarada; el residuo existe **solo** como artefacto de compilación y se declara con su causa. Consecuencia para el instrumento: todo barrido de literales de esta familia debe fijar la extensión, o reporta bytecode como si fuera código.

## 2. `SUPERPOSITION_FACTOR`: lecturas ejecutables por AST

Predicado: nodo `ast.Attribute` con `attr == "SUPERPOSITION_FACTOR"` (o suscripción con esa cadena) en los 273 archivos `.py` de `modules/`, `scripts/` y `main.py`, con los docstrings fuera por construcción del AST.

**Resultado: 0 lecturas ejecutables.**

Menciones que quedan y **no** son criterio (histórico declarado):

| Asiento | Naturaleza |
|---------|-----------|
| `modules/utils/financial_factors.py` — docstring de la clase `FinancialFactors` | el «fósil textual» ya registrado en §Seguimientos (superficie de texto, dueño histórico FASE-H2) |
| `main.py` — docstring del centinela `spark` | describe el retiro y nombra el atributo inexistente que el guardián caza |
| `modules/utils/__pycache__/financial_factors.cpython-313.pyc` | bytecode, excluido de la población |

Conforme a la regla del prompt: **0 lecturas ejecutables (AST), no 0 menciones**.

## 3. Claves inglesas del perfil GBP en los dos caminos

Predicado AST escopetado **por cuerpo de función** (no por archivo): suscripción con clave literal o atributo entre `{claimed, photos, has_whatsapp, has_hours}` dentro de `get_detected_issues` (`modules/utils/dynamic_impact.py`), `_map_brecha_to_issue_type` (`modules/commercial_documents/v4_diagnostic_generator.py`) y `_detectar_fugas` (`modules/scrapers/gbp_auditor.py`).

| Camino | Resultado |
|--------|-----------|
| `get_detected_issues` | **0** |
| `_map_brecha_to_issue_type` | **0** |
| `_detectar_fugas` | **0** |

**Falso positivo que el escopeteado por archivo habría producido**: el barrido file-wide de `gbp_auditor.py` sí encuentra la clave `'photos'` repetida en el mapa `confidence` del scraper y un XPath de `By.XPATH` con `'photos'` en el mismo método. **No es el asunto**: es el mapa de confianza de Places, otra clave con otro nombre y otro consumidor. Lo prueba el productor real: `_base_profile()` publica `fotos`, nunca `photos`. Lección aplicada: un barrido por literal verifica el asunto, no la palabra.

Contrapartida legible en el contrato vigente: el docstring de `get_detected_issues` enlista las cuatro claves retiradas —prosa que describe el retiro, permitida por la regla del prompt y por `L30`.

## 4. `found=True` vacío del stub

| Predicados | Resultado |
|------------|-----------|
| AST en `modules/scrapers/booking_scraper.py`: `keyword arg="found" value=True` y `dict` con clave `'found'` → `True` | **0** |
| Literal en el stub (`grep "found=True"`) | 2 — el docstring del módulo («`scrape()` **declaraba** `found=True»…») y el comentario que encabeza `ESTADO_STUB_RETIRADO` («nunca `found=True` con datos en None»). Prosa que documenta el retiro |
| Estado real publicado por el stub | `found=False`, `data={}`, `data_status=ESTADO_STUB_RETIRADO = "STUB_RETIRADO"` |
| AST file-wide en `modules/` (control de no-confusión) | 6 ocurrencias ejecutables en **otros tres módulos**: `asset_generation/site_presence_checker.py` (2 dict), `scrapers/google_travel_scraper.py` (2 kwarg), `scrapers/serpapi_client.py` (2 kwarg). **Otro asunto**: no son el stub de `D24`; un barrido global por la palabra las reportaría como residuo del stub |

**Veredicto**: 0 lecturas ejecutables del `found=True` vacío en la población del AC8.
