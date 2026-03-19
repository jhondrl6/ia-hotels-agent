# 🐛 Errores Frecuentes — IA Hoteles Agent

> [!NOTE]
> **Propósito**: Catálogo de errores resueltos para resolución rápida.
> **Trigger**: El usuario dice "Documenta este error" después de resolver un problema.

---

## Índice de Errores

| ID | Error | Categoría | Estado |
|----|-------|-----------|--------|
| ERR-001 | `inject_code()` Plugin Required | Deployer | ✅ Documentado |
| ERR-002 | No LLM API Key Configured | LLM Provider | ✅ Documentado |
| ERR-003 | PRECIO_AUSENTE en Diagnóstico | Decision Engine | ✅ Documentado |
| ERR-004 | Código no se guarda en WPCode (sin error) | WordPress/WAF | ✅ Documentado |
| ERR-005 | Package 'unknown' en Guía de Entrega | Delivery | ✅ Documentado |
| ERR-006 | Bloqueo WAF Persistente (Divi Integration Falla) | WordPress/WAF | ✅ Documentado |

---

## Errores Documentados

### ERR-001: inject_code() Plugin Required

**Síntoma**:
```
WPCodeError: Plugin not installed on target site
```

**Causa Raíz**: El hotel no tiene el plugin WPCode instalado en WordPress.

**Solución**:
1. Usar vía asistida/manual en lugar de CLI automatizado
2. Ejecutar `/despliegue_asistido` (skill disponible)
3. Ver [GUIA_OPERATIVA_FREELANCER_VISPERAS.md](../docs/GUIA_OPERATIVA_FREELANCER_VISPERAS.md)

**Referencia**: Sesión 2025-12-17, [Plan Remoto.md](../docs/Plan%20Remoto.md)

---

### ERR-002: No LLM API Key Configured

**Síntoma**:
```
Error: No LLM API key configured
```

**Causa Raíz**: El archivo `.env` no está cargado o las variables `DEEPSEEK_API_KEY` / `ANTHROPIC_API_KEY` no existen.

**Solución**:
1. Ejecutar `/llm_env_rerun` (skill disponible)
2. O manualmente: verificar `.env` existe y contiene las claves

**Referencia**: Sesión 2025-12-15, [README.md#troubleshooting](../README.md#-troubleshooting)

---

### ERR-003: PRECIO_AUSENTE en Diagnóstico

**Síntoma**:
- Diagnóstico muestra fuga `PRECIO_AUSENTE`
- Valores de pérdida parecen inflados

**Causa Raíz**: Bug corregido en `report_builder_fixed.py` — el scraper no detectaba precio correctamente.

**Solución**:
1. Verificar que se usa `report_builder_fixed.py` (no versión antigua)
2. Re-ejecutar diagnóstico

**Referencia**: Sesión 2025-12-16, Auditoría Vísperas

---

### ERR-004: Código no se guarda en WPCode (sin mensaje de error)

**Síntoma**:
- Al guardar código HTML/JS en WPCode, aparece "Ajustes guardados"
- El código desaparece del editor al recargar la página
- No se muestra ningún mensaje de error explícito

**Causa Raíz**: Firewall WAF (mod_security) en servidor LiteSpeed bloqueando tags `<script>`, `<style>`, o caracteres no-ASCII (tildes, emojis).

**Solución**:
1. **Usar solo caracteres ASCII**: Eliminar tildes, emojis y símbolos especiales del código.
2. **Crear snippets PHP**: Envolver el HTML en un snippet PHP que ejecute vía hook `wp_footer`.
3. **Contactar hosting**: Solicitar desactivación temporal de mod_security (requiere acceso de administrador).
4. **Inyectar CSS vía Personalizador**: El "CSS adicional" de WordPress Customizer suele no ser bloqueado.

**Referencia**: Sesión 2025-12-25, Despliegue Concierge Hotel Vísperas

---

### ERR-005: Package 'unknown' en Guía de Entrega

**Síntoma**:
- El archivo `implementation_guide.md` generado muestra `Paquete: unknown` o metadatos vacíos.

**Causa Raíz**: Puntero a `self.current_package` no inicializado en el método `execute()` del `DeliveryManager`.

**Solución**:
1. Verificar que el código en `modules/delivery/manager.py` tiene la línea `self.current_package = package` al inicio del método `execute()`.
2. Re-ejecutar el comando de entrega (`audit` o similar).

**Referencia**: Sesión 2025-12-29, Refactorización v2.6.1

**Referencia**: Sesión 2025-12-29, Refactorización v2.6.1

---

### ERR-006: Bloqueo WAF Persistente (WPCode + Divi Integration Fallan)

**Síntoma**:
- WPCode no guarda el snippet (o lo guarda vacío).
- Divi > Integración: Guarda "exitosamente", pero el código no aparece en el frontend.
- Fallan incluso versiones "limpias" (solo texto/emojis) o imágenes simples.

**Causa Raíz**: Reglas WAF (ModSecurity) extremadamente agresivas en hostings compartidos sanitizan `POST` requests en `admin-ajax.php` y `options.php`, eliminando silenciosamente cualquier etiqueta HTML/Script.

**Solución**:
1.  **Bypass Definitivo**: Usar **Divi Theme Builder (Generador de Temas)**.
2.  Crear/Editar **Pie de Página Global**.
3.  Insertar un **Módulo de Código** (Gris).
4.  **Estilos Force**: Usar estilos `inline` con `!important` (`style="... !important"`) dentro del HTML. El Theme Builder usa una tabla diferente en la BD (`wp_posts` layout) que suele saltarse la sanitización estricta de opciones globales.

**Referencia**: Sesión 2026-01-02, Hotel Vísperas (Resolución WAF Agresivo).

---

## Errores Archivados

> Errores que ya no aplican pero se mantienen por referencia histórica.

*Ninguno por ahora.*

---

## Agregar Nuevo Error

Cuando el agente documente un nuevo error, debe seguir este formato:

```markdown
### ERR-XXX: [Nombre Descriptivo]

**Síntoma**:
[Mensaje de error o comportamiento observado]

**Causa Raíz**: [Por qué ocurre]

**Solución**:
1. [Paso 1]
2. [Paso 2]

**Referencia**: Sesión [fecha], [documento relacionado]
```
