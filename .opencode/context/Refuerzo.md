# Refuerzo de iah-cli: diagnóstico defendible e implementación verificable

> **Revisión:** 2026-09-21, ampliada con la evaluación de implementación en sitio.
> **Propósito:** priorizar mejoras que aumenten la precisión, defensibilidad, reproducibilidad y viabilidad comercial del diagnóstico y su implementación gestionada.
> **Marco rector:** `ROADMAP.md`, especialmente §1, P3/P6/P7, §5, T5, §7.5, §8, §9 y §10. Este documento lo complementa; no redefine el producto ni autoriza implementaciones, gastos, envíos o despliegues.

## 1. Qué se busca reforzar

**El producto es el diagnóstico sobre la fuga de reservas directas, con evidencia, precisión declarada y acciones consecuentes. Los agentes, frameworks y automatizaciones son medios de producción, no el producto.**

Esto no significa terminar el servicio entregando archivos para que el hotel los instale. El roadmap contempla implementación SEO/AEO/GEO y deploy con aprobación (`ROADMAP.md` §5 y §8, Producto 2). La propuesta de TAREA7 promete «nosotros implementamos todo»: si el trabajo se limita a entregar una carpeta, queda una diferencia entre la promesa y el servicio ejecutado.

**Modelo recomendado:** implementación gestionada por el operador de iah-cli, asistida y progresivamente automatizada. El hotel aporta datos, accesos delegados y aprobaciones; no tiene que ejecutar las tareas técnicas. El riesgo comercial señalado por el operador es que delegar la instalación al hotel derive en errores o inacción, insatisfacción y falta de resultados; no se ha medido aquí su frecuencia ni su impacto en conversiones.

El refuerzo debe permitir responder mejor:

1. ¿La cifra es plausible para este hotel y qué incertidumbre conserva?
2. ¿Cada hallazgo tiene evidencia y una acción justificada?
3. ¿Lo prometido corresponde a los assets realmente entregables?
4. ¿Puede identificarse el resultado final de una ejecución sin reconstruirlo manualmente?
5. ¿Puede repetirse el proceso sin mezclar hoteles, duplicar efectos ni perder trazabilidad?
6. ¿El coste y el tiempo del diagnóstico, instalación y revisión permiten sostener el servicio?
7. ¿Los cambios autorizados quedaron instalados y comprobados en el sitio correcto, sin dañar trabajo ajeno?

No se incorpora una tecnología porque aparezca en una vacante, facilite una entrevista o amplíe el catálogo de capacidades. La formación personal puede continuar fuera de este alcance, sin convertirse en una obligación arquitectónica de iah-cli.

## 2. Punto de partida: capacidades reales y límites

El repositorio dispone de auditoría, validación cruzada, escenarios financieros, generación documental, revisores, Juez determinista y controles sobre la entrega. Son capacidades que deben aprovecharse, no reemplazarse por defecto.

| Observación verificada en la evaluación | Implicación para el refuerzo | Fuente |
|---|---|---|
| `v4complete` se ejecuta principalmente desde `main.py`; usa el harness, pero no delega en él todo el flujo | Trabajar sobre el recorrido efectivo, no asumir que migrar `modules/orchestration_v4/two_phase_flow.py` migra el producto | `main.py:1462`, `main.py:1663`, `main.py:1757` |
| La recuperación del harness aplica estrategias acotadas de reintento, ajuste y escalamiento | Conservar límites explícitos; no describirla como reparación autónoma general | `agent_harness/self_healer.py:331` |
| Los revisores combinan comprobaciones deterministas y extracción LLM compartida | El LLM propone; el Juez decide. La revisión reduce riesgos dentro de su cobertura, no garantiza ausencia de errores | `main.py:3361`, `ROADMAP.md` §7.2 |
| Una corrida histórica terminó con gates preliminares aprobados, Tribunal bloqueante, ZIP suprimido y `EXIT=0` | Separar éxito del proceso, aprobación y disponibilidad del entregable | `evidence/tarea7-corrida.log:277`, `evidence/tarea7-corrida.log:318`, `evidence/tarea7-corrida.log:323`, `evidence/tarea7-corrida.log:370` |
| El bloqueo de esa corrida tiene una corrección posterior demostrada offline | No reutilizar el fallo histórico como prueba de que sigue ocurriendo en una ejecución nueva | `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-0/resultados-y-observaciones.md:44` |
| `hook-pdf` produce un gancho a partir de documentos existentes; no genera la propuesta comercial | Tratarlo como instrumento de prospección, distinto del paquete certificado | `main.py:1555`, `ROADMAP.md` §8 |
| El manifiesto de dependencias contiene una ruta editable local y paquetes exclusivos de Windows | Preparar reproducibilidad antes de prometer portabilidad o despliegue en Linux | `requirements.txt:131`, `requirements.txt:244` |

