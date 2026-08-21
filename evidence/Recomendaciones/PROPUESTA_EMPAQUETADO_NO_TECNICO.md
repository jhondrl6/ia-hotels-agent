# Propuesta: Resolución Gap "Empaquetado no técnico"

**Fuente:** `evidence/Recomendaciones/Resultados.ini` § Gap Analysis, línea 8-11
**Fecha revisión:** 2026-07-09
**Estado:** DISEÑO — pendiente de implementación en próxima sesión
**Restricciones operativas (confirmadas con el usuario):**
  1. El PDF toma datos del output completo de v4_complete: los 2 documentos .md (01_DIAGNOSTICO + 02_PROPUESTA) como base primaria + v4_complete_report.json como fuente estructurada complementaria. Cero invención, cero suposición.
  2. El destinatario es el hotel al que hace referencia ese output. v4_complete es dinámico por diseño: cada hotel genera su propio output. El PDF siempre contiene datos del propio hotel, nunca de un caso ajeno anonimizado.
  3. El sistema debe ser reutilizable: mismos templates, distintos hoteles = distintos datos.

---

## 1. El Gap

```
Gap: Empaquetado no técnico
Estado hoy: Output .md técnico; hotelero no lee JSON-LD
Yo solo puedo: Sí: 1 PDF de 2 páginas "Cuánto pierde su hotel" con datos del propio hotel (generado por v4_complete).
               Plantilla única reutilizable, datos dinámicos por cliente
Requiere equipo: Diseño pro (opcional, Canva basta)
```

### Por qué el output actual no sirve para venta

| Archivo real | Líneas | Problema |
|--------------|--------|----------|
| `01_DIAGNOSTICO_Y_OPORTUNIDAD_20260707_121029.md` | 339 | Habla de JSON-LD, schemas, scores — el hotelero cierra la pestaña |
| `02_PROPUESTA_COMERCIAL_20260707_121034.md` | 343 | Tablas con "Schema Hotel", "OpenGraph", "FAQ Schema" — ruido técnico |
| `luxorhotel_*.zip` | 110 archivos | El hotelero nunca abre un ZIP |

> **Nota de vigencia (FASE-P2-B):** la estructura del ZIP actual es limpia y bien organizada:
> `deliveries/{hotel_id}_{date}.zip` contiene `README_DELIVERY.md`, `MANIFEST.json`,
> `IMPLEMENTATION_ORDER.md` + assets. Ver `modules/delivery/delivery_packager.py`.
> El problema de fondo sigue siendo el mismo: el hotelero no abre ZIPs tecnicos.

> **Nota:** la propuesta comercial YA está bien redactada en español llano ("Nosotros hacemos todo. Usted solo atiende huéspedes.") pero está enterrada entre 343 líneas de markdown y mezclada con detalles técnicos.

### Lo que el hotelero necesita

Un documento de 2 páginas que:
1. Abra con un número grande e impactante (la fuga en COP)
2. Explique en español llano qué significa ese número
3. Muestre las 3 brechas principales detectadas EN SU HOTEL
4. Incluya su score digital vs. promedio regional (contexto de qué tan mal está)
5. Tenga un call-to-action claro y de bajo riesgo

---

## 2. Datos disponibles en el output de v4_complete (catálogo completo)

Verificado contra los archivos reales del caso Luxorhotel. **Estos son los ÚNICOS datos que el PDF puede usar.** El output de v4_complete por hotel son 3 fuentes:

- **01_DIAGNOSTICO_Y_OPORTUNIDAD_{timestamp}.md** — diagnóstico técnico (datos de visibilidad, brechas, scores, reseñas GBP)
- **02_PROPUESTA_COMERCIAL_{timestamp}.md** — propuesta comercial (fuga, proyección, ROI, pricing, servicios, garantías)
- **v4_complete_report.json** — datos estructurados (campos financieros, opportunity_scores, gate_results, pricing)

> **Criterio de precedencia:** cuando un dato existe en múltiples fuentes, el .md tiene prioridad sobre el JSON para lo que se muestra al hotelero (el .md ya tiene el dato formateado y validado por los gates de publicación). El JSON se usa para campos estructurados que el script necesita leer programáticamente (ej: opportunity_scores ordenados por rank).

### 2.1 Datos del hotel

