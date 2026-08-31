# Lista de Prospectos v2 — Verificación Post-Sismo

> **Base:** `01_Lista_Prospectos_Eje_Cafetero.md` (compilada 2026-07-21, PRE-sismo; sus fichas de detalle siguen siendo válidas para datos de contacto y debilidad digital).
> **Creada:** 2026-08-26. **Método:** Protocolo Post-Terremoto §6.5 del CONTEXTO MAESTRO v3.0.
> **Evento:** Terremoto M7.4 del 2026-08-10 (epicentro San José del Palmar).

## Reglas de uso

1. **Solo se contactan hoteles con estado `OPERANDO` o `OPERANDO CON DAÑOS LEVES`** verificado hace ≤7 días.
2. `CERRADO / DAÑO GRAVE` = excluido de prospección; registro respetuoso, re-evaluación a 90+ días (futuro cliente de relanzamiento cuando reabra).
3. Estados `SIN VERIFICAR` requieren verificación activa ANTES de cualquier contacto (fuentes en orden: Cotelco/alcaldías → Google Maps/Booking: ¿reservable? ¿reseñas/posts recientes? → llamada/visita).
4. La v1 queda como histórico: usar SUS fichas para teléfonos y detalle, NUNCA sus estados.
5. **Presencia de sitio web propio NO es criterio de inclusión ni exclusión.** El pipeline iah-cli v4.72.2 acepta como entrada `--url` cualquier ficha del hotel: sitio propio, ficha de Google Maps o listado de OTA (fallback chain Places API → Google Travel → SerpAPI). Filtrar prospectos "solo los que tienen sitio web" se descarta (decisión usuario 2026-08-27): contradice la tesis de negocio (Contexto Maestro §2/§4 — el cliente ideal es el hotel que PIERDE reservas directas por depender de OTAs) y descartaría a los mejores prospectos. La señal de debilidad digital se re-audita caso a caso (ver "Re-auditoría de debilidad digital" más abajo).

---

## Re-auditoría de debilidad digital (2026-08-27)

