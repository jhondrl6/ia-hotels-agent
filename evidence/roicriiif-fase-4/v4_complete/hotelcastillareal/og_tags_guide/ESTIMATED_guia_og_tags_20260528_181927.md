# Guía de Open Graph Tags - Hotel

## ¿Qué son Open Graph Tags?

Son meta tags que controlan cómo se muestra su sitio cuando se comparte en redes sociales.

## Estado Actual
No detectable (requiere implementación)

## Impacto por Red Social

| Red Social | Sin OG | Con OG |
|-----------|--------|--------|
| Facebook | Imagen aleatoria | Imagen seleccionada por usted |
| LinkedIn | Sin preview rica | Con imagen, título, descripción |
| WhatsApp | Solo URL | Con imagen y título |
| Twitter | Sin imagen | Con tarjeta rica |

## Implementación

Agregue en el <head> de su sitio:

```html
<!-- Open Graph / Facebook -->
<meta property="og:type" content="website" />
<meta property="og:url" content="" />
<meta property="og:title" content="Hotel - Hotel Boutique en [Ciudad]" />
<meta property="og:description" content="[Descripción de 155-200 caracteres]" />
<meta property="og:image" content="[URL de imagen 1200x630px]" />

<!-- Twitter -->
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="Hotel" />
<meta name="twitter:description" content="[Descripción]" />
<meta name="twitter:image" content="[URL de imagen]" />
```

## Imagen Recomendada
- Dimensiones: 1200x630px (Facebook/LinkedIn)
- Formato: JPG o PNG
- Tamaño máximo: 5MB
- Contenido: Foto atractiva del hotel con buena iluminación

## Verificación

1. Facebook Sharing Debugger: https://developers.facebook.com/tools/debug/
2. LinkedIn Post Inspector: https://www.linkedin.com/post-inspector/
3. Twitter Card Validator: https://cards-dev.twitter.com/validator