| Fuente | Campo | Valor Luxorhotel | Placeholder PDF | Obligatorio |
|--------|-------|------------------|-----------------|------------|
| JSON | `hotel_name` | `"Luxorhotel"` | `{{HOTEL_NOMBRE}}` | SÍ |
| JSON | `url` | `"http://www.luxorhotel.com.co/"` | `{{HOTEL_URL}}` | SÍ |
| JSON | `region` | `"Eje Cafetero"` | `{{HOTEL_REGION}}` | SÍ |
| 01_DIAGNOSTICO línea 11/20 | Título H2 | `"Cl. 24 #8-35, Pereira, Risaralda, Colombia"` | `{{HOTEL_DIRECCION}}` | SÍ |
| 01_DIAGNOSTICO línea 204 | GBP status | `"277 reviews, 4.1/5 rating"` | `{{GBP_RESEÑAS}}` + `{{GBP_RATING}}` | SÍ (capturado del GBP por el sistema) |

> **Nota sobre reseñas:** v4_complete captura las reseñas del Google Business Profile durante la ejecución. No son un dato externo manual — son output dinámico del sistema. Cada hotel obtendrá sus propias reseñas y rating.

### 2.2 Datos financieros (la cifra de impacto)

| Fuente | Campo | Valor Luxorhotel | Placeholder PDF | Notas |
|--------|-------|------------------|-----------------|-------|
| JSON + 02_PROPUESTA línea 30 | Fuga mensual (expected_monthly) | `$3.741.696 COP` | `{{FUGA_MENSUAL}}` | **La cifra gancho principal** |
| 01_DIAGNOSTICO líneas 227-229 | Escenario mínimo | `$2.993.356 COP/mes` | `{{FUGA_MINIMA}}` | Rango inferior (70% confianza) |
| 01_DIAGNOSTICO línea 229 | Escenario máximo | `$4.490.035 COP/mes` | `{{FUGA_MAXIMA}}` | Rango superior (10% confianza) |
| 01_DIAGNOSTICO línea 15 | Comisión OTA real | `$7.741.440 COP` | `{{COMISION_OTA_REAL}}` | Lo que paga al año en comisiones |
| 02_PROPUESTA línea 134/154 | Recuperación proyectada 6 meses | `$5.041.935 COP` | `{{RECUPERACION_6M}}` | Curva de maduración 4 pilares × recovery factor 35% |
| 02_PROPUESTA línea 188 | ROI | `2.10X` | `{{ROI}}` | Calculado sobre OPEX (no CAPEX+OPEX) |
| 02_PROPUESTA línea 133 | Fuga total 6 meses | `$22.450.176 COP` | `{{FUGA_6M}}` | Fuga bruta acumulada |

> El PDF usa `FUGA_MENSUAL` como cifra gancho principal. `RECUPERACION_6M` y `ROI` van en página 2 como proyección. Los escenarios min/max se reservan para la llamada.

### 2.3 Scores de visibilidad digital (4 pilares)

| Fuente | Pilar | Su hotel | Promedio regional | Placeholder |
|--------|-------|----------|-------------------|-------------|
| 01_DIAGNOSTICO línea 160 | SEO Local | 25/100 | 59/100 | `{{SEO_SCORE}}` / `{{SEO_REGIONAL}}` |
| 01_DIAGNOSTICO línea 161 | GEO | 61/100 | 77/100 | `{{GEO_SCORE}}` / `{{GEO_REGIONAL}}` |
| 01_DIAGNOSTICO línea 162 | AEO | 15/100 | 44/100 | `{{AEO_SCORE}}` / `{{AEO_REGIONAL}}` |
| 01_DIAGNOSTICO línea 163 | IAO | 0/100 | 20/100 | `{{IAO_SCORE}}` / `{{IAO_REGIONAL}}` |

> Estos scores ya vienen con promedio regional incluido en el .md. El PDF puede mostrar una tabla compacta "Su hotel vs. promedio regional" — el hotelero entiende "25 vs 59" sin saber qué es SEO.

### 2.4 Brechas detectadas (top 3)

**Discrepancia conocida entre fuentes:** el JSON `opportunity_scores` y el 01_DIAGNOSTICO tienen ordenamientos y COP ligeramente distintos para las brechas. El 01_DIAGNOSTICO secciona "LAS 3 FUGAS PRINCIPALES" (líneas 119-131) con un narrativo editado para el hotelero. El JSON tiene los datos crudos con `rank` y `total_score`.

