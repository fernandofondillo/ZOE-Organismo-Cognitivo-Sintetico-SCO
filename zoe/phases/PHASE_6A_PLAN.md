# FASE 6A — Epistemic Validation System + Dashboard Capsules

> **Objetivo**: ZOE regula cómo adquiere, valida y consolida conocimiento nuevo. Las cápsulas se cargan y gestionan desde el Dashboard.

## Las 4 opciones de Fase 6A

### Opción 1 — EpistemicValidator (validación por fuente y dominio)

**Problema**: cuando ZOE detecta un gap y consulta a un LLM, almacena la respuesta con confianza media sin validar. Si la respuesta está sesgada o es incorrecta, se propaga.

**Solución**: módulo `EpistemicValidator` que aplica política de confianza por fuente y dominio antes de aceptar conocimiento nuevo.

**Componentes**:
- `zoe/core/epistemic_validator.py` — clase `EpistemicValidator`
- Política `SOURCE_TRUST` con 14 fuentes categorizadas (capsule:verified=0.95, llm:gpt-4o=0.50, etc.)
- Política `SENSITIVE_DOMAINS` (medical, psychological, legal, safety, financial) que requieren doble verificación
- Cap de confianza para auto-aprendido: máximo 0.50 sin verificación cruzada
- Métodos: `validate_new_knowledge(claim, source, context) → ValidationResult`

**Resultado**: el conocimiento nuevo entra al sistema con confianza limitada o es rechazado automáticamente.

### Opción 2 — Knowledge Quarantine (cuarentena activa)

**Problema**: aunque un claim entre con confianza baja, el sistema podría usarlo para decisiones críticas.

**Solución**: módulo `KnowledgeQuarantine` que marca conocimiento no validado como `quarantine=True` y bloquea su uso en decisiones críticas.

**Componentes**:
- `zoe/core/knowledge_quarantine.py` — clase `KnowledgeQuarantine`
- Las memorias en cuarentena NO se usan para: respuestas a usuarios en dominios sensibles, decisiones de acción externa, mutaciones arquitecturales
- Las memorias en cuarentena SÍ se usan para: brainstorming, exploración, suggestion de hipótesis al ScientificEngine
- Plan de verificación: cada entrada en cuarentena tiene `verification_plan` con fuentes requeridas y timeout
- Si no se valida en 30 días → el Curator la poda

**Resultado**: conocimiento no validado no causa daño aunque sea incorrecto.

### Opción 3 — CrossValidator (triple verificación multi-fuente)

**Problema**: una sola fuente (incluso GPT-4o) puede estar sesgada o alucinar.

**Solución**: módulo `CrossValidator` que coordina consulta a múltiples fuentes y solo consolida si hay acuerdo.

**Componentes**:
- `zoe/core/cross_validator.py` — clase `CrossValidator`
- Protocolo de 3 fuentes: LLM-A + LLM-B + cápsula relacionada (o tercera fuente)
- Si 3/3 coinciden → confianza 0.75, sale de cuarentena
- Si 2/3 coinciden → confianza 0.65, sigue en cuarentena con `pending_third_source`
- Si 1/3 o divergencia total → rechazo, marca conflicto
- Solo se aplica en dominios sensibles o cuando hay contradicción detectada

**Resultado**: el conocimiento auto-aprendido se valida con múltiples fuentes independientes antes de consolidarse.

### Opción 4 — Federación epistémica (validación entre ZOEs)

**Problema**: 100 ZOEs activas pueden aprender lo mismo 100 veces independientemente, cada una con su sesgo local.

**Solución**: extensión de la federación existente con tipo de mensaje `knowledge_validation_request` para que las ZOEs se validen entre sí.

**Componentes**:
- Nuevo tipo de mensaje federado en `zoe/core/federation.py`
- Cuando ZOE-A aprende algo y lo valida localmente, lo envía a peers con `knowledge_validation_request`
- Peers responden: `confirmed` (ya lo tenían validado), `contradicted` (tienen evidencia contraria), `unknown` (no lo saben)
- Si ≥2 peers confirman → confianza sube a 0.85, sale de cuarentena
- Si algún peer contradice → conflicto, requiere validación científica externa
- Mecanismo de revisión por pares científica aplicado a organismos cognitivos

**Resultado**: las ZOEs se validan colectivamente. El conocimiento consolidado en una se propaga verificado a las demás.

