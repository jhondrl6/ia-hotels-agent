# 03 — Rectificaciones B1, B2 y B3 (texto antes, texto después, numstat y segundo camino)

Regla de gobierno que manda sobre el cómo: `ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md` §4.C, cierre —
«los estados actuales incorrectos se rectifican con atribución, no se reconstruye el pasado». Ninguno de
los tres textos falsos se borró: los tres se **conservan** y se anotan con el recurso que el árbol ya
usa, `⟦…⟧` (U+27E6 / U+27E7) con **fecha** y **causa**.

La forma se copió de los dos precedentes correctos del propio árbol, que se leyeron antes de escribir:
`06-checklist-implementacion.md` (casilla ⟦E5⟧, anotación «Vencido en parte el 2026-09-24» sobre las
líneas del span 163-168) y `10-analisis-post-implementacion.md` (fila «Contrato de C cerrado el
2026-09-23», con su anotación homóloga). El árbol no ganó una cuarta variante del recurso.

---

## B1 — `.opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/README.md`, bloque de cabecera

**Antes** (línea 18 de la cabecera, íntegra):

> **Estado de B: consultar §13 de la fuente única enlazada abajo.** El bloque B está autorizado;
> el bloque C y el piloto FASE-C no lo están. Fuente única de resultados y estados D1/S13:

**Después** (releído desde disco, UTF-8; el texto anterior sigue literal, con el bloque anotado
incrustado a media línea):

> el bloque C y el piloto FASE-C no lo están. ⟦**Vencido en parte el 2026-09-24 y rectificado el
> 2026-09-24 al medirlo**: de esta frase queda en pie solo la segunda mitad — **el piloto FASE-C sí sigue
> sin autorización**. El **bloque C** de `ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md` **sí está autorizado
> y ejecutado desde el 2026-09-24**, y lo que ejecutaron fueron **enmiendas documentales sobre los cuatro
> planes**; su matriz y su veredicto viven en el único resumen de C,
> `evidence/…/BLOQUE-C-ENMIENDAS-2026-09-24/02-resultados-bloque-c.md`. **Y eso no es FASE-C**, en los dos
> sentidos que este plan distingue: las enmiendas no ejecutaron ninguna fase de los cuatro planes, y lo
> único que separa el estado actual del cierre de la orden sigue siendo el piloto. **Causa**: dos
> afirmaciones contradictorias vivas en este mismo archivo —más abajo ya se declaraba el bloque C
> ejecutado y «eso no es FASE-C»—, sin que la cabecera se llevara detrás de esa corrección y sin
> anotación alguna en torno a la frase falsa. **Autoría no atribuible por evidencia**: la frase no está en
> `HEAD` y no la registra ni el expediente de B ni el de C, que comparten este mismo árbol sin
> commitear; no se le inventa dueño.⟧ Fuente única de resultados y estados D1/S13:

El lector de la cabecera acierta **sin saltar**: la anotación dice el estado correcto, dice que el bloque
C no es FASE-C y dice que lo pendiente es el piloto. No se remite a un «véase §X».

**Numstat contra HEAD**: `44 23` antes de esta sesión → **`56 23`** después. Doce líneas añadidas y
**cero borradas**: las 23 supresiones que ya estaban en el árbol sin commitear no se movieron.
**Delta propio medido por difflib** (`03b`): 1 hunk, +13 líneas / −1, 1.196 caracteres dentro de `⟦…⟧`, y
el resto del hunk es byte a byte el texto anterior.

## B2 — `.opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/06-checklist-implementacion.md`, cabecera

Mismo texto falso, misma rectificación, **mismo bloque anotado literal** (para que el par de cabeceras
del plan no diga dos cosas distintas del mismo hecho). Su cita verificable:

> el bloque C y el piloto FASE-C no lo están. ⟦**Vencido en parte el 2026-09-24 y rectificado el
> 2026-09-24 al medirlo**: … ⟧ Fuente única de resultados y estados D1/S13:

Este archivo **sí** conocía su propio vencimiento: la casilla ⟦E5⟧ ya llevaba desde el 2026-09-24 la
anotación «**Vencido en parte el 2026-09-24**: el **bloque C** … se autorizó y ejecutó ese día … **el
piloto FASE-C sí sigue sin autorización**». Lo que no tenía era la cabecera: el documento se conocía a sí
mismo por el pie y arrancaba con la frase falsa.

**Numstat contra HEAD**: `54 17` → **`66 17`** (+12, cero borradas). **Delta por difflib**: 1 hunk, +13/−1,
1.196 caracteres anotados, el resto idéntico.

## B3 — `evidence/…/BLOQUE-C-ENMIENDAS-2026-09-24/02-resultados-bloque-c.md`, renglón JEV de la matriz §1

**Antes**, en la columna «Cambio necesario» del renglón JEV:

> **gap de contrato medido y declarado**: 8 de los 11 campos del piloto no están en la costura, con la
> decisión que sí queda (requested-vs-effective y `usage_normalized`) …

**Después**: el «8» **no se sobrescribió**. Se insertó, pegado a la frase y dentro de la misma celda, un
bloque `⟦…⟧` (1.498 caracteres, sin saltos de línea para no partir la fila de la tabla de 6 columnas) que
publica **los dos métodos y sus dos cifras**, el comando que los produjo y la declaración de que el
consumidor ya traía la cifra correcta. En concreto:

- **Por nombre literal**: de los once nombres exigidos **solo `request_id`** aparece en
  `scripts/decision_client.py` → faltan **10 de 11**.
- **Por identidad semántica declarada** (`proveedor`≈`provider_effective`, `modelo`≈`model_effective`,
  `respuestas`≈`answers`, `usage`≈`usage_raw`, más `request_id` por su propio nombre) → faltan
  **6 de 11**, que son `provider_requested`, `model_requested`, `usage_normalized`, `elapsed_ms`,
  `attempts`, `error_kind`. **Esa es la cifra vigente.**
- El «8» **no reproduce ninguno de los dos métodos**.
- El consumidor real del contrato, `EVALUACION-JEV-TYPESAFE-2026-09-21/README.md` en su párrafo «Gap de
  contrato medido», **ya publicaba los seis** desde antes de esta sesión. Por eso **ese README no se
  editó**: no estaba mal. Lo que estaba mal era el resumen único de C respecto al plano al que C sirvió,
  y se anota **aquí**, en el expediente, que es donde vive la cifra desincronizada.

**Numstat**: el archivo está **sin trackear**, así que `git` no le da numstat. Su delta se midió por
difflib contra la copia congelada en `antes/` (`03b`): **190 líneas antes y 190 después**, 1 hunk de
1 línea, 0 líneas de tabla ganadas o perdidas (`filas por bloque: [8, 6, 14] → [8, 6, 14]`), y **cero**
bloques de tabla con columnas desiguales antes y después. La fila de §1 sigue teniendo sus seis columnas
y sus cinco renglones hermanos intactos.

---

## Segunda vía de cada verificación (M7: no auditar el verde con el instrumento que lo produjo)

| Propiedad | Primer camino | Segundo camino, independiente |
|---|---|---|
| B1/B2 rectificados | el barrido reparado los mueve de `c-1` a `b-1` (2 → 0 en `c-1`, `02-barrido-reparado.txt`) | la **fuente autorizada del hecho**, no la anotación: `ORDEN-…-2026-09-22.md` §5, fila «Alcance de implementación» («**C autorizado y ejecutado el 2026-09-24 en su parte documental** … **El piloto sigue sin autorizar**») y su bloque `⟦Estado del bloque C el 2026-09-24⟧` al pie de §4.C |
| B3 rectificado | la anotación insertada | **los lectores del contrato**: `JEV/README.md` (seis nombres, verificados uno a uno en `03b`) y `JEV/01-plan-maestro.md` (los once, extraídos por el instrumento de la línea «Contrato requerido para el piloto», no tecleados a mano) |
| «no se movió nada más» | difflib `antes/` vs disco + `⟦…⟧` suprimido recuperable | **otro instrumento**: `git diff --numstat` contra HEAD, donde las **supresiones no cambian** (23 → 23 y 17 → 17) y sólo crecen las adiciones |
| los 3 archivos son los únicos tocados | `huellas.py compare` sobre 56 rutas: 3 cambiados, 53 idénticos | `git status --porcelain` contado por ruta sobre `.opencode/plans/Archives/` y los dos expedientes de B: **0 modificados** |

---

## Defectos propios de esta sesión, declarados (un rojo propio se arregla; ninguno se tapa)

1. **Comprobación de EOL falsa.** `grep -c $'\r'` sobre un archivo devolvió «237», que es **el número de
   líneas**, no de retornos de carro: el patrón degenera a vacío y casa todo. Sobre esa lectura decidí que
   los tres objetivos eran CRLF y el primer aplicador **inyectó 12 CR en archivos LF puros**. Detectado
   por el propio aplicador (`CR antes/despues: 0 / 12`), que no daba por supuesta la lectura del grep.
   Arreglado: medida repetida con dos instrumentos (`tr -dc` y `Python`), restaurados los dos archivos
   desde `antes/` (sha256 verificado idéntico al PRE) y el aplicador pasó a **heredar el EOL del archivo**.
   Ninguno de los tres objetivos estaba en CRLF: los tres son LF puro.
2. **Ventana de anotación insuficiente.** La primera versión del barrido buscaba una pareja `⟦…⟧`
   **completa** dentro de ±6 líneas. Mi anotación abre en la propia línea falsa y cierra trece líneas más
   abajo, así que en POST devolvía un falso «vencida sin anotación». Arreglado con **spans** por archivo
   (`anotado()`), con su control positivo impreso y con el límite declarado.
3. **Corchete equivocado en el verificador M5.** `\N{LEFT WHITE SQUARE BRACKET}` **no** es U+27E6:
   resuelve a U+301A. El supresor de anotaciones no encontraba nada y el predicado «el original es
   recuperable» daba un falso «NO» permanente. Corregido a `chr(10214)`/`chr(10215)` y añadido un control
   que exige que el supresor **encuentre** los 12 spans `⟦…⟧` de `06-checklist` —3 de ellos con patrón
   de rectificación, y el precedente de E5 entre ellos— y que suprimirlos deje estrictamente menos
   caracteres (24.430 < 26.271), antes de creer cualquier resultado suyo.