**Decisión:** el PDF usa el JSON `opportunity_scores[0..2]` para los datos estructurados (nombres, COP, justificaciones) porque ya vienen ordenados por `rank` y son programáticamente extraíbles. El 01_DIAGNOSTICO sección 4 se usa como referencia de tono/narrativa.

| Rank | Campo JSON | Valor Luxorhotel | Placeholder |
|------|------------|------------------|-------------|
| 1 | `opportunity_scores[0].brecha_name` | `"Canal Directo Cerrado (Sin WhatsApp)"` | `{{BRECHA_1_NOMBRE}}` |
| 1 | `opportunity_scores[0].estimated_monthly_cop` | `808206.0` | `{{BRECHA_1_COP}}` |
| 1 | `opportunity_scores[0].justification` | `"Viajeros quieren reservar..."` | `{{BRECHA_1_JUSTIFICACION}}` |
| 2 | `opportunity_scores[1].brecha_name` | `"Visibilidad Local (Google Maps)"` | `{{BRECHA_2_NOMBRE}}` |
| 2 | `opportunity_scores[1].estimated_monthly_cop` | `808206.0` | `{{BRECHA_2_COP}}` |
| 2 | `opportunity_scores[1].justification` | `"73% de busquedas son 'cerca de mi'..."` | `{{BRECHA_2_JUSTIFICACION}}` |
| 3 | `opportunity_scores[2].brecha_name` | `"Sin Schema de Hotel (Invisible para IA)"` | `{{BRECHA_3_NOMBRE}}` |
| 3 | `opportunity_scores[2].estimated_monthly_cop` | `763306.0` | `{{BRECHA_3_COP}}` |
| 3 | `opportunity_scores[2].justification` | `"Su sitio no tiene datos estructurados..."` | `{{BRECHA_3_JUSTIFICACION}}` |

### 2.5 Pricing y estructura financiera (oferta)

| Fuente | Campo | Valor Luxorhotel | Placeholder PDF |
|--------|-------|------------------|-----------------|
| 02_PROPUESTA línea 46 | Fee mensual | `$400.000 COP/mes` | `{{PRECIO_MENSUAL}}` |
| 02_PROPUESTA línea 164 | Setup fee (CAPEX) | `$2.500.000 COP` | `{{SETUP_FEE}}` |
| 02_PROPUESTA línea 166 | OPEX 6 meses | `$2.400.000 COP` | interno (cálculo) |
| JSON | `pricing.tier` | `"boutique"` | interno |
| Resultados.ini § P3 | Express | `$120.000 COP` | `{{PRECIO_EXPRESS}}` (constante del plan de negocio) |

> El precio de Diagnóstico Express $120K proviene de `config/pricing.yaml` (`express_price: 120000`, FASE-P0-A como fuente unica). El template lleva el $120K como constante, con este comentario de trazabilidad. Si pricing.yaml cambia, se edita el template una vez.

### 2.6 Datos que NINGUNA fuente contiene (prohibido usar)

La versión anterior de esta propuesta tenía una lista negra extensa basada solo en el JSON. Al incluir los .md como fuente, la mayoría de esos datos YA están disponibles. Esta es la lista negra revisada — datos que genuinamente no existen en NINGÚN output de v4_complete:

- ❌ **Caso real de otro hotel anonimizado** — el sistema no genera datos comparativos entre hoteles. Cada output es individual.
- ❌ **"$X recuperados" (histórico real)** — la proyección ($5M/6meses) es una estimación basada en curva de maduración, no un caso cerrado. El PDF no debe presentarla como hecho consumado.
- ❌ **Logo/marca del consultor** — el output no incluye assets gráficos. El PDF es texto+datos.

**Si en el futuro v4_complete incluye estos datos, se añaden al template. Hasta entonces, NO existen.**

### 2.7 Caveat de calidad: Tier B/C en datos financieros (pre-Express)

El JSON incluye un gate `financial_validity` que puede tener status WARNING. El frontmatter YAML del 01_DIAGNOSTICO expone `financial_evidence_tier` (línea 9):

```yaml
financial_evidence_tier: "B"   # puede ser "A", "B", o "C"
```

