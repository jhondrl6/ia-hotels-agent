Investiga el estado promedio de visibilidad digital de hoteles boutique y pequeños en 3 regiones turísticas de Colombia. Necesito datos reales, no estimaciones genéricas.

   REGIONES A INVESTIGAR:
   1. Eje Cafetero (Pereira, Manizales, Armenia, Santa Rosa de Cabal, Salento)
   2. Antioquia (Medellín, Guatapé, Jardín, Santa Fe de Antioquia)
   3. Caribe colombiano (Cartagena, Santa Marta, Taganga, Palomino, San Andrés)

   DATOS REQUERIDOS POR REGIÓN:

   Para cada región, consulta Google Maps/Places para una muestra de 15-20 hoteles boutique (10-60 habitaciones). Para CADA hotel registra:

   A) DATOS GEO (Google Business Profile):
   - Nombre del hotel
   - Rating promedio (escala 0-5, con 1 decimal)
   - Cantidad de reseñas
   - Cantidad de fotos
   - Tiene horarios publicados: sí/no
   - Tiene sitio web vinculado: sí/no

   B) DATOS AEO (Infraestructura para IA):
   - Tiene Schema.org Hotel detectado: sí/no
   - Tiene Schema FAQPage: sí/no
   - Tiene Open Graph tags (og:title, og:description): sí/no
   - Tiene robots.txt que permite crawlers de IA: sí/no

   C) DATOS SEO:
   - Tiene sitio web propio (no solo perfil OTA): sí/no
   - Velocidad móvil estimada (buena/regular/mala) - usar PageSpeed Insights si es posible para 3-5 muestras por región

   FORMATO DE ENTREGA - JSON estricto:

   ```json
   {
     "regiones": {
       "eje_cafetero": {
         "muestra": 15,
         "hotels": [
           {
             "nombre": "string",
             "ciudad": "string",
             "rating": 4.3,
             "reviews": 127,
             "fotos": 45,
             "has_hours": true,
             "has_website": true,
             "schema_hotel": true,
             "schema_faq": false,
             "open_graph": false,
             "robots_ai_friendly": true,
             "has_own_website": true,
             "mobile_speed": "regular"
           }
         ]
       },
       "antioquia": { "muestra": N, "hotels": [...] },
       "caribe": { "muestra": N, "hotels": [...] }
     },
     "default": {
       "nota": "Promedio nacional calculado a partir de las 3 regiones combinadas",
       "muestra_total": N
     }
   }
   ```

   REGLAS:
   - Busca hoteles que aparezcan en Google Maps al buscar "hotel boutique [ciudad]"
   - Prioriza hoteles independientes, no cadenas grandes (Marriott, Hilton, etc.)
   - Si no puedes verificar un dato específico para un hotel, omite ese campo (no inventes)
   - Para mobile_speed, si no puedes medir, omite el campo (se calculará aparte)
   - Incluye al menos 10 hoteles por región, idealmente 15-20
   - Ordena los hoteles dentro de cada región por ciudad