# ROADMAP iah-cli — Estrategia Comercial (90 días)

> **Versión**: v2.0 (2026-04-18) — Reescritura basada en audit v2
> **Estado proyecto**: v4.31.1 — Pipeline operativo
> **Principio rector**: Un cliente pago vale más que 100 leads gratuitos.
> **Horizonte**: 90 días operativos. Se reescribe trimestralmente.
> **Corrección técnica**: `v4lite` no existe; se usa `spark` (stages geo+ia, <5 min).
> **Estado**: 0 clientes. 0 validación de mercado.

---

## FASE 0: Fundación técnica (COMPLETADO)

**Estado**: v4.31.1 — Pipeline v4complete operativo.

Lo que ya existe y funciona:
- Pipeline v4complete: diagnóstico → propuesta → assets → coherencia
- Comando `spark`: diagnóstico rápido <5 min (stages geo + ia). Genera: `spark_report.md`, `whatsapp_script.txt`, `quick_win_action.md`, `metrics_summary.json`
- 17 workflows definidos (.agents/workflows/)
- Agent harness con handlers, timeout, memory
- 409 módulos Python, 2224 tests, 0 regresión
- Coherence Score 0.84, Publication Ready: true

**Nota sobre spark**: Marcado como deprecado pero funcional. Para el caso de uso de outreach pre-ejecutado es exactamente lo necesario (rápido, barato, ~$0.05 USD/prospecto en APIs). No se construye nada nuevo.

**Conclusión**: El motor está listo. Falta el canal de distribución y la validación de mercado.

---

## FASE 0.5: Validación y primer contacto (2 semanas)

**Objetivo**: Antes de construir cualquier canal, validar que el dolor existe y que alguien paga por resolverlo.

**Por qué aquí**: No se puede vender "visibilidad digital" a hoteleros sin saber si ellos reconocen ese problema, cómo lo verbalizan, y cuánto están dispuestos a pagar. Todo lo demás depende de esto.

### Producto 1: Diagnóstico Express — $120.000 COP (~$30 USD)

**No es gratuito.** Gratis atrae curiosos, no compradores. El Express filtra intención real y cubre costo operativo. Solo quienes pagan el Express reciben propuesta de implementación.

| ID | Entregable | Detalle | Estimación |
|----|-----------|---------|------------|
| V-01 | ICP definido | 4 condiciones verificables: 8-25 hab, propiedad familiar con sucesión (hijo/hija 25-40 años que "lleva lo digital" — es el comprador real), fuera de dependencia total Booking, ticket >$280k COP/noche. Lista de 30-40 hoteles de Cotelco Quindío/Risaralda + Airbnb Plus/Luxe + TripAdvisor top 50 regional | 1 día |
| V-02 | 5 entrevistas de validación | 20 min cada una, sin vender. Solo escuchar. Output: 5 frases textuales del dolor del hotelero. **Guía**: el dolor que verbalizan NO es "baja visibilidad" sino frases como: "Booking me cobra 18% de comisión", "No tengo tiempo de actualizar nada", "Mi sobrino lleva eso" (= nadie lo lleva), "Ya pagué una agencia y no pasó nada", "En temporada baja no viene nadie". El servicio debe traducirse al lenguaje de SU dolor, no al revés. | 2-3 días |
| V-03 | Pre-ejecución spark sobre prospectos | `python main.py spark --url "<maps-url>"` para cada hotel. Capturar hallazgo más fuerte de `metrics_summary.json` | 1-2 días |
| V-04 | Landing minimalista | 1 página: quién soy + 1 caso + botón WhatsApp. Dominio + Vercel. Sin diagnóstico gratuito en el hero | 1 sesión |
| V-05 | Script de outreach personalizado | 3 variantes por tipo de hallazgo (schema ausente, sin fotos, horario desactualizado). Cada mensaje lleva dato propio del hotel. **Template base**: `Hola [nombre], vi que [Hotel] en [ciudad]. Hice una revisión rápida y tu ficha de Google Maps tiene [hallazgo específico]. Eso te está costando [consecuencia tangible]. ¿Te paso el reporte completo? Son 3 páginas, cuesta $120k, y si ya tienes el problema identificado puedes arreglarlo tú mismo sin contratarme.` | 1 sesión |

