# Plan Maestro v2.5.0 — Hospitalidad 4.0 (Ajuste 2026)

> **Versión**: 2.5.0 (Actualización Crítica v2.6 Ready)  
> **Fecha**: 2026-02-14  
> **Cambio principal**: Alineación con Benchmarking 2026 (Salario +23%, RevPAR Caribe $600k+) e integración de Umbrales de Decisión v2.5.  
> **Datos fuente**: `data/benchmarks/plan_maestro_data.json` (Versión sincronizada 2026)

---

## 1. Cambios Clave vs v2.4.3

| Aspecto | v2.4.3 | v2.5.0 |
|---------|--------|--------|
| Motor de decisión | Umbrales 2025 | **Umbrales v2.5 (Alta Sensibilidad)** |
| Foco Estratégico | Visibilidad AEO | **Autoridad GEO + Protocolo MCP** |
| Costo Inacción | Basado en RevPAR <$300k | **Basado en RevPAR 2026 (Caribe $600k+)** |
| Implementación | Kit Sin IT | **Kit Sin IT + Automatización "Invisible Service"** |
| Tolerancia CAC | $800k COP | **$1,000,000 COP (Ajuste por ticket premium)** |

---

## 1.1 Costo de Inacción por Región (Actualizado 2026)

**Impacto total acumulado por pérdida de conversión y exclusión de IA**:
- **$25.0M COP/mes** (Caribe - Basado en RevPAR $602k)
- **$12.0M COP/mes** (Antioquia - Basado en RevPAR $359k)
- **$8.5M COP/mes** (Eje Cafetero - Basado en RevPAR $197k)

**Ajuste v2.5**: La brecha de conversión es ahora más letal debido al aumento del **23% en los costos laborales**. Cada reserva no capturada directamente obliga al hotelero a pagar comisiones de OTAs con un margen de utilidad operativa reducido.

---

## 1.2 Indicadores de Volumen (Base de Cálculo 2026)

Para la triangulación del Protocolo de Verdad 4.0, se utilizan los siguientes indicadores regionales como base para el Motor de Decisión:

| Región | Reservas/Mes (Prom.) | Valor Reserva (Prom.) | % Canal Directo |
| :--- | :--- | :--- | :--- |
| **Caribe** | 350 | $900,000 COP | 50% |
| **Antioquia** | 250 | $350,000 COP | 50% |
| **Eje Cafetero** | 200 | $300,000 COP | 50% |

---

## 5.1 Arquitectura de Paquetes v2.5

| Paquete | Resuelve | Entregables Técnicos Específicos | Inversión | Para Quién |
|---------|----------|----------------------------------|-----------|------------|
| **Starter GEO** | Invisibilidad Local | • Ficha de Google optimizada (GEO Ready)<br>• Presencia en mapas de agentes IA<br>• 3 publicaciones/mes con datos estructurados | $1.8M | GBP Score <60 |
| **Pro AEO** | Exclusión IA | • JSON-LD optimizado para búsqueda generativa<br>• 50 FAQs estructuradas para Perplexity/ChatGPT<br>• **Prep-Kit para Protocolo MCP** | $3.8M | Web Score ≥75 |
| **Pro AEO Plus** 🔥 | **IA + Conversión** | • Todo lo de Pro AEO + Botón WA Tracking<br>• 1 fix web crítico para reserva directa<br>• **Guía de Cierre "Invisible Service" (WhatsApp)** | **$4.8M** | **Brecha conversión ≥$2.5M** |
| **Elite** | Dominio Total | • Todo lo de Pro AEO Plus<br>• **Endpoint MCP (Acceso real-time para IA)**<br>• Entrenamiento de 3 agentes IA con contenido del hotel | $7.5M | **RevPAR ≥$180k** (Eje Cafetero Ready) |
| **Elite PLUS** | Autoridad Máxima | • Todo lo de Elite + Monitoreo de 10 consultas IA<br>• **Certificado "Hotel IA-Ready"** y Reserva Directa<br>• Kit físico de autoridad | $9.8M | **Impacto total ≥$6M/mes** |

---

## 5.2 Motor de Decisión Inteligente (v2.5)

El motor ahora es más sensible a las pérdidas menores para compensar el alza de costos operativos.

### Tabla de Decisión Visual (7 Reglas Actualizadas)

| Condición | Brecha Dominante | Impacto Total | RevPAR | Web Score | GBP Score | **→ Paquete** |
|----|------------|------ |--------|-----------|-----------|---------------|
| 1️⃣ | Cualquiera | **≥$6M** | Cualquiera | Cualquiera | Cualquiera | **Elite PLUS** |
| 2️⃣ | Conversión | ≥$2.5M | **≥$180k** | Cualquiera | Cualquiera | **Elite** |
| 3️⃣ | Conversión | ≥$2.5M | <$180k | Cualquiera | Cualquiera | **Pro AEO Plus** |
| 4️⃣ | IA         | <$6M | Cualquiera | ≥75 | Cualquiera | **Pro AEO** |
| 5️⃣ | IA         | <$6M | Cualquiera | <75 | Cualquiera | **Pro AEO Plus** |
| 6️⃣ | GEO        | <$6M | Cualquiera | Cualquiera | <60 | **Starter GEO** |
| 7️⃣ | GEO        | <$6M | Cualquiera | Cualquiera | ≥60 | **Pro AEO** |

---

## 7.1 Umbrales de Decisión v2.5

| Umbral | Valor Anterior (2025) | Valor Nuevo (2026) | Uso |
|--------|-----------------------|--------------------|-----|
| `impacto_catastrofico` | $8,000,000 | **$6,000,000** | Regla 1: Elite PLUS automático |
| `revpar_premium` | $250,000 | **$180,000** | Regla 2: Elite (Inclusión Eje Cafetero) |
| `brecha_conversion_critica` | $3,000,000 | **$2,500,000** | Regla 3: Pro AEO Plus |
| `web_score_alto` | 75 | 75 | Discrimina Pro AEO vs Plus |
| `cac_maximo_cop` | $800,000 | **$1,000,000** | Tolerancia de adquisición |

---

## 9. Protocolo de Sincronización

1.  Validar narrativa en este documento.
2.  **REPLICAR VALORES EN `data/benchmarks/plan_maestro_data.json`**.
3.  Ejecutar `python scripts/test_v23_integration.py` (Actualizar tests para nuevos umbrales).

---
**Generado**: 2026-02-14  
**Motor**: DecisionEngine v2.5.0 (Ajuste por Inflación Laboral)  
**Firma**: IAH · Hospitalidad 4.0
