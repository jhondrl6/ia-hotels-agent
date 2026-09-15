# FASE-P6: Generación y validación multi-hotel

**ID**: TRIBUNAL-ENFORCEMENT-OBS-2026-09-11 / FASE-P6
**Objetivo**: Corregir el **productor** de los defectos que FASE-P4 observó (F-P4.1 stub de `IMPLEMENTATION_ORDER.md`, F-P4.3 fallback de onboarding sin WhatsApp, F-P4.7 identidad del ZIP suprimido, F-P4.9 matriz multi-hotel, F-P4.8/F-P4.2 causalidad), para que el tribunal decida correctamente **según la evidencia de cada hotel** — no para aprobar siempre. Funciona offline, sin exigir otra corrida real.
**Dependencias**: FASE-P5 ✅ (cierre técnico) + FASE-P4 ✅ (hallazgos con dueño). **No** requiere Tier A real ni GA4/GSC del hotel.
**Presupuesto**: **FUERA DE SERVICIO (R2.1, D-PRE.1/D-V2.1)** — sin calibración comparable; registrar medida real, unidad y corte al cerrar, sin inventar estimación.
**Complejidad técnica**: ALTA (cross-capas: main.py, contrato de assets, onboarding, tribunal/delivery)
**Modo de ejecución**: SESIÓN PRINCIPAL (sin comando largo; matriz con perfiles sintéticos/anonimizados)
**Skill**: `phased_project_executor.md` v2.24.0

---

## Contexto

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-P1…P4 | ✅ (ver `dependencias-fases.md`) |
| FASE-P5 | ✅ cierre técnico (puerta AC-S4 registrada) |
| FASE-P6 | ← ESTA FASE |
| RELEASE | pendiente, después de P6 |

### Lecciones capitalizadas aplicables a esta fase
(filtras de `00-lecciones-capitalizadas.md` §2 y §1.b — DA6/DA7/DA5/DA12 del retrieve)

| ID | Lección (una línea) | Qué cambia en ESTA fase |
|----|---------------------|-------------------------|
| DA6 / DA7 | Identidad del asset frente a catálogo estático | AC-G1: la orden se construye desde la ruta real del ZIP, no del nombre canónico exacto |
| DA5 | Configuración OPS separada del entorno | AC-G2: el cargador de onboarding no depende de un YAML ajeno |
| L-T4A.5 | Un test puede pasar sin ejecutar la rama que certifica | AC-G5: cada camino causal se cierra revirtiendo el fix (NR7), no simulando el veredicto |
| L-PF6 / L-PF10 | "Sin hallazgos" ≠ "no midió" | AC-G3: la huella del `.zip.tmp` se toma del objeto real leído por los revisores, no se afirma |

---

## Tareas (R3: 4 tareas, 0 comandos largos)

### Tarea 1: Instrucciones desde la entrega real (AC-G1)
- Revisar el paso de `Path(a.path).name` en `main.py`, `AssetResponsibilityContract.get_implementation_order` / `generate_delivery_template`, `ImplementationOrderGenerator` y `DeliveryPackager.write`: relacionar la identidad de cada asset con su **ruta real dentro del ZIP**, preservando fecha y prefijo `ESTIMATED_`.
- Los tipos fuera del catálogo de 6 nombres deben tener **disposición explícita**, nunca desaparecer en silencio.
- **No** rellenar la plantilla ni ampliar una whitelist de nombres por hotel.

### Tarea 2: Entrada de datos independiente del entorno (AC-G2)
- Corregir `_load_latest_onboarding_data` y su invocación FASE-D para resolver `observations.json` aunque falte `clientes/` o no haya YAML ajeno, tanto en output por defecto como alternativo.
- Rastrear WhatsApp fuente → `_observation_to_onboarding_format` → validación: propagar **solo** evidencia realmente disponible; ausencia de dato no se convierte en teléfono inventado, `verified` ni aprobación automática.

### Tarea 3: Identidad del paquete suprimido (AC-G3)
- Guardar `package_evidence.sha256` y `package_evidence.member_count` en el acta desde el `.zip.tmp` real leído por los revisores, **antes** de `suppress()`.
- Mantener la supresión y el contrato single-write; no conservar ni publicar el ZIP bloqueado. La huella identifica el objeto, no reconstruye su contenido.

### Tarea 4: Matriz multi-hotel y causalidad (AC-G4 / AC-G5)
- Reproducir al menos **tres perfiles offline** en entorno limpio: el caso Don Alfonso **sin datos sensibles** y dos perfiles sintéticos/anonimizados.
- Probar productor, ZIP real, revisores y Juez juntos en los **tres caminos separados**: gates permiten/revisores permiten; mismos gates permiten/revisor objeta → bloqueo; gates ya bloquean.
- Conservar NR1 y NR7. **No** escribir un acta a mano como sustituto del flujo ni debilitar los gates para obtener un ZIP.

**Criterios de aceptación**: los de `06-checklist-implementacion.md` §FASE-P6 (AC-G1…AC-G5) y `01-plan-maestro.md` §4 FASE-P6.

---

## Post-Ejecución (OBLIGATORIO)

1. `dependencias-fases.md`: P6 ✅ con fecha e iteraciones medidas (unidad + corte declarado).
2. `README.md`: tabla de progreso.
3. `09-documentacion-post-proyecto.md`: acumular (cambios en productor/contrato/onboarding; sin módulos nuevos salvo que aparezcan).
4. `10-analisis-post-implementacion.md`: fila + lecciones + métricas + límite de la matriz offline.
5. `00-lecciones-capitalizadas.md` §2: realidad contra promesa.
6. `evidence/FASE-P6/`: tres perfiles, los tres caminos causales, pares NR7.
7. `python scripts/build_lesson_index.py --check` (y regenerar el par `.md`+`.json` si vence).
8. `run_all_validations.py --quick`.

**NO esperar a la siguiente sesión.**

---

## Criterios de Completitud (CHECKLIST)

- [ ] AC-G1: orden de implementación derivado de la ruta real del ZIP; tipos fuera del catálogo con disposición explícita; sin relleno manual ni whitelist por hotel
- [ ] AC-G2: onboarding resuelve `observations.json` sin YAML ajeno; WhatsApp solo con evidencia real (sin `verified` inventado)
- [ ] AC-G3: `package_evidence.sha256` / `member_count` del `.zip.tmp` antes de `suppress()`; single-write intacto
- [ ] AC-G4: matriz reproducible con ≥3 perfiles offline
- [ ] AC-G5: los tres caminos causales probados con NR7 (incluido gates-permiten/revisor-objeta → bloqueo); NR1 conservado
- [ ] Iteraciones medidas y escritas (unidad + corte declarado — un `—` no cierra)
- [ ] `run_all_validations.py --quick` TOTAL PASS
- [ ] Post-ejecución completada (8 puntos)

**NO marcar la fase como completada si algún criterio falla.**

---

## Restricciones

- **NO** exigir ni autorizar una nueva corrida real de red: la matriz es offline con perfiles sintéticos/anonimizados; una corrida nueva requiere otra sesión con consentimiento/frescura/coste explícitos.
- **NO** tocar datos sensibles del cliente en los perfiles; el caso Don Alfonso entra anonimizado.
- **NO** modificar el detector (`_is_template_stub`) para hacerlo pasar, ni debilitar gates para producir un ZIP.
- Tier A real sigue pendiente de GA4/GSC del hotel; esta fase no lo certifica ni lo finge.
