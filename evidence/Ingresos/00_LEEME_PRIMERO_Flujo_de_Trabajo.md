# Kit Comercial — Diagnóstico de Fuga de Reservas Directas
# FLUJO DE TRABAJO COMPLETO | Proyecto: iah-cli | Fecha: 2026-07-21

## ¿Qué es esto?

Sistema de venta de diagnósticos de visibilidad digital a hoteles del Eje Cafetero.
Producto: corres iah-cli v4complete → entregas informe que cuantifica en pesos
las reservas que el hotel pierde hacia Booking/OTAs/competencia → vendes la
implementación de las correcciones → vendes monitoreo mensual recurrente.

---

## ESTRUCTURA DE ARCHIVOS

```
evidence/
│
├── 00_LEEME_PRIMERO_Flujo_de_Trabajo.md   ← ESTE ARCHIVO (el mapa)
│
├── 01_Lista_Prospectos_Eje_Cafetero.md    ← A QUIÉN venderle (30 hoteles priorizados)
├── 02_Mensaje_Prospeccion_WhatsApp.md     ← CÓMO conseguir la cita (4 mensajes)
├── 03_Guion_Reunion_Venta.md              ← CÓMO vender en los 20 minutos
├── 04_Estructura_Precios.md               ← CUÁNTO cobrar (4 niveles + políticas)
│
└── Guion.md                               ← Documento base: modelo de negocio y ruta 30 días
```

---

## FLUJO DE TRABAJO EN 6 FASES

```
FASE 1          FASE 2           FASE 3         FASE 4        FASE 5        FASE 6
PREPARAR   →   CONTACTAR   →   REUNIRSE   →   ENTREGAR   →   IMPLEMENTAR  →  RETENER
(archivo 01)   (archivo 02)    (archivo 03)    (iah-cli)      (upsell)      (recurrente)
                                        ↓
                                  (archivo 04: precios, siempre a la mano)
```

### FASE 1 — PREPARAR (antes del primer contacto)
**Archivo:** `01_Lista_Prospectos_Eje_Cafetero.md`

1. Tomar el top 10 de la tabla priorizada.
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

1. Enviar Mensaje 1 (variante según el tipo de hotel) personalizando la línea 1
   con el hallazgo real de la Fase 1.
2. Horario: martes-jueves, 9-11 am o 3-5 pm.
3. Si responde con interés → Mensaje 2 → agendar reunión con día/hora concreta.
4. Si no responde: Follow-up día 4-5 (Mensaje 3), cierre día 9-10 (Mensaje 4).
5. Registrar todo en el pipeline (ver sección PIPELINE abajo).

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
3. META ESTRATÉGICA: 4-5 clientes en este nivel = $1,2M-2,5M COP/mes
   recurrente → cotización pensional como independiente sostenida.

---

## PIPELINE (registro de seguimiento)

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

## METAS DE LA RUTA DE 30 DÍAS (del documento base Guion.md)

- Semana 1: Fase 1 completa + pulir PDF gancho con caso muestra (Luxor)
- Semana 2: 15-20 contactos enviados + 2-3 publicaciones en X/Instagram
  con hallazgos anonimizados (marketing gratis)
- Semana 3-4: 5-8 reuniones → 1-3 diagnósticos pagos ($400K-2,4M COP)

## REGLAS TRANSVERSALES (resumen de todo el kit)

1. Hablar de RESERVAS y PESOS, nunca de tecnología en primer contacto.
2. Precio solo DESPUÉS de mostrar la fuga en pesos.
3. 50% anticipado siempre. Sin anticipo no hay corrida.
4. Si regatean: bajar alcance, nunca precio. Piso: $300.000.
5. Máximo 2-3 demos gratis al mes.
6. Todo contacto queda registrado con próxima acción y fecha.
