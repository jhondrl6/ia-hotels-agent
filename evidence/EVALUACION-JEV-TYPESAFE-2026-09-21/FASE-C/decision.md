# FASE-C — decision del piloto JEV (EVALUACION-JEV-TYPESAFE-2026-09-21)

**`run_status = INCOMPLETO` · `decision = null`** · 2026-10-04 · protocolo CONGELADA
(sha `140577a0…277d` disco / `7caed9dc…0728` blob LF)

Esta hoja no interpreta la corrida: la deja en condiciones de que el operador emita uno de los cuatro
literales sin tener que reconstruir nada. Los tres huecos que impiden emitir mechanically están medidos
con su comando en `informe_comparativa.json` y enumerados como CR-1..CR-4.

---

## 1. La regla congelada, aplicada tal cual

| Criterio | Umbral | Medido | Instrumento | Veredicto |
|---|---|---|---|---|
| `cobertura_min` | 0.95 | **0.5 = 1/2 en los tres brazos** | `recuperacion_medida` (testado) | **NO CUMPLE** |
| `margen_vs_deepseek` | 0.25 (dif. abs. de extremo_a_extremo) | — | **no existe** (CR-1) | **NO-EVALUABLE**, no 0.0 |
| `suficiencia_minima` | 0.5 | 0.5 (2 de 4 pertinentes) | `muestra.json` + `etiquetas.json` | CUMPLE |
| `latencia_max` | 30 000 ms | Jev 48.478 / 395.794 · DS 1392.648 / 1133.547 | ledger por llamada | CUMPLE |
| `tratamiento_abstenciones` | denominador aparte | Jev 0 abst. + 1 sin elección por fallo · DS 1 abst. (`ninguna-aplica`) | `respuestas.jsonl` | publicado aparte |

El único cociente de adopción que llegó medido hasta el fondo es `cobertura_min`, y **no lo mide el
modelo que se evalúa: lo mide la capa fría, que es la misma para los tres brazos**. Por eso los tres
valores son idénticos (H1): la comparación entre brazos no puede sostenerse en la recuperación.

## 2. Los cuatro cocientes, por brazo

| Brazo | recuperación | precisión entre propuestas | recall importante | extremo a extremo |
|---|---|---|---|---|
| capa fría (k=8, sin red) | **1/2 = 0.5** | n/a (no propone una elección) | **NO ESTIMADO** | **NO ESTIMADO** |
| DeepSeek (`deepseek-chat` → eco `deepseek-flash`) | **1/2 = 0.5** | **NO ESTIMADO** | **NO ESTIMADO** | **NO ESTIMADO** |
| Jev (`jev-1.13.0`) | **1/2 = 0.5** | **NO ESTIMADO** | **NO ESTIMADO** | **NO ESTIMADO** |

`NO ESTIMADO` = `{"value": null, "numerator": null, "denominator": null, "motivo":
"instrumento_no_implementado"}` en `informe_comparativa.json`. No se rellenó a mano: `metrics()` lee
`prec_num`/`rec_num` pero el único sitio del repo que los produce es un fixture
(`tests/quality_gates/jev_pilot/test_jev_pilot_offline.py:113-115`).

## 3. Lo que pasó en eval, par por par

| par | etiqueta | target en los 8 | Jev | DeepSeek |
|---|---|---|---|---|
| `REFACTOR-WHATSAPP-ENTREGA-2026-09-18::D-AJUST.1` | pertinente · **alta** | **NO** | **FALLO** `TypeSafeAPIConnectionError`, 48 ms, `request_id` null, usage `no_intentada`, reserva no liberada como cero | elige `ninguna-aplica` (p 0.50, conf 0.55) — abstención correcta: su lección no estaba en la lista |
| `EVALUACION-JEV-TYPESAFE-2026-09-21::D-AJUST.4` | pertinente · media | SÍ (puesto 2) | elige `D-AJUST.4` (conf 0.90, p 0.91) · 395 ms · usage 1778/145 | elige `D-AJUST.4` (conf 0.95, p 0.90) · 1133 ms · usage 932/158 |

**El par de importancia ALTA es el que no se recuperó.** De ahí sale el 0.5 y de ahí sale también que
DeepSeek se abstuviera bien: `ninguna-aplica` existe precisamente para cuando nada casa.

## 4. Los cuatro literales, con su base

- **ACTIVAR — excluido por medición, no por criterio.** `cobertura_min` 0.95 contra 0.5 medido con el
  instrumento testado. No depende de ningún hueco de instrumento.
