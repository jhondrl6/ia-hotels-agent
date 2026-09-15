# Informe de observación — FASE-P4 (corrida con datos reales)

**Plan**: TRIBUNAL-ENFORCEMENT-OBS-2026-09-11 · **Fase**: FASE-P4
**Fecha de la corrida**: 2026-09-14, 18:36–18:39 (≈3 min de reloj)
**Comando ejecutado**: `python main.py v4complete --url https://hoteldonalfonso.com/ --output output/FASE-P4_donalfonso_obs`
**Hotel**: Hotel Don Alfonso (Pereira, `eje_cafetero`, `boutique_10_25`) · 11 hab · ocupación derivada 42,4 % · ADR 330 000 COP · canal directo 30 %
**Modo**: **observación**, no entrega a cliente. No se entregó ZIP a tercero; de hecho no se publicó ninguno (§punto 2).

> **Cifras COP**: los valores monetarios de este hotel quedan **solo** en
> `evidence/FASE-P4/corrida/detalle-valores.md` (ruta gitignoreada). El remoto
> `github.com/jhondrl6/ia-hotels-agent` es **público** (medido con `gh repo view --json visibility`
> → `PUBLIC`), y el paquete de corrida es material de cliente real. Aquí se citan campos, etiquetas
> de precision y relaciones, no las cifras.
>
> Distinción que hace falta explicitar: los **datos de entrada** del hotel (11 hab, 140 reservas/mes,
> ADR 330 000, 30 % directo) ya son públicos en este repo — `data/hotel_observations/observations.json`
> está versionado y empujado. Lo que **no** era público y sí se genera en la corrida son las
> **proyecciones derivadas** (pérdida esperada, escenarios, comisión OTA) y el diagnóstico/propuesta
> redactados: esos quedan fuera del control de versiones.

---

## 1. Qué se propuso observar y con qué decisión

Q4/DA-P1.9 fijó que **el hotel provee el dato por contacto del operador**. La Tarea 1 midió primero
si eso estaba cerrado; resultado en `t3a-sonda-candidatos.md`/`.json`:

| Hecho medido | Valor |
|---|---|
| Candidatos que resuelven en el pipeline | **6 de 6** en `data/hotel_observations/observations.json`, vía el fallback del cargador (`_load_latest_onboarding_data` → `_observation_to_onboarding_format`). Ninguno exige que el agente llene un YAML (línea roja i intacta) |
| Consentimiento registrado | **0 de 6**. No existe campo ni archivo por hotel → se cerró con la declaración del operador en `consentimiento-donalfonso.md` (2026-09-14) |
| Frescura | 54–60 días; **ningún verificador mecánico** aplica límite (el loader solo lo hace si `ONBOARDING_FRESHNESS_HOURS` está definida, y no lo está) → aceptado con límite escrito |
| Techo de tier medido antes de correr | `B_PLUS` para los 6 (`ga4_available=False`, `gsc_available=False`, con los predicados reales de AC-F5) |
| Baseline del delta | `evidence/FASE-E2E/` → **Salento Real**, `tier B`. No hay corrida previa de ningún otro candidato en `output/` |

**Efecto sobre el escenario de "cierre sin P4"**: **no aplica**. El disparador estaba redactado como
"si al iniciar P4 no hay dato con fuente", y **sí lo hay** — para seis hoteles, por una ruta que el
propio cargador ya resuelve. DA-P1.9 incluso declaraba "T3a satisfecha hoy" para Don Alfonso/Luxor.
Diferir P4 habría sido leer el disparador al revés.

**Coste de elegir un hotel distinto al del baseline**: el delta mezcla dos causas (hotel + pipeline).
Se declara en el §7 y no se disfraza.

## 2. Los 9 puntos del §5 del maestro

### Punto 1 — `evidence_tier` con dato real y primer piso
`financial_scenarios_*.json → breakdown.evidence_tier = B_PLUS` (serializado `"B+"`).
`first_floor_rule = {applied: true, reason: "evidence_tier B+ → máximo condicional", source_artifact:
"financial_scenarios_20260914_183818.json → breakdown.evidence_tier"}`.

