# Precios y Paquetes - IA Hoteles Agent

## Version 4.72.0 - Actualizado agosto 2026

> **Fuente unica de pricing:** `config/pricing.yaml` (FASE-P0-A del plan CREDIBILIDAD-NUMERICA-2026-08-20).
> Los valores en este documento se derivan de esa configuracion. Si hay discrepancia,
> `config/pricing.yaml` siempre tiene precedencia.

### Tiers de Pricing (desde config/pricing.yaml)

| Tier | % de fuga capturada | Precio min (COP) | Precio max (COP) | Descripcion |
|------|---------------------|-------------------|-------------------|-------------|
| Boutique | 3.5% | $800.000 | $2.500.000 | Hoteles boutique y pequenos (10-25 hab) |
| Standard | 2.5% | $1.800.000 | $3.800.000 | Hoteles estandar y medianos (26-60 hab) |
| Large | 2.0% | $3.500.000 | $7.500.000 | Hoteles grandes (60+ hab) |

**Gates de ratio precio/perdida:** min 3x, max 6x, ideal 4.5x.

### Paquetes Comerciales

| Paquete | Fee mensual (COP) | Setup unico (COP) | Diagnostico | Quick Wins |
|---------|-------------------|--------------------|-------------|-------------|
| Express | $120.000 | -- | Diagnostico express (5 pag, 72h) | 0 (diagnostico puro) |
| Starter | Segun tier | Segun tier | Diagnostico v4complete | 1 quick win |
| Professional | Segun tier | Segun tier | Diagnostico v4complete + competencia | 3 quick wins |
| Enterprise | Segun tier | Segun tier | Diagnostico avanzado + contenido IA | 5 quick wins |

> El fee mensual y el setup se calculan dinamicamente por el motor financiero
> (`modules/financial_engine/`) segun el tier del hotel, la fuga estimada y los
> gates de ratio. Los valores de referencia en `config/pricing.yaml`:
> `monthly_default: $1.200.000 COP`, `setup_fee_default: $2.500.000 COP`,
> `floor_price: $1.200.000 COP`, `express_price: $120.000 COP`.

### Desglose de Servicios

#### Express ($120.000 COP)
- Diagnostico v4complete con datos reales del hotel (Tier A)
- PDF de 5 paginas con fuga exacta, 3 escenarios, top 5 acciones
- Entrega en 72 horas
- Garantia: si la fuga es menor al precio del Express, se informa y termina

#### Starter
- Analisis de brechas (web, GBP, redes sociales)
- Diagnostico v4complete con coherencia minima
- 1 quick win implementado (boton WhatsApp, FAQ basica o schema simple)
- Reporte ejecutivo mensual

#### Professional
- Todo lo del Starter mas:
- Analisis de competencia local (top 3)
- 3 quick wins implementados
- Schema avanzado (Hotel, Organization, FAQ)
- Optimizacion de GBP

#### Enterprise
- Todo lo del Professional mas:
- Analisis de mercado completo
- 5 quick wins implementados (incluye assets premium)
- Schema completo (Review, Video, Event)
- Campana de contenido IA (3 publicaciones/mes)
- Dashboard en tiempo real

### Politica de Precios

1. **Facturacion**: Mensual adelantado
2. **Contrato**: Minimo 3 meses, renovacion automatica
3. **Descuentos**:
   - Pago anual: 10% de descuento
   - Multiples propiedades (2+ hoteles): 15% adicional
   - Hoteles boutique (<50 habitaciones): 5% adicional
4. **Implementacion**: Tarifa unica de setup (ver `setup_fee_default` en pricing.yaml)
5. **Cancelacion**: Con 30 dias de anticipacion

### Politica de Coherencia de Pricing

> **Regla (FASE-P0-A):** Toda cifra de pricing en documentos comerciales, propuestas,
> PDFs ganchos y output del sistema DEBE provenir de `config/pricing.yaml` o ser
> calculada por `modules/financial_engine/` consumiendo esa fuente. Nunca hardcodear
> cifras divergentes.
>
> Los benchmarks regionales (ADR, occupancy) se obtienen de
> `data/benchmarks/regional_adr_2026.json` (master, FASE-P1-A).

### Contacto Comercial

**Ventas Latinoamerica**: ventas@iah-cli.com  
**Soporte Tecnico**: soporte@iah-cli.com

### Historial de Cambios

| Version | Fecha | Cambios |
|---------|-------|----------|
| 4.72.0 | 21/08/2026 | Unificacion con config/pricing.yaml (FASE-P0-A). Eliminados precios USD desconectados |
| 2.6.2 | 17/03/2026 | Actualizacion de precios post-analisis de mercado Q1 2026 |
| 2.6.1 | 01/02/2026 | Anadido paquete Elite Plus |
| 2.6.0 | 15/01/2026 | Reestructuracion completa de paquetes |