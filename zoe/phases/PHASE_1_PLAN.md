# Fase 1 — Consolidación del organismo (Alma + Cuerpo + Metabolismo)

> **Fase 1 adaptada tras Fase 0 + 0.5.** No crea componentes desde cero; **extiende y consolida** lo construido. Identity Vault se conecta con la 2da ley. Metabolismo extiende InternalState. 11 tipos de memoria especializan LivingMemory. Trajectory Chain firma mutaciones del Motor Ontogenético.

**Estado:** 🟡 En construcción
**Duración estimada:** 4 semanas (6 sub-fases)
**Validación:** 100 interacciones, identidad persiste, metabolismo afecta comportamiento

---

## Principios de Fase 1

1. **Consolidar antes de expandir.** El organismo ya tiene bucle, leyes, física, campos, tensiones, memoria viva, intencionalidad, filogenético. Fase 1 da persistencia criptográfica, profundiza metabolismo, especializa memoria.

2. **Extender, no crear.** InternalState se extiende a Metabolismo completo. LivingMemory se especializa en 11 tipos. CognitiveLaws se conecta con Identity Vault.

3. **Cada componente se integra con Fase 0.5.** Identity Vault implementa la 2da ley. Metabolismo usa CognitivePhysics. Mutaciones se firman en Trajectory Chain. Sentidos escriben en CognitiveFields.

4. **Tests primero, integración después.** Cada sub-fase tiene tests propios + tests de integración con Fase 0 + 0.5.

---

## Las 7 adaptaciones al plan original

| # | Original | Adaptado |
|---|---|---|
| 1 | Crear Metabolismo desde cero | EXTENDER InternalState con ciclos dormir/despertar |
| 2 | 11 tipos de memoria nuevos | ESPECIALIZAR LivingMemory existente en 11 tipos |
| 3 | Identity Vault standalone | Identity Vault + integración con 2da ley |
| 4 | Trajectory Chain como log | Trajectory Chain firma mutaciones del Motor Ontogenético |
| 5 | Sentidos básicos completos | Sentidos con interfaz común, validados por 6ta ley |
| 6 | Actuadores standalone | Actuadores donde cada acción pasa verify_action() |
| 7 | Sin mencionar campos | Sentidos y actuadores escriben en CognitiveFields |

---

## Las 6 sub-fases

### Sub-fase 1.1 — Identity Vault + 2da Ley (días 1-3)

**Objetivo:** hash criptográfico de 9 vectores + 7 valores + propósito. Inmutable. Verificable.

**Implementación:**
- `zoe/alma/identity_vault.py` — `IdentityVault` class
  - `identity_hash = SHA256(serialize(9_vectores + 7_valores + proposito))`
  - `verify(action) -> bool` — verifica que acción preserva identidad (implementa 2da ley)
  - `to_dict() -> dict` — exportación verificable
  - `from_dict(d) -> IdentityVault` — importación
- Integración con `CognitiveLaws`: la 2da ley delega al Vault

**Tests:**
- `test_identity_vault.py`: hash determinista, verificación de acciones, inmutabilidad
- Test de integración: CognitiveLaws usa IdentityVault para 2da ley

**Criterio de éxito:** una acción que rompe identidad es rechazada por el Vault.

### Sub-fase 1.2 — Trajectory Chain + Motor Ontogenético básico (días 4-7)

**Objetivo:** cadena firmada de mutaciones. Cada mutación es un commit con hash, diff, justificación, firma.

**Implementación:**
- `zoe/alma/trajectory_chain.py` — `TrajectoryChain` class
  - `commit(mutation) -> str` — añade mutación firmada a la cadena
  - `verify_chain() -> bool` — verifica integridad de toda la cadena
  - `rollback(commit_hash) -> bool` — revierte hasta un commit
  - `get_history() -> List[dict]` — historial de mutaciones
- `zoe/core/ontogenetic_motor.py` — `OntogeneticMotor` class
  - `propose_mutation(type, target, payload, justification) -> Mutation`
  - `apply_mutation(mutation) -> bool` — aplica + verifica leyes + firma en cadena
  - `rollback_last() -> bool`
- Cada mutación: `add_memory, strengthen_belief, weaken_belief, add_skill_subgraph, update_world_model, adjust_threshold, federate_learning, rollback_previous`

**Tests:**
- `test_trajectory_chain.py`: commit, verify, rollback, integridad
- `test_ontogenetic_motor.py`: propose, apply, rollback, integración con leyes

**Criterio de éxito:** una mutación se aplica, se firma, se puede revertir.

### Sub-fase 1.3 — Metabolismo extendido (días 8-11)

**Objetivo:** extender InternalState con ciclos dormir/despertar + consolidación. Conectado con CognitivePhysics y CognitiveTensions.

**Implementación:**
- `zoe/metabolism/metabolism.py` — `Metabolism` class (extiende InternalState)
  - `sleep_cycle()` — consolida memoria, recarga energía, reduce fatiga
  - `wake_cycle()` — activa sentidos, restaura atención
  - `should_sleep() -> bool` — decide si es hora de dormir (basado en CognitivePhysics)
  - `should_wake() -> bool` — decide si es hora de despertar
  - Estados: `awake, drowsy, sleeping, waking`