La señal "sin web propia" de la lista v1 (compilada 2026-07-21) está **obsoleta**. Evidencia:
- **Hotel Salento Real (#4):** tiene sitio oficial `hotelsalentoreal.com` (34 hab, reservas online). La ficha v1 decía "sin web propia clara".
- **Hotel Vísperas (#9):** tiene sitio oficial `hotelvisperas.com` (confirmado 2026-08-27). La ficha v1 decía "solo listados OTAs; sin web propia".

Conclusión: el filtro "incluir solo hoteles con sitio web" se **descarta** (decisión usuario 2026-08-27). Razones:
1. Contradice la tesis de negocio (Contexto Maestro §2/§4): el cliente ideal es el hotel que depende de OTAs y pierde reservas directas — justamente los que no tienen (o tienen débil) sitio propio.
2. El pipeline iah-cli v4.72.2 **no requiere** sitio propio del hotel para producir diagnóstico: acepta `--url` de ficha Google Maps / OTA, con fallback chain Places API → Google Travel → SerpAPI. Evidencia en código: `archives/gbp_profiles.json` usa URL de Maps como entrada canónica; `tests/regression/test_hotel_visperas_conflicts.py` es suite de regresión sobre el hotel sin dependencia de sitio propio. *(Ejecución en vivo de un caso 100% sin-sitio-propio queda PENDIENTE: el venv local requiere `python-dotenv` y el caso de prueba inicial — Vísperas — resultó tener sitio; la arquitectura lo confirma por diseño.)*
3. La señal de debilidad digital se re-audita **caso a caso** corriendo `v4complete` sobre la URL real del hotel (propia o de Maps/OTA) — no se asume a priori.

**Acción:** para los prospectos de Santa Rosa y Cerritos, verificar presencia de sitio propio real antes de etiquetar "debilidad", pero esa verificación NUNCA es criterio de inclusión/exclusión. El ejemplo `hotelsalentoreal.com` se usa aquí como PRUEBA de que la lista necesita re-auditoría de debilidad digital, no como filtro de inclusión.

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
| 5 | Hotel Guadalupe Plaza | Dosquebradas | ALTO-MEDIO | **OPERANDO** (confirmar daños leves por llamada) | IMPT 203 rev 10/10, momondo 242 rev 8.0, Kayak; Dosquebradas s/evidencia cierre | **Contactar**; llamada confirmatoria de daños |
| 6 | Hotel Platino Plaza | Dosquebradas | ALTO-MEDIO | **OPERANDO** (confirmar daños leves por llamada) | Trip.com 8.7, IMPT 9.3 (27 rev), Booking city page reservable | **Contactar**; llamada confirmatoria de daños |
| 7 | Hotel Tangara | Dosquebradas | ALTO-MEDIO | **OPERANDO** (confirmar daños leves por llamada) | letsbookhotel/skyscanner/IMPT reservable; web 26-ago s/cierre | **Contactar**; llamada confirmatoria de daños |
| 8 | Finca Hotel Villa Ilusión | Dosquebradas | ALTO-MEDIO | **OPERANDO** (confirmar daños leves por llamada) | IMPT 220 rev 9.3, Expedia reservable; s/cierre reportado | **Contactar**; llamada confirmatoria de daños |
| 9 | Hotel Vísperas | Santa Rosa (vía termales) | POR VERIFICAR | **OPERANDO** | momondo 801 rev 9.4, Airbnb 4.82; web propia confirmada hotelvisperas.com (2026-08-27) — señal "sin web" de v1 OBSOLETA; Santa Rosa s/cierre reportado | **Contactar (embudo)** |
| 10 | Hotel Recreacional Marcelandia | Santa Rosa (km 3) | POR VERIFICAR | **OPERANDO** | momondo 589 rev 8.9, hotel.com.au reservable | **Contactar (embudo)** |
| 11 | Hotel El Mirador del Cocora | Salento | BAJO | SIN VERIFICAR | — | Fase 1 |
| 12 | Mahalo Hostal Boutique | Salento | BAJO | SIN VERIFICAR | — | Fase 1 |
| 13 | Colina del Sol Hotel Hacienda | Quimbaya | ALTO | SIN VERIFICAR | — | Fase 5 |
| 14 | Finca Hotel Los Girasoles | Quimbaya | ALTO | SIN VERIFICAR | — | Fase 5 |
| 15 | Finca Hotel Casa Nostra | Quimbaya | ALTO | SIN VERIFICAR | — | Fase 5 |
| 16 | Hotel Campestre Nogal de Cafetal | Quimbaya | ALTO | SIN VERIFICAR | — | Fase 5 |
| 17 | Finca Hotel Jardín Cafetero del Quindío | Quimbaya | ALTO | SIN VERIFICAR | — | Fase 5 |
| 18 | Origen Finca Hotel | Quimbaya | ALTO | SIN VERIFICAR | — | Fase 5 |
| 19 | Pausa Hospedaje Filandia | Filandia | MEDIO | SIN VERIFICAR | — | Fase 3 |
| 20 | Hostal La Luz de la Colina | Filandia | MEDIO | SIN VERIFICAR | — | Fase 3 |
| 21 | Hostal Amelia Filandia | Filandia | MEDIO | SIN VERIFICAR | — | Fase 3 |
| 22 | Hospedaje Mandarinos Filandia | Filandia | MEDIO | SIN VERIFICAR | — | Fase 3 |
| 23 | La Casita Filandia | Filandia | MEDIO | SIN VERIFICAR | — | Fase 3 |
| 24 | Mot Mot Glamping | Filandia | MEDIO | SIN VERIFICAR | — | Fase 3 |
| 25 | Alua Glamping | Filandia | MEDIO | SIN VERIFICAR | — | Fase 3 |
| 26 | Hotel Cafe Bernal | Armenia zona norte | MEDIO | SIN VERIFICAR | — | Fase 4 |
| 27 | Hostería Mi Mónaco | Armenia periferia | MEDIO | SIN VERIFICAR | — | Fase 4 |
| 28 | Finca Hotel Nuestro Sueño | Montenegro (vía Panaca) | POR VERIFICAR | SIN VERIFICAR | — | Fase 4 |
| 29 | Casa Azul Boutique Hostel | Pereira (La Elvira) | MEDIO | SIN VERIFICAR | — | Fase 4 |
| 30 | La Iguana Café y Hostal | Pereira (Arboleda) | MEDIO | SIN VERIFICAR | — | Fase 4 |
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

## Resultado de verificación del top 10 — Paso 0 (2026-08-26)

Método §6.5: fuentes gremiales/prensa → Google Maps/Booking (¿reservable? ¿reseñas recientes?) → llamada (pendiente para varios, ver notas). Búsquedas ejecutadas vía Keenable contra Booking, momondo, Trip.com, IMPT, Expedia, Airbnb, Kayak, Skyscanner, Trivago, Atrápalo y prensa (El País).

| # | Hotel | Municipio | Estado verificado | Entra al embudo |
|---|-------|-----------|------------------|-----------------|
| 1 | Finca Hotel Don Julio (reemplaza a Condina) | Santa Rosa de Cabal | OPERANDO* (verificar same-day + web propia) | SÍ, tras verificar teléfono y web |
| 2 | Hotel Cataluña Pereira | Pereira centro | CERRADO / DAÑO GRAVE — EXCLUIDO | NO |
| 3 | Hostal Ciudad de Segorbe | Salento | OPERANDO | SÍ |
| 4 | Hotel Salento Real Eje Cafetero | Salento | OPERANDO | SÍ |
| 5 | Hotel Guadalupe Plaza | Dosquebradas | OPERANDO (confirmar daños leves) | SÍ |
| 6 | Hotel Platino Plaza | Dosquebradas | OPERANDO (confirmar daños leves) | SÍ |
| 7 | Hotel Tangara | Dosquebradas | OPERANDO (confirmar daños leves) | SÍ |
| 8 | Finca Hotel Villa Ilusión | Dosquebradas | OPERANDO (confirmar daños leves) | SÍ |
| 9 | Hotel Vísperas | Santa Rosa | OPERANDO | SÍ |
| 10 | Hotel Recreacional Marcelandia | Santa Rosa | OPERANDO | SÍ |

**Recuento:** 8 de 10 en `OPERANDO` (≥5). ✅ La regla de prudencia NO se activa → la ola de mensajes procede.

**Excluidos:** #2 Cataluña (daño grave confirmado, re-evaluar 90+ días). ~~#1 Condina~~ — **CERRADO in situ 2026-08-29: NO OPERATIVO**, excluido (re-evaluar 2026-11-29); su slot del top 10 lo ocupa **Finca Hotel Don Julio** (Santa Rosa de Cabal, OPERANDO* pendiente de verificación same-day + web propia + teléfono).

**Acciones pendientes previas a enviar (Semana 1):**
- Llamadas confirmatorias de daños leves a los 4 de Dosquebradas (#5–#8) por riesgo municipal ALTO-MEDIO (la web no discrimina "daño leve" vs intacto; la llamada cierra la distinción OPERANDO vs OPERANDO CON DAÑOS LEVES).
- ~~Llamada a #1 Condina para decidir inclusión o archivo definitivo.~~ **CERRADO 29-08 in situ: NO OPERATIVO → excluido.** Nueva acción: validar #1 Finca Hotel Don Julio (teléfono + web propia + estado same-day) antes de sumarlo a la ola.
- Verificar teléfonos de los 8 OPERANDO (Google Maps) antes del primer WhatsApp.
- Primer contacto 100% empático (§6.5.3) para Salento y Santa Rosa; para Dosquebradas, confirmar daños antes de definir tono.

### Teléfonos verificados de los 8 OPERANDO (Google Maps / agregadores, 2026-08-26)

| # | Hotel | Municipio | Teléfono verificado | Fuente |
|---|-------|-----------|---------------------|--------|
| 3 | Hostal Ciudad de Segorbe | Salento | +57 310 825 2436 | momondo / thecoffeeroutes |
| 4 | Hotel Salento Real Eje Cafetero | Salento | +57 316 629 6142 | momondo (coincide v1) |
| 5 | Hotel Guadalupe Plaza | Dosquebradas | +57 317 543 9207 | momondo / TheGuide (3175439207) |
| 6 | Hotel Platino Plaza | Dosquebradas | +57 314 654 3050 | Trip.com |
| 7 | Hotel Tangara | Dosquebradas | +57 316 328 9569 | turismo.dosquebradas.gov.co |
| 8 | Finca Hotel Villa Ilusión | Dosquebradas | +57 315 271 1519 | momondo (front desk) |
| 9 | Hotel Vísperas | Santa Rosa | +57 316 824 5636 | momondo |
| 10 | Hotel Recreacional Marcelandia | Santa Rosa | +57 320 204 2595 | momondo / hotelscombined |

Nota: los números son celulares colombianos (formato +57 3XX…), válidos para WhatsApp. Todos los 8 OPERANDO tienen teléfono verificado; Villa Ilusión (#8) se confirmó vía momondo (front desk) al no exponer fijo en su sitio oficial ni Booking.

---

## Orden de verificación recomendado (re-priorización post-sismo)

La prioridad de contacto de la v1 (Pereira centro primero) queda **invertida**. Nuevo orden por probabilidad de encontrar `OPERANDO` + intensidad del dolor de demanda:

- **Fase 1 — Salento (6 hoteles):** riesgo estructural bajo + turismo colapsado = prospectos intactos con el máximo dolor. Mensaje ideal: reactivación ("ser la respuesta cuando pregunten quién está abierto"). Empieza aquí.
- **Fase 2 — Santa Rosa de Cabal (5):** verificar estado del municipio primero; los de la ruta termal dependen de flujo regional.
- **Fase 3 — Filandia (7):** daño medio; verificar edificio por edificio.
- **Fase 4 — Armenia periferia + Montenegro + Pereira no céntrico + Cerritos (Corregimiento Pereira, keyword "Zona de Cerritos") (8):** campestres, fuera de cascos antiguos. Cerritos añadido 2026-08-27 (Hotel Amazilia como ancla; ver censo). Conteo Fase 4: #26, #27, #28, #29, #30, E6, E9, C1.
- **Fase 5 — Dosquebradas, Quimbaya, Pereira centro (10):** alta tasa de exclusión esperada (Cataluña ya está fuera; Condina en verificación). Verificar igual (los que operan capturan demanda desplazada), pero sin apurar contactos.

**Resultado de la re-priorización:** el top de contacto inicial pasa de {Condina, Cataluña} a {Segorbe, Salento Real, Mirador del Cocora, Mahalo, Natura Cocora, Vista Hermosa} — todos de Salento.

## Censo de nuevos candidatos (tarea de las semanas 1–2)

- Los ~130 hoteles de Cotelco "con daños leves que siguen operando" NO están en la v1 (que excluía cadenas y hoteles pulidos). Tras el sismo, cualquier hotel `OPERANDO` con debilidad digital es candidato.
- Fuente de censo: Google Maps por municipio ("hotel + Salento/Filandia/Santa Rosa…"), filtrando los que sigan "abierto" en la ficha.
- **Censo Cerritos (Corregimiento de Pereira, keyword "Zona de Cerritos")** añadido 2026-08-27: Hotel Amazilia (Vía Pereira-Cerritos, Entrada 8 Cafelia — confirmado real en Trip.com/Kayak, solo OTA, sin web propia localizada) como ancla de Fase 4; candidatos adicionales por verificar propio sitio: Finca Hotel Cerritos Plaza, Casa Toscana, Estancia El Caney (todos en OTAs).
- Un hotel cerrado que REABRA tras reparaciones = cliente ideal de relanzamiento digital (registrarlos al detectarlos, contacto a 90+ días).

## Nota sobre datos financieros

Toda fuga estimada para prospectos post-sismo usa ocupación REAL declarada por el hotel, no el benchmark pre-sismo (51,2%). Ver §6.5 del CONTEXTO MAESTRO v3.0.