## Dashboard Capsules — carga interactiva

**Problema**: hoy las cápsulas se cargan solo vía YAML del caso de uso. No hay forma de gestionarlas dinámicamente.

**Solución**: UI en el Web Dashboard con 3 vistas:

1. **Listado de cápsulas disponibles**: tabla con nombre, dominio, trust level, entries, compatible use cases. Botón "Cargar" para inyectar en caliente.
2. **Cápsulas cargadas**: lista de cápsulas activas en esta ZOE con entries cargadas, fecha de carga, hash verificado. Botón "Descargar" para quitar.
3. **Crear nueva cápsula**: formulario simplificado (nombre, dominio, trust level, descripción) que invoca el scaffold CLI y crea la estructura en disco. Editor básico de entradas.

**Endpoints nuevos**:
- `GET /api/capsules` — listar disponibles
- `GET /api/capsules/loaded` — listar cargadas
- `POST /api/capsules/load` — cargar en caliente
- `POST /api/capsules/unload` — descargar
- `POST /api/capsules/create` — crear nueva vía scaffold
- `GET /api/capsules/{name}/info` — info detallada
- `POST /api/capsules/{name}/validate` — validar

**UI en Dashboard**: nuevo panel "Cápsulas" accesible desde el menú lateral, con las 3 vistas en tabs.

## Plan de implementación

### Step 1 — EpistemicValidator (Opción 1)
1. `zoe/core/epistemic_validator.py` con políticas
2. `ValidationResult` dataclass con status, confidence, reason, quarantine
3. Tests: validación por fuente, dominio sensible, cap, contradicción

### Step 2 — Knowledge Quarantine (Opción 2)
1. `zoe/core/knowledge_quarantine.py` con gestión de cuarentena
2. Integración con LivingMemory (campo `quarantine` en metadata)
3. Integración con Critic y Curator (no usar cuarentena para crítico)
4. Plan de verificación con timeout
5. Tests: cuarentena activa, expiración, uso restringido

### Step 3 — CrossValidator (Opción 3)
1. `zoe/core/cross_validator.py` con protocolo triple
2. Integración con ScientificEngine (coordina las 3 consultas)
3. Integración con EpistemicValidator (resuelve cuarentena al validar)
4. Tests: triple coincidencia, divergencia, contradicción con cápsula

### Step 4 — Federación epistémica (Opción 4)
1. Nuevo tipo `knowledge_validation_request` en `federation.py`
2. Endpoint federado para responder confirmaciones
3. Integración con CrossValidator (peers como tercera fuente)
4. Tests: federación confirma, federación contradice, federación unknown

### Step 5 — Carga de cápsulas en runtime
1. Modificar `run_use_case.py` para cargar cápsulas del YAML
2. Modificar `cli_chat.py` para cargar cápsulas compatibles
3. Método `load_capsule(name)` en `CognitiveLoopV5` para carga en caliente
4. Método `unload_capsule(name)` para descarga
5. Mutación firmada `capsule_loaded` / `capsule_unloaded`

### Step 6 — Dashboard Capsules UI
1. Endpoints `/api/capsules*` en `web_dashboard.py`
2. UI HTML/JS con 3 tabs: disponibles, cargadas, crear
3. WebSocket para notificación de carga/descarga
4. Botones de acción: cargar, descargar, validar, crear

### Step 7 — Tests integrales
1. Tests de Fase 6A: `test_phase6a_epistemic.py`
2. Tests de integración Dashboard capsulas: `test_dashboard_capsules.py`
3. Verificar no-regresión: 630 tests previos + nuevos

## Métricas de éxito

| Métrica | Antes (V1.0) | Objetivo (V1.1 con 6A) |
|---|---|---|
| Conocimiento nuevo aceptado sin validación | 100% | Solo cuarentena (0%) |
| Confianza máxima auto-aprendido | 0.7 | 0.50 (cuarentena) → 0.75 (triple) → 0.85 (federado) |
| Validación cruzada multi-fuente | No | Sí, obligatoria en sensible |
| Federación epistémica | No | Sí, revisión por pares |
| Cápsulas cargables en runtime | No | Sí, desde Dashboard |
| Cápsulas gestionables desde UI | No | Sí, 3 vistas |
| Tests | 630 | 700+ |
| Reject de conocimiento contradictorio | No | Automático |
