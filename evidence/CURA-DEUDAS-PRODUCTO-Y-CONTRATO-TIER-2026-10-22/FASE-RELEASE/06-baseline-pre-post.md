# Baseline pre/post — FASE-RELEASE-4.82.0 (2026-10-24)

## 1. H8: el literal `APROBADO-CONDICIONAL-PENDING-ONBOARDING` en la narrativa vigente

**Población declarada**: `docs/GUIA_TECNICA.md` y `ROADMAP.md`, por archivo completo (`grep -c`), sin filtro de sección. `CHANGELOG.md` y `docs/contributing/REGISTRY.md` quedan **fuera por diseño** (H8 los conserva como registro histórico; medidos: 5 ocurrencias en `CHANGELOG`, todas dentro de entradas de release anteriores).

**Ancla del PRE**: `git show HEAD:<ruta>` con `HEAD = b05768c` (la revisión anterior a esta fase), no la memoria de la sesión. El prompt publicaba 5 en `GUIA_TECNICA` y 4 en `ROADMAP` como antecedente del 2026-10-23; **el PRE medido contra HEAD casa con ese antecedente: 5 y 4**.

| Archivo | PRE (HEAD `b05768c`) | POST (árbol de trabajo) | Delta |
|---------|----------------------|--------------------------|-------|
| `docs/GUIA_TECNICA.md` | 5 | 7 | **+2** |
| `ROADMAP.md` | 4 | 2 | **−2** |
| **Total** | **9** | **9** | **0** |

**La resta no dice lo que importa y se declara.** El delta +2 de `GUIA_TECNICA` no es narrativa vencida que regresó: son las **dos menciones que escribe la nota de cambios v4.82.0 para nombrar lo que se retiró** (la fila de FASE-C en la tabla por fase y el párrafo de backwards compatibility). Lo que el criterio de H8 exige es otra cosa: que **ninguna prosa vigente publique el literal como el veredicto actual**.

**Atribución de las 9 ocurrencias POST, línea a línea** (leídas en el árbol de trabajo):

| # | Archivo | Línea | Rol | ¿Aserción vigente? |
|---|---------|-------|-----|--------------------|
| 1 | `GUIA_TECNICA` | 21 | Fila FASE-C de la nota v4.82.0: describe el **defecto retirado** | no (habla en pretérito y nombra el retiro) |
| 2 | `GUIA_TECNICA` | 33 | Párrafo «Rompente» de la nota v4.82.0: documenta el **cambio de literal** | no (dice «cambia de X a Y») |
| 3 | `GUIA_TECNICA` | 130 | **§regla de primer piso** — objetivo de H8: re-escrita a `APROBADO-CONDICIONAL` y el literal viejo queda marcado «antes de esa release … quedó retirado» | **no** (antes: **sí**) |
| 4 | `GUIA_TECNICA` | 186 | Nota v4.76.0 FASE-E2E: veredicto que **produjo la corrida Salento Real** (2026-09) | no (historia con fecha) |
| 5 | `GUIA_TECNICA` | 2606 | Nota v4.47.0: contrafactual **medido el 2026-09-20** sobre acta archivada | no (historia con fecha) |
| 6 | `GUIA_TECNICA` | 2616 | **Límite vigente** («el techo real con tier B **sigue siendo** …») — objetivo de H8: re-escrito al veredicto actual con el retiro nombrado | **no** (antes: **sí**) |
| 7 | `GUIA_TECNICA` | 2874 | Nota FASE-E2E de REFACTOR-WHATSAPP: «la entrega que produjo» (2026-10-07) | no (historia con fecha) |
| 8 | `ROADMAP` | 184 | **Regla 4 de la cascada de precisión** — objetivo de H8: re-escrita a `APROBADO-CONDICIONAL` + `conditional_reason`, con referencias **por símbolo** en lugar de `judge.py:38`/`:450-462` | **no** (antes: **sí**) |
| 9 | `ROADMAP` | 312 | Fila «FASE-0 offline (2026-09-20)» de la tabla de contrafactuales | no (historia con fecha) |

**Aserciones vigentes: PRE 5 → POST 0** (las tres corregidas en `ROADMAP` —184, §Veredictos, deuda P5— y dos en `GUIA_TECNICA` —130, 2616—; las dos últimas líneas de `ROADMAP` corregidas salieron del conteo de ocurrencias porque se re- escribieron sin el literal). **4 ocurrencias quedan como historia fechada** y **5 nombran el retiro**.

**Verificador mecánico de esta resta: NO EXISTE** (`L-R.4`). Ningún instrumento del repo decide si una mención del literal es «aserción vigente» o «registro histórico»: la atribución de la tabla se hizo leyendo las 9 líneas y su sección, y el crudo por línea está en `04-h8-*-baseline_pre.txt` / `05-h8-*-baseline_post.txt`. Quien quiera gobernar esto con un gate tiene que escribir el predicado, no re-copiar esta tabla.

## 2. Conteos del README (E8b), medidos por comando sobre el árbol de trabajo

| Métrica del README | Valor publicado | Comando | Medido | Resultado |
|--------------------|-----------------|---------|--------|-----------|
| «12 archivos YAML» (`config/`) | 12 | `ls config/*.yaml \| wc -l` | 12 | ✅ |
| «25 subdirectorios, 21 con pruebas» (`tests/`) | 25 / 21 | `find tests -maxdepth 1 -type d \| tail -n +2 \| wc -l` y `find tests -mindepth 2 -maxdepth 2 -name '*.py' \| xargs -n1 dirname \| sort -u \| wc -l` | 25 / 21 | ✅ |
| «Modulos funcionales (24 directorios)» | 24 | `find modules -maxdepth 1 -type d \| tail -n +2 \| wc -l` | 24 | ✅ |

**No todo el README era cifra.** Su tabla de comandos publicaba `spark` como «Deprecado | Legacy v3.x», que es **narrativa vigente falsa** desde FASE-A de este plan: la ruta se retiró y el centinela informa y sale 0 (`AC5`). Corregida a «Retirado | Centinela: informa el retiro y sale 0 (v4.82.0) | Usar `v4complete`», en línea con `AGENTS.md` §Comandos CLI, que FASE-A ya había re-anchado.

## 3. Funciones de prueba (método canónico, sin tocar el árbol)

| Sedida | Comando | Medido |
|--------|---------|--------|
| HEAD `b05768c` | `git grep -c -E "^\s*def test_" HEAD -- tests` (suma) | **5.483** |
| Árbol de trabajo | `grep -rE "^\s*def test_" tests --include=*.py \| wc -l` | **5.483** |

Coinciden: esta fase no añadió ni retiró funciones. La resta por fase (R2.7) vive en `09` §D y la nota de ronda, en `docs/cobertura-historia.md`; **ninguna de las dos se re-transcribe aquí**. El desfase entre el retrato commiteado de `AGENTS.md` §Cobertura (cabecera 5.334) y estos dos números se declara como seguimiento con dueño Operador en `10-analisis` §Seguimientos.

## 4. Derivados y validaciones (exit leído sin tubería, `L21`)

| Instrumento | Exit | Crudo |
|-------------|------|-------|
| `run_all_validations.py --quick` tras el bump | 0 (13/13) | `01-quick-post-bump.txt` |
| `version_consistency_checker.py` tras el bump | 0 | `02-version-consistency-post-bump.txt` |
| `sync_versions.py --check` | 0 | `03-sync-versions-check.txt` |
