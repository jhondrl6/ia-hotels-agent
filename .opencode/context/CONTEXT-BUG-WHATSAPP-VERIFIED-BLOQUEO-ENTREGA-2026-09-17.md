# CONTEXT-BUG-WHATSAPP-VERIFIED-BLOQUEO-ENTREGA-2026-09-17

> **Tipo**: Contexto de decisión con evidencia medida (insumo para sesión de orquestación → plan).
> **Disparador**: la corrida de observación FASE-P4 (`v4complete` sobre hoteldonalfonso.com, 2026-09-14) produjo `NOT_READY_FOR_PUBLICATION` y el tribunal **suprimió el ZIP**. La prueba del enforcement es válida, pero no dejó entregables. Al ahondar en las causas aparece un bug determinista: **con la ruta de datos del warehouse, cualquier hotel real queda bloqueado de fábrica.**
> **Tesis (una línea)**: `_check_whatsapp_verified` no distingue *"el hotel no tiene WhatsApp"* de *"esta ruta de datos nunca lo pregunta"* — y trata el segundo caso como error bloqueante.
> **Estado**: **SIN IMPLEMENTAR.** Esta sesión NO toca código. Los §5-§9 son insumo; la decisión de qué fix queda para la sesión de plan.
> **Re-verificación**: todos los anchors `archivo:línea` de este documento fueron releídos contra HEAD `e8010ce` (v4.77.0) el 2026-09-17, no copiados de la auditoría. Correcciones respecto al informe original en §2d.

---

## 1. Resumen ejecutivo — tres defectos apilados, no uno

| # | Defecto | Ubicación | Efecto |
|---|---------|-----------|--------|
| **D1 — Adaptador** | La ruta `observations.json → onboarding` no puede transportar WhatsApp en **ninguna** de sus tres capas: el instrumento de recolección no lo pregunta, el esquema lo prohíbe, y el adaptador lo mapea con 4 claves | `data/hotel_observations/forms/contact_form_ES.md:231-238` (privacidad: "NO pedir ni almacenar… teléfono directo"), `hotel_observations.schema.json` `$defs/observation` (21 propiedades, **sin** propiedad de contacto, `additionalProperties: False`), `main.py:3877-3882` (`_FIELD_MAP` = 4 claves) | `whatsapp_number` nunca se anexa a `ValidationSummary` → el check cae en la rama de error |
| **D2 — Cableado** | Las dos llamadas a `coherence_validator.validate()` dentro del orquestador **no pasan `whatsapp_html_detected`**, aunque el parámetro existe y el auditor lo produce | `modules/asset_generation/v4_asset_orchestrator.py:309-312` y `:447-451` (ambas omiten el kwarg; `main.py` sí lo pasa en 4 sitios: 2446, 2544, 2766, 3646) | El rescate de `coherence_validator.py:437-444` (HTML detectado → score 0.5, `severity="info"`) es **inalcanzable** en el informe canónico, que es justamente el que leen los gates |
| **D3 — Recuperación imposible** | `AssessmentBuilder.with_validation()` recibe `whatsapp_validation` y lo **descarta** | `modules/assessment_builder.py:116-122` (el parámetro no se usa; llamado desde `main.py:2938`) | Aguas abajo del builder no hay forma de reconstruir la confianza de WhatsApp |

**Consecuencia combinada**: con datos del warehouse, la verificación de WhatsApp **no puede pasar** ni puede degradarse a advisory. `is_coherent=False` → gate bloqueado → ZIP suprimido. Es un falso positivo estructural, no un caso límite.

**Lo que NO es este bug** (importante para no sobredimensionar el fix): el tribunal hizo lo correcto. El pipeline le entregó un veredicto `is_coherent=False` con un check `severity="error"` abierto, y bloqueó. El defecto está **aguas arriba del tribunal**, en la producción del veredicto. Arreglar `whatsapp_verified` no cambia ninguna garantía del enforcement.

---

## 2. La cadena trazada, capa por capa

### 2a. Quién produce el dato

`ValidatedField(field_name="whatsapp_number", …)` se anexa en **un solo lugar** del repo: `main.py:2232-2275`, una cadena de 4 ramas, todas dependientes de la auditoría en vivo:

| Rama | Condición | Confidence |
|------|-----------|------------|
| `main.py:2240` | `whatsapp_validation.confidence == VERIFIED` (Web + GBP coinciden) | VERIFIED |
| `main.py:2249` | `== CONFLICT` | CONFLICT |
| `main.py:2257` | `elif whatsapp_web` (una sola fuente) | ESTIMATED 0.5 |
| `main.py:2266` | `elif whatsapp_html_detected` | ESTIMATED 0.6 (`value="detected_via_html"`) |

Ninguna rama se dispara desde la ruta del warehouse: `whatsapp_validation`, `whatsapp_web` y `whatsapp_html_detected` vienen del auditor (`modules/auditors/v4_comprehensive.py:161, 695, 1852`), no de `onboarding_data`. Y `modules/onboarding/` tiene **0 coincidencias** en `whatsapp|tel[eé]fono` (verificado por grep, 2026-09-17). El formulario de onboarding tampoco captura canales de contacto.

### 2b. Quién decide

`coherence_validator.py:392-461`, tabla de ramas medida línea por línea:

| Condición | Línea | score | severity | passed |
|-----------|-------|-------|----------|--------|
| No hay asset `whatsapp_button` | `:424-431` | 1.0 | info | True |
| Sin campo **y** `whatsapp_html_detected` | `:437-444` | 0.5 | info/warning | `not is_blocking` |
| **Sin campo, sin HTML** | `:446-453` | **0.0** | **error** | `not is_blocking` → **False** |
| Campo con confidence ≥ 0.9 | `:461+` | 1.0 | — | True |
| Campo con confidence < 0.9 | — | — | error | False |

Los dos escapes existen y ninguno funciona en la ruta del warehouse:
1. `whatsapp_html_detected` → anulado por D2.
2. `site_presence_report["whatsapp_button"].presence_status == "exists"` → boost a 0.95 en `:458-459`. Sí se cableó (`v4_asset_orchestrator.py:311, 450`), pero exige que el **sitio sea alcanzable**. En la corrida P4 devolvió `status: "verification_failed"`, `confidence: 0.3`, `site_verified: false` (`evidence/FASE-P4/corrida/output/v4_complete/hoteldonalfonso/v4_audit/site_presence_snapshot.json`).

### 2c. Cómo se vuelve bloqueo

```python
# coherence_validator.py:176-185
errors = [c for c in self.checks if c.severity == "error" and not c.passed]
...
is_coherent = len(errors) == 0 and overall_score >= threshold
```

**Un solo** check `severity="error"` sin pasar fuerza `is_coherent=False` **independientemente del score**. Peso del check en el score: 0.5 de 6 checks (`:101-108`) — de ahí la paradoja medida: score 0.897 con veredicto negativo.

Y el gate que lo consume:

```python
# publication_gates.py:604-608
passed = coherence_verdict_passes(coherence_score, self.config.coherence_threshold,
                                  assessment.get("is_coherent"))
# publication_gates.py:624-649  → BLOCKED con mensaje "meets threshold ... but validator declared is_coherent=False"
```

`publication_gates.py` tiene **0 referencias a `whatsapp_verified`** (verificado por `grep -c`, 2026-09-17). La puerta FASE-F solo lee el veredicto binario; **el nombre del check culpable se pierde** al cruzar la frontera gate↔validador. Eso explica por qué el bloqueo tardó en diagnosticarse y por qué conviene preservarlo en el fix (§6, AC-4).

### 2d. Correcciones al informe original

| Claim previo | Verificado 2026-09-17 |
|--------------|----------------------|
| "el orquestador pierde el rescate; `main.py` lo preserva" | **Peor de lo reportado**: `v4_asset_orchestrator.py:500` hace `final_coherence_report = post_coherence_report if post_coherence_report else coherence`. **Ambas** ramas vienen de llamadas sin el kwarg. No existe una ruta de fallback que conserve el rescate. |
| "el warehouse tiene 21 propiedades" | Confirmado, pero están en `$defs/observation` (el nivel raíz tiene 6). `whatsapp` no aparece en **ninguna** capa del archivo; `observations.json` tampoco lo contiene (6 observaciones, 0 coincidencias). |
| "`contacto` aparece en el esquema" | Falso positivo de grep: es el valor de enum `source: "contacto_directo"` (`:122`), no un campo de contacto. La afirmación "el esquema no tiene propiedad de contacto" se mantiene. |

