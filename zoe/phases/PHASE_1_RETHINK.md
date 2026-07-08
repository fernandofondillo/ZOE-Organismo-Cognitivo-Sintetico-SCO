# Reflexión: ¿hay que adaptar Fase 1 tras Fase 0 + 0.5?

## Lo que Fase 0 + 0.5 trajo que no estaba en el plan original de Fase 1

El plan original de Fase 1 (doc 14 §5.2) decía:
- Identity Vault criptográfico
- Trajectory Chain con firmas ECDSA
- Metabolismo funcional (presupuesto, fatiga, ciclos dormir/despertar)
- Sentidos básicos completos (lenguaje, filesystem, reloj, email opcional)
- Actuadores (lenguaje, código sandbox, tools)
- 11 tipos de memoria (esqueletos, se llenarán en Fase 3)

Tras construir Fase 0 + 0.5, la situación cambió:

## Lo que YA tenemos construido (de Fase 0 + 0.5)

1. **InternalState (Fase 0)** — energía, fatiga, arousal, atención
   → Ya es metabolismo básico. Fase 1 debe EXTENDER, no crear.

2. **LivingMemory (Fase 0.5)** — memoria que piensa, con 7 operaciones
   → Ya es memoria viva funcional. Fase 1 debe ESPECIALIZAR en 11 tipos.

3. **CognitiveLaws (Fase 0.5)** — 6 leyes verificadas en cada acción
   → Fase 1 debe conectar con Identity Vault (2da ley: preservar identidad).

4. **CognitivePhysics (Fase 0.5)** — 12 magnitudes, including memory_elasticity
   → Fase 1 debe alimentar el metabolismo con estas magnitudes.

5. **CognitiveTensions (Fase 0.5)** — 5 tensiones que afectan fatiga, descanso
   → Fase 1 debe integrar ciclos dormir/despertar con tensiones.

6. **IntentionalityMotor (Fase 0.5)** — genera intenciones
   → Fase 1 debe usar intenciones para guiar consolidación en sueño.

7. **PhylogeneticMotor (Fase 0.5)** — evolución de especie
   → Fase 1 debe firmar mutaciones filogenéticas con Identity Vault.

8. **CognitiveLoopV05 (Fase 0.5)** — bucle integrado
   → Fase 1 debe extender este bucle, no crear uno nuevo.

## Adaptaciones necesarias a Fase 1 original

### Adaptación 1: Metabolismo como extensión, no creación
- Original: "Metabolismo funcional (presupuesto, fatiga, ciclos dormir/despertar)"
- Adaptado: "EXTENDER InternalState con ciclos dormir/despertar + conectar con CognitivePhysics"
- No crear Metabolism desde cero; evolucionar InternalState.

### Adaptación 2: 11 tipos de memoria como especialización de LivingMemory
- Original: "11 tipos de memoria (esqueletos)"
- Adaptado: "Especializar LivingMemory en 11 tipos con backing stores"
- No crear 11 memorias nuevas; añadir 11 tipos a LivingMemory existente.

### Adaptación 3: Identity Vault conectado a CognitiveLaws
- Original: "Identity Vault criptográfico (hash SHA-256)"
- Adaptado: "Identity Vault + integración con 2da ley (preservar identidad)"
- El Vault no es standalone; es la implementación de la 2da ley.

### Adaptación 4: Trajectory Chain como mutaciones firmadas
- Original: "Trajectory Chain con firmas ECDSA"
- Adaptado: "Trajectory Chain que firma mutaciones del Motor Ontogenético"
- No es solo log; es cadena criptográfica de mutaciones.

### Adaptación 5: Sentidos como módulos intercambiables
- Original: "Sentidos básicos completos"
- Adaptado: "Sentidos con interfaz común, validados por 6ta ley (modularidad)"
- Aplicar la 6ta ley: todo módulo puede reemplazarse.

### Adaptación 6: Actuadores con verificación de leyes
- Original: "Actuadores (lenguaje, código sandbox, tools)"
- Adaptado: "Actuadores donde cada acción pasa por verify_action()"
- Las leyes ya filtran; los actuadores deben respetarlas.

### Adaptación 7: Integración con CognitiveFields
- Original: no mencionado
- Adaptado: "Sentidos y actuadores escriben en campos cognitivos"
- Aprovechar la infraestructura de campos compartidos.

## Lo que NO cambia de Fase 1 original

- Identity Vault criptográfico (hash SHA-256 de 9 vectores + 7 valores)
- Trajectory Chain con firmas ECDSA
- 11 tipos de memoria especializados
- Deploy en VPS CEO con 30 días de uso real
- 100 interacciones, identidad persiste, metabolismo afecta comportamiento

## Nueva prioridad: consolidación antes de expansión

Tras Fase 0 + 0.5, el organismo ya tiene:
- Bucle cognitivo ✅
- 6 leyes ✅
- 12 magnitudes físicas ✅
- 6 campos ✅
- 5 tensiones ✅
- Memoria viva ✅
- Intencionalidad ✅
- Filogenético (esqueleto) ✅

Fase 1 debe CONSOLIDAR (dar persistencia criptográfica, profundizar metabolismo, especializar memoria) antes de EXPANDIR (nuevas capacidades).

## Sub-fases revisadas

Sub-fase 1.1: Identity Vault + 2da ley
Sub-fase 1.2: Trajectory Chain + Motor Ontogenético básico
Sub-fase 1.3: Metabolismo extendido (ciclos dormir/despertar + consolidación)
Sub-fase 1.4: 11 tipos de memoria especializados (sobre LivingMemory)
Sub-fase 1.5: Sentidos y actuadores completos
Sub-fase 1.6: Integración + demo + validación 100 interacciones
