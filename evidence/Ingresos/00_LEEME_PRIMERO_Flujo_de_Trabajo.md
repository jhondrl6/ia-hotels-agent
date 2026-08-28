# Kit Comercial — Diagnóstico de Fuga de Reservas Directas
# FLUJO DE TRABAJO COMPLETO | Proyecto: iah-cli | Fecha: 2026-07-21 | Actualizado: 2026-08-27 (post-sismo)

> **Precedencia de fuentes (CONTEXTO MAESTRO v3.0):** `config/pricing.yaml` > CONTEXTO MAESTRO v3.0 > este kit.
> Cualquier cifra o regla de aquí que las contradiga está SUPERADA. El sprint vigente de 30 días es el §7 del maestro.

## ¿Qué es esto?

Sistema de venta de diagnósticos de visibilidad digital a hoteles del Eje Cafetero.
Producto: corres iah-cli v4complete → entregas informe que cuantifica en pesos
las reservas que el hotel pierde hacia Booking/OTAs/competencia → vendes la
implementación de las correcciones → vendes monitoreo mensual recurrente.

---

## ESTRUCTURA DE ARCHIVOS

```
evidence/Ingresos/
│
├── 00_LEEME_PRIMERO_Flujo_de_Trabajo.md   ← ESTE ARCHIVO (el mapa)
│
├── 01_Lista_Prospectos_v2_post_sismo.md   ← A QUIÉN venderle HOY (estados post-sismo verificados, §6.5)
├── 01_Lista_Prospectos_Eje_Cafetero.md    ← Fichas de detalle (histórico pre-sismo: teléfonos SÍ, estados NO)
├── 02_Mensaje_Prospeccion_WhatsApp.md     ← CÓMO conseguir la cita (Mensajes 1-4 + VARIANTES POST-SISMO D/E/F)
├── 03_Guion_Reunion_Venta.md              ← CÓMO vender en los 20 minutos (+ ADAPTACIÓN POST-SISMO)
├── 04_Estructura_Precios.md               ← Lógica de anclaje y objeciones (cifras SUPERADAS: manda pricing.yaml)
│
├── 05_Pipeline_PostSismo.md               ← REGISTRO VIVO (§8): funnel por hotel + próxima acción con fecha
├── 06_Borradores_Mensaje1_Paso0.md        ← 8 Mensajes 1 ya redactados con hallazgo real (listos para enviar)
├── PROMPT_Sesion_Semana1.md               ← Prompt de arranque de la sesión de prospección (pegar al iniciar)
│
└── Guion.md                               ← Documento base histórico (modelo de negocio; 3 preguntas de validación)
```

---

## PROTOCOLO POST-SISMO (vigente desde 2026-08-10 — §6.5 del CONTEXTO MAESTRO v3.0)

Terremoto M7.4 (epicentro San José del Palmar). Mientras el mercado esté en recuperación:

1. **Clasificar antes de contactar.** Solo hoteles `OPERANDO` u `OPERANDO CON DAÑOS LEVES` según
   `01_Lista_Prospectos_v2_post_sismo.md`. `CERRADO / DAÑO GRAVE` = excluido (re-evaluar a 90+ días).
2. **Verificar el mismo día de cada envío** (Maps/Booking: ¿reservable? ¿reseñas recientes?).
   La lista es la base de trabajo, NO el estado actual del hotel.
3. **Empatía primero.** Nunca abrir con la cifra de fuga ante un hotel afectado. Las variantes
   post-sismo D/E/F del archivo 02 REEMPLAZAN las aperturas A/B/C mientras dure la reactivación.
4. **Las cifras son techo, no promesa.** Los benchmarks regionales son pre-sismo (ocupación 51,2%,
   ADR $280K): toda estimación Tier B/C lleva disclaimer reforzado y la fuga se calcula con la
   ocupación REAL que declare el hotel, nunca con el benchmark.

---

## FLUJO DE TRABAJO EN 6 FASES