---

## 3. Evidencia de la corrida P4 (Don Alfonso, 2026-09-14)

| Hecho | Artefacto |
|-------|-----------|
| Sitio inalcanzable: `Empty HTML response for https://hoteldonalfonso.com/` | `evidence/FASE-P4/corrida/corrida.log:4` |
| `WhatsApp: Datos insuficientes para validación` → `whatsapp_validation = None` | `corrida.log:157`; mecanismo en `main.py:1786-1808` |
| Origen warehouse de los financieros (`adr_cop: user_provided`, `occupancy_rate: onboarding`, `direct_channel_percentage: onboarding`) | `.../v4_audit/gate_report_20260914_183821.json` |
| Check culpable, literal: `{"name":"whatsapp_verified","passed":false,"score":0.0,"message":"WhatsApp button requiere validación pero no hay campo 'whatsapp_number'","severity":"error"}` | `.../v4_audit/coherence_validation.json` (`is_coherent: false`, `overall_score: 0.9`, 5/6 checks pasan) |
| `whatsapp_status: "UNKNOWN"`, `whatsapp_confidence: 0.0` | `.../v4_complete_report.json` |
| Score pre-gen 0.8966 vs 0.9 canónico (dos cifras del mismo concepto) | `gate_report_20260914_183821.json` vs `coherence_validation.json` |
| Bloqueo final: NOT_READY → se borran docs → `⛔ ZIP SUPPRIMIDO` (`:331`), sin reintento (`:342`, decisión Q1b) | `corrida.log:279-287, 310, 331, 342` |

**Nota de honestidad sobre la causalidad**: en esa corrida el bloqueo estuvo **sobredeterminado** — fallaron las dos salidas de forma independiente (sitio caído ⇒ `whatsapp_html_detected=False`; `verification_failed` ⇒ sin boost). Por tanto **la corrida P4 no prueba D2 por sí sola**; lo prueba la lectura de código (§2b, §2d). Un sitio alcanzable hoy seguiría bloqueado por D2 aunque el HTML muestre el botón. Esta distinción es lo que evita que el plan confunda "arreglar este hotel" con "arreglar el bug".

**Hallazgo asociado a mantener en el alcance**: `corrida.log:4` contiene una API key de Gemini en texto plano (finding **F-P4.5**, §8 no-negociable 5). Verificado 2026-09-17: el archivo está excluido por `.gitignore:161` (`evidence/FASE-P4/corrida/`), así que **no está publicado** en el repo público — pero sí en disco, y cualquier fixture o copia de la evidencia lo puede propagar. Su rotación/limpieza es un trabajo aparte.

---

## 4. Por qué esto importa ahora (contexto de producto)

- El enforcement O1-cuarentena se certificó en v4.77.0 sobre **esta** corrida como único caso real. Si la única corrida real del sistema está bloqueada por un falso positivo, el tribunal nunca ha bloqueado *ni dejado pasar* un caso representativo: la certificación es sólida como mecánica, **ciega como calibración**.
- La ruta del warehouse es la que el plan eligió para operar sin auditoría en vivo (observación → `v4complete`). Su caso de uso queda inutilizado por D1.
- El umbral de coherencia (0.8) **no está en discusión** y no debe moverse (ver §8).

---

## 5. Direcciones de fix, con tradeoffs

Las cuatro son independientes y **componibles**. Ninguna se recomienda a ciegas; la recomendación va al final.

### F-A — Cablear `whatsapp_html_detected` al orquestador
Añadir el kwarg en `v4_asset_orchestrator.py:309-312` y `:447-451`, alineándose con `main.py:2544`.
- **+**: corrige D2, que es un **defecto de intención** (el parámetro existe y nadie lo pasa). 2 líneas. Devuelve al orquestador la semántica que el resto del pipeline ya asume.
- **−**: no arregla la ruta del warehouse con sitio inalcanzable (Don Alfonso seguiría bloqueado). Solo funciona si el HTML es accesible.
- **Riesgo**: bajo. No amplía superficie de datos.