**Comando spark para pre-ejecutar prospectos**:
```bash
# spark ejecuta solo geo + ia stages (<5 min cada uno)
python main.py spark --url "https://maps.google.com/..." --output ./outreach/prospect_01
# Output: spark_report.md + whatsapp_script.txt + quick_win_action.md + metrics_summary.json
```
Costo: ~$0.05 USD/prospecto. 40 prospectos = ~$2 USD total.

**Nota sobre "gratis"**: El diagnóstico gratuito solo existe como **contenido público** (Reels, comparativas regionales, posts). NUNCA como trato individual 1:1 con un hotel. Cada interacción directa es de pago desde el primer segundo. El 80% de "leads" de diagnósticos gratuitos en B2B nunca compra — cuesta tiempo del fundador, no dinero.

**Tasas esperadas de outreach**: 15-20% de lectura, 5-8% de respuesta, 2-3% de conversación comercial. Con 40 mensajes: 1-2 conversaciones reales. Eso no es fracaso, es la realidad B2B hotelera regional. El gancho es el dato personalizado (hallazgo de spark), no el volumen.

**Gate de validación**: Al final de FASE 0.5 se tienen 5 frases textuales del dolor del hotelero y una lista de 30-40 prospectos con hallazgo pre-ejecutado. Si no se consiguen las 5 entrevistas, se ajusta el ICP antes de continuar.

---

## FASE 1: Landing + Outreach + Primer Express pago (4 semanas)

**Objetivo**: Primer contacto comercial real. Primer Diagnóstico Express vendido y entregado.

| ID | Entregable | Detalle | Estimación |
|----|-----------|---------|------------|
| O-01 | 30-40 mensajes personalizados enviados | 1 por hotel, con hallazgo propio de spark. WhatsApp/email según disponibilidad | 3-5 días |
| O-02 | Llamadas agendadas | 15 min con los que respondan. Objetivo: 2-4 conversaciones comerciales reales | Semana 2 |
| O-03 | Primer Express vendido | $120k COP. Entrega manual: reporte v4complete personalizado con narrativa del hallazgo | Semana 3 |
| O-04 | Debrief primer cliente | Qué preguntó, qué valoró, qué ignoró. `clients/01-debrief.md` | Semana 4 |
| O-05 | Segunda ronda outreach | 20 mensajes ajustados con aprendizaje del debrief | Semana 4 |

**Métricas de éxito**:
- 1 Express vendido (umbral mínimo)
- 3-5 Express vendidos (objetivo)
- 2-4 conversaciones comerciales reales
- 5 frases textuales del dolor documentadas

**Gate de validación crítico (Semana 3)**: Si no hay 1 Express vendido, **no** se avanza con el mismo plan. Se revisa ICP, pitch, precio — se rediseña.

---

## FASE 1.5: Instagram como canal de captura activa (paralelo)

**Objetivo**: Instagram no es contenido pasivo; es canal de captura de DMs con intención de compra.

| ID | Entregable | Detalle | Estimación |
|----|-----------|---------|------------|
| IG-01 | Reels educativos con datos reales | Comparativas regionales anónimas del spark. Ej: "El 70% de hoteles en Salento no tienen schema.org" | 1-2/semana |
| IG-02 | DMs con intención de compra | Responder a comentarios con CTA: "Envíanos tu link y te decimos qué tan visible eres" | Continuo |
| IG-03 | Contenido de caso propio | "Mira lo que hice con mi propio sitio" — datos reales de v4complete sobre iahoteles.com | 1 sesión |

**Métricas**: Instagram DMs con intención de compra: 1 (umbral) / 5 (objetivo) al mes.

---