**Vigencia:** estas referencias son el corte de la evaluación, no un estado sincronizado. El ROADMAP v4.2 (2026-09-02) describía al Tribunal como inexistente; la versión v4.3 (2026-09-21) ya lo documenta como operativo con enforcement observado, y en caso de divergencia manda el roadmap actualizado y el código. Sus principios estratégicos orientan la selección; sus afirmaciones operativas se contrastan con código y evidencia reciente. Aquí no se declara G0 abierto ni cerrado, ni se presume cumplida la validación comercial.

### 2.1 TAREA7: conservar fuentes no equivale a tener una entrega aprobada

Inspección local del 2026-09-21 sobre `output/TAREA7-2026-09-19/v4_complete/`:

- `deliveries/` está vacío: **0 archivos**. La evidencia del ZIP suprimido está en el acta, fuera de esa carpeta.
- `hotel_don_alfonso/` conserva **55 archivos**, incluidos assets, guías, metadatos y reportes internos; no son 55 componentes instalables.
- El acta registra **52 entradas históricas** del ZIP suprimido. No son archivos adicionales disponibles ni permiten reconstruir sus bytes: `output/TAREA7-2026-09-19/v4_complete/hotel_don_alfonso/v4_audit/acta_revision.json:92`.
- Hay **11 sidecars de metadatos**: diez declaran `can_use:false` y los once `preflight_status:WARNING`. No se puede considerar el conjunto listo para producción por tener nombres sin prefijo ESTIMATED o confianza numérica alta.
- El llms principal conserva `PENDING_ONBOARDING` y un enlace de inicio vacío. Las FAQ son JSON, no una página terminada. Las variantes de schema/FAQ requieren conciliación, no instalación conjunta automática.
- El reporte identifica WordPress con confianza estimada; no confirma el CMS actual, plugins, hosting ni permisos: `output/TAREA7-2026-09-19/v4_complete/hotel_don_alfonso/v4_audit/audit_report_20260919_150111.json:198`.

Fuentes concretas del contenido pendiente: `output/TAREA7-2026-09-19/v4_complete/hotel_don_alfonso/llms_txt/llms_20260919_150131.txt:3` y `output/TAREA7-2026-09-19/v4_complete/hotel_don_alfonso/llms_txt/llms_20260919_150131_metadata.json:11`. Promesa de implementación: `output/TAREA7-2026-09-19/v4_complete/02_PROPUESTA_COMERCIAL_20260919_150131.md:42`.

Reproducción de los conteos actuales, desde la raíz, sin ejecutar el pipeline:

```bash
python -B - <<'PY'
from pathlib import Path
import json
base = Path('output/TAREA7-2026-09-19/v4_complete')
assets = base / 'hotel_don_alfonso'
metadata = [json.loads(p.read_text(encoding='utf-8')) for p in assets.rglob('*_metadata.json')]
print('deliveries:', sum(p.is_file() for p in (base / 'deliveries').rglob('*')))
print('hotel_don_alfonso:', sum(p.is_file() for p in assets.rglob('*')))
print('metadata:', len(metadata))
print('can_use=false:', sum(m.get('can_use') is False for m in metadata))
print('WARNING:', sum(m.get('preflight_status') == 'WARNING' for m in metadata))
PY
```

