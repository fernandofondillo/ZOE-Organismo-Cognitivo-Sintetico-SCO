# Fase 0.5 — De arquitectura a teoría de organismo cognitivo

> **Salto cualitativo.** Fase 0 construyó un bucle cognitivo funcional. Fase 0.5 lo eleva de "arquitectura de IA" a "teoría de organismo cognitivo digital" mediante 7 innovaciones del CEO que se integran sin desconstruir lo hecho.

**Estado:** 🟡 En construcción
**Duración estimada:** 1-2 sesiones
**Validación:** organismo con leyes, campos, tensiones y física cognitiva, generando pensamientos más ricos que Fase 0

---

## Las 7 innovaciones del CEO a integrar

| # | Innovación | Qué cambia | Componente nuevo |
|---|---|---|---|
| 1 | **Leyes Cognitivas de ZOE** | Define organismo por leyes, no por componentes | `CognitiveLaws` |
| 2 | **Campos Cognitivos** | Cognición ocurre en campos compartidos, no en mensajes | `CognitiveField` |
| 3 | **Memoria Viva** | Memoria piensa: reorganiza, olvida, fusiona, genera hipótesis | `LivingMemory` |
| 4 | **Motor de Intencionalidad** | Genera continuamente nuevas intenciones, no respuestas | `IntentionalityMotor` |
| 5 | **Tensiones Cognitivas Permanentes** | Inteligencia emerge de conflictos internos, no de alineación | `CognitiveTensions` |
| 6 | **Física Cognitiva** | Magnitudes medibles: energía, masa conceptual, entropía semántica | `CognitivePhysics` |
| 7 | **Motor Filogenético** | Evolución de especie, no solo de individuo | `PhylogeneticMotor` |

**Principio rector:** ninguna innovación rompe lo construido en Fase 0. Todas se añaden como capas que enriquecen el bucle cognitivo existente.

---

## Las 6 Leyes Cognitivas de ZOE

ZOE no se define por componentes (Alma, Mente, Cuerpo...). Se define por leyes que todo componente debe respetar. Como la biología no define un ser vivo por sus órganos, sino por homeostasis, evolución, metabolismo, adaptación, autopoiesis.

### Primera Ley — Principio de Utilidad Cognitiva

> *Toda acción debe reducir incertidumbre o aumentar capacidad futura. No puede existir una acción gratuita.*

**Implementación:** cada acción propuesta por el bucle se evalúa contra esta ley. Si no reduce incertidumbre ni aumenta capacidad, se rechaza.

### Segunda Ley — Principio de Preservación de Identidad

> *Toda modificación debe preservar identidad.*

**Implementación:** cada mutación (de memoria, de arquitectura, de estado) se verifica contra el Identity Vault antes de aplicar. Si rompe identidad, se rechaza.

### Tercera Ley — Principio de Proveniencia

> *Todo conocimiento debe poder justificar su origen. No existe memoria "mágica".*

**Implementación:** cada entry en cualquier tipo de memoria debe tener `provenance` (fuente, timestamp, justificación). Sin provenance, no se almacena.

### Cuarta Ley — Principio de Coste Cognitivo

> *Todo proceso consume recursos. Nadie puede pensar gratis.*

**Implementación:** cada operación del bucle tiene un coste medible en `energy`. Cuando `energy` se agota, el organismo descansa o duerme.

### Quinta Ley — Principio de Confianza Calibrada

> *Toda creencia tiene un nivel de confianza. Nunca existen verdades absolutas.*

**Implementación:** cada creencia/conocimiento en memoria tiene `confidence ∈ [0,1]`. El organismo reporta incertidumbre, no certezas absolutas.

### Sexta Ley — Principio de Modularidad Ontogenética

> *Todo módulo puede ser reemplazado sin romper la identidad. La arquitectura es verdaderamente modular.*

**Implementación:** el Motor Ontogenético puede reemplazar cualquier sub-agente, sentido, o actuador. La identidad (definida por las leyes + el Alma) persiste.

---

## Campos Cognitivos (no mensajes)

La arquitectura actual tiene sub-agentes que intercambian mensajes. Esto crea acoplamiento. La innovación: **campos compartidos**.

Los agentes no se hablan entre sí. Modifican campos compartidos:

| Campo | Qué contiene | Quienes lo modifican |
|---|---|---|
| **Campo de Atención** | A qué se está prestando atención ahora | Perceiver, Forecaster, IntentionalityMotor |
| **Campo Emocional** | Estado emocional funcional (sorpresa, curiosidad, fatiga) | Forecaster, Metabolism, Critic |
| **Campo Social** | Modelos de otros agentes y usuarios | Perceiver, Memory |
| **Campo Creativo** | Hipótesis, combinaciones, exploraciones | CreativityEngine (Fase 2), IntentionalityMotor |
| **Campo Causal** | Causa-efecto detectado | Forecaster, WorldModel |
| **Campo Ético** | Evaluación de valores en curso | Critic, IdentityVault |

