# Lista de Prospectos v2 — Verificación Post-Sismo

> **Base:** `01_Lista_Prospectos_Eje_Cafetero.md` (compilada 2026-07-21, PRE-sismo; sus fichas de detalle siguen siendo válidas para datos de contacto y debilidad digital).
> **Creada:** 2026-08-26. **Última actualización:** 2026-09-05 (reemplazo #9: Vísperas → Casa San Carlos Lodge). **Método:** Protocolo Post-Terremoto §6.5 del CONTEXTO MAESTRO v3.0.
> **Evento:** Terremoto M7.4 del 2026-08-10 (epicentro San José del Palmar).

## Reglas de uso

1. **Solo se contactan hoteles con estado `OPERANDO` o `OPERANDO CON DAÑOS LEVES`** verificado hace ≤7 días.
2. `CERRADO / DAÑO GRAVE` = excluido de prospección; registro respetuoso, re-evaluación a 90+ días (futuro cliente de relanzamiento cuando reabra).
3. Estados `SIN VERIFICAR` requieren verificación activa ANTES de cualquier contacto (fuentes en orden: Cotelco/alcaldías → Google Maps/Booking: ¿reservable? ¿reseñas/posts recientes? → llamada/visita).
4. La v1 queda como histórico: usar SUS fichas para teléfonos y detalle, NUNCA sus estados.
5. **Presencia de sitio web propio que pase el guard `own_site_guard` (v4.74.1, blocklist v2) ES requisito para entrar al embudo WhatsApp/v4complete.** El pipeline iah-cli v4.74.x rechaza URLs de OTAs, redes sociales y booking engines antes de cualquier llamada de red/API (`modules/data_validation/own_site_guard.py`; exit code 2). Prospectos sin web propia o cuya "web" sea Facebook/Instagram/hosroom.com/istagram.com quedan marcados como **inviables v4complete** → flujo manual o archivo. La señal de debilidad digital se re-audita caso a caso corriendo `v4complete` sobre la URL del sitio propio validado por el guard.

---

## Re-auditoría de debilidad digital (actualizada 2026-09-05)

La señal "sin web propia" de la lista v1 (compilada 2026-07-21) estaba **obsoleta**. Evidencia:
- **Hotel Salento Real (#4):** tiene sitio oficial `hotelsalentoreal.com` (34 hab, reservas online). La ficha v1 decía "sin web propia clara".
- **Hotel Vísperas (#9):** tenía sitio oficial `hotelvisperas.com` (confirmado 2026-08-27), pero fue marcado **INVIABLE** el 2026-08-31 por Jhon → excluido del embudo.
- **Reemplazo (2026-09-05):** Casa San Carlos Lodge ocupa el cupo #9 (casasancarlos.com, Pereira; `classify_url()` del guard sin bloqueo). Ubicación: vía Marsella Km 6 (dato Jhon 05-09). Estado same-day por confirmar.

**Criterio vigente desde 2026-08-31:** el filtro "web propia que pase el guard `own_site_guard`" **SÍ es requisito** para entrar al embudo WhatsApp/v4complete. Razón: el plan VALIDADOR-URL-PROPIA (v4.74.0) + blocklist v2 (v4.74.1) enforcean que la URL de entrada sea el sitio propio del hotel; URLs de OTAs, redes sociales y booking engines se rechazan antes de cualquier llamada de red/API. Esto NO contradice la tesis de negocio: el cliente ideal sigue siendo el hotel con debilidad digital, pero esa debilidad se diagnostica CON v4complete sobre su sitio propio (no sobre fichas de terceros). Los hoteles sin web propia quedan marcados como inviables v4complete → flujo manual o archivo.

**Acción:** verificar presencia de sitio propio real ANTES de incluir cualquier prospecto en el embudo. Usar `classify_url()` del guard como filtro automático; los dominios `istagram.com` (typo-squat) y `hosroom.com` (booking engine) fueron agregados a la blocklist v2 (2026-08-31) tras detectarse en prospección Maps.

---

## Hallazgos verificados (2026-08-26, prensa y redes oficiales)

| Hallazgo | Evidencia | Impacto en la lista |
|----------|-----------|---------------------|
| **Hotel Cataluña Pereira (#2): DAÑOS GRAVES** | Instagram oficial del hotel (12-ago-2026): "A causa del terremoto, nuestro querido hotel sufrió graves daños" | **EXCLUIDO de prospección** |
| **Hotel Condina Pereira (#1): NO OPERATIVO — verificado in situ 2026-08-29** | Desplazamiento del equipo al lugar + TikTok viral "Cómo quedó el Hotel Condina" | **EXCLUIDO — reemplazado en top 10 por Finca Hotel Don Julio (Santa Rosa de Cabal); re-evaluar Condina 90+ días (2026-11-29)** |
| Hotel Veneton (Dosquebradas) en desmonte | Video Noti90/Instagram | No estaba en la lista; confirma riesgo ALTO en Dosquebradas |
| Balance Cotelco: 33 hoteles afectados, 6 por demoler (Cali), ~$13 mil millones COP en pérdidas sectoriales | Noti90 / AlInstante (ago-2026) | Contexto sectorial; sin lista nominal pública → la verificación es hotel por hotel |
| Quindío: ~2.500 inmuebles con afectaciones; Armenia, Quimbaya y Salento mencionados | Reportes de prensa | Riesgo municipal: ver tabla inferior |
| Salento: "apenas ha habido daños" estructurales, pero turismo colapsado | EFE / reportajes | **Zona prioritaria de contacto: hoteles intactos con máximo dolor de demanda** |
| Pereira: ~66 edificios colapsados, zona de bares dañada, toque de queda inicial | La Patria / Clarín / El País | Riesgo ALTO para hoteles del centro |

## Riesgo municipal estimado (estructura)

| Municipio | Riesgo | Base |
|-----------|--------|------|
| Pereira (centro) | **ALTO** | 66 edificios colapsados; Cataluña grave; Condina afectado |
| Quimbaya | **ALTO** | Basílica dañada, 450 viviendas destruidas, entre los más afectados del Quindío |
| Dosquebradas | **ALTO-MEDIO** | Veneton en desmonte; centro con edificaciones antiguas |
| Montenegro | **POR VERIFICAR** | Colinda con Quimbaya; sin reportes específicos |
| Filandia | **MEDIO** | Listado entre los afectados (El Tiempo), sin cifras |
| Armenia (periferia) | **MEDIO** | Grietas y daños; los prospectos son campestres, fuera del casco |
| Pereira (La Elvira / Arboleda) | **MEDIO** | Zonas no céntricas, edificaciones más recientes |
| Cerritos (Corregimiento de Pereira; keyword "Zona de Cerritos") | **MEDIO** | Periferia norte campestre de Pereira, colindante con centro ALTO; sin reportes de daño consultados. NO es municipio: es corregimiento de Pereira |
| Salento | **BAJO estructural** / crítico en demanda | "Apenas daños"; calles vacías |
| Santa Rosa de Cabal | **POR VERIFICAR** | Sin reportes específicos consultados. **ANCLA TERMINAL:** prioridad estratégica por ruta termal (Termales Santa Rosa / San Vicente); flujo regional depende de Pereira centro (ALTO). Prospectos entran por dolor de demanda termal |

---

## Tabla de verificación (30 top de la v1 + extras relevantes)

| # | Hotel | Municipio | Riesgo municipal | Estado post-sismo | Evidencia / Fuente | Próxima acción |
|---|-------|-----------|------------------|-------------------|--------------------|----------------|
| 1 | Finca Hotel Don Julio (reemplaza a Condina, cerrado in situ 29-08) | Santa Rosa de Cabal | MEDIO | **OPERANDO*** (reservable en Booking/Agoda 29-08; verificar same-day) | Booking/Agoda/Trivago/Google Hotels activos; **sin web propia detectada** (solo OTAs + IG @fincahoteldonjulio) | **Verificar web propia + teléfono** antes de Mensaje 1 (si no tiene web = caso Segorbe) |
| 2 | Hotel Cataluña Pereira | Pereira centro | ALTO | **CERRADO / DAÑO GRAVE — EXCLUIDO** | Instagram oficial 12-ago + web 26-ago: listados históricos sin disponibilidad confirmada | **EXCLUIDO**; re-evaluar a 90+ días |
| 3 | Hostal Ciudad de Segorbe | Salento | BAJO | **OPERANDO** | Booking activo (364 rev, 8.2) + Trip.com rev 2026; Salento riesgo BAJO | **Contactar (embudo)** |
| 4 | Hotel Salento Real Eje Cafetero | Salento | BAJO | **OPERANDO** | Booking activo (296 rev, 8.6, Genius); web propia confirmada hotelsalentoreal.com (34 hab, reservas online) — señal "sin web" de v1 es OBSOLETA; debilidad GBP/AEO/schema por verificar con v4complete | **Contactar (embudo)** |
| 5 | Hotel Guadalupe Plaza | Dosquebradas | ALTO-MEDIO | **OPERANDO** (confirmado 31-08) | IMPT 203 rev 10/10, momondo 242 rev 8.0, Kayak; **SIN WEB PROPIA** (verificado 31-08) → inviable v4complete | Flujo manual o archivo |
| 6 | Hotel Platino Plaza | Dosquebradas | ALTO-MEDIO | **OPERANDO** (confirmado 31-08) | Trip.com 8.7, IMPT 9.3 (27 rev), Booking city page; **SIN WEB PROPIA** (verificado 31-08) → inviable v4complete | Flujo manual o archivo |
| 7 | Hotel Tangara | Dosquebradas | ALTO-MEDIO | **OPERANDO** (confirmado 31-08) | letsbookhotel/skyscanner/IMPT reservable; **SIN WEB PROPIA** (verificado 31-08) → inviable v4complete | Flujo manual o archivo |
| 8 | Finca Hotel Villa Ilusión | Dosquebradas | ALTO-MEDIO | **OPERANDO** (confirmado 31-08) | IMPT 220 rev 9.3, Expedia reservable; **CON WEB PROPIA** (verificado 31-08) → v4complete viable | Contactar (embudo); confirmar daños leves vs intacto |
| 9 | Casa San Carlos Lodge (reemplaza a Vísperas, archivado 31-08) | Pereira (vía Marsella Km 6) | MEDIO | OPERANDO* (verificar same-day §6.5) | casasancarlos.com ✅ PASSED guard (classify_url, 05-09); web oficial con motor de reservas activo; +57 311 220 1220 (web oficial); ubicación vía Marsella Km 6 (dato Jhon 05-09); lodge de lujo = Tier A potencial | Contactar (embudo); verificar estado same-day |
| 10 | Hotel Recreacional Marcelandia | Santa Rosa (km 3) | POR VERIFICAR | **OPERANDO** | momondo 589 rev 8.9, hotel.com.au reservable; **SIN WEB PROPIA** (verificado 31-08) → inviable v4complete | Flujo manual o archivo |
| 11 | Hotel El Jardín Salento | Salento | BAJO | OPERANDO* (verificar same-day §6.5) | hoteleljardinsalento.com ✅ PASSED guard; +57 310 595 3017; 4.3★ Maps | Contactar (embudo); Mensaje 1 con hallazgo real |
| 12 | HOTEL D'LYON | Santa Rosa de Cabal | POR VERIFICAR | OPERANDO* (verificar same-day §6.5) | hoteldlyonsrc.com ✅ PASSED guard; +57 310 538 6037; 4.3★ Maps | Contactar (embudo); Mensaje 1 + contacto |
| 13 | Sazagua Pereira Hotel Boutique | Cerritos, Pereira | MEDIO | OPERANDO* (verificar same-day §6.5) | sazagua.com ✅ PASSED guard; +57 313 649 4579; 4.7★ Maps | Contactar (embudo); boutique = Tier A/B potencial |
| 14 | Hotel Rosales Suites | Pereira | MEDIO | OPERANDO* (verificar same-day §6.5) | hotelrosalesuites.com ✅ PASSED guard; +57 322 587 6653; 4.4★ Maps | Contactar (embudo); Mensaje 1 + contacto |
| 15 | Hotel San Antonio del Cerro | La Virginia/Cerritos | MEDIO | OPERANDO* (verificar same-day §6.5) | hotelsanantoniodelcerro.com.co ✅ PASSED guard; 606 340 0229 (fijo; capturar celular); 4.4★ Maps | Obtener WhatsApp/celular + Mensaje 1 |
| 16 | San Vicente Reserva Termal | Santa Rosa — Termales | POR VERIFICAR | OPERANDO* (verificar same-day §6.5) | sanvicente.com.co ✅ PASSED guard; +57 320 693 3707; 4.3★ Maps | Contactar (embudo); resort termal = Tier A potencial |
| 17 | Termales Tierra Viva | Villamaría (Caldas, vía Gallinazo) | POR VERIFICAR | **OPERANDO** (confirmado por Jhon 31-08; sin afectaciones) | termalestierraviva.com ✅ PASSED guard (URL proporcionada por Jhon); +57 301 261 7394; 4.5★ Maps (5,123 opiniones) | Contactar (embudo); verificación same-day YA hecha → Mensaje 1 (Var D); resort termal = Tier A potencial |
| 18 | Hotel El Mirador del Cocora | Salento | BAJO | SIN VERIFICAR | — | Fase 1 |
| 19 | Mahalo Hostal Boutique | Salento | BAJO | SIN VERIFICAR | — | Fase 1 |
| 20 | Colina del Sol Hotel Hacienda | Quimbaya | ALTO | SIN VERIFICAR | — | Fase 5 |
| 21 | Finca Hotel Los Girasoles | Quimbaya | ALTO | SIN VERIFICAR | — | Fase 5 |
| 22 | Finca Hotel Casa Nostra | Quimbaya | ALTO | SIN VERIFICAR | — | Fase 5 |
| 23 | Hotel Campestre Nogal de Cafetal | Quimbaya | ALTO | SIN VERIFICAR | — | Fase 5 |
| 24 | Finca Hotel Jardín Cafetero del Quindío | Quimbaya | ALTO | SIN VERIFICAR | — | Fase 5 |
| 25 | Origen Finca Hotel | Quimbaya | ALTO | SIN VERIFICAR | — | Fase 5 |
| 26 | Pausa Hospedaje Filandia | Filandia | MEDIO | SIN VERIFICAR | — | Fase 3 |
| 27 | Hostal La Luz de la Colina | Filandia | MEDIO | SIN VERIFICAR | — | Fase 3 |
| 28 | Hostal Amelia Filandia | Filandia | MEDIO | SIN VERIFICAR | — | Fase 3 |
| 29 | Hospedaje Mandarinos Filandia | Filandia | MEDIO | SIN VERIFICAR | — | Fase 3 |
| 30 | La Casita Filandia | Filandia | MEDIO | SIN VERIFICAR | — | Fase 3 |
| 31 | Mot Mot Glamping | Filandia | MEDIO | SIN VERIFICAR | — | Fase 3 |
| 32 | Alua Glamping | Filandia | MEDIO | SIN VERIFICAR | — | Fase 3 |
| 33 | Hotel Cafe Bernal | Armenia zona norte | MEDIO | SIN VERIFICAR | — | Fase 4 |
| 34 | Hostería Mi Mónaco | Armenia periferia | MEDIO | SIN VERIFICAR | — | Fase 4 |
| 35 | Finca Hotel Nuestro Sueño | Montenegro (vía Panaca) | POR VERIFICAR | SIN VERIFICAR | — | Fase 4 |
| 36 | Casa Azul Boutique Hostel | Pereira (La Elvira) | MEDIO | SIN VERIFICAR | — | Fase 4 |
| 37 | La Iguana Café y Hostal | Pereira (Arboleda) | MEDIO | SIN VERIFICAR | — | Fase 4 |
| E1 | Hotel Natura Cocora | Salento | BAJO | SIN VERIFICAR | — | Fase 1 |
| E2 | Hospedaje Vista Hermosa | Salento | BAJO | SIN VERIFICAR | Reservas por WhatsApp (ficha Google) | Fase 1 |
| E3 | San Remo Ecolodge | Santa Rosa (zona termal) | POR VERIFICAR | SIN VERIFICAR | — | Fase 2 |
| E4 | El Bambú | Santa Rosa (cerca termales) | POR VERIFICAR | SIN VERIFICAR | — | Fase 2 |
| E5 | Finca del Café — Casa Típica | Santa Rosa | POR VERIFICAR | SIN VERIFICAR | — | Fase 2 |
| E6 | Hotel Golden Suite Pereira | Pereira | MEDIO | SIN VERIFICAR | — | Fase 4 |
| E7 | Hotel Entre Lomas | Dosquebradas (El Tambo) | ALTO-MEDIO | SIN VERIFICAR | WhatsApp v1: +57 320 562 8066 | Fase 5 |
| E8 | Finca Turística Machangara | Quimbaya | ALTO | SIN VERIFICAR | — | Fase 5 |
| E9 | Finca Hotel Valparaíso | Armenia periferia | MEDIO | SIN VERIFICAR | — | Fase 4 |
| C1 | Hotel Amazilia | Cerritos (Corregimiento Pereira) | MEDIO | SIN VERIFICAR | Trip.com/Kayak/BestVacation: solo OTA; Vía Pereira-Cerritos Entrada 8 Cafelia; web propia por confirmar | Fase 4 |

---

## Resultado de verificación del top 10 — Paso 0 (actualizado 05-09)

Método §6.5: fuentes gremiales/prensa → Google Maps/Booking (¿reservable? ¿reseñas recientes?) → llamada (pendiente para varios, ver notas). Búsquedas ejecutadas vía Keenable contra Booking, momondo, Trip.com, IMPT, Expedia, Airbnb, Kayak, Skyscanner, Trivago, Atrápalo y prensa (El País). Verificación web propia 31-08: guard `own_site_guard` v4.74.1 + blocklist v2.

| # | Hotel | Municipio | Estado verificado | Web propia (guard) | Entra al embudo v4complete |
|---|-------|-----------|------------------|--------------------|---------------------------|
| 1 | Finca Hotel Don Julio (reemplaza a Condina) | Santa Rosa de Cabal | OPERANDO* (verificar same-day) | Sin web detectada (solo OTAs + IG) | NO (inviable hasta confirmar web) |
| 2 | Hotel Cataluña Pereira | Pereira centro | CERRADO / DAÑO GRAVE — EXCLUIDO | — | NO |
| 3 | Hostal Ciudad de Segorbe | Salento | OPERANDO | SIN WEB PROPIA | NO (flujo manual) |
| 4 | Hotel Salento Real Eje Cafetero | Salento | OPERANDO | hotelsalentoreal.com ✅ PASSED | SÍ |
| 5 | Hotel Guadalupe Plaza | Dosquebradas | OPERANDO (confirmado 31-08) | SIN WEB PROPIA (verificado 31-08) | NO (flujo manual) |
| 6 | Hotel Platino Plaza | Dosquebradas | OPERANDO (confirmado 31-08) | SIN WEB PROPIA (verificado 31-08) | NO (flujo manual) |
| 7 | Hotel Tangara | Dosquebradas | OPERANDO (confirmado 31-08) | SIN WEB PROPIA (verificado 31-08) | NO (flujo manual) |
| 8 | Finca Hotel Villa Ilusión | Dosquebradas | OPERANDO (confirmado 31-08) | CON WEB PROPIA (verificado 31-08) ✅ PASSED | SÍ |
| 9 | Casa San Carlos Lodge (reemplaza a Vísperas 05-09) | Pereira (vía Marsella Km 6) | OPERANDO* (verificar same-day) | casasancarlos.com ✅ PASSED (classify_url 05-09) | SÍ |
| 10 | Hotel Recreacional Marcelandia | Santa Rosa | OPERANDO | SIN WEB PROPIA (verificado 31-08) | NO (flujo manual) |

**Recuento top 10 (tras reemplazo 05-09):** 3 de 10 viables v4complete (#4, #8, #9 Casa San Carlos). 5 sin web propia (#3, #5, #6, #7, #10). 1 excluido por daño grave (#2). 1 por verificar web (#1). Vísperas (inviable 31-08) archivado → ver excluidos definitivos.

**+ Nuevos candidatos Maps (31-08):** 6 hoteles con web propia que PASAN el guard (#11–#16) + 1 aportado por Jhon (#17 Termales Tierra Viva). **+ Reemplazo Vísperas (05-09):** Casa San Carlos Lodge (#9, casasancarlos.com, Pereira) aportado por Jhon, pasa el guard. Total viables v4complete: **10** (#4, #8, #9, #11, #12, #13, #14, #15, #16, #17). Cuello de botella RESUELTO.

**Excluidos definitivos:** #2 Cataluña (daño grave), Vísperas (inviable 31-08; su cupo #9 fue reasignado a Casa San Carlos Lodge el 05-09), Condina (no operativo in situ 29-08). Re-evaluar todos a 90+ días.

**Acciones pendientes previas a enviar (Semana 1):**
- Verificar estado post-sismo same-day (§6.5) de los 6 candidatos Maps restantes (#11–#16) antes del primer WhatsApp. (#17 Tierra Viva ya confirmado sin afectaciones por Jhon 31-08.)
- Obtener celular de #15 San Antonio del Cerro (solo fijo publicado).
- Obtener teléfono + verificar web de Don Julio (#1).
- Decidir flujo para los 5 sin web (#3, #5, #6, #7, #10): contacto manual con diagnóstico verbal / archivar.
- Primer contacto 100% empático (§6.5.3) para Salento y Santa Rosa; para Dosquebradas, confirmar daños antes de definir tono.

### Teléfonos verificados — Viables v4complete (10 hoteles)

| # | Hotel | Municipio | Teléfono | Fuente |
|---|-------|-----------|----------|--------|
| 4 | Hotel Salento Real Eje Cafetero | Salento | +57 316 629 6142 | momondo (coincide v1) + Maps |
| 8 | Finca Hotel Villa Ilusión | Dosquebradas | +57 315 271 1519 | momondo (front desk) |
| 9 | Casa San Carlos Lodge | Pereira (vía Marsella Km 6) | +57 311 220 1220 | Web oficial (05-09) |
| 11 | Hotel El Jardín Salento | Salento | +57 310 595 3017 | Google Maps |
| 12 | HOTEL D'LYON | Santa Rosa de Cabal | +57 310 538 6037 | Google Maps |
| 13 | Sazagua Pereira Hotel Boutique | Cerritos, Pereira | +57 313 649 4579 | Google Maps |
| 14 | Hotel Rosales Suites | Pereira | +57 322 587 6653 | Google Maps |
| 15 | Hotel San Antonio del Cerro | La Virginia/Cerritos | 606 340 0229 (fijo; capturar celular) | Google Maps |
| 16 | San Vicente Reserva Termal | Santa Rosa — Termales | +57 320 693 3707 | Google Maps |
| 17 | Termales Tierra Viva | Villamaría (Caldas) | +57 301 261 7394 | Google Maps |

Nota: todos son celulares colombianos (+57 3XX…) válidos para WhatsApp, excepto #15 que solo tiene fijo publicado (requiere obtener celular). Los 10 viables tienen teléfono verificado y web propia que pasa el guard `own_site_guard` v4.74.1.

---

## Orden de contacto recomendado (actualizado 05-09)

Prioridad por probabilidad de conversión + intensidad del dolor de demanda + viabilidad v4complete confirmada:

- **Prioridad 1 — Viables listos (#4, #8):** Salento Real y Villa Ilusión ya tienen diagnóstico v4complete corrido o listo para correr. Contactar primero.
- **Prioridad 2 — Nuevos Maps Salento (#11):** El Jardín Salento está en zona conocida (Salento, riesgo BAJO). Verificar same-day + Mensaje 1.
- **Prioridad 3 — Nuevos zona termal (#12, #16, #17):** D'Lyon, San Vicente Reserva Termal y Termales Tierra Viva (Villamaría). Zona termal con dolor de demanda post-sismo; #17 tiene 5,123 opiniones (operación grande = Tier A) y ya está **confirmado OPERANDO sin afectaciones** (Jhon 31-08) → listo para Mensaje 1 (Var D). Verificar same-day solo #12 y #16.
- **Prioridad 4 — Pereira/Cerritos (#9, #13, #14, #15):** Casa San Carlos Lodge (reemplazo de Vísperas, 05-09), Sazagua, Rosales Suites, San Antonio del Cerro. Verificar same-day + Mensaje 1. #15 requiere obtener celular primero.
- **Fase manual/archivo — Sin web propia (#3, #5, #6, #7, #10):** decidir flujo manual con diagnóstico verbal o archivar.
- **Fase 1–5 — Lista original SIN VERIFICAR (#18–#37, E1–E9, C1):** verificar estado post-sismo y presencia de web propia antes de incluir. Usar `classify_url()` del guard como filtro automático.

**Santa Rosa de Cabal AGOTADA** en prospección Maps (31-08): solo 2 con web propia encontradas (#12 D'Lyon, #16 San Vicente). No buscar más en esta zona salvo nueva evidencia.

## Censo de nuevos candidatos (actualizado 05-09)

- **Prospección Google Maps completada 31-08:** 22 fichas revisadas en Pereira / Salento / Santa Rosa de Cabal (urbana + zona termal) → 6 nuevos candidatos con web propia que PASAN el guard (#11–#16) + **#17 Termales Tierra Viva aportado por Jhon** (termalestierraviva.com, Villamaría/Caldas — eje termal contiguo). Filtro: dominio real (no Facebook/Instagram/booking engine) + `classify_url()` del guard `own_site_guard` v4.74.1 (blocklist v2 incluye `hosroom.com` y `istagram.com`). Cupo #9 reasignado el 2026-09-05 a Casa San Carlos Lodge (casasancarlos.com, Pereira), aportado por Jhon y validado con `classify_url()`.
- Los ~130 hoteles de Cotelco "con daños leves que siguen operando" NO están en la v1 (que excluía cadenas y hoteles pulidos). Tras el sismo, cualquier hotel `OPERANDO` con web propia que pase el guard es candidato.
- Fuente de censo adicional (si se requiere ampliar): Google Maps por municipio ("hotel + Filandia/Montenegro/Armenia…"), filtrando los que sigan "abierto" en la ficha Y tengan web propia real. Verificar cada URL con `classify_url()` antes de incluir.
- Un hotel cerrado que REABRA tras reparaciones = cliente ideal de relanzamiento digital (registrarlos al detectarlos, contacto a 90+ días).

## Nota sobre datos financieros

Toda fuga estimada para prospectos post-sismo usa ocupación REAL declarada por el hotel, no el benchmark pre-sismo (51,2%). Ver §6.5 del CONTEXTO MAESTRO v3.0.