El bloqueo histórico fue `VACUOUS_RECALL`; su corrección posterior pasó a aprobación condicional en un contrafactual offline. **No volvió a aprobar estos archivos ni acreditó su instalación.** Preparar el contenido, autorizar el paquete e instalarlo son controles distintos. Los archivos bloqueados sirven como evidencia o material de prueba aislado, nunca como atajo para desplegar evitando al Tribunal.

### 2.2 Despliegue disponible frente a instalación requerida

| Componente | Capacidad observada en código | Límite para implementación gestionada |
|---|---|---|
| WordPress REST | Autenticación y creación de posts; el CLI solicita borradores | No es instalación integral de los assets v4; upload e inyección de código devuelven fallo explícito |
| FTP | Comprueba que los campos de credenciales no estén vacíos | No realiza conexión ni subida; no debe reportarse como acceso remoto probado |
| Plan de deploy | Contempla cuatro nombres legacy para botón, barra, schema y artículo | No constituye un adaptador general para los nombres y tipos de TAREA7 ni planifica archivos raíz, FAQ o páginas |
| Autorización de deploy | Localiza archivos y ejecuta acciones con credenciales | No exige acta aprobatoria ni coincidencia del hash del paquete; tampoco contiene el ciclo completo de respaldo, idempotencia, reversión y verificación remota |
| Tests de ejecución | Usan `FakeConnector` para comprobar llamadas | No demuestran instalación en un sitio real; no se ejecutaron durante esta evaluación |

Fuentes: `modules/deployer/connectors/wordpress_connector.py:88`, `modules/deployer/connectors/wordpress_connector.py:123`, `modules/deployer/connectors/ftp_connector.py:47`, `modules/deployer/manager.py:82`, `modules/deployer/manager.py:381` y `tests/test_deploy_execute_actions.py:13`.

**Señal que no debe confundirse con aceptación:** `site_verification_applied` se produce como `len(self.skipped_assets) > 0` en `modules/asset_generation/v4_asset_orchestrator.py:168`. Indica omisión de assets durante generación, no que nuestros cambios se hayan instalado. No sirve como comprobante de deploy, ni la detección de presencia previa sustituye una observación posterior fresca.

## 3. Prioridades que sí aportan al repositorio

### 3.1 Precisión del diagnóstico y calidad del onboarding

**Aporte:** reducir el riesgo de producir una cifra internamente coherente pero poco plausible para el hotel. Alineación: P7 y D-10 del roadmap.

Trabajo pertinente:

- Verificar cómo se capturan, validan y conservan los datos operativos del hotel, incluida su procedencia, fecha y confianza.
- Comprobar que el render respeta el nivel de evidencia: rango y descargo cuando no corresponde presentar una cifra exacta.
- Aprovechar o completar el contraste entre la estimación previa y el recálculo con datos de onboarding, sin duplicar una capacidad que ya exista.
- Registrar inputs, versión del cálculo, resultados y explicación de la diferencia; distinguir el cambio de datos del cambio de modelo.
- Mantener separada la comprobación de plausibilidad de la coherencia entre documentos.

**Evidencia de cierre:** un caso reproducible antes/después del onboarding, con fuentes identificadas y diferencias explicables, además de pruebas de datos faltantes, contradictorios y valores extremos. Si no hay datos operativos autorizados, pueden verificarse contratos offline, pero no declararse validación real del hotel.

**Límite:** un cálculo con mejores inputs no equivale a observar la pérdida económica real ni demuestra causalmente un ROI. El contraste mide sensibilidad y consistencia del diagnóstico; los resultados comerciales requieren medición posterior independiente.

### 3.2 Resultado final de entrega inequívoco

**Aporte:** impedir que una integración confunda «el comando terminó» con «se puede entregar al cliente». Alineación: P6, G0 y G11.

Trabajo pertinente:

