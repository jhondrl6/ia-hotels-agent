# `instantaneas/` — copias versionadas de lo que el write-back publicó

Un archivo por publicación hecha con `scripts/validate_qmind_writeback.py --upload <PLAN> --file … --title …`
(o con `--upload` a secas): aquí queda la **instantánea** de los bytes que se ingerieron, con su sha256
registrado en `../registro.json`.

**Qué sirve.** `verificar_contenido()` no pregunta «existe una fuente con ese título», y desde la cura de
`CURA-INSTRUMENTOS-QMIND-S15-2026-10-07` (FASE-A1, schema `1.1`) tampoco compara esta copia contra el cuerpo del
plan. Son **tres** comprobaciones con identidad propia:

- **¿el plan cambió?** → `sha_cuerpo` (el sha del cuerpo del repo en el momento de publicar, grabado en el
  registro) contra el sha del cuerpo actual. Esta es la puerta de vigencia.
- **¿la copia del repo sigue siendo lo que se publicó?** → `sha256` del registro contra el sha de esta copia.
- **¿lo publicado casa con el servidor?** → `metadata.fileSha256` del `source list` como primera vía y la
  **descarga + sha256** como verificación de esa promesa (`PROMESA-ROTA` si la descarga la desmiente).

Por eso publicar una **copia saneada** (`--file`) deja de ser estructuralmente vencible: los bytes ingeridos y el
crudo del plan son dos cosas distintas y el registro guarda las dos identidades. Sin la copia en el repo no hay
con qué casar la segunda y la tercera pregunta, y el veredicto sería una opinión sobre un título.

**Las entradas `1.0` no se rellenan.** Una entrada anterior a la cura no tiene `sha_cuerpo` y sale
`NO-EVALUABLE por migracion`: calcular el sha de hoy y escribirlo en la entrada vieja daría verde por
construcción. El resumen del verificador imprime un `[CONTADOR]` con cuántas entradas se dictaminaron por cuerpo,
cuántas tuvieron fidelidad remota medida y cuántas quedaron NO-EVALUABLE.

**Nace vacío y así debe leerse.** Cero archivos = cero publicaciones registradas; el check `[17/18]` declara
`NO-EVALUABLE` en ese estado y **no** PASS. Hoy hay dos entradas del plan padre y **un solo** byte-exacto: las dos
publicaciones compartieron nombre por el slug truncado, así que los bytes de la primera están perdidos. Gobernar el
nombre (AC3) ya no es prosa pendiente: lo gobierna `slug_de_instantanea()` desde FASE-A2.

**Cómo se nombra una instantánea (AC3 landed, 2026-10-08).** El nombre es
`<plan>--<título-saneado>--<huella>.md`: el prefijo legible conserva `plan` y `titulo` con todo lo que no sea
`[A-Za-z0-9._-]` convertido en `_`, y la `huella` son los 16 primeros hexádigitos del `sha256` que la propia
entrada declara. El presupuesto total (`NOMBRE_INSTANEA_MAXIMO`, 120 caracteres) se reserva **desde el final**:
la huella siempre cabe y el recorte cae sobre el prefijo. Dos contenidos distintos no pueden compartir nombre,
y como todo nombre termina en `--<hex>.md`, ninguno puede ser `README.md` — el archivo que sigue en este
directorio lo escribe un humano y el escritor no lo toca.

**Escritor único:** `validate_qmind_writeback.py` (`registrar_publicacion()`). No editar a mano: un archivo
aquí que no corresponda a una subida real convierte la verificación en una promesa falsa.