**Tier A NO observado.** El techo vino de la analítica ausente, no del cableado (eso lo cerró AC-F5 en
P3-B): ver punto 9.

### Punto 2 — ¿alcanza `APROBADO-PARA-ENTREGA`?
**No, y por una vía distinta a la esperada.** Veredicto final `BLOQUEADO`. Secuencia medida en el log:

```
[OK] Paquete en cuarentena: .../deliveries/hoteldonalfonso_20260914.zip.tmp
FASE-T1b: Verdict: BLOQUEADO
⛔ ZIP SUPPRIMIDO: Tribunal verdict is BLOQUEADO.
```

Medido después: `deliveries/` queda **sin ningún `*.zip` ni `*.zip.tmp`**, y el acta conserva
`corrective_actions[]` con `owner` en cada entrada. Es la **primera observación en datos reales de los
dientes que P2 instaló** — antes de este plan ningún veredicto había impedido un paquete.

La **provisionalidad** que pedía el prompt ya no aplica: no hay enforcement pendiente (P2 cerró Q1=sí).

### Punto 3 — comportamiento de Bots 1–4 con dato rico
Los cuatro corrieron y los cuatro hallaron algo: `reviewer_reports` = 4 × `OK_WITH_FINDINGS`,
`critical_count = 1` cada uno, `verdict_recommendation = BLOQUEAR` en los cuatro.

| Bot | Hallazgo CRITICAL | Lectura |
|---|---|---|
| 1 `diagnosis_reviewer` | `VACUOUS_RECALL` | Preexistente del plan anterior: sigue vivo |
| 2 `alignment_reviewer` | `MISSING_ARTIFACT`: no existe `02_PROPUESTA_COMERCIAL*.md` | Ver §3.deps abajo |
| 3 `asset_reviewer` | `EMPTY_DELIVERY_TEMPLATE`: `IMPLEMENTATION_ORDER.md` 470 bytes, secciones vacías | **Detección verdadera en ZIP real** (§hallazgos F-P4.1) |
| 4 `honesty_reviewer` | `MISSING_ARTIFACT` (misma causa que Bot 2, redactada como `BLOQUEAR`) | Doble conteo (§hallazgos F-P4.2) |

Falsos positivos buscados y descartados: sospeché que Bot 3 había leído el ZIP de **otro** hotel (no
hay ZIP propio en el árbol final, y en `output/` sí hay tres `hotelsalentoreal_*.zip` con ese mismo
`IMPLEMENTATION_ORDER.md` de 468 bytes). **Descartado con el log**: el revisor corrió sobre el
`.zip.tmp` de **esta** corrida, que se suprimió después. No hay contaminación cruzada; el hallazgo es
que la plantilla del paquete es realmente un stub.

### Punto 4 — fidelidad del acta (lo que corrigió AC-F2)
`acta_revision.evidence_tier == "B+"` **coincide** con la fuente del escenario, y el `reason` del
primer piso cita `financial_scenarios_*.json`, no el MANIFEST. En esta corrida el MANIFEST **no
existe** (ZIP suprimido antes del publish), así que la divergencia C↔B del plan anterior **ya no es
alcanzable por la ruta vieja**: el acta se ancla a un artefacto anterior al packaging. **AC-F2
observado en real, no solo en test.**

### Punto 5 — gap advisory (revisores vs veredicto)
**No observable en esta corrida, y hay que decirlo sin rodeos.** La primera pasada del Juez
(`Verdict (pre-revision)`, antes de los 4 Bots) ya era `BLOQUEADO` por gates. Los revisores añadieron
4 CRITICAL y 4 acciones correctivas, pero **no cambiaron el resultado**: el caso que motivó Q1 —
*gates aprueban y un revisor objeta* — no se ejercitó. Los dientes están y se activaron, pero esta
corrida no prueba el contrafactual. Queda como límite de la fase (§5) y como material para AC-V1.

