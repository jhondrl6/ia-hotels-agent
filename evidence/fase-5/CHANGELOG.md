# Changelog - IA Hoteles Agent

Todos los cambios notables de este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [4.5.3] - 2026-03-15

### 🎯 Objetivo
Adoptar enfoque de comunicación del diagnóstico antiguo (25/feb) sin perder validaciones técnicas de v4.5.2

### 🔧 Cambios Implementados

**Estructura de Diagnóstico Restaurada:**
- Narrativa "Antes/Ahora" que crea urgencia (PARTE 1)
- Comparativa regional: Su Hotel vs Promedio (PARTE 2)
- Las 4 Razones con costos específicos (PARTE 3)
- Quick Wins con timings concretos (PARTE 5)
- Plan 7/30/60/90 días (PARTE 6)
- Anexo Técnico con validaciones al final

**Estructura de Propuesta Restaurada:**
- Resumen Ejecutivo con pérdida mensual
- Proyección financiera mes a mes (6 meses)
- Plan 7/30/60/90 días detallado
- Garantías específicas (3 garantías)
- Mapeo problemas→soluciones→assets visible

**Assets Conectados:**
- Metadata de conexión: problem_solved, impact_cop, priority, timing
- README.md en cada folder de asset con justificación de ventas

### 📁 Archivos Modificados

| Archivo | Cambio |
|---------|--------|
| templates/diagnostico_v4_template.md | Estructura de ventas completa |
| templates/propuesta_v4_template.md | Estructura de ventas completa |
| asset_diagnostic_linker.py | Metadata de conexión |
| v4_proposal_generator.py | Variables de proyección mensual |

### Métricas

| Métrica | Valor |
|---------|-------|
| Tests | 1434+ passing |
| Coherence | ≥ 0.8 |
| Desconexiones | 0 |
| Hard contradictions | 0 |

## [4.5.2] - 2026-03-13

### 🎯 Objetivo

Completar FASE-5: Validación de coherencia y preparación para publicación.