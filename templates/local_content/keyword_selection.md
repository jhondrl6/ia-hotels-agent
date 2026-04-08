## Template: Keyword Selection Strategy

Seleccion de keywords long-tail locales para hoteles boutique del Eje Cafetero.

### Logica de seleccion

1. Resolver templates segun tipo de hotel (`_resolve_templates()`):
   - `termales` → termales + boutique + general
   - `eco` → parque_natural + cafe + general
   - `cafe` → cafe + boutique + general
   - `pueblo` → pueblo_patrimonio + general
   - `boutique` → boutique + general
   - `general` → general

2. Expandir placeholders en templates:
   - `{location}` → hotel_data["city"]
   - `{region}` → location_context["region"] || hotel_data["state"]
   - `{nearby_city}` → location_context["nearby_city"] || "Pereira"

3. Ordenar por prioridad (KEYWORD_PRIORITY):
   - "precios" → 5 (mayor intencion de compra)
   - "hotel" / "hospedarse" → 4
   - "mejor" / "que hacer" / "tour" / "experiencias" → 3
   - "como llegar" / "restaurantes" / "sitios turisticos" / etc → 2
   - Sin match → 1

4. Tomar top 5 keywords (maximo)

### Templates por tipo de hotel

#### termales
- "termales {location} precios"
- "hotel cerca termales {location}"
- "que llevar a termales {location}"
- "mejores termales {region}"
- "termales {location} desde {nearby_city}"

#### parque_natural
- "parque nacional {location} como llegar"
- "senderismo {location} recomendaciones"
- "ecoturismo {region} mejores planes"
- "fauna y flora {region}"
- "donde alojarse cerca parque {location}"

#### pueblo_patrimonio
- "que hacer en {location}"
- "hotel boutique {location} Colombia"
- "fin de semana en {location}"
- "gastronomia {region}"
- "visitar {location} desde {nearby_city}"

#### cafe
- "tour del cafe {location}"
- "finca cafetera {region} visita"
- "mejor epoca para visitar {location}"
- "hospedaje entre cafetales {region}"
- "experiencias cafeteras {location}"

#### boutique
- "hotel boutique {location} Colombia"
- "donde hospedarse en {location}"
- "mejor hotel boutique {region}"
- "hotel encantador {location} precio"
- "alojamiento exclusivo {location}"

#### general
- "que hacer en {location}"
- "como llegar a {location}"
- "restaurantes cerca de {location}"
- "sitios turisticos {region}"
- "plan turismo {location} fin de semana"

### Referencia en codigo

Implementado en `LocalContentGenerator._select_keywords()` y
`LocalContentGenerator._resolve_templates()` en
`modules/asset_generation/local_content_generator.py`.
