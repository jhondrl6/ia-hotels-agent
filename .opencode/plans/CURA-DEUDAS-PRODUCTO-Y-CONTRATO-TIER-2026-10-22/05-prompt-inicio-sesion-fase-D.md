# FASE-D — `R1`: contrato GBP en los dos caminos (`D28`, `N2`, `N3`, `DA-C3`)

**ID**: FASE-D · **Plan**: `CURA-DEUDAS-PRODUCTO-Y-CONTRATO-TIER-2026-10-22`
**Objetivo**: un solo vocabulario para el perfil GBP, aplicado tanto al detector de `v4audit` (`get_detected_issues`) como al de `v4complete` (`PainSolutionMapper`/`map_brecha_to_issue_type`); “sin schema” deja de ser “perfil abandonado”; un perfil completo produce 0 brechas y 0 COP falsos.
**Dependencias**: FASE-A ✅.
**Complejidad técnica**: ALTA · **Duración estimada**: 3-4 horas
**Modo de ejecución**: **DIRECTO** (decisión arquitectónica cross-module; regla DT-3).

## Contexto

`get_detected_issues` espera claves en inglés (`claimed`, `photos`, `has_whatsapp`, `has_hours`, `has_faq`) y un `schema_data` que su llamador pasa siempre `{}`. `_base_profile()` escribe español (`existe`, `fotos`, `horarios`, `whatsapp_visible`, `website`, `posts`, `tiene_qa`). Sobre un perfil perfecto devuelve 6 brechas y `calculate_impacts` produce 39.600.000 COP/mes en el reproductor sintético. Pero el baseline de `v4complete` **no usa ese detector**: usa `PainSolutionMapper.detect_pains` y `v4_diagnostic_generator._map_brecha_to_issue_type`, que **también** convierte `no_hotel_schema` y `low_citability` en `PERFIL_ABANDONADO`. Curar solo `get_detected_issues` dejaría viva la misma semántica en el camino que sí entrega el diagnóstico.

`gbp_leak_detector.py` es un módulo sin importador de producción y conserva el vocabulario español correcto; su lógica se sustituye, no se borra sin relevo. `N2` colapsa `PERFIL_ABANDONADO` y `CERO_ACTIVIDAD_RECIENTE` en la misma etiqueta.

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-A | ✅ |

### Base Técnica Disponible
- `modules/utils/dynamic_impact.py` (`get_detected_issues`, `calculate_impacts`, `PERDIDA_MENSUAL_BASE`)
- `modules/scrapers/gbp_auditor.py` (`_base_profile`, `_detectar_fugas`, `tipo_map`)
- `modules/scrapers/gbp_leak_detector.py` (`_detectar_fugas` con vocabulario español)
- `modules/commercial_documents/pain_solution_mapper.py` (`detect_pains`, los `Pain` de `v4complete`)
- `modules/commercial_documents/v4_diagnostic_generator.py` (`_map_brecha_to_issue_type`, `_identify_brechas`)
- `modules/auditors/v4_comprehensive.py` (`_audit_gbp`, datos que alimentan el diagnóstico)

### Lecciones capitalizadas aplicables a esta fase

| ID | Lección (una línea) | Qué cambia en ESTA fase |
|----|---------------------|-------------------------|
| D-T4B-A1 | Una suite verde puede certificar sin ejercitar el contrato real | Tarea 3 prueba con la forma real de `_base_profile()` y con `PainSolutionMapper` |
| L-SR3 | Una sola fuente de verdad para el estado de un servicio | Un vocabulario, dos caminos |
| DA-C3 | vacío ≠ ausente | `None` = no medido; `{}`/sin schema = medido ausente; schema válido = presente |
| L-T4A.5 | Un test puede pasar sin ejecutar la rama que dice certificar | Mutation check: claves inglesas restauradas → 6 brechas |
| L-V2 | Quien cambia un contrato barre sus consumidores | El mapa de `_map_brecha_to_issue_type` es consumidor del mismo contrato |

## Tareas