```
FASE 1          FASE 2           FASE 3         FASE 4        FASE 5        FASE 6
PREPARAR   →   CONTACTAR   →   REUNIRSE   →   ENTREGAR   →   IMPLEMENTAR  →  RETENER
(archivo 01)   (archivo 02)    (archivo 03)    (iah-cli)      (upsell)      (recurrente)
                                        ↓
                                  (archivo 04: precios, siempre a la mano)
```

> **Condiciones canónicas de la escalera (D2 / `config/pricing.yaml`):** el Express se paga COMPLETO
> al encargar ($120.000) y se entrega en ≤72 h; la Implementación va 50% anticipo / 50% contra entrega.
> Donde estas fases hablan de "Nivel 2/3" del archivo 04, hoy se lee Implementación y Seguimiento.

### FASE 1 — PREPARAR (antes del primer contacto)
**Archivo:** `01_Lista_Prospectos_v2_post_sismo.md` (estados) + v1 (solo fichas de detalle)

1. Tomar el top 10 de la tabla priorizada (post-sismo: 8 OPERANDO verificados; detalle en `05_Pipeline_PostSismo.md`).
2. Verificar teléfonos pendientes: buscar cada hotel en Google Maps → la ficha
   muestra teléfono/WhatsApp. Actualizar la tabla (15-20 min de trabajo).
3. Para los 3 primeros prospectos: capturar evidencia de debilidad digital:
   - Captura de búsqueda "hotel en [zona]" en Google Maps (¿sale o no sale?)
   - Captura de pregunta a ChatGPT: "recomiéndame un hotel en [ciudad]"
   - Revisar su web/redes: ¿solo Booking? ¿solo Instagram?
4. Anotar: habitaciones aprox. + tarifa promedio (de su Booking/web) →
   calcular fuga estimada con la fórmula del archivo 03.

**Salida de la fase:** 3 prospectos listos con teléfono verificado + evidencia
+ fuga estimada calculada.

### FASE 2 — CONTACTAR
**Archivo:** `02_Mensaje_Prospeccion_WhatsApp.md`

1. Enviar Mensaje 1 (VARIANTES POST-SISMO D/E/F según el estado del hotel) personalizando la línea 1
   con el hallazgo real — borradores listos en `06_Borradores_Mensaje1_Paso0.md`.
2. Horario: martes-jueves, 9-11 am o 3-5 pm.
3. Si responde con interés → Mensaje 2 → agendar reunión con día/hora concreta.
4. Si no responde: Follow-up día 4-5 (Mensaje 3), cierre día 9-10 (Mensaje 4).
5. Registrar todo en el pipeline vivo `05_Pipeline_PostSismo.md` (Estado funnel + próxima acción con fecha).

**Meta:** 5 contactos/semana → 1-2 reuniones/semana.

### FASE 3 — REUNIRSE (los 20 minutos)
**Archivo:** `03_Guion_Reunion_Venta.md` + `04_Estructura_Precios.md`

1. Preparación 30 min antes (checklist del archivo 03): corrida del diagnóstico,
   PDF gancho impreso, fuga calculada.
2. Ejecutar los 6 bloques del guion: Apertura → Problema en pesos → 3 hallazgos
   → Solución → Precio → Cierre.
3. El PDF gancho SE ENTREGA siempre, compre o no.
4. Si compra: 50% anticipado antes de correr nada. Acordar fecha de entrega.
5. El mismo día: WhatsApp de seguimiento + actualizar pipeline.

### FASE 4 — ENTREGAR (el diagnóstico pago)
**Herramienta:** iah-cli v4complete + PDF gancho

1. Correr diagnóstico completo contra el sitio del hotel.
2. Generar informe PDF + preparar sesión de entrega de 1 hora.
3. Entregar en 3-5 días hábiles. Cobrar el 50% restante.
4. Al final de la sesión de entrega: presentar la propuesta de implementación
   (Nivel 2 del archivo 04) con la fuga ya cuantificada.