### F-B — Transportar WhatsApp por la ruta del warehouse
Propiedad de contacto en `$defs/observation` + clave en `_FIELD_MAP` (`main.py:3877-3882`) + campo en el formulario.
- **+**: ataca D1 de frente; es la única vía que desbloquea el modo "sin auditoría en vivo".
- **−**: **choca con una decisión documentada**, no con un olvido. `contact_form_ES.md:233-234` prohíbe "pedir ni almacenar… teléfono directo del dueño", y `:237-238` restringe publicar el archivo en repos públicos sin consentimiento. Un número de WhatsApp comercial publicado en el sitio del hotel **no es** "teléfono directo del dueño", pero la línea no traza esa distinción: hay que escribirla explícitamente o el cambio es una violación apparent del contrato de privacidad.
- **Riesgo**: medio-alto. `additionalProperties: False` → cualquier writer/validador existente rechaza la clave nueva hasta actualizar el esquema; y `observations.json` es contenido versionado.
- **Requiere decisión de producto** (del usuario, no del plan): ¿qué se considera canal almacenable?

### F-C — Degradar `whatsapp_verified` a `blocking=False`
`coherence_config.py:60-65`.
- **+**: un valor de config, destraba todo inmediatamente.
- **−**: **pierde la protección que justifica la existencia del check**. El check se escribió contra un incidente concreto (botón de WhatsApp inventado). Hoy, con `blocking=False`, la rama `:446-453` pasa a `severity="warning"` y un `whatsapp_button` sin ninguna evidencia podría publicarse. Es el peor tradeoff del conjunto: cura el falso positivo introduciendo falsos negativos, que es la clase de fallo que el tribunal fue construido para cazar.
- **Riesgo**: alto desde el punto de vista de garantía de producto.

### F-D — Reconectar `whatsapp_validation` en `with_validation`
`assessment_builder.py:116-122`.
- **+**: elimina un parámetro muerto que hoy es una trampa para quien lea el código.
- **−**: **no está claro que deba reconectarse**. Puede ser residuo de una simplificación deliberada (el commentario vecino de `with_coherence:173` indica que hubo barridos de payload sin consumidores). Antes de escribirle comportamiento hay que preguntar por qué se vació.
- **Riesgo**: medio (podría re-introducir doble fuente de verdad).
- **Alternativa F-D'**: **borrar** el parámetro y su argumento en `main.py:2938`. Más honesto si la respuesta a la pregunta anterior es "ya no se usa".

### Recomendación (para que la sesión de plan la confirme o la rechace)

**F-A + una quinta opción, F-E, que es la que resuelve el bug de semántica; F-B diferido con decisión de producto explícita; F-C descartado.**

**F-E — Separar "ausencia estructural" de "verificación fallida".** El verdadero bug no es que falte el dato ni que falte el kwarg: es que el check codifica *dos* estados distintos como un solo `severity="error"`.

- "Pregunté el número en dos fuentes y no concuerdan / no alcanzan umbral" → **error, bloqueante** (protección legítima, conservarla intacta).
- "Esta ruta de datos nunca pregunta el número" → **no evaluable**, no un fallo.

Mecánica propuesta: el check recibe la señal de **disponibilidad de la fuente** (no solo el HTML) y emite un estado `not_evaluable` — score neutro, `severity="info"`, y **el check se excluye del denominador del score** en vez de contar como 0.0. Esto es coherente con la disciplina que el propio repo ya declaró dos veces: AC-G2 en `main.py:3873-3876` ("la ausencia de un campo no se convierte en valor inventado"), y el anti-patrón `contact_form_ES.md:257-259` ("Si no tienes el dato, deja el campo ausente"). Hoy el sistema **respeta** la ausencia en el dato y la **castiga** en la coherencia.

F-A es pre-requisito práctico de F-E: sin el kwarg cableado, el check no tiene forma de saber qué ruta alimentó el `ValidationSummary`, y F-E se queda sin señal que consumir.

**Coste de F-E**: toca el modelo de `CoherenceCheck` (necesita un estado no-binario) y por tanto su contrato de serialización y los consumidores del acta. Es el fix más caro de los cinco y el único que cierra el bug en vez de esquivarlo. Si el plan quiere una fase corta, F-A sola deja el sistema **menos roto pero todavía roto**, y eso debe decirse en el título de la fase, no en una nota al pie.

