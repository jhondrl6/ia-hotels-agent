# Fuente pública de precios — Hotel Don Alfonso (registrada en FASE-A)

**Fecha de la observación:** 2026-09-19
**Fuente:** `https://donalfonsohotel.com/tienda/` — **señalada por el operador** en esta sesión con la aclaración de que el material es público.
**Método:** una única petición HTTP GET con `urllib` (User-Agent de navegador), parseo del HTML en memoria para listar los precios. **Sin pipeline, sin `v4complete`, sin scraper del repositorio, sin lectura de área privada.** 200 OK, 110.627 caracteres, URL final idéntica a la solicitada.
**Qué hace y qué NO hace este registro:** deja constancia fechada de una **segunda fuente que corrobora** dos campos del dato operativo. **No** modifica `data/hotel_observations/observations.json`, **no** alimenta el warehouse, **no** produce `onboarding_provenance.json` (eso es H, AC14) y **no** es consentimiento ni autorización de entrega.

## Lo que dice la página

Catálogo WooCommerce con 12 productos: **11 alojamientos nombrados + 1 "Salón de eventos x día"**.

| Habitación | Precio (COP) | Desviación vs 330.000 |
|---|---|---|
| Carmen Rosa | 330.000 | 0 |
| Doña Amanda Jaramillo | 330.000 | 0 |
| Doña Maria Jaramillo | 330.000 | 0 |
| Doña Olga Vélez | 330.000 | 0 |
| Mamá Chía | 330.000 | 0 |
| Maria Dolores | 330.000 | 0 |
| Doña Fabiola Jaramillo | 320.200 | −9.800 |
| Maria Adelaida | 301.300 | −28.700 |
| Doña Libia Jaramillo | 272.700 | −57.300 |
| Doña Eucaris Jaramillo | 249.900 | −80.100 |
| Don Alfonso Jaramillo | 395.000 | +65.000 |
| Salón de eventos x día *(no es alojamiento)* | 350.000 | — |

Estadísticos sobre los 11 alojamientos (calculados localmente desde la tabla): mínimo **249.900**, máximo **395.000**, moda **330.000** (6 de 11), mediana **330.000**, media **319.918**. Rango total = 44 % del valor registrado.

## Contrastación con el dato del 2026-07-22

| Campo del registro | Valor gobernante hoy | Lo que aporta la página | Estado tras esta observación |
|---|---|---|---|
| `rooms` | 11 | 11 productos de alojamiento | **CORROBORADO con cero divergencia**, fuente pública fechada 2026-09-19 |
| `avg_reservation_cop` / `adr_cop` | 330.000 | 330.000 es la moda **y** la mediana de la lista | **CORROBORADO con una salvedad de medida** (abajo) |
| `monthly_reservations` | 140 | no observable públicamente | **SIN cambio** — sigue en el dato de hace 59 días |
| `direct_channel_percentage` | 30,0 | no observable públicamente | **SIN cambio** — ídem |

**Salvedad de medida (por qué no se declara "precio gobernante"):** una tarifa de tienda es **precio lista por noche**; `adr_cop` es tarifa diaria promedio **realizada** y `avg_reservation_cop` es **valor por reserva**. Coinciden en 330.000, pero son tres magnitudes distintas y la página muestra además una dispersión real (249.900 a 395.000) que el valor único del registro no captura. Aceptar el precio público como gobernante exigiría declarar el **productor y la derivación** (¿mediana?, ¿por habitación?, ¿con o sin salón), y esa decisión pertenece a la regla "No Defaults in Money" del motor financiero y, si las fuentes llegaran a divergir, a la semántica de `CONFLICT` que el propio plan prohíbe resolver eligiendo un número.

## Efecto sobre el pendiente de vigencia

Reduce el problema, no lo cierra. Lo que faltaba era una segunda fuente datada sobre la **URL viva** para los campos que mandan dinero y capacidad de habitaciones: eso ya existe desde esta observación, con método reproducible en una línea. Lo que sigue cubierto solo por el registro de 2026-07-22 es **reservas/mes y canal directo**, que son de operación interna —y son los que alimentan los escenarios financieros y el `direct_channel_pct` que en la corrida de referencia salió de default (`default_sources: {"direct_channel_percentage": "default"}`). Y ninguna de las dos cosas sustituye el consentimiento: la página dice qué cobra el hotel, no autoriza a entregarle un informe.

**Consecuencia registrada para H (AC14):** `onboarding_provenance.json` puede citar esta fuente con URL, fecha, método y los dos campos que corrobora, declarando además que **no** produjo ningún valor nuevo — el número gobernante sigue siendo el del registro, ahora con respaldo.

## Límite de esta observación

Intenté verificar por qué vía entra un precio al pipeline hoy (scraper disponible, campo de onboarding o benchmark regional) para poder decir si hace falta un writer o ya existe, y el clasificador de permisos denegó incluso las búsquedas locales posteriores. **Ese punto queda sin verificar**, y por eso esta fila no propone mecanismo de ingesta: propone registro con procedencia.