- **RECHAZAR — no la emite esta sesión.** Es la salida natural de ese 0.5, pero el literal que gobierna
  adoptar Jev es el margen extremo_a_extremo (NO-EVALUABLE) y en la pata Jev hubo un fallo operativo;
  el mandato reserva RECHAZAR para magnitud medida y prohíbe que un fallo operativo se vista de
  rechazo. **El operador sí puede emitirlo leyendo esta hoja.**
- **MUESTRA-INSUFICIENTE — ponible, con base publicada.** `suficiencia_minima` se cumple, pero el
  denominador efectivo de la comparación es **1 par** (el único con elección utilizable en ambos brazos)
  y un par no discrimina un margen de 0.25. Si se lee así, la salida es **muestra nueva**, nunca
  re-etiquetar la congelada.
- **COSTE-NO-PAGADO — bloqueado.** `usd` sigue null y fuera de gobernanza; no hay decisión de coste sin
  coste en gobernanza.

## 5. AC7: tres cosas separadas

| Campo | Valor | Base |
|---|---|---|
| `jev_recommendation` | **NO ADOPTAR; MANTENER COMO BRAZO MEDIBLE** | funcionó de punta a punta donde la red respondió (preflight AC12 OK, reserva AC8, attempts 1, usage observado, eco = pin, request_id) y acertó en el único par utilizable; 1 de 2 envíos perdido por transporte; **1 par no es una base de calidad** |
| `d6_eligibility` | **NO ELEGIBLE en esta fase** | su disparador es *pertinencia aceptable* + *candidatos nuevos*, **no** que gane Jev. Pertinencia: NO CUMPLE (0.5 < 0.95). Candidatos: CUMPLE (**9** pendientes para el plan, medidos con `candidatos_de_pertinencia` sobre índice FRESCO, sin red: D-B, D-D, DA-C3, L-D5, L-ENT.9, L-P6.3, L-SR3, L-SR4, L-T2B.1) |
| `transfer_status` | **PENDIENTE** | esta pegada prohíbe tocar el hermano y los planes archivados; mover D7/D6 exige instrucción literal con archivos y alcance nombrados, y estado re-leído |

La pata que falla en D6 es una propiedad de la capa fría, común a los tres brazos: no se arregla
cambiando de proveedor.

## 6. Incertidumbre y límites declarados

- n=2 en eval, n=1 con elección utilizable en ambos brazos: cualquier cociente que se implemente después
  tendrá resolución de medio punto.
- **Alias móvil**: DeepSeek pidió `deepseek-chat` y el servicio devolvió `deepseek-flash` en los 2
  envíos (y en las 4 sondas del 2026-10-04). El comparador no es estrictamente reproducible.
- Los brazos no reciben literalmente los mismos bytes: Jev ve los enunciados de los candidatos en los
  `criteria` de la pregunta; DeepSeek los ve en el `CONTEXTO` y la pregunta solo lista ids. Igual
  información, distinto canal — límite de comparabilidad, no defecto de la corrida.
- Tres monedas separadas: `usage_observed` publicado por llamada; `cost_calculated` y `cost_billed` en
  null con su motivo.
- Cuenta de la etapa: **4 llamadas de 12**, 0 envíos de conectividad.

## 7. Cambios requeridos (lo que falta para que la fase pueda cerrarse emitiendo)

| id | cambio | por qué no se hizo aquí |
|---|---|---|
| CR-1 | contador de clasificación (`prec_num`, `rec_num`) y cociente extremo a extremo, como instrumento **testado**, offline y regenerable desde los registros persistidos | AC10 prohíbe publicar el número con lógica nueva sin test; §5 prohíbe editar `scripts/` y `tests/` |
| CR-2 | `report` y `decide` implementados (`decide` → EXIT 2; `report` fuera del parser) | ídem |
| CR-3 | `run` debe propagar `--etiquetas` y resolver la credencial del SDK sin exigir que el llamador cargue `.env` | medido: por CLI el brazo muere en `TypeSafeError: No API key was provided` y `run_resumen.json` sale con `recuperacion: null` |
| CR-4 | re-anclar `tests/quality_gates/jev_pilot/test_jev_pilot_protocolo_check.py:43` al estado CONGELADA | es el aviso que la propia aserción anunció para FASE-C; editar `tests/` está prohibido en esta fase |

**Materia prima congelada:** `respuestas.jsonl`, `ledger.jsonl`, `ledger-deepseek.jsonl` y
`registro_deepseek.json` permiten a CR-1 y CR-2 producir los tres cocientes restantes **sin re-abrir la
corrida ni enviar nada**.

---

*Esta sesión no commiteó, no empujó, no corrió L3, no escribió back en QMind, no tocó al hermano y no
ofreció abrir FASE-RELEASE.*
