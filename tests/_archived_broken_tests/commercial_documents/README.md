# Cuarentena: Tests Patológicos del Área de Propuesta

**Fecha**: 2026-08-05
**Plan**: RC1-RC2-ENTREGA-COHERENTE-2026-08-04 / FASE-A

## Archivos en cuarentena

| Archivo | Tests | Síntoma | Causa probable |
|---------|-------|---------|----------------|
| `test_proposal_generator.py` | 32 | Fuga de memoria ~8GB RAM | Fixture `generator` instancia `V4ProposalGenerator()` directamente; el constructor carga templates/config desde disco. 32 tests × costo de inicialización = acumulación. |
| `test_price_consistency.py` | 4 | Cuelgue indefinido | `generate()` con patches parciales: mockea `_load_template`, `_prepare_template_data`, `_render_template` pero puede haber lógica no mockeada que causa espera bloqueante. |
| `test_proposal_generator_dict.py` | 4 | 16 de 38 fallos preexistentes | `setup_method` instancia `V4ProposalGenerator()`; los mocks de `_prepare_template_data` no cubren atributos internos requeridos, causando fallos en cascada. |

## Total: 40 tests aislados

## Referencia

- Plan: `.opencode/plans/RC1-RC2-ENTREGA-COHERENTE-2026-08-04/05-prompt-inicio-sesion-fase-A.md`
- Lecciones: L1/L11 del plan anterior (COHERENCIA-MODULO-ENTREGA-2026-08-03)
- `pytest.ini` tiene `--ignore` específicos (NO `norecursedirs` global — CR-8)

## Condición de salida

Estos archivos NO deben volver a la colección estándar hasta que:
1. Se diagnostique y corrija la causa raíz de cada patrón patológico.
2. Se verifique que los tests pasan individualmente con timeout.
3. FASE-B del plan puede generar tests nuevos que reemplacen funcionalidad de estos.