Los tiers según el 01_DIAGNOSTICO (línea 249):
- **Tier A:** Basado en Google Analytics + Search Console + datos reales del hotel
- **Tier B:** Basado en benchmarks regionales + datos web públicos
- **Tier C:** Basado en datos limitados de su web + valores default del motor financiero

**Esto importa porque el pipeline tiene DOS pasadas de v4_complete:**

```
PASADA 1 (pre-venta, sin datos del hotel):
  v4_complete con datos públicos → Tier B o C → fuga ESTIMADA
  → generate_hook_pdf.py → PDF gancho con disclaimer de estimación

PASADA 2 (post-Express, con datos reales del hotel):
  Hotel paga $120K Express → entrega datos reales (habitaciones, reservas,
  ADR, % canal directo) → v4_complete con datos del hotel → Tier A
  → cifra EXACTA (ya NO es el PDF gancho de 2 páginas, es el
  diagnóstico Express de 5 páginas)
```

La línea 113 del 01_DIAGNOSTICO confirma qué datos necesita el hotel para llegar a Tier A: "número de habitaciones, reservas mensuales promedio, valor promedio de reserva (COP) y porcentaje de canal directo."

**Implicancia para el PDF gancho (SIEMPRE es pre-Express, Tier B/C):**

El PDF gancho de 2 páginas **siempre** se genera desde la PASADA 1 (pre-venta). El `financial_evidence_tier` será B o C. El disclaimer debe decir: "Estimación basada en datos públicos de la región y perfil del hotel. El diagnóstico Express confirma el número exacto con sus datos reales." Esto es consistente con lo que ya hace el 01_DIAGNOSTICO (línea 103).

Si en el futuro el template se reutiliza para el PDF del Express (5 páginas, post-pago), el disclaimer cambiaría a "Cifra basada en sus datos reales" cuando `financial_evidence_tier == "A"`. Pero ese es otro PDF, otro template, otro momento del ciclo de venta.

### 2.8 Datos que vienen del benchmark regional (uso limitado)

`data/benchmarks/regional_adr_2026.json` (master, FASE-P1-A) provee:
- ADR Eje Cafetero boutique (10-25 hab): `$280.000 COP` — `{{ADR_REGION}}`
- Occupancy regional Eje Cafetero: `51.2%`

> **Nota de vigencia (FASE-P2-B):** este archivo se autodefine como `valid_for_exact_projection: false`
> y `epistemic_status: regional_benchmark`. Version anterior citaba $420K (obsoleto; el benchmark
> maestro v1.1.0 calibro $280K vs Don Alfonso $330K y Castilla Real $282K, excluyendo
> Luxor $200K por hotel de paso). Verificar siempre contra el JSON master.
> Se puede usar en el PDF SOLO como contexto regional, NO como afirmacion del hotel individual.
> El ADR regional ya aparece en el 02_PROPUESTA (linea 36).

---

## 3. Estructura del PDF de 2 páginas