---

## 6. Verificación propuesta (pares verde/rojo, metodo NR7)

NR7 exige que cada AC de bloqueo tenga un check que **prende en rojo al romper** y verde al arreglar — no solo un test unitario del camino feliz. Cada fila es un par medible:

| AC | Verde | Rojo (inyección de falla) |
|----|-------|---------------------------|
| **AC-1** El orquestador preserva el rescate por HTML | Corrida con HTML que contiene el botón + sin campo en `ValidationSummary` → `whatsapp_verified.score == 0.5`, `severity != "error"`, `is_coherent == True` | Revertir el kwarg en `v4_asset_orchestrator.py:309` → el mismo fixture debe dar `is_coherent == False` |
| **AC-2** Ausencia estructural no bloquea | `ValidationSummary` construido por la ruta warehouse (0 campos de WhatsApp) → el check reporta `not_evaluable`, `is_coherent == True`, y el score **no** incluye el peso 0.5 en el denominador | Forzar la rama antigua (`:446-453`) → bloquea |
| **AC-3** La protección real sigue viva | `whatsapp_button` generado + `whatsapp_number` con confidence < 0.9 → `severity="error"`, `is_coherent == False` | **Este par no se reversiona**: prueba que el fix no degradó la garantía. Si AC-3 pasa a verde con el fix, el fix es F-C encubierto |
| **AC-4** El culpable es legible | `gate_report.json` del coherence gate incluye el nombre del check que originó el bloqueo (hoy se pierde: `publication_gates.py` tiene 0 refs a `whatsapp_verified`) | Generar un fixture con el check en `not_evaluable` + otro check en error → el reporte debe señalar **solo** el segundo |
| **AC-5** No regresión de umbral | `coherence_threshold` sigue en 0.8 en las tres capas de config | — (assert de constante, no par) |

**Tests que hoy fijan el comportamiento actual** y hay que revisar antes de tocar (inventario, no sentencia): `tests/regression/test_whatsapp_conflicts.py` (4 functions), `tests/regression/test_hotel_visperas_conflicts.py`, `tests/commercial_documents/test_coherence_generated_assets.py`, `tests/commercial_documents/test_promised_assets_production.py`, `tests/asset_generation/test_site_presence_adapter.py`, `tests/quality_gates/test_domain_gates.py`.

**Advertencia de alcance**: `modules/quality_gates/domain_gates.py:348-384` contiene un **segundo** `_check_whatsapp_verified`, que lee `assessment["contact"]["whatsapp"]` — un campo que el builder nunca popula. El módulo tiene **0 importadores en producción** (código muerto con tests vivos en `test_domain_gates.py`). Un plan que busque `whatsapp_verified` encontrará dos definiciones y puede "arreglar" la equivocada mientras sus tests siguen verdes. Decisión explícita requerida: archivar, o documentar por qué existe.

---

## 7. Alcance: arreglar esto NO produce entregables todavía

Bloqueo **independiente**, documentado en F-P4.1 (`evidence/FASE-P4/informe-observacion.md`): **`IMPLEMENTATION_ORDER.md` es un stub de 468 bytes** en los 4 paquetes del corpus baseline medidos por ese finding (medición propia 2026-09-17 sobre `evidence/FASE-P4/corrida/baseline-snapshot/deliveries/hotelsalentoreal_20260911_unpacked/IMPLEMENTATION_ORDER.md`). Los 4 revisores lo reportan y producen `EMPTY_DELIVERY_TEMPLATE`.

> Precisión que conviene llevar al plan: en la corrida de Don Alfonso **no** se observó ese artefacto entregado — el ZIP fue suprimido antes, por el gate de coherencia. Así que F-P4.1 está probado sobre el corpus baseline, no sobre la corrida de observación; para Don Alfonso es una sospecha razonable (mismo writer) pero sin medir. Los dos bloqueos están en serie, no en paralelo: resuelto D1/D2, el pipeline llegará al revisor y ahí puede aparecer el segundo.

