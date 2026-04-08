# Guía de Optimización SEO para Hotelvisperas

**Fecha de generación:** 2026-04-07 18:40:22

---

## 1. Revisión de Metadatos

### Title Tag (Título de Página)

| Aspecto | Estado |
|---------|--------|
| Valor actual | ⚠️ Sin title tag configurado |
| Longitud | 0 caracteres ⚠️ Longitud no óptima |
| Estado general | ✅ Correcto |

**Recomendaciones:**
- ✅ Title tag personalizado detectado
- 📝 Verificar que incluya palabras clave relevantes

### Meta Description (Descripción Meta)

| Aspecto | Estado |
|---------|--------|
| Valor actual | ⚠️ Sin meta description |
| Longitud | 0 caracteres ⚠️ Longitud no óptima |
| Estado general | ✅ Correcto |

**Recomendaciones:**
- ✅ Descripción personalizada detectada
- 📝 Verificar que incluya palabras clave y llamada a la acción

---

## 2. Checklist de Implementación

### Metadatos (Prioridad Alta)

- [ ] Revisar y personalizar title tag
- [ ] Revisar y personalizar meta description
- [ ] Verificar que title y description sean únicos en cada página
- [ ] Incluir palabras clave principal en los primeros 50 caracteres

### Estructura de Encabezados (Prioridad Alta)

- [ ] ❌ Falta etiqueta H1 principal
- [ ] Usar solo una etiqueta H1 por página
- [ ] Usar encabezados H2-H6 de forma jerárquica

### Schema Markup (Prioridad Media)

- Implementar schema Hotel
- Implementar schema BreadcrumbList
- Considerar schema FAQPage si hay sección de preguntas frecuentes


### URLs Amigables (Prioridad Media)

- [ ] URLs limpioas con guiones (ej: /habitaciones/deluxe)
- [ ] Evitar parámetros largos
- [ ] Incluir palabra clave principal en URL

---

## 3. Recomendaciones de Schema Markup

### Schema Hotel (Obligatorio)

```json
{
  "@context": "https://schema.org",
  "@type": "Hotel",
  "name": "Hotelvisperas",
  "description": "Descripción del hotel y propuesta de valor principal",
  "address": {
    "@type": "PostalAddress",
    "addressLocality": "Santa Rosa de Cabal",
    "addressCountry": "CO"
  },
  "telephone": "+57 606 123 4567",
  "priceRange": "$80-150"
}
```

### Schema AggregateRating (Recomendado)

```json
{
  "@type": "AggregateRating",
  "ratingValue": "4.5",
  "reviewCount": "150"
}
```

---

## 4. Próximos Pasos

1. **Inmediato (esta semana):**
   - Corregir title tag si es genérico
   - Corregir meta description si es genérica

2. **Corto plazo (próximas 2 semanas):**
   - Implementar schema Hotel
   - Revisar estructura de encabezados

3. **Mediano plazo (próximo mes):**
   - Auditoría completa de contenido
   - Optimización de imágenes

---

## 5. Voice Search Keywords - Eje Cafetero (FASE-B AEO)

**Keywords de voz para consultas en español en la region del Eje Cafetero:**

| Keyword de Voz | Intencion |
|----------------|-----------|
| "hoteles boutique cerca del Valle del Cocora" | Busqueda de alojamiento cerca de naturaleza |
| "hotel con spa en Santa Rosa de Cabal" | Busqueda de bienestar relaxation |
| "lugar donde tomar cafe de origen en Pereira" | Experiencia cafe de especialidad |
| "hoteles termales en el Eje Cafetero" | Busqueda de turismo termal |
| "hotel familiar cerca de Salento" | Alojamiento familiar rural |
| "mejores restaurantes en el Valle del Cocora" | Informacion complementaria |
| "clima en Pereira hoy" | Utilidad viaje |

**Implementacion:**
- Incluir estas keywords en el contenido de la pagina de inicio
- Usar naturalmente en meta description y headings
- Crear contenido especifico sobre experiencias locales

---

*Documento generado automáticamente por IA Hoteles - FASE-B AEO Voice-Ready*