**Implementación:** `CognitiveField` es un espacio compartido con:
- `state`: estado actual del campo
- `contributors`: quién contribuyó
- `tension`: nivel de tensión en el campo
- `history`: evolución reciente

Los sub-agentes leen/escriben campos en vez de mandarse mensajes.

---

## Memoria Viva

La memoria actual es una base de datos pasiva. La innovación: **memoria que piensa**.

`LivingMemory` no solo almacena. Activamente:
- **Reorganiza:** mueve entries entre tipos (episódica → semántica tras consolidación)
- **Olvida:** poda entries de baja saliencia/confianza
- **Fusiona:** combina entries similares en una sola
- **Resume:** comprime entries antiguas en resúmenes
- **Generaliza:** extrae patrones de entries múltiples
- **Detecta contradicciones:** marca entries que se oponen
- **Genera hipótesis:** propone nuevas entries basadas en patrones

**Implementación:** `LivingMemory` corre como sub-agente en el bucle. En cada iteración (o en ciclos de sueño), ejecuta una de estas operaciones.

---

## Motor de Intencionalidad

El bucle actual responde a observaciones. La innovación: **generar continuamente nuevas intenciones**.

`IntentionalityMotor` produce "deseos cognitivos" — no respuestas. Ejemplos:
- "Quiero entender por qué X ocurrió"
- "Quiero explorar el concepto Y"
- "Quiero verificar mi hipótesis sobre Z"
- "Quiero consolidar lo aprendido hoy"
- "Quiero comunicar mi estado al usuario"

Estas intenciones alimentan el bucle. El organismo no espera input para tener objetivos.

**Implementación:** `IntentionalityMotor` genera intenciones basadas en:
- Tensiones cognitivas activas
- Sorpresa acumulada
- Energía disponible
- Patrones en memoria viva

---

## Tensiones Cognitivas Permanentes

La inteligencia no emerge de la alineación. Emerje del **conflicto interno**.

| Tensión | Polo A | Polo B |
|---|---|---|
| Curiosidad vs Eficiencia | Explorar nuevo | Explotar conocido |
| Identidad vs Adaptación | Mantenerse fiel | Cambiar con entorno |
| Descanso vs Productividad | Ahorrar energía | Lograr objetivos |
| Honestidad vs Empatía | Decir verdad | No herir |
| Especialización vs Generalización | Profundizar | Ampliar |

Cada tensión tiene un nivel (0-1) que cambia con el tiempo. El organismo "siente" estas tensiones y las resuelve generando pensamiento/acción.

**Implementación:** `CognitiveTensions` mantiene 5 tensiones. Cada iteración del bucle las evalúa y decide cuál priorizar.

---

## Física Cognitiva

La aportación científica potencial: **magnitudes medibles** que gobiernan el organismo.

| Magnitud | Definición matemática | Unidad |
|---|---|---|
| **Energía cognitiva** | Presupuesto de cómputo disponible | eCog |
| **Masa conceptual** | Número de conexiones de un concepto en memoria | mCon |
| **Temperatura cognitiva** | Nivel de actividad del bucle (iteraciones/s) | tCog |
| **Presión de incertidumbre** | Sorpresa acumulada no resuelta | pUnc |
| **Potencial creativo** | Diversidad de hipótesis generadas | pCre |
| **Entropía semántica** | Diversidad de conceptos activos | hSem |
| **Gravedad de objetivos** | Atracción de intenciones sobre atención | gObj |
| **Inercia de identidad** | Resistencia al cambio de valores | iIden |
| **Resonancia conceptual** | Similitud entre conceptos activos | rCon |
| **Fricción cognitiva** | Coste de cambiar de contexto | fCog |
| **Elasticidad de memoria** | Capacidad de reorganización | eMem |
| **Densidad causal** | Concentración de relaciones causales | dCau |

**Implementación:** `CognitivePhysics` calcula estas magnitudes en cada iteración. Afectan decisiones del bucle.

---

## Motor Filogenético

El Motor Ontogenético cambia un individuo. El Motor Filogenético cambia la especie.

```
ZOE A descubre mejora arquitectural
        ↓
Publica en Pool Filogenético
        ↓
Otras ZOEs (B, C, D...) la prueban
        ↓
Solo si mejora métricas verificables → la incorporan
        ↓
Especies ZOE diverge/converge con criterio
```

**Implementación:** `PhylogeneticMotor` (esqueleto en Fase 0.5, operativo en Fase 4):
- `publish_improvement(zoe_id, mutation)`
- `try_improvement(zoe_id, mutation)` → evaluar en sandbox
- `incorporate_improvement(zoe_id, mutation)` → aplicar si pasa tests
- `species_state()` → estado de la especie ZOE