## FASE 2: 3-5 Express + 1 implementación + 1 palanca (6 semanas)

**Objetivo**: Escalar de Express a implementación. Activar un canal indirecto.

### Producto 2: Implementación SEO/AEO/GEO — $1.500.000–$3.500.000 COP (~$350–850 USD)

Solo se ofrece a quienes ya pagaron el Express.

| ID | Entregable | Detalle | Estimación |
|----|-----------|---------|------------|
| IM-01 | 3-5 Express entregados | Reportes v4complete personalizados. Cada uno genera aprendizaje | Semanas 1-4 |
| IM-02 | Propuesta de implementación | Al hotel con mayor dolor de los Express. Precio según alcance | Semana 4-5 |
| IM-03 | Primer cliente de implementación | Cerrar o aprender por qué no cerró | Semana 5-6 |
| IM-04 | 1 palanca asimétrica activada | Contactar Cotelco Quindío/Risaralda, Fontur, agencias de turismo regional, o universidades (UTP, UniQuindío) | Semana 4 |

**Palancas disponibles**:

| Palanca | Acción | Multiplicador |
|---------|--------|---------------|
| Cotelco Quindío/Risaralda | Charla gratuita "Visibilidad digital 2026" | 30-80 hoteleros en una sala |
| Fontur / Cámara de Comercio Armenia | Pitch programa fortalecimiento digital | Presupuesto público |
| Agencias de turismo regional | White-label: ellos venden tours, tú diagnósticos | Canal indirecto |
| Universidades (UTP, UniQuindío) | Caso de estudio académico → PR orgánica | Credibilidad + backlinks |

**Objetivo de 6 semanas**:
- 3-5 Express vendidos (~$400k–$600k COP facturados)
- 1 implementación firmada (~$1.5M–$3.5M COP)
- 5 entrevistas de validación + 5 debriefs postventa
- 1 palanca asimétrica activa

---

## FASE 3: Caso publicable + contenido AEO con datos reales

**Objetivo**: Convertir los primeros clientes en contenido que genere tracción orgánica. Solo se ejecuta tras tener 1+ caso pago.

| ID | Entregable | Detalle | Estimación |
|----|-----------|---------|------------|
| CA-01 | Caso de uso publicado | "Cómo llevamos [Hotel X] de score Y a Z en 30 días" — datos reales, screenshots | 1 sesión |
| CA-02 | Contenido AEO para la web | Artículos que respondan preguntas reales de hoteleros (usando las frases textuales de las entrevistas) | 1-2 sesiones |
| CA-03 | Comparativa regional | "El 70% de hoteles en el Eje Cafetero no tienen schema.org" — datos agregados anónimos | 1 sesión |
| CA-04 | llms.txt | Archivo `/llms.txt` describiendo servicio, capacidades, cómo citarte | 30 min |

**Dependencias**: Al menos 1 caso pago completado.

---

## FASE 4: Monetización recurrente y escalado de canales

**Objetivo**: Convertir el modelo manual en repetible. Solo se ejecuta tras 3+ Express entregados y 1 implementación cerrada.

| ID | Entregable | Detalle | Disparador |
|----|-----------|---------|------------|
| MR-01 | Automatización WhatsApp con spark | El hotelero envía URL por WhatsApp, recibe spark en minutos | 10+ Express manuales entregados |
| MR-02 | Reporte trimestral regional | Agregado anónimo "Salud Digital Hotelera del Eje Cafetero" | 15+ hoteles diagnosticados |
| MR-03 | Kit de entrega profesional | PDF con diagnóstico + propuesta + plan de acción | Parcialmente existe |
| MR-04 | Seguimiento automático periódico | "Tu hotel tenía score X hace 30 días, hoy tiene Y" | 5+ clientes activos |

---

## ANEXO: Visión 12-24 meses (ex-FASES 5-7)

Estas fases no se eliminan, pero requieren disparadores verificables antes de ejecutarse.

