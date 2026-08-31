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
| 1 | Finca Hotel Don Julio (reemplaza a #1 Condina) | — | Pendiente (no publicado en fuentes web; capturar vía Maps/Instagram) | OPERANDO* (reservable en Booking/Agoda 29-08; sin reportes de afectación — verificar same-day §6.5) | Por capturar (hab/tarifa/fuga) | Pendiente contacto | D | ⚠️ **SIN WEB PROPIA detectada** (solo OTAs + IG @fincahoteldonjulio) → confirmar con pregunta directa; si no tiene web = mismo caso #3 Segorbe (v4complete inviable → flujo manual o reemplazo). Obtener teléfono + evidencia digital antes del Mensaje 1 |
| 2 | Hotel Cataluña Pereira | — | — | CERRADO / DAÑO GRAVE — EXCLUIDO | — | Excluido | — | Re-evaluar 90+ días (2026-11-26) |
| 3 | Hostal Ciudad de Segorbe | — | +57 310 825 2436 | OPERANDO | — | Pendiente contacto | D | SIN WEB PROPIA (verificado 27-08) → inviable v4complete/PDF gancho; decidir flujo manual o reemplazo |
| 4 | Hotel Salento Real Eje Cafetero | — | +57 316 629 6142 (✓ doble verificada: Maps + v4complete) | OPERANDO | ~10 hab est.·$280K est.·fuga est. $4,0M/mes (Tier B) | Pendiente contacto | D | **DESBLOQUEADO 28-08** (plan SR-PIPELINE-FIXES v4.73.0; smoke 7/7: docs comerciales 01/02 + ZIP ✓). Contactar: verificar Maps/Booking mismo día del envío (§6.5) + Mensaje 1 |
| 5 | Hotel Guadalupe Plaza | — | +57 317 543 9207 | OPERANDO (confirmado 31-08) | — | Pendiente contacto | F | **SIN WEB PROPIA** (verificado 31-08) → inviable v4complete/PDF gancho; flujo manual o reemplazo. Mensaje 1 (F) si se decide contacto |
| 6 | Hotel Platino Plaza | — | +57 314 654 3050 | OPERANDO (confirmado 31-08) | — | Pendiente contacto | F | **SIN WEB PROPIA** (verificado 31-08) → inviable v4complete/PDF gancho; flujo manual o reemplazo. Mensaje 1 (F) si se decide contacto |
| 7 | Hotel Tangara | — | +57 316 328 9569 | OPERANDO (confirmado 31-08) | — | Pendiente contacto | F | **SIN WEB PROPIA** (verificado 31-08) → inviable v4complete/PDF gancho; flujo manual o reemplazo. Mensaje 1 (F) si se decide contacto |
| 8 | Finca Hotel Villa Ilusión | — | +57 315 271 1519 | OPERANDO (confirmado 31-08) | — | Pendiente contacto | F | **CON WEB PROPIA** (verificado 31-08) → v4complete viable. Confirmar daños leves vs intacto; si intacto pasa a Var D. Verif. Maps/Booking día envío + Mensaje 1 |
| 9 | Hotel Vísperas | — | +57 316 824 5636 | OPERANDO | — | Excluido | — | **INVIABLE** (verificado 31-08 por Jhon) → archivado; buscar reemplazo en Google Maps |
| 10 | Hotel Recreacional Marcelandia | — | +57 320 204 2595 | OPERANDO | — | Pendiente contacto | D | **SIN WEB PROPIA** (verificado 31-08) → inviable v4complete/PDF gancho; flujo manual o reemplazo |

(*) OPERANDO con llamada pendiente para confirmar "daños leves". Hasta confirmar, Variante F (máxima prudencia) y línea 1 genérica (sin mencionar daños). Si confirma daños leves → sigue F con tono empático reforzado. Si confirma intacto → pasa a Variante D.

---

## NUEVOS CANDIDATOS — PROSPECCIÓN GOOGLE MAPS (31-08)

> Fuente: búsqueda directa en Google Maps (Pereira, Santa Rosa de Cabal, Salento) + 1 aporte directo de Jhon. Filtro doble: **web propia** (dominio real, no Facebook/Instagram/booking engine) **Y pase del guard `own_site_guard` del plan VALIDADOR-URL-PROPIA-2026-08-30** (`classify_url` ejecutado contra cada URL). 22 fichas revisadas → 6 cumplen; +1 aportado (#17).

| # | Hotel | Teléfono | Web propia (guard) | Rating | Zona | Estado funnel | Var. | Próxima acción + fecha |
|---|-------|----------|-------------------|--------|------|----------------|------|------------------------|
| 11 | **Hotel El Jardín Salento** | +57 310 595 3017 | hoteleljardinsalento.com ✅ PASSED | 4.3★ | Salento (Cl 7 #5-22) | Pendiente contacto | D | Verificar estado post-sismo same-day (§6.5) + redactar Mensaje 1 con hallazgo real + contacto |
| 12 | **HOTEL D'LYON** | +57 310 538 6037 | hoteldlyonsrc.com ✅ PASSED | 4.3★ | Santa Rosa de Cabal (Cl 17 #11-50) | Pendiente contacto | D | Verificar estado post-sismo same-day + Mensaje 1 + contacto |
| 13 | **Sazagua Pereira Hotel Boutique** | +57 313 649 4579 | sazagua.com ✅ PASSED | 4.7★ | Cerritos, Pereira (Km 5 vía Quimbayita) | Pendiente contacto | D | Verificar estado post-sismo same-day + Mensaje 1 + contacto (boutique = Tier A/B potencial) |
| 14 | **Hotel Rosales Suites** | +57 322 587 6653 | hotelrosalesuites.com ✅ PASSED | 4.4★ | Pereira (Cra 9 #25-44) | Pendiente contacto | D | Verificar estado post-sismo same-day + Mensaje 1 + contacto |
| 15 | **Hotel San Antonio del Cerro** | 606 340 0229 (fijo; capturar celular) | hotelsanantoniodelcerro.com.co ✅ PASSED | 4.4★ | La Virginia/Cerritos (Km 1 vía Cerritos) | Pendiente contacto | D | Obtener WhatsApp/celular (solo fijo publicado) + verificar estado same-day + Mensaje 1 |
| 16 | **San Vicente Reserva Termal** | +57 320 693 3707 | sanvicente.com.co ✅ PASSED | 4.3★ | Santa Rosa de Cabal — Termales (Potreros) | Pendiente contacto | D | Verificar estado post-sismo same-day + Mensaje 1 + contacto (resort termal = Tier A potencial) |
| 17 | **Termales Tierra Viva** | +57 301 261 7394 | termalestierraviva.com ✅ PASSED (URL aportada por Jhon) | 4.5★ (5,123 opiniones) | Villamaría, Caldas (Km 2 vía Enea Gallinazo) | Pendiente contacto | D | **OPERANDO sin afectaciones** (confirmado por Jhon 31-08) → redactar Mensaje 1 con hallazgo real + contacto (resort termal = Tier A potencial) |

**Descartados en la misma pasada:** Grand Palace (solo "istagram.com" — dominio typo, no sitio real), Castellón Plaza, Escocia, La Porra, Kimaná Hostal, Cielito Lindo, Yellow Hotel Maraya, Catalina Plaza, Torre Ejecutiva, Hotel 925, Palmas de Salento, Natura Cocora, Tumbaga88 (sin web); Pereira 421 (Facebook → BLOQUEADA por el guard), Carriqui Garden y Suite Santa Rosa (solo booking engine hosroom.com), Santa Juana, Aparta Hotel Termales (sin web).
**Santa Rosa de Cabal AGOTADA** (búsqueda urbana + zona termal): solo 2 con web propia (D'Lyon #12, San Vicente #16).
**Nota técnica:** `istagram.com` y `hosroom.com` fueron AGREGADOS a la blocklist v2 del guard (v4.74.1) el 31-08 tras esta detección; hoy ambos son BLOQUEADOS automáticamente. El descarte original fue por juicio humano y quedó formalizado en el código.

---

## RESUMEN Paso 0 (actualizado 31-08 — reestructuración)
- **Con web propia + guard PASSED (v4complete viable): 9** → #4 Salento Real, #8 Villa Ilusión, #11 El Jardín Salento, #12 D'Lyon, #13 Sazagua, #14 Rosales Suites, #15 San Antonio del Cerro, #16 San Vicente Reserva Termal, #17 Termales Tierra Viva. Cuello de botella RESUELTO.
- **Sin web propia (v4complete inviable):** #3 Segorbe, #5 Guadalupe, #6 Platino, #7 Tangara, #10 Marcelandia → flujo manual o archivar.
- **Excluidos:** #2 Cataluña (daño grave), #9 Vísperas (inviable 31-08), Condina (no operativo).
- **Por verificar:** #1 Don Julio (teléfono pendiente, probablemente sin web).
- Prioridad de contacto: #4 y #8 (ya preparados) → #11 El Jardín (misma zona conocida Salento) → #12/#16/#17 zona termal → #13/#14/#15 Pereira-Cerritos.

---

## TAREAS SEMANA 1 (reestructuradas 31-08)
- [x] ~~Llamadas a #5–#8 (Dosquebradas)~~ **RESUELTO 31-08:** #5 Guadalupe, #6 Platino, #7 Tangara = OPERANDO sin web; #8 Villa Ilusión = OPERANDO con web.
- [x] ~~Llamada a #1 Condina~~ **CERRADO 29-08 in situ: NO OPERATIVO** → excluido, reemplazado por Don Julio.
- [x] ~~Verificar web de #9 Vísperas y #10 Marcelandia~~ **RESUELTO 31-08:** Vísperas inviable → excluido; Marcelandia sin web.
- [x] ~~🔴 CRÍTICO: ampliar lista en Google Maps~~ **RESUELTO 31-08:** 22 fichas revisadas (Pereira, Salento, Santa Rosa urbana + termales) → 6 nuevos candidatos con web propia que PASAN el guard (#11–#16); +1 aporte de Jhon (#17 Tierra Viva). Embudo: 9 viables. Santa Rosa agotada.
- [ ] Redactar Mensajes 1 para #11–#17 con hallazgo real (plantilla 06_Borradores) — requiere verificación de debilidad digital de cada uno.
- [ ] Obtener celular de #15 San Antonio del Cerro (solo tiene fijo publicado).
- [ ] Obtener teléfono + verificar web de Don Julio (#1).
- [ ] Decidir flujo para los 5 sin web (#3, #5, #6, #7, #10): contacto manual con diagnóstico verbal / archivar.
- [ ] Capturar evidencia de debilidad digital de #4 Salento Real y #8 Villa Ilusión antes del Mensaje 2.
- [ ] Enviar Mensaje 1 a #4 Salento Real y #8 Villa Ilusión (verificación same-day §6.5 antes).
- [ ] Completar columna "Tamaño·tarifa·Fuga est." de los que respondan/agenden.
- [ ] Registrar cada envío/follow-up en la columna "Estado funnel" + fecha.

---

## LOG DE ACTUALIZACIONES
| Fecha | Cambio |
|-------|--------|
| 2026-08-26 | Paso 0 completo: 8 OPERANDO verificados + teléfonos; pipeline inicial creado. Villa Ilusión #8 confirmada (+57 315 271 1519). |
| 2026-08-27 | **Corrida técnica Semana 0 (hito §7)** contra Salento Real #4: v4complete **2 min** (18:01:42→18:03:41, tope 45) + hook-pdf ✓ → `output/v4_complete/deliveries/hotelsalentoreal_gancho.pdf`. WhatsApp auto-verificado +573166296142 (= teléfono del pipeline). Coherencia 0.84–0.88; 7 brechas reales (sin Schema Hotel, AEO 15 vs 44 regional, SEO 25 vs 59). **Bloqueo:** gate `proposal_asset_alignment` (4 assets prometidos no generados) → docs comerciales eliminados y ZIP abortado; arreglar ANTES de vender (§7). **Dualidad de precios detectada:** pricing.yaml `monthly_default` $1,2M vs maestro §5 $400K/mes (el hook usa $1,2M; la propuesta aplicó floor $400K). #3 Segorbe: SIN WEB confirmada → inviable v4complete. #1 Condina: pasa a verificación física in situ. |
| 2026-08-28 | **#4 Salento Real DESBLOQUEADO:** plan `SR-PIPELINE-FIXES-2026-08-27` cerrado (v4.73.0; 11 fases ✅; VERIFY AC1–AC13 13/13 SUPERADOS). Corrida final D-PF7 smoke **7/7**: READY_FOR_PUBLICATION, coherencia 0.88, `promised_assets_exist` PASSED (1.0), docs comerciales 01/02 + ZIP generados (`evidence/FASE-SR-H2/`), financiera idéntica al baseline. #4 listo para contactar → verificar Maps/Booking el mismo día del envío (§6.5). |
| 2026-08-28 | **Dualidad de precios RESUELTA:** `pricing.yaml` `monthly_default` $1,2M → **$400K**, alineado con maestro §5, escalera canónica y lo que la propuesta H2 + gate `pricing_compliance` ya usaban (`monthly_price_cop: 400000`). Tests pricing/hook/gate sin regresión (1 fallo preexistente certificado en HEAD: `test_tiers_boutique_min_price` espera 1,2M vs yaml 800K); validaciones quick 6/6. Hook PDF regenerado con $400K/mes → `output/salentoreal_final_v4c_h2/v4_complete/deliveries/hotelsalentoreal_gancho.pdf` (el PDF viejo con $1,2M ya no existía en disco). |
| 2026-08-29 | **#1 Condina EXCLUIDO — verificado in situ:** el hotel sufrió afectaciones por el terremoto y **NO está operativo** (desplazamiento del equipo). Pasa a archivo con re-evaluación 90+ días (2026-11-29). **Reemplazo decidido: Finca Hotel Don Julio** (Santa Rosa de Cabal, IG @fincahoteldonjulio). Verificación web 29-08: reservable en Booking/Agoda/Trivago/Google Hotels → OPERANDO* pendiente confirmación same-day; **sin web propia detectada** (solo OTAs + Instagram) → mismo riesgo de viabilidad que #3 Segorbe para v4complete/PDF gancho; teléfono no publicado → capturar vía Maps/IG. Cuenta de viables para la ola: 7 con teléfono + Don Julio por verificar. |
| 2026-08-31 | **Verificación web Dosquebradas completada:** #5 Guadalupe Plaza, #6 Platino Plaza, #7 Tangara = OPERANDO confirmados, **SIN WEB PROPIA** → v4complete inviable (flujo manual o reemplazo). #8 Villa Ilusión = OPERANDO confirmada, **CON WEB PROPIA** → v4complete viable. Nuevo balance: 2 con web (#4, #8), 4 sin web (#3, #5, #6, #7), 3 por verificar (#1, #9, #10). Tareas Semana 1 actualizadas. |
| 2026-08-31 | **REESTRUCTURACIÓN del top 10:** #10 Marcelandia **SIN WEB PROPIA** → v4complete inviable. #9 Vísperas **INVIABLE** → excluido (reemplazo pendiente). Solo quedan 2 viables para v4complete+WhatsApp (#4 Salento Real, #8 Villa Ilusión) = cuello de botella. **Acción crítica aprobada:** ampliar lista prospectando en Google Maps hoteles del Eje Cafetero CON WEB PROPIA + teléfono. |
| 2026-08-31 | **PROSPECCIÓN GOOGLE MAPS COMPLETADA:** 22 fichas revisadas en Pereira / Salento / Santa Rosa de Cabal (urbana + zona termal) → **6 nuevos candidatos con web propia** (#11 El Jardín Salento, #12 D'Lyon, #13 Sazagua, #14 Rosales Suites, #15 San Antonio del Cerro, #16 San Vicente Reserva Termal). **Todas las URLs validadas contra el guard `own_site_guard`** (plan VALIDADOR-URL-PROPIA-2026-08-30): 6/6 PASSED; Facebook de Pereira 421 BLOQUEADA por el guard (confirma descarte). Embudo viable: **8 hoteles**. Pendiente: celular de #15 (solo fijo), borradores Mensaje 1 con hallazgo real para #11–#16, verificación post-sismo same-day de cada nuevo candidato. Observación para revisión trimestral de `config/url_blocklist.yaml`: `istagram.com` (typo-squat) y `hosroom.com` (booking engine) pasan el guard técnicamente. |
| 2026-08-31 | **#17 Termales Tierra Viva INCLUIDO (aporte de Jhon):** URL `termalestierraviva.com` → guard PASSED (`classify_url`, netloc limpio). Ficha Maps capturada: 4.5★ con 5,123 opiniones, celular +57 301 261 7394, Villamaría/Caldas (Km 2 vía Enea Gallinazo, eje termal contiguo a Santa Rosa). **Estado post-sismo confirmado por Jhon el mismo día: OPERANDO, sin afectaciones** → verificación same-day cerrada, listo para Mensaje 1 (Var D). Embudo viable: **9 hoteles**. Mismo día se publicó **blocklist v2 (v4.74.1)**: `istagram.com` + `hosroom.com` agregados a `config/url_blocklist.yaml` con tests de contrato (65/65 verde) → el gap de la nota anterior queda cerrado en código. `01_Lista_Prospectos_v2_post_sismo.md` sincronizada (criterio guard, #17, renumeración #18–#37). |