### Punto 6 — AC17/AC19 del predecesor con cifras reales
- `precision_tier = "C"` y `can_show_exact_money = False` → la política de no-show-exact funcionó con
  dato real (el dato operativo era Tier B+, no A).
- Fuentes del calculador con dato real: `adr = user_provided`, `occupancy = onboarding`,
  `direct_channel = onboarding`. En el baseline eran `regional_v410` / `regional` / `default`. **El
  pipeline consumió el dato verificado**; no fue un `B+` decorativo.
- Siguen siendo **una sola base de pérdida visible en el artefacto** (`expected_monthly_cop`); la
  segunda base que AC19/§5.5 reclamaba divergente no aparece como clave propia en el JSON de esta
  corrida → **AC19 no se puede cerrar mirando este artefacto** (R2.4: ⚠️, no ✅).
- Dato del hotel con contradicción interna ya registrada en `consentimiento-donalfonso.md`:
  `is_transit_hotel=false` (heurística de ocupación) contra `hotel_self_label="paso"` (auto-etiqueta).

### Punto 7 — delta vs la corrida E2E del predecesor (R2.3, L-VUP-14)
Instrumento: `diff_estructural_corridas.py`, con **selftest obligatorio antes de la corrida**
(`--selftest` → 15 artefactos parseados, 0 claves por artefacto = fallo, diff cero con input idéntico,
mutación plantada detectada). Salida: `corrida/detalle-valores.md`.

| Medida | Valor |
|---|---|
| Artefactos comparados con par | 14 |
| Cambios de valor | 435 |
| Artefactos del baseline **sin par** en la corrida | 1 → `ia_readiness_report.json` (F-P4.4) |
| Altas estructurales | `acta_revision`: `reviewer_reports`, `enforcement`, `corrective_actions` — las tres del contrato P2, ahora vistas en un artefacto real y no en un test |
| Claves que desaparecen | `audit_report`, `delivery_quality_report`, `gate_report`, `proposal_asset_matrix` pierden members (diferente hotelería y corrida bloqueada) |

**Los 435 cambios no son un delta de pipeline**: son dos hoteles distintos. El número que sí vale es
estructural (filas ALTA/BAJA arriba) y la coincidencia de las 6 cláusulas P6 en régimen nuevo.

### Punto 8 — estado real de `reviewer_reports` (NR8)
Longitud **4** (el `[]` del plan anterior desapareció del artefacto real). Los cinco miembros del enum
están cubiertos por los tests de P2; **esta corrida ejerció exactamente uno** (`OK_WITH_FINDINGS`).
No se vio `NOT_RUN` (no ocurrió: los Bots leyeron el `.zip.tmp`), ni `ARTIFACT_MISSING` como estado de
revisor (sí como tipo de hallazgo, que es otra cosa), ni `READER_FAILED`.

Sección `## Reportes de Revisores` **presente** en el MD, junto con `## Acciones correctivas` y
`## Enforcement` → AC-E0 verificado en un artefacto real.

### Punto 9 — banderas efectivas y techo de tier (AC-O0)
`ga4_available = False`, `gsc_available = False`, medidos **en la misma corrida** con los predicados
que AC-F5 hoistearon (`GoogleAnalyticsClient.is_available()`, `GoogleSearchConsoleClient.is_configured()`).
`enforcement.enabled = true` y el acta declara el knob `GATE_BLOCKING_ENABLED` (AC-E4).

**Dueño del techo: la analítica del hotel (T3b), no el pipeline.** El cableado quedó cerrado en P3-B y
la regla FASE-1 sigue exigiendo las dos conexiones. Para ver `A` hace falta GA4 **y** GSC del hotel, no
más código. La nota de "Tier A inalcanzable por construcción" queda **confirmada como superada** y
sustituida por esta: inalcanzable por falta de credenciales/propiedad del hotel.

## 3. Hallazgos nuevos (ninguno corregido aquí — L-V.4: hallazgo → seguimiento con dueño)