- Identificar conjuntamente el resultado de gates, QA, veredicto final, enforcement, acciones correctivas y paquete correspondiente a la ejecución.
- Distinguir aprobación plena, aprobación condicional, bloqueo, fallo técnico y ausencia de entregable.
- Vincular el paquete publicado con su ruta, hash y ejecución; no seleccionar simplemente el ZIP más reciente.
- Preservar la decisión determinista existente, sin crear otro Juez ni reimplementar gates en una integración externa.
- Verificar que la política de envío no se satisface únicamente por código de salida cero, readiness preliminar o existencia de un archivo.

**Evidencia de cierre:** casos controlados de aprobación, condición pendiente, bloqueo, error del Tribunal y fallo de empaquetado; cada uno produce una decisión final interpretable y ninguna entrega externa indebida.

**Cautela actual:** `main.py:3456` conserva una rama que intenta publicar la cuarentena cuando falla el enriquecimiento del Tribunal. La existencia de un ZIP no prueba por sí misma aprobación. Cualquier automatización de entrega exige resolver o controlar explícitamente esa situación bajo el contrato autorizado; este documento no modifica dicha política.

### 3.3 Implementación gestionada y verificada en sitio

**Aporte prioritario:** cerrar el paso entre assets preparados y cambios efectivos en la web, sin trasladar al hotel la ejecución técnica. Alineación: T5, D-09 y Producto 2 del roadmap. No es crear una plataforma horizontal ni eliminar la revisión humana.

**Dictamen:** parcialmente automatizable, con alto potencial en tareas mecánicas sobre un CMS confirmado. La recomendación es instalación asistida y progresivamente automatizada bajo responsabilidad del operador, no un agente universal que modifique cualquier sitio. No se cuantifica un porcentaje de automatización ni un ahorro sin medir un piloto real.

| Trabajo | Automatización posible, no capacidad actual acreditada | Condición |
|---|---|---|
| Publicar llms.txt | Transferencia y comprobación automatizables | Contenido completo, rutas válidas y acceso seguro a la raíz |
| Integrar schema y Open Graph | Automatizable tras adaptar al CMS | Fuente canónica, datos confirmados y conciliación con plugins/metadatos existentes |
| FAQ y contenido local | Borradores y publicación programables | Contenido visible aprobado, plantilla, URLs e identificadores estables; un JSON no es la página |
| robots.txt | Edición asistida y verificable | Fusionar reglas existentes; no sobrescribir restricciones o sitemap ciegamente |
| GA4/GTM y eventos | Automatización parcial | Cuentas, permisos, consentimiento y comprobación de eventos; no confundir falta de acceso con ausencia en el sitio |
| GBP, fotos y reseñas | Gestión asistida/programable según acceso | Roles autorizados, contenido y decisiones comerciales |
| Comprobación posterior | Automatizable para criterios concretos | Lectura fresca, contenido esperado, renderizado y pruebas funcionales |
| Políticas y datos del hotel | Captura y validación asistidas | Confirmación del responsable; no inferirlos para completar una plantilla |

**Dos controles, sin duplicar el Tribunal:**

1. **Calidad del paquete:** el Tribunal conserva la decisión sobre los artefactos y su evidencia.
2. **Aceptación de la instalación:** un verificador comprueba que los cambios autorizados quedaron correctamente aplicados en el sitio y entorno indicados. No necesita otro Juez LLM.

```text
Paquete con aprobación exigida y datos confirmados
→ plan de cambios para dominio, entorno y assets identificados
→ respaldo y prueba en staging
→ aprobación vinculada al plan y sus hashes
→ instalación controlada
→ comprobación fresca del sitio publicado
→ evidencia y aceptación
```

El deploy conserva el requisito de `APROBADO-PARA-ENTREGA` del roadmap (§5, tabla de contrato de producto), además de aprobación del cambio externo. Un veredicto condicional, un ZIP existente o los archivos fuente no sustituyen ese requisito. Diseñar y probar contratos offline no requiere desplegar el paquete histórico ni alterar sus evidencias.

Trabajo pertinente:

- Reutilizar el deployer donde sea adecuado y completar primero un conector específico; mapear assets v4 a operaciones reales, no renombrarlos para hacer pasar el plan legacy.
- Vincular hotel, dominio, entorno, paquete y hashes; comprobar que el sitio no cambió desde la aprobación antes de escribir.
- Usar accesos delegados de alcance mínimo y transporte cifrado. No persistir secretos en actas, logs o paquetes.
- Mantener un registro de objetos gestionados para actualizar en lugar de duplicar; separar contenido propio de código y configuración ajenos.
- Respaldar el estado previo y definir reversión selectiva. Ante fallos, detener acciones dependientes y recuperar lo gestionado cuando sea seguro; no borrar todo el header/footer.
- Verificar contenido remoto, JSON-LD, ausencia de duplicidades y comportamiento móvil/eventos cuando apliquen. Un HTTP 200 o la presencia previa no bastan.

**Piloto recomendado, sujeto a autorización propia:** un WordPress confirmado, un staging y pocos cambios vinculados a brechas reales, con contenido validado. Probar instalación, reejecución sin duplicados, interrupción, reversión y preservación del trabajo ajeno; después verificar los cambios autorizados en producción. No soportar varios CMS a la vez.

**Herramientas:** la primera necesidad son conectores ejecutores y comprobaciones HTTP/de navegador. Entre las tecnologías evaluadas, **n8n es la candidata para coordinar** accesos pendientes, aprobaciones, ejecución, incidencias y seguimiento; no sustituye conectores, no certifica éxito y no es requisito del primer piloto. FastAPI solo se justifica si hace falta una interfaz controlada al ejecutor; Docker sirve a la reproducibilidad, no a resolver la instalación en el CMS. LangGraph, RAG y voz no resuelven esta brecha y permanecen fuera del alcance.

**Evidencia de cierre:** cambios identificados, aprobados, instalados y verificados con registro antes/después; reejecución y reversión probadas; tiempo humano y coste total medidos. No se da por cerrada la instalación por tener un acta del paquete ni por pasar tests con conectores falsos.

**Contrato comercial:** separar diagnóstico, implementación con alcance definido y seguimiento. Delimitar accesos, tareas, exclusiones y aceptación en lugar de prometer «implementamos todo» sin límites. El hotel valida información y permisos; el operador asume la ejecución técnica. No prometer reservas, posicionamiento o ROI por haber instalado assets.

**Generado ≠ aprobado ≠ instalado ≠ verificado ≠ resultado comercial observado.**

### 3.4 Trazabilidad por ejecución y recuperación segura

**Aporte:** reducir reconstrucción manual, mezcla de evidencias y repetición accidental de operaciones. Alineación: P1/P3 y objetivos B-05/B-06 del roadmap.

Trabajo pertinente:

- Identificar cada ejecución y asociar inputs, hotel, artefactos, versiones, estados y errores.
- Resolver los artefactos por pertenencia a la ejecución, no únicamente por timestamp o nombre reciente.
- Aislar salidas y revisar también memoria, índices y cachés compartidos: un directorio de output distinto no demuestra aislamiento completo.
- Definir qué operación puede repetirse, cuál requiere comprobación previa y cuál necesita decisión humana.
- Mantener ejecución serial mientras no esté demostrada la seguridad de la concurrencia; no añadir workers solo para aumentar throughput.

**Evidencia de cierre:** una interrupción controlada deja estado suficiente para continuar de forma segura; una repetición no mezcla hoteles ni duplica efectos externos. Si un tramo no es reanudable, el sistema lo declara en lugar de prometer recuperación exacta.

**Límite:** el historial JSON del harness no equivale a un checkpoint completo del pipeline. La persistencia de un framework tampoco vuelve idempotentes las operaciones existentes.

### 3.5 Entorno reproducible y coste observable

**Aporte:** poder operar y mantener el mismo producto sin depender de particularidades no declaradas de una máquina. Alineación: reproducibilidad y G5.

Trabajo pertinente:

- Definir el intérprete y las dependencias realmente necesarios para el recorrido de producción.
- Resolver dependencias a rutas locales y requisitos específicos de plataforma antes de intentar una instalación portable.
- Preservar los pins de seguridad; no degradarlos para hacer coincidir un entorno derivado.
- Probar instalación y ejecución controlada en un entorno limpio, sin trasladar secretos ni outputs de clientes.
- Medir duración integral, consumo de proveedores, reintentos y tiempo humano de preparación, instalación, verificación y retrabajo. Las tarifas teóricas o estimaciones del permission gate no sustituyen el coste observado.

**Evidencia de cierre:** el caso de referencia se reproduce en el entorno declarado y deja métricas con unidad, alcance y fuente. Los consumos no medidos se declaran como tales, no como cero. El margen del servicio incluye trabajo técnico y soporte, no solo coste de generación del diagnóstico.

Docker o CI/CD pueden instrumentar este objetivo cuando exista una necesidad operativa concreta; no son entregables obligatorios por prestigio tecnológico ni equivalen por sí solos a un servicio empresarial.

### 3.6 Prospección asistida, separada de la entrega certificada

**Aporte:** utilizar el diagnóstico para abrir conversaciones comerciales sin convertir iah-cli en una plataforma. Alineación: §7.5 y §8 del roadmap.

| Operación | Condición de uso |
|---|---|
| Preparar gancho y mensaje personalizado | URL propia validada, evidencia defendible, rango si corresponde, coste controlado y revisión humana antes del envío |
| Prospectar con `hook-pdf` | No requiere acta de entrega certificada; no se presenta como diagnóstico final aprobado |
| Entregar el producto certificado | Requiere el contrato de entrega, acta final, condiciones de evidencia satisfechas y decisión comercial correspondiente |
| Implementación gestionada en sitio | Es una operación distinta del envío; requiere la aprobación de paquete y cambio, accesos y comprobación posterior definidos en §3.3 |
| Automatizar entrega o deploy por WhatsApp | Fuera de este refuerzo, conforme a la exclusión expresa del roadmap |

La exclusión por WhatsApp no prohíbe el deploy técnico supervisado que contempla T5. n8n puede coordinar tanto la prospección como el proceso de implementación de §3.3, si resuelve una repetición observada con menor coste total; no autoriza por sí mismo ninguna operación externa. No se prescribe convertir el CLI en una API pública ni montar colas distribuidas.

Antes de conectar un servicio externo: definir autorización, límites de consumo, validación de entradas, privacidad, identidad de ejecución y prevención de duplicados. Probar primero con entrega simulada; no convertir la existencia de un workflow en permiso para enviar.

**Evidencia de cierre:** una solicitud puede rastrearse hasta su resultado; los duplicados no provocan envíos repetidos; el gancho no se confunde con una entrega certificada. El valor comercial se mide con conversaciones, pagos, implementaciones aceptadas y debriefs, no por cantidad de automatizaciones.

## 4. Qué queda excluido de este refuerzo

| Propuesta original | Motivo de exclusión |
|---|---|
| Migración del pipeline o Tribunal a LangGraph/LangChain | No se demostró una mejora frente a los componentes actuales; añade coste de migración y riesgo sobre contratos ya implementados |
| RAG normativo y bases vectoriales como nueva capa de producto | No hay un problema medido de precisión del diagnóstico que justifique esa solución; recuperar texto tampoco garantiza vigencia, aplicabilidad ni corrección jurídica |
| Recepción virtual, Twilio, ElevenLabs y reservas por voz | Constituyen otra operación de producto, con datos transaccionales, latencia, privacidad y disponibilidad distintos de la auditoría hotelera |
| Integración PMS, SaaS multiusuario, dashboard y plataforma horizontal | Exceden el foco actual y las exclusiones del roadmap |
| Entrega automática de PDFs al terminar el CLI | Código de salida, readiness preliminar y existencia de artefactos no certifican la autorización final |
| Formación por frameworks, guiones de entrevista y promesas laborales | No son resultados del repositorio ni justifican modificar su arquitectura |
| Promesas de eliminar alucinaciones, asegurar corrección legal o demostrar ROI mediante escenarios | Exceden la evidencia y la cobertura de los controles existentes |

