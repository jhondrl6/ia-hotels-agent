# Constancia — verificación obligatoria de la Tarea 1: ¿el ZIP empaqueta el acta?

> Ordenada por `evidence/FASE-P1/decision-enforcement.md` §DA-P1.4, último punto:
> *«Verificación obligatoria en P2 (abierta aquí, no improvisable): comprobar si el ZIP
> empaqueta el acta (ActaWriter escribe en v4_audit_dir). Si la contuviera, el acta
> publicada debe ser la enriquecida, nunca la pre-veredicto»*.
> El prompt de FASE-P2 la repite como criterio de la Tarea 1 con la cláusula
> *«anotar el resultado en la evidencia aunque no exija cambio»*.

## Resultado medido

**Sí lo empaquetaba.** Sobre el único ZIP de una corrida real que queda en el árbol de
trabajo (`output/` está en `.gitignore`, así que esta es la muestra disponible, no una
selección):

```
$ python -c "import zipfile; \
  print(zipfile.ZipFile('output/v4_complete/deliveries/hotelsalentoreal_20260911.zip').namelist())"
total members: 40
  ...
  ASSETS/v4_audit/acta_revision.json
  ASSETS/v4_audit/acta_revision.md
```

Causa estructural: `ActaWriter` escribe en `v4_audit_dir = output/<hotel>/v4_audit`, y
`DeliveryPackager._collect_files` recorre `source_dir.rglob("*")` con
`source_dir = output/<hotel>`. El acta cae dentro del barrido y viaja como
`ASSETS/v4_audit/acta_revision.*`. El único filtro que la descartaba era el de frescura
(`mtime >= latest_run_ts − 60 s`), y en una corrida normal **la cumple**, porque el Juez
escribía el acta justo antes del packaging.

## Por qué el enunciado es insatisfacible bajo O1-cuarentena

La cláusula pide que, si el ZIP contiene el acta, esa copia sea **la enriquecida**. La
secuencia contractual de DA-P1.4 hace que eso no pueda cumplirse:

```
write()  → serializa los bytes del ZIP          (aquí se fijaría el miembro del acta)
  ↓
4 Bots   → leen MANIFEST.json / IMPLEMENTATION_ORDER.md / ASSETS/ **de ese ZIP**
  ↓
enrich() → el Juez decide con los informes      (el acta enriquecida nace aquí)
  ↓
publish()/suppress()
```

El acta enriquecida **necesita** los informes; los informes **necesitan** el ZIP; el ZIP
necesitaría contener el acta enriquecida. No es un problema de orden resoluble moviendo
la escritura: es un círculo estricto. Y su alternativa material —reescribir los miembros
del `.tmp` tras el veredicto— es un segundo pase de escritura sobre el mismo archivo, que
es la opción **O3 descartada en DA-P1.4**, además de romper la consistencia
`MANIFEST.files[].size_bytes` que `_validate_zip` defiende.

## Decisión derivada

`DA-P2.1` (en `10-analisis-post-implementacion.md`): **el acta deja de viajar en el
paquete de cliente**. Se excluye por nombre en
`DeliveryPackager._INTERNAL_DOC_PREFIXES = ("acta_revision",)`, junto a la ruta que ya
usaba `_is_excluded_from_zip` para los reportes internos de gates.

Consecuencias verificables:

- El ZIP publicado **no puede** contener un acta pre-veredicto ni vieja: no contiene
  acta. El enunciado de DA-P1.4 queda satisfecho en su propósito (que el paquete nunca se
  contradiga a sí mismo) y ya no depende del orden de la corrida.
- El acta vive donde el contrato §3.3 dice que mira el operador: `v4_audit/`, junto al
  `delivery_blocked` implícito en el stdout del bloqueo.
- El miembro desaparece del `MANIFEST.json` y del conteo de `_validate_zip` con el mismo
  cambio, porque ambos se derivan de `_collect_files`.
- **Cambio visible para el cliente** (un paquete con 2 miembros menos): se declara en el
  CHANGELOG de FASE-RELEASE, no en silencio.

## Test que fija el resultado

`tests/delivery/test_p2_cuarentena_zip.py::test_el_paquete_no_contiene_el_acta` — escribe
un `acta_revision.json`/`.md` **viejos** en `v4_audit/` antes de empaquetar (simulando el
re-run sobre un directorio con residuos, que es el caso que el filtro de frescura no
garantiza) y afirma que ni el ZIP ni su MANIFEST los contienen. Verde con la exclusión; el
invariante no tiene mutación NR7 propia porque **no es un AC del contrato** sino la
respuesta a una verificación — su evidencia es esta constancia más el test.