### Página 1 — "¿Cuánto pierde su hotel?" (EL GANCHO)

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│   {{HOTEL_NOMBRE}}                                  │
│   {{HOTEL_DIRECCION}}                               │
│   {{GBP_RESEÑAS}} reseñas · {{GBP_RATING}}★         │
│                                                     │
│   ¿CUÁNTO ESTÁ PERDIENDO CADA MES?                  │
│                                                     │
│   ${{FUGA_MENSUAL_FORMATEADO}} COP                  │
│                                                     │
│   En comisiones a OTAs por reservas                  │
│   que pudieron ser directas.                        │
│   (Estimación basada en datos de la región           │
│   y perfil de su hotel.)                            │
│                                                     │
│   ───────────────────────────────────────────       │
│                                                     │
│   3 fugas principales detectadas:                  │
│                                                     │
│   1. {{BRECHA_1_NOMBRE}}                            │
│      ~${{BRECHA_1_COP_FORMATEADO}}/mes              │
│   2. {{BRECHA_2_NOMBRE}}                            │
│      ~${{BRECHA_2_COP_FORMATEADO}}/mes              │
│   3. {{BRECHA_3_NOMBRE}}                            │
│      ~${{BRECHA_3_COP_FORMATEADO}}/mes              │
│                                                     │
│   ───────────────────────────────────────────       │
│                                                     │
│   Su visibilidad digital vs. promedio regional:     │
│                                                     │
│   SEO: {{SEO_SCORE}}/100  (región: {{SEO_REGIONAL}})│
│   GEO: {{GEO_SCORE}}/100  (región: {{GEO_REGIONAL}})│
│   AEO: {{AEO_SCORE}}/100  (región: {{AEO_REGIONAL}})│
│   IAO: {{IAO_SCORE}}/100  (región: {{IAO_REGIONAL}})│
│                                                     │
└─────────────────────────────────────────────────────┘
```

> Cambios respecto a la versión anterior: (a) añadido dirección del hotel y reseñas GBP, (b) añadido disclaimer de estimación debajo de la cifra, (c) añadido tabla de 4 pilares con promedio regional, (d) eliminado score SEO aislado (ahora va con los otros 3 pilares).

### Página 2 — "Cómo se resuelve"

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│   CÓMO SE RESUELVE                                  │
│                                                     │
│   Se implementan las correcciones técnicas          │
│   (visibilidad, datos para IA, ficha optimizada).   │
│   El hotelero no toca nada técnico.                 │
│                                                     │
│   ───────────────────────────────────────────       │
│                                                     │
│   PROYECCIÓN DE RECUPERACIÓN                        │
│                                                     │
│   En 6 meses: ${{RECUPERACION_6M_FORMATEADO}} COP   │
│   ROI: {{ROI}} (sobre fee de servicio)              │
│   Fuga total sin actuar: ${{FUGA_6M_FORMATEADO}}    │
│   COP en 6 meses.                                   │
│                                                     │
│   ───────────────────────────────────────────       │
│                                                     │
│   EMPEZAR SIN RIESGO                                │
│                                                     │
│   Diagnóstico Express: ${{PRECIO_EXPRESS}} COP      │
│   (constante del plan de negocio)                   │
│                                                     │
│   • Le confirmamos el número EXACTO de fuga         │
│   • Entrega en 72 horas                             │
│   • Si la fuga es menor al precio del Express,      │
│     se lo decimos y ahí termina. Usted no pierde.  │
│                                                     │
│   [Contactar por WhatsApp / Email]                  │
│                                                     │
└─────────────────────────────────────────────────────┘
```

> Cambios respecto a la versión anterior: (a) añadido bloque de proyección con recuperación 6M, ROI y fuga acumulada sin actuar, (b) el precio del Express ahora es placeholder (no hardcoded), (c) la garantía "si la fuga es menor a $120K" ahora referencia el placeholder para que sea consistente si el precio cambia.

> **Nota de diseño:** No hay "página 2 caso anonimizado" porque v4_complete es dinámico — cada hotel recibe SUS propios datos, no los de otro hotel. La página 2 usa exclusivamente datos del hotel actual + constantes del plan de negocio.

---

## 3.1 Flujo de venta: dónde entra el PDF en el ciclo

El PDF gancho de 2 páginas es para **segundo contacto**, después de que el prospecto ya respondió. El flujo completo tiene dos pasadas de v4_complete:

```
PASADA 1 — PRE-VENTA (Tier B/C, datos públicos):

1. WhatsApp con dato gancho rápido (sin PDF)
   "Su hotel aparece en Booking pero no responde preguntas de Google/IA — ¿le interesa saber cuánto pierde por eso?"
        │
        ▼
2. Prospecto responde → corres v4_complete sobre su URL (~5 min)
   → genera diagnóstico con benchmarks regionales (Tier B/C)
        │
        ▼
3. Generas PDF gancho con SUS datos estimados (generate_hook_pdf.py)
   → disclaimer: "Estimación basada en datos públicos de la región"
        │
        ▼
4. Envías PDF + agendas llamada de descubrimiento (20 min)
        │
        ▼
5. En la llamada: presentar Diagnóstico Express ($120K)

PASADA 2 — POST-EXPRESS (Tier A, datos reales del hotel):

6. Hotel paga $120K → entrega datos reales:
   habitaciones, reservas mensuales, ADR, % canal directo
        │
        ▼
7. v4_complete con datos del hotel (~5 min)
   → genera diagnóstico con cifra EXACTA (Tier A)
        │
        ▼
8. Entrega Diagnóstico Express: PDF de 5 páginas con fuga exacta,
   3 escenarios, top 5 acciones (ya NO es el PDF gancho de 2 pág)
        │
        ▼
9. Propuesta de Implementación ($2.5M) si la fuga lo justifica
```