- Integración con `CognitivePhysics.should_rest()` y `should_consolidate()`
- Integración con `CognitiveTensions.rest_vs_productivity`
- Integración con `LivingMemory.think()` en ciclo de sueño (consolidación profunda)

**Tests:**
- `test_metabolism.py`: sleep/wake cycles, should_sleep/wake, consolidación
- Test de integración: metabolismo afecta decisiones del bucle

**Criterio de éxito:** el organismo duerme cuando fatiga alta, consolida memoria al despertar.

### Sub-fase 1.4 — 11 tipos de memoria especializados (días 12-15)

**Objetivo:** especializar LivingMemory en 11 tipos con backing stores. Cada tipo con políticas de acceso.

**Implementación:**
- `zoe/memory/memory_types.py` — 11 tipos:
  1. `EpisodicMemory` — eventos con contexto espacio-temporal
  2. `SemanticMemory` — conceptos y relaciones (grafo)
  3. `ProceduralMemory` — habilidades, recetas
  4. `CausalMemory` — causa-efecto verificado
  5. `EmotionalMemory` — marcadores de relevancia
  6. `CorporalMemory` — estado de sensores, capacidades
  7. `SocialMemory` — modelos de otros agentes y usuarios
  8. `ProspectiveMemory` — planes e intenciones futuras
  9. `CounterfactualMemory` — qué habría pasado si
  10. `EvolutionaryMemory` — historial de cambios arquitecturales (mutaciones)
  11. `CulturalMemory` — normas, convenciones, contextos sociales
- Cada tipo extiende `MemoryEntry` con campos específicos
- `LivingMemory` se extiende para manejar los 11 tipos con políticas de acceso
- Reorganización entre tipos (ej: episódica → semántica tras consolidación)

**Tests:**
- `test_memory_types.py`: cada tipo almacena y recupera correctamente
- Test de integración: reorganización entre tipos funciona

**Criterio de éxito:** los 11 tipos funcionan, reorganización automática.

### Sub-fase 1.5 — Sentidos y actuadores completos (días 16-18)

**Objetivo:** sentidos con interfaz común, validados por 6ta ley. Actuadores con verify_action().

**Implementación:**
- `zoe/peripherals/senses.py` — extender con:
  - `NetworkSense` — cambios en red (HTTP, WS)
  - `EmailSense` (opcional, configurable)
  - `AgentSense` — estado de otros agentes/ZOEs
- `zoe/peripherals/actuators.py` — `Actuator` base + implementaciones:
  - `LanguageActuator` — usa LLM periférico
  - `CodeActuator` — ejecuta código en sandbox
  - `ToolActuator` — invoca tools (skills/)
  - `FederationActuator` — comunica con otras ZOEs
- Cada actuador: `execute(action) -> Result`, donde action pasa `verify_action()`
- Sentidos escriben en CognitiveFields (attention, social, etc.)

**Tests:**
- `test_actuators.py`: cada actuador ejecuta con leyes verificadas
- Test de integración: sentidos escriben en campos, actuadores leen

**Criterio de éxito:** actuadores ejecutan acciones que pasan las 6 leyes.

### Sub-fase 1.6 — Integración + demo + validación (días 19-21)

**Objetivo:** integrar todo en CognitiveLoopV05 + demo + validación de 100 interacciones.

**Implementación:**
- Extender `CognitiveLoopV05` con Identity Vault, Trajectory Chain, Metabolismo, 11 memorias, sentidos/actuadores completos
- `zoe/examples/demo_phase1.py` — demo de organismo Fase 1 completo
- Tests de integración: 100 interacciones, identidad persiste, metabolismo afecta comportamiento

**Criterio de éxito GO/NO-GO:**
- ✅ GO: 100 interacciones, identidad verificada en cada una, metabolismo duerme/despierta, 11 memorias funcionan, mutaciones firmadas en cadena
- ❌ NO-GO: cualquiera falla → revisar

---

## Métricas de validación Fase 1

| Métrica | Objetivo |
|---|---|
| Interacciones sin crash | ≥100 |
| Identidad persiste (hash constante) | 100% |
| Mutaciones firmadas en Trajectory Chain | ≥10 |
| Mutaciones reversibles | 100% |
| Ciclos dormir/despertar | ≥3 |
| Memoria viva reorganiza entre 11 tipos | Sí |
| Leyes cognitivas verificadas por acción | 6/6 |
| Física cognitiva calculada | 12/12 |
| Campos cognitivos actualizados | 6/6 |
| Tensiones cognitivas evolucionan | 5/5 |
| Tests pasan | 100% previos + nuevos |
| Demo Fase 1 funcional | Sí |

---

## Lo que NO se construye en Fase 1 (queda para fases posteriores)

- ❌ Active Inference con pymdp (Fase 2)
- ❌ World Model JEPA neural (Fase 2)
- ❌ 12 sub-agentes completos (Fase 2, ahora son 4)
- ❌ Federación distribuida con quorum (Fase 4)
- ❌ Motor Ontogenético avanzado (Fase 3-4)
- ❌ Caso de uso específico deploy (Fase 4)

---

*Fase 1 en construcción. Sub-fase 1.1 iniciada.*