### Tarea 1: Gate de `gbp_leak_detector`
**Objetivo**: confirmar el destino por defecto (sustitución, no borrado): su lógica de vocabulario español se porta como implementación del contrato y la copia muerta se retira tras el relevo, con test que la releve.
**Criterios de aceptación**:
- [ ] Decisión escrita en `10-analisis` §Decisiones antes de editar código
- [ ] El test de relevo demuestra que la lógica portada produce el mismo resultado que la copia muerta sobre el mismo perfil

### Tarea 2: Vocabulario único y schema tri-estado
**Objetivo**: `get_detected_issues` consume la forma real de `_base_profile()`; `PainSolutionMapper` y `_map_brecha_to_issue_type` usan el mismo vocabulario. `schema_data` distingue `None` (no medido), `{}`/`tiene_hotel_schema=False` (medido ausente) y schema válido (presente).
**Archivos afectados**: `modules/utils/dynamic_impact.py`, `modules/scrapers/gbp_auditor.py`, `modules/scrapers/gbp_leak_detector.py`, `modules/commercial_documents/pain_solution_mapper.py`, `modules/commercial_documents/v4_diagnostic_generator.py`.
**Criterios de aceptación**:
- [ ] Las cuatro claves inglesas desaparecen del contrato; el productor y los dos caminos comparten vocabulario
- [ ] `PERFIL_ABANDONADO` se decide por actividad del perfil, no por ausencia de schema
- [ ] `no_hotel_schema` y `low_citability` dejan de mapearse a `PERFIL_ABANDONADO`; `no_og_tags` deja de mapearse a `FOTOS_INSUFICIENTES` o se justifica por escrito
- [ ] `schema_data=None` no dispara brecha; `schema_data={}` sí distingue “medido ausente”

### Tarea 3: Diente de frontera (AC3) + mutation check
**Objetivo**: perfil completo (reclamado, 40 fotos, 4.6, 120 reseñas, horarios, whatsapp, website, actividad, Q&A) → **0 brechas** en `get_detected_issues` y **0 brechas** en `PainSolutionMapper`; `calculate_impacts` sobre perfil perfecto → **0 COP**.
**Criterios de aceptación**:
- [ ] Verde con el fix; mutante (claves inglesas restauradas) → 6 brechas; par en `evidence/…/FASE-D/`
- [ ] El test de `PainSolutionMapper` usa la forma real del audit de `v4complete`, no un fixture del detector
- [ ] La cifra de `calculate_impacts` sobre perfil perfecto es 0 (hoy: 39.600.000 COP/mes en el reproductor)

### Tarea 4: `N2` etiqueta propia y relevo
**Objetivo**: `CERO_ACTIVIDAD_RECIENTE` con etiqueta propia; dos entradas de `tipo` idéntico imposibles; los textos no repiten la misma queja.
**Criterios de aceptación**:
- [ ] `tipo_map` no colapsa las dos brechas
- [ ] El test de deduplicación aguas abajo demuestra que no se undercounta
- [ ] La copia muerta se retira o se marca tras el relevo

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| diente perfil completo | `tests/` (nuevo, forma real de `_base_profile`) | 0 brechas; rojo con mutante |
| diente `PainSolutionMapper` | `tests/` (nuevo) | 0 brechas con el audit de `v4complete`; mapa sin schema→abandono |
| schema vacío/ausente | `tests/` (nuevo) | `None` ≠ `{}`; dos resultados legibles |
| relevo de `gbp_leak_detector` | `tests/` (nuevo) | La lógica portada coincide con la copia muerta |

**Comando de validación**: `./venv/Scripts/python.exe -m pytest <tests-nuevos> -q` + `run_all_validations.py --quick`. Par pre/post (R2.3).

## Post-Ejecución (OBLIGATORIO)

