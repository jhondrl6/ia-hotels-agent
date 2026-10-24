# Consentimiento de la corrida única — Hotel Don Alfonso (plan CURA-DEUDAS-PRODUCTO-Y-CONTRATO-TIER-2026-10-22)

**Plan**: CURA-DEUDAS-PRODUCTO-Y-CONTRATO-TIER-2026-10-22 — condición de entrada de FASE-E2E, criterio de
aceptación de la Tarea 1 (`consentimiento-corrida.md` **de esta corrida**).

**Quien declara**: el operador del proyecto, el **2026-10-24** en el chat de esta sesión. Proveniencia del texto,
declarada sin adorno: el agente puso la letra sobre la mesa como opción (a) de una pregunta de consentimiento y el
Operador la **adoptó por selección**, así que el alcance no lo redactó el agente en solitario ni el texto es un
dictado libre; es la formulación que el Operador eligió y que aquí se transcribe literal en `autoriza`.

**Alcance que ampara**: la corrida única (1/1, sin reintento) de `v4complete` sobre la URL amparada y el ZIP
publicable que produzca, corriendo con el dato operativo cuya edad se declara vencida abajo.

## Acta machine-readable

<!-- iah-consentimiento -->
{"url_amparada": "https://www.donalfonsohotel.com/", "fecha_captura_aceptada": "2026-07-22", "limite_de_frescura_dias": 90, "edad_declarada_dias": 94, "vence_el": "2026-10-20", "autoriza": "Autorizo la corrida única de v4complete sobre https://www.donalfonsohotel.com/ con la captura 2026-07-22 (94 días, techo de 90 vencido el 2026-10-20) y el ZIP publicable que produzca", "declarado_por": "Jhond (operador)", "fecha": "2026-10-24"}

## La edad del dato, estampada

`metadatos.fecha_captura` del onboarding es **2026-07-22**. Medido hoy 2026-10-24: **94 días** de edad contra el
techo de 90 días que publicó el baseline, cuya ventana venció el **2026-10-20**. Es la **opción (b) dictada por el
Operador** el 2026-10-24 («Git Commit +L3 + Condición de frescura B.», asiento en `01-plan-maestro.md` §5 y en
`evidence/…/FASE-E2E-PRE/condicion-frescura-decision-b.txt`): se corre con la captura vigente y se declara la edad,
sin re-capturar.

Este documento **no cura** el vencimiento: lo **acepta** y lo deja visible. Dos hechos del instrumento, medidos en
el pre-vuelo de esta fase:

- `ONBOARDING_FRESHNESS_HOURS` está **ausente** del entorno, y el loader (`main._load_latest_onboarding_data`) solo
  corta por frescura si esa variable existe. Por eso la captura vencida no deshabilita la rama YAML.
- Fijar esa variable con el dato vencido pondría el loader en fail-closed: sin onboarding, el tribunal trueca
  `ANALYTICS_CEILING` por `ONBOARDING_INCOMPLETE` y AC7 deja de ser alcanzable. Es la razón por la que se descartó
  la vía (c), no una preferencia de estilo.

## No reutiliza el acto ajeno

**No** se ampara en `evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-E2E/consentimiento-corrida.md` (dictado el
2026-10-12 para la corrida de aquel plan). Ese documento ampara su propia corrida y lo declara por escrito, y su
ventana venció el 2026-10-20, así que no habilita ningún spawn posterior ni siquiera por préstamo. Queda publicado e
intacto; esta fase no lo edita.

## Límites que este documento no cierra

- **El veredicto no está garantizado**: si el tribunal sale `BLOQUEADO`, la cuarentena del ZIP es un resultado
  válido del sistema curado y no pide decisión nueva. Este acto autoriza el intento.
- **Contador de intentos**: 0/1 al firmar. La corrida que se lanza bajo este acto lo deja en 1/1 y no hay segunda.
- **Divulgación al cliente**: la edad vive en el YAML y en este pre-vuelo; **no** se imprime en `01_DIAGNOSTICO` ni
  en `02_PROPUESTA`. Decidir si corresponde al documento comercial es del Operador y su sede es FASE-VERIFY o una
  fase propia, no E2E (que prohíbe tocar el render).
- **Credenciales**: la presencia de `DEEPSEEK_API_KEY` / `ANTHROPIC_API_KEY` / `LLM_PROVIDER` no se sondió en esta
  sesión porque la política de la herramienta bloquea el acceso a `.env` sin autorización expresa. Se declara por el
  nombre de la variable, nunca por valor; el baseline del 2026-10-12 corrió con extracción pagada y sus recibos están
  versionados.
- **Fuentes congeladas**: `data/hotel_observations/observations.json` y el YAML del onboarding no se editan.
