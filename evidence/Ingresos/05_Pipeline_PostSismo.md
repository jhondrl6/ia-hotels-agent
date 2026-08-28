# Pipeline Post-Sismo — Registro de Prospección (§8 CONTEXTO MAESTRO v3.0)

> **Creado:** 2026-08-26 (Paso 0 completo). **Base:** `01_Lista_Prospectos_v2_post_sismo.md` (estados verificados) + `02_Mensaje_Prospeccion_WhatsApp.md` (variantes D/E/F).
> **Regla §6.5:** solo se contacta a hoteles `OPERANDO` u `OPERANDO CON DAÑOS LEVES`. CERRADO = excluido, re-evaluar 90+ días.
> **Actualización:** diaria, 10 min. Funnel: Contactado → Respondió → Reunión → Express vendido → Implementación → Retenido.
> **Benchmarks:** 20 contactos → 5–8 respuestas (≥25%) → 3–5 reuniones → 1–2 ventas.

## Campos
Hotel | Contacto (a confirmar) | Teléfono (Paso 0) | Estado post-terremoto (§6.5) | Tamaño·tarifa·Fuga est. (Semana 1) | Estado funnel | Variante mensaje | Próxima acción + fecha

---

## TOP 10 — REGISTRO INICIAL (Paso 0)

| # | Hotel | Contacto | Teléfono (Paso 0) | Estado post-terremoto | Tamaño·tarifa·Fuga | Estado funnel | Var. | Próxima acción + fecha |
|---|-------|----------|-------------------|------------------------|---------------------|----------------|------|------------------------|
| 1 | Hotel Condina Pereira | — | (v1: por confirmar) | AFECTADO — VERIFICACIÓN FÍSICA EN CURSO | — | No contactar | — | Desplazamiento in situ (2026-08-27): confirmar estado y decidir inclusión/archivo |
| 2 | Hotel Cataluña Pereira | — | — | CERRADO / DAÑO GRAVE — EXCLUIDO | — | Excluido | — | Re-evaluar 90+ días (2026-11-26) |
| 3 | Hostal Ciudad de Segorbe | — | +57 310 825 2436 | OPERANDO | — | Pendiente contacto | D | SIN WEB PROPIA (verificado 27-08) → inviable v4complete/PDF gancho; decidir flujo manual o reemplazo |
| 4 | Hotel Salento Real Eje Cafetero | — | +57 316 629 6142 (✓ doble verificada: Maps + v4complete) | OPERANDO | ~10 hab est.·$280K est.·fuga est. $4,0M/mes (Tier B) | Pendiente contacto | D | Corrida técnica 27-08: 2 min, PDF gancho ✓; docs comerciales bloqueados por gate (ver LOG). Contactar tras revisión técnica |
| 5 | Hotel Guadalupe Plaza | — | +57 317 543 9207 | OPERANDO* (llamar p/ daños leves) | — | Pendiente contacto | F | Llamada confirmatoria daños + Mensaje 1 (F) |
| 6 | Hotel Platino Plaza | — | +57 314 654 3050 | OPERANDO* (llamar p/ daños leves) | — | Pendiente contacto | F | Llamada confirmatoria daños + Mensaje 1 (F) |
| 7 | Hotel Tangara | — | +57 316 328 9569 | OPERANDO* (llamar p/ daños leves) | — | Pendiente contacto | F | Llamada confirmatoria daños + Mensaje 1 (F) |
| 8 | Finca Hotel Villa Ilusión | — | +57 315 271 1519 | OPERANDO* (llamar p/ daños leves) | — | Pendiente contacto | F | Llamada confirmatoria daños + Mensaje 1 (F) |
| 9 | Hotel Vísperas | — | +57 316 824 5636 | OPERANDO | — | Pendiente contacto | D | Verif. Maps/Booking día envío + Mensaje 1 |
| 10 | Hotel Recreacional Marcelandia | — | +57 320 204 2595 | OPERANDO | — | Pendiente contacto | D | Verif. Maps/Booking día envío + Mensaje 1 |

(*) OPERANDO con llamada pendiente para confirmar "daños leves". Hasta confirmar, Variante F (máxima prudencia) y línea 1 genérica (sin mencionar daños). Si confirma daños leves → sigue F con tono empático reforzado. Si confirma intacto → pasa a Variante D.

---

## RESUMEN Paso 0
- 8 de 10 OPERANDO (≥5) → regla de prudencia NO se activa → la ola procede.
- 2 excluidos: #1 Condina (llamada pendiente), #2 Cataluña (daño grave).
- Teléfonos: 8/8 verificados (Villa Ilusión #8 confirmada 2026-08-26).
- Embudo listo para primera ola (Semana 1): 5–10 WhatsApp martes–jueves 9–11 am / 3–5 pm.

---

## TAREAS SEMANA 1 (pendientes antes/para enviar)
- [ ] Llamadas a #5–#8 (Dosquebradas) para cerrar OPERANDO vs OPERANDO CON DAÑOS LEVES.
- [ ] Llamada a #1 Condina para decidir inclusión o archivo.
- [ ] Capturar evidencia de debilidad digital (GBP/schema/AEO) de los 3 primeros a contactar (Maps + ChatGPT) antes del Mensaje 2.
- [ ] Completar columna "Tamaño·tarifa·Fuga est." de los que respondan/agenden.
- [ ] Registrar cada envío/follow-up en la columna "Estado funnel" + fecha.

---

## LOG DE ACTUALIZACIONES
| Fecha | Cambio |
|-------|--------|
| 2026-08-26 | Paso 0 completo: 8 OPERANDO verificados + teléfonos; pipeline inicial creado. Villa Ilusión #8 confirmada (+57 315 271 1519). |
| 2026-08-27 | **Corrida técnica Semana 0 (hito §7)** contra Salento Real #4: v4complete **2 min** (18:01:42→18:03:41, tope 45) + hook-pdf ✓ → `output/v4_complete/deliveries/hotelsalentoreal_gancho.pdf`. WhatsApp auto-verificado +573166296142 (= teléfono del pipeline). Coherencia 0.84–0.88; 7 brechas reales (sin Schema Hotel, AEO 15 vs 44 regional, SEO 25 vs 59). **Bloqueo:** gate `proposal_asset_alignment` (4 assets prometidos no generados) → docs comerciales eliminados y ZIP abortado; arreglar ANTES de vender (§7). **Dualidad de precios detectada:** pricing.yaml `monthly_default` $1,2M vs maestro §5 $400K/mes (el hook usa $1,2M; la propuesta aplicó floor $400K). #3 Segorbe: SIN WEB confirmada → inviable v4complete. #1 Condina: pasa a verificación física in situ. |
