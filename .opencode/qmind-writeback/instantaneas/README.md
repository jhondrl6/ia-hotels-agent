# `instantaneas/` — copias versionadas de lo que el write-back publicó

Un archivo por publicación hecha con `scripts/validate_qmind_writeback.py --upload <PLAN> --file … --title …`
(o con `--upload` a secas): aquí queda la **instantánea** de los bytes que se ingerieron, con su sha256
registrado en `../registro.json`.

**Qué sirve.** `verificar_contenido()` no pregunta «existe una fuente con ese título»: compara el sha de esta
copia contra el cuerpo del plan (¿el publicado sigue siendo el cierre?) y, por la vía remota, contra lo que el
notebook entrega (`metadata.fileSha256` como primera vía y la descarga como verificación de esa promesa). Sin
la copia en el repo no hay con qué casar, y el veredicto sería una opinión sobre un título.

**Nace vacío y así debe leerse.** Cero archivos = cero publicaciones registradas; el check `[17/18]` declara
`NO-EVALUABLE` en ese estado y **no** PASS. La primera entrada la escribe el momento B del plan
`VERIFICADOR-ESCRITURA-QMIND-2026-09-20` (maestro §6): la ingesta de cierre del plan padre, con autorización
literal y presupuesto propios.

**Escritor único:** `validate_qmind_writeback.py` (`registrar_publicacion()`). No editar a mano: un archivo
aquí que no corresponda a una subida real convierte la verificación en una promesa falsa.
