# Guía de Optimización SEO para Hotel Vísperas

**Fecha de generación:** 2026-03-16 12:41:53

---

## 1. Revisión de Metadatos

### Title Tag (Título de Página)

| Aspecto | Estado |
|---------|--------|
| Valor actual | No configurado |
| Longitud | 0 caracteres ⚠️ Longitud no óptima |
| Estado general | ✅ Correcto |

**Recomendaciones:**
- ✅ Title tag personalizado detectado
- 📝 Verificar que incluya palabras clave relevantes

### Meta Description (Descripción Meta)

| Aspecto | Estado |
|---------|--------|
| Valor actual | No configurado... |
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
  "name": "Hotel Vísperas",
  "description": "Descripción del hotel...",
  "address": {
    "@type": "PostalAddress",
    "addressLocality": "Ciudad",
    "addressCountry": "CO"
  },
  "telephone": "+57XXX",
  "priceRange": "$$"
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

*Documento generado automáticamente por IA Hoteles*
