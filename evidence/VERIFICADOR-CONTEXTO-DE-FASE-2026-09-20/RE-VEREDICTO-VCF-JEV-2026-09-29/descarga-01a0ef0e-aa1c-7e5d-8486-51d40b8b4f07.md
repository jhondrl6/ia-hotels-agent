# Lección — una orden de re-verificación arranca por la matriz vigente de la fuente única
# (2026-09-28)

**Regla.** Toda orden de re-verificación arranca leyendo **la matriz vigente de la fuente única** del
plan, antes de re-medir cualquier hallazgo. En este repositorio esa fuente es
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-B-REMEDIACION-2026-09-23/00-resumen-cierre-B.md`
y su **§13** es la única matriz vigente: §1–§12 son antecedentes rectificados, no aceptación actual.

**Por qué (medido, no asserted).** La orden que se curó el 2026-09-28 llevaba dos hallazgos que su
propia fuente única ya había juzgado:

- «D1 con dueño colgante» — refutado por §13, que dice «**D1 CERRADA** en su alcance». La pasada del
  censo omitió la fila D1 y el censo salió con una fila muerta de más.
- «12/16 vencido» — congelado por la anotación que el propio plan se puso el 2026-09-26 en AC16 de su
  maestro, y por §11-17, que rechazó re-copiar la cifra del día («copiar 4,453 en `AGENTS.md` sería
  publicar la cifra que el próximo commit invalida»). Medido el 2026-09-28, los denominadores vivos del
  verificador ya eran **quick 13 / completo 17**, o sea que la foto que se quería «actualizar» había
  caducado dos veces.

Y una tercera consecuencia del mismo modo de fallar: los veredictos que la orden traía como heredados
tampoco casaban con su fuente. AC12 y AC14 llegaban como `PARCIAL` y su propio cierre de fase los había
certificado `CUMPLIDO` y `CUMPLIDO — con rojo` en
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/criterios-de-completitud.md`.

**Cómo se aplica.**

1. Leer la matriz vigente y sus filas RECHAZADO antes de medir.
2. Tratar todo estado heredado de un resumen, un transcript o una orden anterior como **hipótesis**: se
   re-mide contra disco o caduca.
3. Publicar cada cifra **con su comando y su población**. El par 518/66 de la fila §S17 no reproduce con
   ningún ancla, con ningún instrumento, ni en la revisión que lo firmó — y las cifras que traía esta
   orden tampoco: 174/32 y 793/77 corresponden a **todos los ficheros versionados** y a un árbol con
   archivo sin versionar dentro, mientras la fila habla de «corpus marcado versionado» (`.md`), que da
   167/29 y 604/73.
4. Un veredicto sobre el trabajo de otra sesión vive en el **expediente**, no en el plan anotado.

**Límite de la regla.** Leer la matriz no exime de re-medir: el 2026-09-28 la matriz estaba bien y aun
así cinco afirmaciones en presente del corpus estaban contradichas por disco (F1–F5). La matriz dice
**cuál es el estado vigente**; el disco dice **si el texto lo refleja**.