| ID | Hallazgo | Evidencia | Dueño propuesto |
|---|---|---|---|
| **F-P4.1** | `IMPLEMENTATION_ORDER.md` del paquete es un stub de ~470 bytes con secciones vacías, y lo es **también** en los tres ZIP de Salento Real. Con los dientes de P2, eso significa que **cualquier corrida real queda bloqueada por este CRITICAL**, entrega válida o no. El resolutor real está en `DeliveryPackager` (`if HAS_ASSET_CONTRACT and (core_assets or geo_assets)` → `AssetResponsibilityContract.generate_delivery_template`) | `revision_assets.json`, `acta_revision.corrective_actions`, hashes de los 3 ZIP | `equipo-assets` (ya nombrado en `corrective_actions`) + **decisión de producto**: ¿un stub debe bloquear? |
| **F-P4.2** | El bloqueo por gates ocurre **antes** de componer los documentos comerciales, así que `01_`/`02_` no existen y Bots 2 y 4 emiten CRITICAL por una causa ya resuelta por el gate. En cualquier corrida bloqueada, el acta tendrá ~2 CRITICAL inflados del mismo hecho y el veredicto no puede ser otro que BLOQUEADO | `BLOCKED_BY_GATES.md` (18:38:21) + `revision_alineacion.json` + `revision_honestidad.json`; `artifacts_read` de Bot 4 | P2/contrato §2.1 (matriz): distinguir "ausente porque el gate frenó" de "ausente debiendo existir" |
| **F-P4.3** | El gate que bloqueó es `coherence`: score 0,8967 ≥ umbral 0,8 pero `is_coherent=False` por **un** check de severidad error, `whatsapp_verified` ("no hay campo `whatsapp_number`"). El campo no está porque la ruta `observations.json → onboarding` no carga WhatsApp, no porque el hotel no lo tenga. Un **hueco del adaptador** bloquea la publicación | `gate_report_*.json`, `coherence_validation.json`, `BLOCKED_BY_GATES.md` | `modules/onboarding` / adaptador `_observation_to_onboarding_format` |
| **F-P4.4** | `ia_readiness_report.json` existía en el baseline y **no** se escribió en esta corrida. Su escritor está en `modules/auditors/v4_comprehensive.py`; sin atribuir por qué desapareció (¿condicionado al gate? ¿a la caída del provider?) | filas ALTA/BAJA del diff, `discover()` del script | métricas advisory — **sin dueño asignado aún** |
| **F-P4.5** | **El log de corrida imprime una clave de API en texto plano** dentro del error 403 de Gemini (`key=AIza…`). Aquí quedó en un archivo gitignoreado, pero cualquier `cp` de un log a un documento versionado o a un `05-prompt` la publica. El repo es público. **Corrección de este hallazgo al medir su verificador**: sí existe un check de secretos y **sí** corre en pre-commit (`validate-plan` → `run_all_validations.py --check`, paso `[4/9]`) — pero su cobertura medida es: **solo `*.py`**, excluye cualquier ruta con `test`, y casa **4 patrones de asignación** (`DEEPSEEK_/ANTHROPIC_/GOOGLE_/GOOGLEMAPS_API_KEY = "…"`) en vez de **formatos de clave**. Sondeo: una clave en texto dentro de un `.md`/`.log` **no casa ningún patrón**; el mismo valor como asignación en `.py` sí. El defecto no es la ausencia del verificador sino su forma: mira dónde se *asigna* una clave en código, no dónde aparece escrita | `corrida/corrida.log` (redactado al citarlo), `run_all_validations.py::_check_no_secrets`, sondeo de patrones | `scripts/run_all_validations.py` (extender a `*.md`/`*.log`/`*.json` y a formatos `AIza…`/`sk-…`) + scrubbing del error del provider — **prioridad alta** |
| **F-P4.6** | Deriva de provider contra el baseline: la corrida anterior registró `Using DeepSeek as LLM provider`; esta llamó a **Gemini y recibió 403**, y el flujo continuó (never-block). La equivalencia con el baseline no es estricta | log `LLM query failed for gemini: 403` | configuración de providers |
| **F-P4.7** | El fallback que permite que un hotel **sin YAML** consuma `observations.json` depende de que `output/clientes/` tenga **al menos un** YAML ajeno (`if _fallback_dir.exists() and any(...glob("*_onboarding.yaml"))`). Con el directorio vacío, Don Alfonso habría corrido **en defaults en silencio**, que es la condición de equivalencia que L-VUP-13 prohíbe pasar por alto | `main.py` bloque FASE-D (S7) + sondeo directo de la cadena (paso a paso en `t3a_sonda_candidatos.py`) | cargador de onboarding |
| **F-P4.8** | El baseline del delta (`evidence/FASE-E2E/`) está **excluido de git** por la regla de `.gitignore` que protege material de cliente en un remoto público: existe solo en esta máquina. AC-O2 lo congela con hashes (66 archivos, `MANIFIESTO-baseline.json`, sha256 agregado `35a77d38…`), pero **no** lo vuelve durable para un clon limpio | `git ls-files evidence/FASE-E2E/` → 0; `git check-ignore` → línea 154 | R2.6-hermana: hace falta un baseline versionable sin datos de cliente |
| **F-P4.9** | **El enforcement borra su propia evidencia.** `suppress()` unlinka el `.zip.tmp` que los cuatro revisores acaban de leer, así que al día siguiente nadie puede verificar qué miró Bot 3 — en esta misma sesión eso generó una sospecha falsa de contaminación cruzada (tres ZIP de Salento Real con el mismo `IMPLEMENTATION_ORDER.md` de 468 bytes son lo único que queda en disco). El registro de la ruta resuelta vive solo en un log gitignoreado | log `[OK] Paquete en cuarentena: hoteldonalfonso_20260914.zip.tmp` → `⛔ ZIP SUPPRIMIDO`; `find output -name "*.zip*"` no devuelve ningún miembro de este hotel | **FASE-RELEASE**: que el acta consigne `sha256` y recuento de miembros del paquete desechado (el packager ya tiene los bytes finalizados antes del rename) |