### FASE 5: Integración Operativa
- Conector PMS básico (datos de ocupación, ADR)
- Integración GA4 multi-hotel
- **Disparador**: 10 clientes de implementación activos (no 5)

### FASE 6: Hotel Graph
- Schema Definition, Graph Builder, Persistencia, Impact Analyzer
- Community Detection (Leiden), NaturalQuery
- **Disparador**: 20 hoteles activos (el ROI de un grafo con <20 nodos es negativo)

### FASE 7: Escalamiento
- Multi-idioma (inglés, portugués)
- Cumplimiento turístico
- Ecosistema de skills comunitarios
- **Disparador**: 3 clientes que lo paguen explícitamente

---

## OKRs — Primeros 90 días

> Métricas de **supervivencia**, no de tracción.

| Métrica | Umbral | Objetivo | Frecuencia |
|---------|--------|----------|------------|
| Entrevistas de validación | 3 | 5 | Una vez, semana 1 |
| Prospects en lista ICP-filtrada | 20 | 40 | Una vez, semana 1 |
| Mensajes personalizados enviados | 20 | 40 | Semanal |
| Conversaciones comerciales reales | 2 | 5 | Mensual |
| Diagnósticos Express pagados | 1 | 5 | Mes 1-2 |
| Clientes de implementación | 0 | 1 | Mes 2-3 |
| Palancas asimétricas activadas | 0 | 1 | Trimestral |
| Instagram DMs con intención de compra | 1 | 5 | Mensual |

**Métricas eliminadas temporalmente** (se reintroducen en mes 4+):
- Ranking Google para keywords
- Menciones en ChatGPT/Perplexity
- Leads orgánicos desde web
- Velocidad Lighthouse

---

## Principios rectores

1. **Un cliente pago vale más que 100 leads gratuitos.** Toda métrica de "lead" sin intención de pago es vanidad.
2. **Manual antes que automático, específico antes que general.** Nada se automatiza sin haberse hecho manualmente 10 veces.
3. **Cobrar valida mejor que encuestar.** La willingness-to-pay es el único indicador no engañable.
4. **El tiempo del fundador es el único recurso escaso.** Toda decisión se evalúa por costo de oportunidad sobre ese tiempo.
5. **Cada fase genera valor comercial verificable antes de avanzar.**

---

## Riesgos

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Hoteleros no reconocen valor de SEO/AEO/GEO | Alta | Alto | Entrevistas de validación FASE 0.5 |
| Temporada baja (mayo-junio) reduce urgencia | Media | Medio | Pitch: "prepárate para temporada alta" |
| Fundador se distrae perfeccionando pipeline vs vender | Alta | Alto | Gate semana 3: si no hay venta, se congelan commits no-venta |
| Agencias locales copian el pitch | Baja-Media | Bajo | Ventaja es el pipeline, no el pitch |
| Cliente #1 pide reembolso | Media | Alto | Express tiene entregable tangible; reembolso solo si no se entrega |

---

## Costos operativos (primeros 90 días)

| Concepto | Costo |
|----------|-------|
| Dominio | ~$12 USD/año |
| Hosting (Vercel/Netlify) | $0 |
| spark sobre 40 prospectos | ~$2 USD (APIs geo + ia) |
| WhatsApp API (usuario inicia → FEP 72h gratis) | $0 |
| v4complete para Express entregados | ~$2-5 USD por diagnóstico |
| **Total estimado 90 días** | **< $50 USD** |

---

## Deuda técnica del ROADMAP

- Ortogonalidad de métricas en pipeline legacy (gbp_auditor.py): aplicar cuando se active. Tracking: CHANGELOG v4.22.0.
- `spark` está marcado como deprecado. Si cumple función comercial, mantener vivo. Re-evaluar tras 10+ usos manuales.

---

> *Revisión: semanal las primeras 6 semanas, luego quincenal. Triggers: completar FASE 0.5 o cerrar primer Express, lo que ocurra primero.*
> *Próxima revisión estratégica: 2026-06-19*