Estas exclusiones no son una lista de fases futuras comprometidas. Reabrir alguna exige un problema concreto del producto, beneficio medido frente a una alternativa más simple, coste de operación y decisión explícita compatible con el roadmap.

El horizonte de benchmarks y aprendizaje agregado de `ROADMAP.md` §14, H3 continúa sujeto a sus disparadores y permisos; no se transforma aquí en un proyecto de RAG ni se presume cumplido.

## 5. Orden de trabajo y criterio de adopción

1. **Revalidar el punto de partida:** localizar qué parte ya está implementada o en un plan activo y qué evidencia falta. No convertir pendientes antiguos del roadmap en nuevos desarrollos por defecto.
2. **Preparar contenido defendible y aprobación inequívoca:** corregir las brechas confirmadas de precisión, datos pendientes y contrato de entrega. No instalar fuentes bloqueadas ni confundir un fix offline con aprobación nueva.
3. **Cerrar la última milla con un piloto acotado:** confirmar un CMS y accesos autorizados, completar las operaciones necesarias para pocos cambios reales y demostrar instalación, reejecución, reversión y comprobación. No posponer toda implementación a una futura plataforma ni ampliar a varios CMS antes de medir el primero.
4. **Reforzar trazabilidad y reproducibilidad donde impidan comprobar lo anterior:** mantener núcleo y contratos existentes. Evaluar n8n después de definir y probar el circuito del ejecutor; adoptarlo solo si reduce coordinación o errores medibles.
5. **Mantener prospección asistida en paralelo:** no exigir el cierre de todas las mejoras técnicas para preparar un gancho válido; sí conservar sus límites comerciales y de revisión.
6. **Escalar solo con evidencia:** comprobar en las fuentes vigentes los disparadores de calidad, coste y validación comercial de `ROADMAP.md` §9 y §10. No inferir que están cumplidos por tener tests verdes, un paquete generado o un POST exitoso.

Para aceptar una mejora deben quedar definidos:

- Problema observado y artefacto que lo demuestra.
- Comportamiento actual, alternativa mínima y beneficio esperado.
- Prueba antes/después que preserve los contratos existentes.
- Coste operativo, riesgos y responsable de la decisión.
- Para cambios en sitio: permisos, alcance, aprobación, recuperación y evidencia de aceptación.
- Criterio de aceptación verificable y límite de lo que no se ha medido.

No se fija un plazo de 8–12 semanas sin alcance, disponibilidad y presupuesto. Tampoco se abren planes paralelos que dupliquen trabajo: cada brecha confirmada debe incorporarse al plan que ya la gobierne o recibir un alcance específico autorizado. La preparación de assets y evidencia del plan `REFACTOR-WHATSAPP-ENTREGA-2026-09-18` no equivale a implementar deploy; su maestro excluye esa operación de su corrida (`.opencode/plans/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/01-plan-maestro.md:151`). Este contexto no amplía ese alcance silenciosamente.

## 6. Resultado esperado y límites de esta revisión

El refuerzo es útil si iah-cli produce diagnósticos más plausibles y permite convertir las acciones contratadas en cambios instalados y verificados, con menos ambigüedad operativa y coste conocido. No basta con entregar archivos ni corresponde ampliar el catálogo tecnológico sin ese beneficio.

Esta revisión es documental, basada en lectura de código, inspección de entornos, inventario local y evidencia histórica. No ejecuta una nueva auditoría hotelera ni un despliegue, no acredita accesos o instalación real, no certifica precisión económica o ahorro y no verifica pagos o disparadores comerciales. No modifica el roadmap, el pipeline ni las políticas de entrega.

**Decisión de enfoque: diagnóstico defendible más implementación gestionada y verificable; automatizar tareas concretas, no prometer autonomía universal.**
