# Medición de la superficie de falso positivo del patrón CRITICAL (AC10 / cura N7)

**Fase**: FASE-B · **Plan**: CURA-COSTURA-TRIBUNAL-2026-10-11 · **Fecha**: 2026-10-11
**Código medido**: `modules/quality_gates/tribunal/honesty_reviewer.py`, símbolos
`VERIFICATION_GROUP_LENGUAJE`, `VERIFICATION_GROUP_CUANTIFICADOR`, `VERIFICATION_PATTERNS`,
`VERIFICATION_SCAN_GROUPS`, `coincidencias_lenguaje_de_verificacion`.

## Cómo se midió (AC10: con el patrón del código, no con uno equivalente)

El arnés importa los dos patrones del módulo y recorre la función del revisor; no re-escribe
ningún regex. Se ejecutó **por stdin** (`PYTHONUTF8=1 ./venv/Scripts/python.exe - <<'PY'`) para
no versionar un `.py` bajo `evidence/` ni `tests/`, que habría movido los contadores del gate
`wiring_report --check`. El comando y su forma están en `09_medicion_falso_positivo_crudo.txt`.

Corpus: las 6 propuestas reales del repo — 3 versionadas (`evidence/FASE-E2E`, `evidence/FASE-F`,
`evidence/FASE-I`) y 3 bajo `output/` (que está en `.gitignore`), dos de ellas la misma copia del
run de referencia del 2026-10-07 (14.690 caracteres).

## Las dos cifras por patrón

Unidad declarada: **ocurrencias en el texto** (literal, case-insensitive, por token) y
**coincidencias matcheadas** (lo que devuelve el patrón del código). La tercera columna es lo que
el revisor **emite** tras la cura estructural de AC10.

### Run de referencia: `output/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/.../02_PROPUESTA_COMERCIAL_20261007_093402.md`

| Grupo | Literales en el texto | Matcheadas **antes** de la cura | Matcheadas **con el patrón curado** | Emitidas como hallazgo |
|-------|----------------------:|--------------------------------:|------------------------------------:|-----------------------:|
| LENGUAJE (`verificad[oa]s?\|confirmad[oa]s?\|validad[oa]s?\|dato real\|cifra exacta`) | 1 | 1 | 1 | 1 |
| CUANTIFICADOR (`100%`, `total`, `absoluto`, `definitivo`) | 10 (5 `total` + 5 `100%`) | 5 (solo los `total`) | 10 | 2 |

### Corpus completo (6 propuestas)

| Grupo | Literales | Matcheadas con el patrón curado | Emitidas tras la cura |
|-------|----------:|--------------------------------:|----------------------:|
| LENGUAJE | 5 | 5 | 5 |
| CUANTIFICADOR | 56 | 56 | 12 |

## Lo que la medición muestra

1. **La frontera estaba rota** (cifra del plan, re-confirmada): con `\b` después de `%`, **0 de los
   5 literales `100%`** del run de referencia matcheaban. El `\b` tras un no-palabra exige un
   carácter de palabra al lado y nunca lo hay (`100% suyo`, `100% |`). Con `(?<!\d)100[ \t]*%`
   pasan de 0 a 5 coincidencias: el patrón **gana alcance**, no lo pierde.
2. **El falso positivo era estructural, no léxico.** De las 5 coincidencias del grupo de
   cuantificadores antes de la cura, **3 son totales financieros o de tabla** («fuga total
   estimada es de $21.067.200 COP», «Total recuperación proyectada (6 meses): $4.731.342 COP»,
   `| **Total CAPEX** |`) y **2 son absolutos de prosa** («Protección total para usted» bajo el
   encabezado `## 🛡️ GARANTÍAS`, y «### 5. Transparencia total»). La auditoría del 2026-10-11
   caracterizaba 4 de 5 como financieros o de tabla; **re-medido con el patrón del código: son 3**.
3. Los 5 `100%` del corpus real están **todos en filas de tabla o en celdas de cobertura**, no en
   prosa de garantía. Por eso la cura no es «apagar el grupo» sino **filtrar por contexto**.

## Criterio de la cura (documentado, con dueño de fase)

`VERIFICATION_SCAN_GROUPS` declara el filtro por grupo:

- **LENGUAJE_VERIFICACION** — sin filtro estructural: una celda de tabla que dice «Día 1
  (Verificado)` con `evidence_tier=B` es exactamente lo que Bot 4 existe para señalar. Filtrarla
  por estar en una tabla sería curar el ruido apagar el diente.
- **CUANTIFICADOR_ABSOLUTO** — se emite solo **fuera de fila de tabla markdown** (`LINEA_DE_TABLA`)
  y **fuera de una línea que declara un monto** (`MONTO_DECLARADO`: `$` + dígito, o cifra con
  separadores de miles seguida de `COP`/`USD`). Es la forma del «contexto de garantía» que proponía
  la AC10: un cuantificador absoluto adherido a una suma o a una columna numérica no es una promesa
  sobre-presentada.

Resultado sobre el run de referencia: de 5 CRITICAL espurios-por-mezcla a **2 CRITICAL de prosa de
garantía**, y el `100%` vuelve a ser detectable (par rojo/verde abajo).

## Par rojo/verde de la frontera (AC10)

| Mutante | Corrida | Resultado |
|---------|---------|-----------|
| M1 — se retira el guard `_es_contexto_financiero` | `01MUT-M1_..._02_ROJO_mutante.txt` | 2 failed / 3 passed |
| M1 — intacto | `01MUT-M1_..._01_VERDE_intacto.txt` | 5 passed |
| M2 — se restaura `\b(100%\|total\|absoluto\|definitivo)\b` (frontera rota otra vez) | `04MUT-M2_..._02_ROJO_mutante.txt` | 4 failed / 1 passed |
| M2 — intacto | `03MUT-M2_..._01_VERDE_intacto.txt` | 5 passed |
| M3 — el estado del acta se computa otra vez solo desde `findings_count` (AC17) | `06MUT-M3_..._02_ROJO_mutante.txt` | 2 failed / 3 passed |
| M3 — intacto | `05MUT-M3_..._01_VERDE_intacto.txt` | 5 passed |

Cada archivo guarda la selección exacta, el `sha256[:12]` del código intacto y la confirmación de
que el árbol volvió a la pre-imagen.

## Consecuencia declarada para FASE-E2E (no es un hallazgo nuevo, es el diseño)

Con este criterio, la propuesta del run único de Don Alfonso **sí** producirá CRITICAL por los dos
absolutos de prosa de garantía más la celda «(Verificado)» de la tabla de timeline: el veredicto
esperado es `BLOQUEADO` y el ZIP quedará en cuarentena. AC14 ya prevé esa salida y pide que el acta
nombre el hallazgo bloqueante y que **esta medición** diga si es verdadero o falso positivo: según
el criterio de arriba, los tres son **verdaderos** (lenguaje de verificación y absolutos de garantía
con `evidence_tier` B+), y los que dejaron de emitirse (3 totales financieros y 5 `100%` de tabla)
eran los falsos. Dueño de la decisión si el operador prefiere otro umbral: FASE-VERIFY lee esta hoja
junto con el acta.

## Lo que esta fase NO cura

- `evidence_tier == "UNKNOWN"` sigue silenciando el check de Bot 4: es AC11 (FASE-C).
- Que un estado `INPUT_NOT_EVALUABLE` impida `APROBADO-PARA-ENTREGA` pero **no** suprima el ZIP:
  `verified_critical` exige `status.is_ok` y eso vive en `judge.py` (FASE-C). Registrado en
  `10-analisis-post-implementacion.md` §Seguimientos con dueño.