---

## Sub-fases de Fase 0.5

### Sub-fase 0.5.1 — Leyes Cognitivas (CognitiveLaws)

**Objetivo:** 6 leyes como principios verificables que rigen todo componente.

**Implementación:** `zoe/core/cognitive_laws.py`
- 6 leyes como funciones `verify_law(law_id, action, context) -> bool`
- Cada acción del bucle pasa por las leyes antes de ejecutarse
- Test: acción que viola ley se rechaza

### Sub-fase 0.5.2 — Física Cognitiva (CognitivePhysics)

**Objetivo:** 12 magnitudes medibles que alimentan decisiones.

**Implementación:** `zoe/core/cognitive_physics.py`
- 12 magnitudes calculadas en cada iteración
- Afectan decisiones del bucle (ej: energía baja → descansar)
- Test: magnitudes se calculan correctamente

### Sub-fase 0.5.3 — Campos Cognitivos (CognitiveFields)

**Objetivo:** 6 campos compartidos en vez de mensajes entre sub-agentes.

**Implementación:** `zoe/core/cognitive_fields.py`
- 6 campos: atención, emocional, social, creativo, causal, ético
- Sub-agentes leen/escriben campos en vez de mensajes directos
- Test: cambios en un campo son visibles para otros agentes

### Sub-fase 0.5.4 — Tensiones Cognitivas (CognitiveTensions)

**Objetivo:** 5 tensiones permanentes que generan pensamiento.

**Implementación:** `zoe/core/cognitive_tensions.py`
- 5 tensiones con niveles (0-1) que cambian con el tiempo
- Cada iteración evalúa tensiones y afecta decisiones
- Test: tensiones evolucionan correctamente

### Sub-fase 0.5.5 — Memoria Viva (LivingMemory)

**Objetivo:** memoria que reorganiza, olvida, fusiona, generaliza.

**Implementación:** `zoe/core/living_memory.py`
- Operaciones: reorganize, forget, merge, summarize, generalize, detect_contradictions, generate_hypotheses
- Corre como sub-agente en el bucle
- Test: tras 100 entries, memoria se reorganiza

### Sub-fase 0.5.6 — Motor de Intencionalidad (IntentionalityMotor)

**Objetivo:** generador continuo de intenciones.

**Implementación:** `zoe/core/intentionality_motor.py`
- Genera intenciones basadas en tensiones, sorpresa, energía, memoria
- Alimenta el bucle con objetivos además de observaciones
- Test: genera intenciones diversas y coherentes

### Sub-fase 0.5.7 — Motor Filogenético (PhylogeneticMotor)

**Objetivo:** esqueleto de evolución de especie.

**Implementación:** `zoe/core/phylogenetic_motor.py`
- `publish_improvement`, `try_improvement`, `incorporate_improvement`
- Pool filogenético (en memoria para Fase 0.5, persistente en Fase 4)
- Test: una mejora publicada puede ser incorporada por otra instancia

### Sub-fase 0.5.8 — Integración en CognitiveLoop

**Objetivo:** integrar todo sin romper Fase 0.

**Implementación:** modificar `zoe/core/cognitive_loop.py`:
- Cada acción pasa por `CognitiveLaws.verify()`
- `CognitivePhysics` se calcula cada iteración
- `CognitiveFields` reemplazan algunos mensajes
- `CognitiveTensions` afectan decisiones
- `LivingMemory` corre como sub-agente
- `IntentionalityMotor` genera intenciones que alimentan el bucle
- `PhylogeneticMotor` disponible para publicar mejoras

### Sub-fase 0.5.9 — Demo y tests

**Objetivo:** demostrar organismo más rico que Fase 0.

**Implementación:**
- `zoe/examples/demo_phase0_5.py`
- Tests para cada componente nuevo
- Comparativa: pensamientos Fase 0 vs Fase 0.5

---

## Métricas de validación Fase 0.5

| Métrica | Objetivo |
|---|---|
| Leyes verificadas por acción | 6/6 |
| Magnitudes de física cognitiva calculadas | 12/12 |
| Campos cognitivos activos | 6/6 |
| Tensiones cognitivas evolucionando | 5/5 |
| LivingMemory reorganiza tras N entries | Sí |
| IntencionalidadMotor genera intenciones diversas | Sí |
| PhylogeneticMotor publica/incorpora mejora | Sí (esqueleto) |
| Tests pasan | 100% nuevos + 100% previos |
| Comparativa vs Fase 0 | Pensamientos más ricos |

---

*Fase 0.5 en construcción. Sin desconstruir Fase 0.*