**Por qué no enviar el PDF en el primer contacto:** cada PDF requiere un v4_complete previo (~5 min de procesamiento por hotel). Enviar PDFs a 20 prospectos en frío = 100 min de procesamiento con tasa de respuesta incierta. Mejor filtrar con un mensaje rápido de WhatsApp primero, y solo generar el PDF para los que respondan.

**Costo real por prospecto que llega a etapa de PDF:** ~5 min v4_complete + ~30 seg generate_hook_pdf = ~6 min. Si 25% de 20 WhatsApp responden, son 5 PDFs = ~30 min de procesamiento total (no 100).

**El PDF gancho de 2 páginas SIEMPRE es pre-Express (Tier B/C).** Los datos reales del hotel llegan después del pago, en la PASADA 2. Para ese momento el PDF ya cumplió su función (abrir la puerta). El deliverable post-Express es otro documento (5 páginas, Tier A).

---

## 4. Sistema reutilizable (cualquier hotel nuevo)

El sistema tiene 3 componentes. Los **componentes 1 y 2 son fijos** (se editan una vez). El **componente 3 es variable** (cambia por hotel).

### Componente 1: `templates/hook_template.md` (FIJO)

Markdown con todos los `{{PLACEHOLDERS}}` de la sección 2. Se edita UNA vez para cambiar diseño, tono o copy. No se toca por hotel.

### Componente 2: `templates/hook_styles.css` (FIJO)

Estilos visuales (márgenes, fuentes, colores, sin número de página). Se edita UNA vez.

### Componente 3: `scripts/generate_hook_pdf.py` (VARÍA en INPUT, no en código)

Lee el output de v4_complete de cualquier hotel — los 2 documentos .md como base + el JSON como fuente estructurada complementaria — reemplaza placeholders, invoca weasyprint. El script NO cambia entre hoteles — solo cambia la ruta del directorio de entrada.

### Fuentes de datos del script (3 archivos por hotel)

iah-cli genera un hotel a la vez en un directorio plano. El script acepta `output/v4_complete/` tal cual — el usuario es responsable de no pisar datos entre hoteles (correr v4_complete → generar PDF → siguiente hotel, secuencial).

```
output/v4_complete/                                  ← directorio plano (un hotel a la vez)
├── 01_DIAGNOSTICO_Y_OPORTUNIDAD_{timestamp}.md    ← base: frontmatter YAML + scores, brechas, reseñas GBP
├── 02_PROPUESTA_COMERCIAL_{timestamp}.md          ← base: frontmatter YAML + fuga, proyección, ROI, pricing
└── v4_complete_report.json                        ← estructurado: opportunity_scores (rank), gates, pricing
```

> **Decisión de implementación (CONFIRMADA):** parsear frontmatter YAML de los .md para datos numéricos/estructurados (financial_value_central, financial_value_range, financial_ota_commission_real, financial_evidence_tier, gate_status) + parsear el JSON para opportunity_scores, gates y pricing. El frontmatter YAML ya está estructurado y es más robusto que regex sobre el cuerpo del markdown. Los .md se usan además para extraer scores de la tabla de visibilidad (SEO/GEO/AEO/IAO con promedios regionales), reseñas GBP y dirección — estos campos no están en el frontmatter pero sí en secciones predecibles del cuerpo.

### Flujo por hotel (idéntico para todos)

```
output/v4_complete/   ← iah-cli genera UN hotel a la vez aquí
  ├── 01_DIAGNOSTICO_Y_OPORTUNIDAD_{timestamp}.md
  ├── 02_PROPUESTA_COMERCIAL_{timestamp}.md
  └── v4_complete_report.json
        │
        ▼
generate_hook_pdf.py --output-dir output/v4_complete/
        │
        ▼
output/v4_complete/deliveries/{hotel_slug}_gancho.pdf
```

### Convención de nombres de salida

- `output/v4_complete/deliveries/{slug}_gancho.pdf` — el PDF gancho (venta)
- `output/v4_complete/deliveries/{slug}_{timestamp}.zip` — el ZIP técnico (post-venta)
- `output/v4_complete/01_DIAGNOSTICO_Y_OPORTUNIDAD_{timestamp}.md` — diagnóstico técnico (interno)
- `output/v4_complete/02_PROPUESTA_COMERCIAL_{timestamp}.md` — propuesta técnica (interno)