### FASE 5 — IMPLEMENTAR (upsell)
**Archivo:** `04_Estructura_Precios.md` (Nivel 2)

1. Implementar assets: schema, GBP, llms.txt, FAQ, correcciones on-page.
2. 50% inicio / 50% entrega. Plazo 2-3 semanas.
3. Al entregar: ofrecer el primer mes de monitoreo gratis (gancho al Nivel 3).

### FASE 6 — RETENER (ingreso recurrente = base pensional)
**Archivo:** `04_Estructura_Precios.md` (Nivel 3)

1. Re-corrida mensual del diagnóstico + informe de variaciones + alertas.
2. Contrato mínimo 3 meses.
3. META ESTRATÉGICA: 4-5 clientes en este nivel = $1,6M–2M COP/mes recurrente
   ($400.000/mes cada uno, escalera canónica) → cotización pensional como
   independiente sostenida.

---

## PIPELINE (registro de seguimiento)

> **El registro vivo es `05_Pipeline_PostSismo.md`** (ya creado: top 10 + teléfonos + funnel).
> Esta tabla define los campos; ahí se actualiza diariamente (10 min).

Llevar este control en Notion, Excel o libreta — pero LLEVARLO:

| Campo | Ejemplo |
|-------|---------|
| Hotel | Hotel Condina |
| Contacto / cargo | Sr. Pérez, administrador |
| Teléfono | 3XX XXX XXXX |
| Tamaño / tarifa | ~25 hab, $180.000 |
| Fuga estimada/mes | ~$2,1M COP |
| Estado | Contactado / Reunión agendada / Propuesta / Ganado / Perdido |
| Último contacto | 2026-07-25 |
| Próxima acción + fecha | Follow-up 2026-07-29 |

Regla: un prospecto sin "próxima acción + fecha" es un prospecto muerto.

---

## METAS DE LA RUTA DE 30 DÍAS (SPRINT §7 del CONTEXTO MAESTRO v3.0 — Día 1: 2026-08-26)

- Semana 0 (26–27 ago): pipeline corriendo; PDF gancho cronometrado; mapa post-sismo top 10
  → Paso 0 CERRADO (8 OPERANDO + teléfonos + borradores listos). Pendiente: corrida cronometrada.
- Semana 1 (28 ago–3 sep): estado operativo top 10 verificado + ≥2 respuestas de primeros contactos
- Semana 2 (4–10 sep): ≥2 reuniones de 20 min con decisores (+1-2 hallazgos anonimizados en X/Instagram)
- Semana 3 (11–17 sep): ≥1 Express PAGO ($120.000; el cobro es ANTES de correr)
- Semana 4 (18–24 sep): caja cobrada + testimonio/caso documentado
- Día 30 (24 sep): revisión kill/pivot obligatoria

Umbrales y reglas de decisión por semana: §7 del maestro (fuente que manda).

## REGLAS TRANSVERSALES (resumen de todo el kit)

1. Hablar de RESERVAS y PESOS, nunca de tecnología en primer contacto.
2. Precio solo DESPUÉS de mostrar la fuga en pesos.
3. 50% anticipado siempre en Implementación; el Express se paga completo al encargar.
   Sin pago no hay corrida.
4. Si regatean: bajar alcance, nunca precio.
5. Escalera canónica (fuente única: `config/pricing.yaml`):
   Gancho $0 → Express $120.000 → Implementación $1,5M–3,5M → Seguimiento $400.000/mes.
6. Máximo 2-3 ganchos gratis al mes; se generan SOLO para quien respondió el WhatsApp.
   Jamás PDF en frío a quien no respondió.
7. Todo contacto queda registrado con próxima acción y fecha (en `05_Pipeline_PostSismo.md`).
8. Ningún contacto sin verificar estado post-sismo ese mismo día (protocolo §6.5, arriba).