1. `dependencias-fases.md`: FASE-D ✅.
2. `README.md`: progreso por referencia a `09` §D.
3. `09-documentacion-post-proyecto.md`: B/D/E de la fase.
4. `10-analisis-post-implementacion.md`: decisión de `gbp_leak_detector`, fila, lecciones y seguimientos.
5. `00-lecciones-capitalizadas.md`: anotar las lecciones citadas.
6. `evidence/…/FASE-D/`: pares rojo/verde, crudo del relevo y `baseline-pre-post.md`.
7. **Derivados al día, como último paso del cierre** (herencia medida de FASE-A y FASE-B): re-publicar el artefacto de Wiring con `validate_wiring.py --write-report` si la fase añadió archivos versionados —un `.py` nuevo en `tests/` **o** en `evidence/` mueve contadores—, y re-publicar el par del índice con `build_lesson_index.py` si la fase anotó lecciones **citando IDs del vocabulario** en `00-lecciones` o `10-analisis` (la prosa que no cita ninguno no lo vence). Verificar los dos con `--check` y leer el exit **sin tubería**: `run_all_validations.py --quick` no goberna la frescura del índice, pero el hook `[6/8]` del pre-commit la corta y bloquea el commit.

Registro:
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-D --fecha <fecha-de-cierre-de-esta-fase> \
    --desc "R1: contrato GBP único en v4audit y v4complete, schema tri-estado y N2 (D28/N2/N3, AC3)" \
    --archivos-nuevos "<rutas nuevas>" --archivos-mod "<rutas modificadas>" --tests "N" --check-manual-docs
```

## Criterios de Completitud (CHECKLIST)

- [x] Gate de `gbp_leak_detector` escrito; relevo probado — decisión `DA-PLAN-9` escrita antes de editar código; matriz perfil a perfil contra la copia real en `evidence/…/FASE-D/relevo-cruce.txt`; copia marcada como retirada (oráculo vivo)
- [x] Vocabulario único en ambos caminos; schema tri-estado — 4 claves inglesas retiradas; `None` ≠ `{}` con resultados legibles (tests `TestSchemaTriEstado`)
- [x] 0 brechas y 0 COP sobre perfil completo; mutante en rojo — diente con la forma real de `_base_profile` (0 brechas, 0 COP); M1 reproduce 6 brechas / 39.600.000 COP/mes (`02-rojo-mutante-m1-claves-inglesas.txt`)
- [x] `N2` sin etiquetas colapsadas; `--quick` verde — `tipo_map` inyectivo, dedupe sin undercount, textos distintos; `--quick` 13/13 (EXIT=0, crudo `12-quick-final.txt`)
- [x] Cinco cortes sin commit; lecciones registradas; evidencia preservada — 5 cortes declarados (implementación → verificación → cierre documental → listo para revisión → espera de autorización), 0 commits; lecciones en `00-lecciones` §5.3 y `L24`; crudos 01–07 + `baseline-pre-post.md` + `par-rojo-verde.md`
- [x] Derivados re-publicados y verificados con `--check` como último paso (Wiring si la fase añadió archivos versionados; índice de lecciones si se citaron IDs del vocabulario), con el exit leído sin tubería — crudos 08–11 y re-verificación final 14–15

## Restricciones

- Presupuesto: tope **60 tool-use**; corte «listo para revisión»; instrumento legado/no comparable si no aplica.
- **No** tocar umbrales numéricos (FASE-F), `booking_scraper` (FASE-H1), `S-CST-1`, archivos congelados ni `v4complete`. El E2E no ejercita `get_detected_issues`: la evidencia de AC3 es el diente de esta fase.
- Citas por símbolos (R2.2).

## Prompt de Ejecución

```bash
Actúa como especialista en el repo iah-cli. Ejecuta únicamente FASE-D del plan .opencode/plans/CURA-DEUDAS-PRODUCTO-Y-CONTRATO-TIER-2026-10-22.
Lee 05-prompt-inicio-sesion-fase-D.md, 01-plan-maestro.md §1, §2, §4 y §5, 00-lecciones-capitalizadas.md §2, dependencias-fases.md y workflow canónico.
OBJETIVO: contrato GBP único en los dos caminos, schema tri-estado y N2; 0 brechas/0 COP sobre perfil completo.
TAREAS: 1 gate de gbp_leak_detector, 2 vocabulario + schema tri-estado, 3 diente AC3 + mutation, 4 N2 y relevo.
CRITERIOS: AC3 (0 brechas en ambos caminos, 0 COP); par rojo/verde en evidence.
VALIDACIONES: pytest; --quick; log_phase_completion.py al cierre.
```