Cuatro artefactos, cuatro audiencias. El PDF es el único que va al hotelero antes de la llamada.

---

## 5. Validaciones obligatorias del script (pendiente de implementación)

Cuando se implemente `generate_hook_pdf.py` en la próxima sesión, DEBE incluir:

1. **Detección de placeholders sin llenar:** después de renderizar, el script debe verificar que el .md final NO contiene ningún `{{...}}`. Si los hay → abortar con error claro listando cuáles faltan.
2. **Validación de campos obligatorios:** si falta `hotel_name`, `FUGA_MENSUAL`, `BRECHA_1..3_NOMBRE`, `SEO_SCORE` o `PRECIO_MENSUAL` → abortar antes de generar.
3. **Resolución de timestamps:** el script debe localizar automáticamente los archivos `01_DIAGNOSTICO_Y_OPORTUNIDAD_*.md` y `02_PROPUESTA_COMERCIAL_*.md` dentro del directorio de output (glob pattern), sin que el usuario tenga que pasar el timestamp manualmente.
4. **Formato COP consistente:** los números monetarios se formatean con separador de miles (.) y sin decimales: `3.741.696`. Esto lo hace el script, no el template.
5. **Slug del hotel:** se genera desde `hotel_name` en minúsculas, sin acentos, sin caracteres especiales. Ej: "Luxorhotel" → `luxorhotel`. Se valida que el slug no esté vacío.
6. **No-sobrescritura accidental:** si el PDF de salida ya existe, el script pregunta o usa `--force`. Nunca sobrescribe silenciosamente.
7. **Modo dry-run:** `--dry-run` muestra qué datos se usarán y dónde quedaría el PDF, sin generar el archivo.
8. **Detección de Tier:** leer `financial_evidence_tier` del frontmatter YAML del 01_DIAGNOSTICO. Si es "B" o "C" → imprimir advertencia: "Datos financieros Tier {tier} — la cifra de fuga se basa en benchmarks regionales. El disclaimer de estimación se incluye en el PDF." Si es "A" → el disclaimer cambia a "Cifra basada en sus datos reales" (aunque en la práctica el PDF gancho siempre será Tier B/C por ser pre-Express).

### Firma prevista del script (a definir en implementación)

```
generate_hook_pdf.py
  --output-dir PATH    # directorio output/v4_complete/ del hotel actual (obligatorio)
                       # el script localiza automáticamente los .md y .json dentro
                       # parsea frontmatter YAML de los .md para datos estructurados
                       # + JSON para opportunity_scores, gates y pricing
  --template PATH      # template .md (default: templates/hook_template.md)
  --style PATH         # template .css (default: templates/hook_styles.css)
  --dry-run            # mostrar datos sin generar PDF
  --force              # sobrescribir PDF existente
  --verbose            # log detallado
```

---

## 6. Decisión pendiente para próxima sesión: stack técnico

El script necesita UNA herramienta para generar PDF. Estado actual en WSL: **NINGUNA instalada**.

| Opción | Peso disco | Iteración diseño | Mantenimiento | Recomendado si... |
|--------|-----------|------------------|---------------|-------------------|
| pandoc + texlive-latex-base | ~500MB | Media (recompilar) | Bajo (template .md + .latex) | Vas a tocar el diseño <5 veces |
| weasyprint (pip + libpango/libcairo del sistema) | ~50MB + ~100MB deps | Alta (CSS directo) | Medio (CSS requiere cuidado) | Vas a iterar diseño seguido |
| HTML imprimible manual (sin instalar nada) | 0 | Alta (abrir Chrome → Imprimir) | Alto (manual por hotel) | Solo para validar contenido antes de elegir stack |

**Recomendación provisional:** instalar **weasyprint**. El template es HTML+CSS (más fácil de iterar que LaTeX), el script Python es nativo (no necesita subproceso), y el peso es 7x menor que la opción pandoc. Decisión final la toma el usuario en la próxima sesión.

---

## 7. Lo que la versión anterior de esta propuesta hizo MAL (lecciones)

Esta sección existe para que la próxima sesión no repita los errores:

1. ❌ Asumió que el JSON era la única fuente de datos — ignoró los 2 documentos .md que contienen dirección, scores GEO/AEO/IAO, reseñas GBP, proyección de recuperación, ROI, CAPEX/OPEX, garantías y servicios. **Corregido:** la sección 2 ahora cataloga datos de las 3 fuentes.
2. ❌ Lista negra (sección 2.6) declaró como "inventados" datos que SÍ están en los .md: "277 reseñas 4.1★" (01_DIAGNOSTICO línea 204), "ROI 2.1X" (02_PROPUESTA línea 188), "$5M recuperados" (02_PROPUESTA línea 134). **Corregido:** la lista negra ahora solo contiene datos que genuinamente no existen en NINGÚN output.
3. ❌ Usó nombres de archivo sin timestamp (`01_DIAGNOSTICO_Y_OPORTUNIDAD.md`) cuando los reales tienen timestamp (`01_DIAGNOSTICO_Y_OPORTUNIDAD_20260707_121029.md`). **Corregido:** el script localiza archivos por glob pattern.
4. ❌ Incluyó una "página 2 caso anonimizado" que contradice la naturaleza dinámica de v4_complete — cada hotel debe recibir SUS propios datos, no los de otro hotel como referencia.
5. ❌ Hardcodeó el brecha_name "WhatsApp" en el template — debe leerse del JSON para que funcione con cualquier hotel.
6. ❌ Propuso 3 opciones de implementación (pandoc, weasyprint, Canva) sin chequear si alguna estaba instalada — todas habría que instalarlas.

**Regla de oro para la próxima sesión:** si un dato no está en la sección 2 de este documento, NO se usa en el PDF. Si necesitas un dato nuevo, primero se verifica que v4_complete lo genera, luego se añade al catálogo de la sección 2, luego al template.

---

## 8. Criterio de avance (para cuando se implemente)

- [ ] `luxorhotel_gancho.pdf` generado desde el output de v4_complete (3 fuentes: 2 .md + JSON)
- [ ] El PDF ocupa exactamente 2 páginas
- [ ] Todos los placeholders están reemplazados (verificado por script, no a ojo)
- [ ] La cifra de fuga es lo primero que se ve, tamaño ≥24pt
- [ ] La página 1 incluye la tabla de 4 pilares con promedio regional
- [ ] La página 1 incluye reseñas GBP y dirección del hotel
- [ ] La página 1 incluye disclaimer de estimación
- [ ] La página 2 incluye proyección de recuperación 6M y ROI
- [ ] El PDF NO contiene ninguna de las afirmaciones prohibidas de la sección 2.6
- [ ] El script funciona con un segundo hotel de prueba (cualquier output que cumpla la estructura)
- [ ] Tiempo de generación <30 segundos por hotel

---

## 9. Resumen de artefactos a crear en próxima sesión

```
output/v4_complete/
├── templates/
│   ├── hook_template.md           (~100 líneas, con placeholders §2)
│   └── hook_styles.css            (~50 líneas, diseño 2 páginas)
├── scripts/
│   └── generate_hook_pdf.py       (~150 líneas, parseo YAML frontmatter + JSON + validaciones §5)
└── deliveries/                    (se crea automáticamente)
    └── luxorhotel_gancho.pdf      (output del script)
```

Tres archivos a crear, ~300 líneas en total. Sin código, sin instalación en esta sesión.

---

## 10. Conexión con el plan de negocio

Esta propuesta resuelve el **gap #2 de 5** del `Resultados.ini` (línea 8-11):

| Gap | Estado |
|-----|--------|
| 1. Lead gen recurrente | Pendiente (P2 § Acción 1-3) |
| **2. Empaquetado no técnico** | **Esta propuesta — DISEÑO listo, implementación pendiente** |
| 3. Automatización ciclo de venta | Pendiente |
| 4. Legal/facturación | Pendiente |
| 5. Onboarding autoguiado | Pendiente |

Una vez implementado, el PDF alimentará directamente la **Acción 2 del P2**: "PDF gancho de 2 páginas: datos del propio prospecto (v4_complete + generate_hook_pdf)" — métrica "Enviado a 20 prospectos; ≥25% responde". El sistema es el mismo para todos los hoteles: template fijo, datos dinámicos del output de v4_complete de cada hotel.