Por tanto el orden importa: **con solo este fix, la corrida de observación sigue sin entregar paquete.** La sesión de plan debe decidir si (i) este plan es *precondition* de una corrida de observación posterior, o (ii) se fusiona con la causa F-P4.1 en una sola fase que sí prometa un `READY_FOR_PUBLICATION` real. La opción (i) repite el patrón que la lección **L-VERIFY.3** registró: cada fase certificó su propio alcance y nadie midió el extremo a extremo; se descubrió en la fase siguiente.

**Relación con el triaje previo (corregido el 2026-09-17)**: este bug **no está triajeado**. `evidence/FASE-VERIFY/T4-triaje.md` fue revisado entero (B1-B5, C1-C9) y ninguna fila lo menciona — es un hallazgo **nuevo** de esta sesión de análisis, así que el plan debe abrirle fila propia en lugar de dar por hecho que ya tiene dueño. Lo que sí existe es su **consecuencia**: la fila **B2** ("contrafactual del enforcement no observado: los gates bloquearon antes que los revisores en la única corrida real") registró el síntoma; este documento aporta la causa raíz. Y **B1** ("el pipeline no volvió a correrse desde P5") explica por qué nadie lo vio: no hubo más corridas.

---

## 8. No-negociables para el plan

1. **No tocar el umbral de coherencia (0.8)** ni el de WhatsApp (0.9). Un umbral más bajo no distingue ausencia de verificación; es F-C con otro nombre.
2. **No inventar el dato.** Cualquier fix que ponga `whatsapp_number` a partir de un benchmark o un valor por defecto viola la política "No Defaults" del repo y AC-G2.
3. **AC-3 no se reversiona** (§6). La protección contra botón fantasma es la razón de ser del check.
4. **F-B exige decisión de privacidad escrita por el usuario** antes de codificarse (`contact_form_ES.md:231-238`). No reinterpretar la restricción en silencio.
5. **No propagar la API key de `corrida.log:4`** (F-P4.5) a ningún artefacto nuevo: ni este contexto, ni fixtures de test, ni evidencia. Referenciarla solo por finding ID y máscara. Su rotación/limpieza es un trabajo aparte.
6. **No modificar el árbol `evidence/FASE-P4/`** — es la evidencia de este análisis. Nuevas mediciones, en subdirectorio propio por plan (convención ya registrada en memoria del proyecto).

---

## 9. Cómo verificar este contexto por cuenta propia

```bash
# Defecto D2 — ni una sola aparición del kwarg en el orquestador
grep -n "whatsapp_html_detected" modules/asset_generation/v4_asset_orchestrator.py   # → 0 coincidencias
grep -n "whatsapp_html_detected" main.py                                            # → 2446, 2544, 2766, 3646

# Defecto D1 — la propiedad de contacto no existe en el warehouse
python -c "import json;s=json.load(open('data/hotel_observations/hotel_observations.schema.json',encoding='utf-8'));print(sorted(s['\$defs']['observation']['properties']),s['\$defs']['observation']['additionalProperties'])"
grep -ril whatsapp data/hotel_observations/ modules/onboarding/                      # → 0 coincidencias

# Defecto D3 — parámetro muerto
grep -n -A6 "def with_validation" modules/assessment_builder.py                     # → solo asigna validation_summary
grep -n "builder.with_validation(" main.py                                           # → 2938

# El gate no conoce el nombre del check
grep -c "whatsapp_verified" modules/quality_gates/publication_gates.py               # → 0

# Los dos _check_whatsapp_verified (trampa de alcance)
grep -rn "def _check_whatsapp_verified" --include=*.py modules/
```

Estructura del check, para no re-leer 70 líneas: `coherence_validator.py:392-461`; la regla del veredicto en `:176-185`; el peso (0.5 de 6) en `:101-108`; la config bloqueante en `coherence_config.py:60-65`.

---

**Creado**: 2026-09-17 · **HEAD**: `e8010ce` (v4.77.0) · **Sesión de origen**: análisis post-corrida FASE-P4, sin implementación.
**Uso previsto**: abrir una sesión nueva con `phased_project_executor` y este archivo como insumo único de partida. La primera decisión de esa sesión es §5 (qué fix) y §7 (alcance con F-P4.1); ambas son del usuario.