## 4. Qué quedó observado y qué no (límites de la fase)

**Observado por primera vez en datos reales:** el ZIP suprimido por veredicto (AC-E2/AC-E5), el acta
con `reviewer_reports` de longitud 4 y `corrective_actions` con dueño (AC-E1/AC-E0), el tier del acta
anclado a `financial_scenarios` (AC-F2), el primer piso aplicado en `B+` (AC-F4) y el detector de
plantilla vacía operando sobre el `.zip.tmp` (AC-F1/AC8).

**NO observado, declarado como límite — no como fallo:**
1. **Tier A** y por tanto `APROBADO-PARA-ENTREGA`: exige GA4+GSC del hotel (T3b). Dueño: analítica del hotel.
2. **El contrafactual que justifica el enforcement** (§punto 5): nunca hubo una corrida donde los
   gates aprobaran y un revisor objetara. Con la F-P4.1 vigente, todo run real se bloquea por la
   plantilla, así que el contrafactual es **inalcanzable hasta arreglar F-P4.1**.
3. Tres de los cuatro estados de NR8 (`NOT_RUN`, `ARTIFACT_MISSING`, `READER_FAILED`) en datos reales.
4. Corpus multi-hotel: S-V10 exige ≥3 hoteles; una corrida no da confianza estadística.

**Condiciones de equivalencia con el baseline** (L-VUP-13, declaradas, no inferidas): hotel distinto ·
dato operativo con 54 días · provider Gemini (403) vs DeepSeek · `--output` alternativo · sin GA4/GSC
en ambos lados · ruta de datos por el adaptador `observations.json`, no por un YAML de onboarding.

## 5. Consecuencia para FASE-RELEASE

- P4 **se ejecutó**: README queda en 6 sesiones, no 5; el escenario de cierre sin P4 no se invoca.
- AC-V1 de RELEASE incorpora esta evidencia y debe registrar el límite del contrafactual (§4.2), que
  es material de certificación y no una omisión de esta fase.
- F-P4.1 y F-P4.5 son las dos que tienen carácter urgente: la primera bloquea el 100 % de las corridas
  reales con los dientes puestos; la segunda puede publicar una clave en un repo público.
- Ninguna se corrigió en esta fase: la restricción de P4 prohíbe tocar código de producción para
  arreglar lo que la corrida observa.

## 6. Artefactos de la fase: qué se versiona y qué no

Verificable con `git status --short --untracked-files=all evidence/FASE-P4/`.

| Ruta | Contenido | ¿Versionado? |
|---|---|---|
| `informe-observacion.md` | este documento | ✅ |
| `consentimiento-donalfonso.md` | declaración del operador + límite de frescura (línea roja iii) | ✅ |
| `t3a_sonda_candidatos.py` + `.json` + `.md` | sonda de candidatos T3a y techo de tier medido | ✅ |
| `diff_estructural_corridas.py` | comparator estructural con `--selftest` (L-VUP-14) | ✅ |
| `help-v4complete.txt`, `help-onboard.txt` | salida real de `--help` (L-VUP-9) | ✅ |
| `baseline-predecesor/MANIFIESTO-baseline.json` | sha256 de los 66 archivos del baseline ajeno + procedencia (AC-O2 / L-B4) | ✅ (solo hashes) |
| `corrida/corrida.log` | log completo de la corrida (contiene una clave de API → F-P4.5) | ❌ gitignoreado |
| `corrida/run/` | **copia de la evidencia antes de analizar** (L-VUP-12): 62 archivos del pipeline | ❌ gitignoreado |
| `corrida/baseline-snapshot/` | copia local del baseline que leyó el comparator | ❌ gitignoreado |
| `corrida/detalle-valores.md` | los 435 cambios de valor con cifras COP | ❌ gitignoreado |

La regla nueva en `.gitignore` (`evidence/FASE-P4/corrida/`) es deliberada y sigue el criterio que ya
excluye `evidence/FASE-E2E/`: el remoto es público. El efecto colateral, declarado: la "copia de
evidencia" del checklist existe en disco pero no viaja al repo, igual que en el predecesor — y F-P4.8
documenta por qué eso es un límite y no una solución.

## 7. Iteraciones (R2.1 / L-R.1)

**Auto-reporte con unidad declarada, no medición.** `evidence/FASE-D/measure_iterations.py` requiere
el transcript `.jsonl` de la sesión, que vive fuera del workspace; `find . -name "*.jsonl"` dentro del
repo devuelve **0 archivos** y el acceso al directorio del cliente fue **denegado por el clasificador**
en FASE-P2 por la misma razón. Es la **segunda sesión seguida** (P2 y P4) en la que D-V2.1 se
reproduce; en P3-A y P3-B el instrumento sí alcanzó el transcript, así que la limitación es del
entorno de esta máquina/cliente, no del instrumento en abstracto.

- Unidad: **llamadas a herramienta de esta sesión**, contadas a mano sobre el historial del agente.
- Total: **≈52 llamadas** en ~30 turnos, de las cuales **3** produjeron el artefacto de la corrida
  (lanzamiento, sondeo de cadena de carga, copia de evidencia) y el resto preparación, medición y
  cierre documental.
- Corte declarado: el momento en que `ZIP SUPPRIMIDO` aparece en el log (18:39), antes del análisis.
- Presupuesto del prompt: **40 iteraciones**. Con esta unidad **no comparable** al conteo de P3-A
  (106 `ids` / 126 `tool_use` medidos por el instrumento) ni al de P3-B (120/120). Se publica la
  incomparabilidad, no se redondea para que parezca cumplimiento: **el presupuesto no puede
  verificarse con la unidad que se tiene**. Refuerza L-P3B.1 (cambiar la regla de presupuestación).
