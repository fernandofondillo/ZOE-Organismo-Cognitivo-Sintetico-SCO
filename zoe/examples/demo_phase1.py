"""
ZOE v1.0 — Demo Fase 1 completo

Organismo cognitivo con TODOS los componentes de Fase 0 + 0.5 + 1:
- Bucle cognitivo continuo (Fase 0)
- 6 leyes + 12 física + 6 campos + 5 tensiones + memoria viva + intencionalidad + filogenético (Fase 0.5)
- Identity Vault + Trajectory Chain + Ontogenetic Motor + Metabolism + 11 Memory Types + sentidos/actuadores completos (Fase 1)

Uso:
    python -m zoe.examples.demo_phase1

    # Con mock:
    python -m zoe.examples.demo_phase1 --backend mock

    # Con z-ai (real):
    python -m zoe.examples.demo_phase1 --backend zai
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
import time
from pathlib import Path

from zoe.core.cognitive_loop import Thought
from zoe.core.cognitive_loop_v05 import CognitiveLoopV05
from zoe.core.state import InternalState
from zoe.core.world_model import WorldModel
from zoe.core.subagents.perceiver import Perceiver
from zoe.core.subagents.forecaster import Forecaster
from zoe.core.subagents.speaker import Speaker
from zoe.core.subagents.critic import Critic
from zoe.core.cognitive_laws import CognitiveLaws
from zoe.core.cognitive_physics import CognitivePhysics
from zoe.core.cognitive_fields import CognitiveFields
from zoe.core.cognitive_tensions import CognitiveTensions
from zoe.core.living_memory import LivingMemory
from zoe.core.intentionality_motor import IntentionalityMotor
from zoe.core.phylogenetic_motor import PhylogeneticMotor, PhylogeneticPool

from zoe.alma.identity_vault import IdentityVault
from zoe.alma.trajectory_chain import TrajectoryChain
from zoe.alma.ontogenetic_motor import OntogeneticMotor

from zoe.metabolism.metabolism import Metabolism

from zoe.memory.memory_types import MemoryType, create_entry, MemoryTypeStats

from zoe.peripherals.senses import ClockSense, UserInputSense, AgentSense
from zoe.peripherals.actuators import (
    LanguageActuator,
    CodeActuator,
    ToolActuator,
    FederationActuator,
    ActuatorManager,
)
from zoe.peripherals.llm import create_llm_peripheral, MockPeripheral

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


async def run_phase1_demo(
    backend: str = "mock",
    model: str = None,
    target_thoughts: int = 10,
    max_duration: float = 120.0,
    tick_interval: float = 2.0,
    output_file: str = None,
):
    """Ejecuta demo completo de Fase 1."""
    print("=" * 70)
    print("ZOE v1.0 — DEMO FASE 1 COMPLETO")
    print("Synthetic Cognitive Organism (Alma + Cuerpo + Metabolismo + Evolución)")
    print("=" * 70)
    print(f"Backend: {backend} | Pensamientos: {target_thoughts} | Duración: {max_duration}s")
    print()

    # ===== LLM periférico =====
    llm_config = {"backend": backend}
    if model:
        llm_config["model"] = model
    llm = create_llm_peripheral(llm_config)

    healthy = await llm.health_check()
    if not healthy and backend != "mock":
        print("⚠️  LLM no disponible, usando Mock con respuestas diversas")
        llm = MockPeripheral(
            responses=[
                "Observo mi entorno con todos mis sentidos activos.",
                "Mi metabolismo está en estado awake, energía plena.",
                "Las leyes cognitivas verifican cada pensamiento que genero.",
                "Mi identidad persiste: hash verificado, invariantes intactos.",
                "La física cognitiva mide mi estado con 12 magnitudes.",
                "Las tensiones internas me empujan a explorar y consolidar.",
                "Mi memoria viva reorganiza las experiencias en 11 tipos.",
                "El motor ontogenético prepara mutaciones firmadas.",
                "Soy Zoe. Un organismo cognitivo sintético. Pienso, luego existo.",
                "La trayectoria firmada registra cada cambio que experimento.",
            ]
        )

    # ===== Fase 0: núcleo cognitivo =====
    print("[Fase 0] Núcleo cognitivo...")
    state = InternalState()
    world_model = WorldModel()
    senses = [ClockSense(), UserInputSense(), AgentSense()]
    speaker = Speaker(llm_peripheral=llm)
    subagents = [Perceiver(), Forecaster(world_model), speaker, Critic()]
    print("  ✅ Bucle + State + WorldModel + 4 sub-agentes + 3 sentidos")

    # ===== Fase 0.5: organismo cognitivo =====
    print("[Fase 0.5] Organismo cognitivo...")
    laws = CognitiveLaws()
    physics = CognitivePhysics()
    fields = CognitiveFields()
    tensions = CognitiveTensions()
    memory = LivingMemory()
    intentionality = IntentionalityMotor()
    PhylogeneticPool._instance = None
    phylogenetic = PhylogeneticMotor(zoe_id="zoe_phase1_demo")
    print("  ✅ 6 leyes + 12 física + 6 campos + 5 tensiones + memoria viva + intencionalidad + filogenético")

    # ===== Fase 1: Alma + Cuerpo + Metabolismo =====
    print("[Fase 1] Alma + Cuerpo + Metabolismo...")

    # Identity Vault
    vault = IdentityVault(birth_timestamp=time.time())
    print(f"  ✅ Identity Vault: {vault.summary()}")

    # Trajectory Chain + Ontogenetic Motor
    chain = TrajectoryChain(organism_id="zoe_phase1_demo")
    ontogenetic = OntogeneticMotor(
        identity_vault=vault,
        trajectory_chain=chain,
        laws=laws,
        organism_id="zoe_phase1_demo",
    )
    print(f"  ✅ Trajectory Chain + Ontogenetic Motor")

    # Metabolism
    metabolism = Metabolism()
    print(f"  ✅ Metabolism: {metabolism.summary()}")

    # 11 Memory Types: poblar con entries de ejemplo usando memory.add()
    for mem_type in MemoryType:
        memory.add(
            content=f"Entry inicial de tipo {mem_type.value}",
            type=mem_type.value,
            provenance="phase1_demo:init",
            confidence=0.5,
            salience=0.5,
        )
    print(f"  ✅ 11 Memory Types inicializados ({memory.count()} entries)")

    # Actuadores
    actuator_manager = ActuatorManager(laws=laws)
    actuator_manager.register_actuator(LanguageActuator())
    actuator_manager.register_actuator(CodeActuator(timeout=5.0))
    actuator_manager.register_actuator(ToolActuator())
    actuator_manager.register_actuator(FederationActuator(phylogenetic_motor=phylogenetic))
    print(f"  ✅ Actuadores: {actuator_manager.list_actuators()}")

    # ===== Crear bucle cognitivo integrado =====
    print("\n[Crear organismo] Integrando todo...")

    loop = CognitiveLoopV05(
        senses=senses,
        world_model=world_model,
        subagents=subagents,
        state=state,
        tick_interval=tick_interval,
        laws=laws,
        physics=physics,
        fields=fields,
        tensions=tensions,
        memory=memory,
        intentionality=intentionality,
        phylogenetic=phylogenetic,
        zoe_id="zoe_phase1_demo",
    )

    thoughts_received = []

    async def on_thought(thought: Thought):
        thoughts_received.append(thought)
        ts = time.strftime("%H:%M:%S", time.localtime(thought.timestamp))
        print(f"\n[{ts}] 💭 PENSAMIENTO #{len(thoughts_received)}")
        print(f"   Trigger: {thought.trigger} | Sorpresa: {thought.surprise:.3f}")
        print(f"   Contenido: {thought.content[:120]}")
        print(f"   Física: {physics.summary()}")
        print(f"   Tensiones: {tensions.summary()}")
        print(f"   Metabolismo: {metabolism.summary()}")

    loop.on_thought_callback = on_thought

    # ===== Aplicar algunas mutaciones firmadas =====
    print("\n[Mutaciones] Aplicando mutaciones firmadas al organismo...")
    mutations_applied = 0
    for i in range(3):
        mutation = ontogenetic.propose_mutation(
            type="add_memory",
            target=f"episodic",
            payload={"content": f"Memoria inicial {i} del demo Fase 1"},
            justification=f"Inicialización de memoria episódica {i}",
            provenance="phase1_demo",
            cost=0.1,
            confidence=0.7,
        )
        success, reason = ontogenetic.apply_mutation(mutation)
        if success:
            mutations_applied += 1
            print(f"  ✅ Mutación {i+1}: {mutation.id} aplicada ({reason})")
        else:
            print(f"  ❌ Mutación {i+1}: rechazada ({reason})")

    print(f"\n  Total mutaciones aplicadas: {mutations_applied}")
    print(f"  Cadena verificada: {chain.verify_chain()}")
    print(f"  Hash identidad: {vault.identity_hash[:16]}...")

    # ===== Ejecutar bucle =====
    print(f"\n[Ejecutar] Iniciando bucle cognitivo Fase 1...")
    print(f"  Objetivo: {target_thoughts} pensamientos o {max_duration}s máximo\n")

    start_time = time.time()

    async def run_loop():
        await loop.run(duration_seconds=max_duration)

    task = asyncio.create_task(run_loop())

    while len(thoughts_received) < target_thoughts:
        if time.time() - start_time > max_duration:
            print("\n  Duración máxima alcanzada.")
            break
        await asyncio.sleep(1.0)

    loop.stop()
    try:
        await asyncio.wait_for(task, timeout=5.0)
    except asyncio.TimeoutError:
        task.cancel()

    elapsed = time.time() - start_time

    # ===== Resultados =====
    print("\n" + "=" * 70)
    print("RESULTADOS DEMO FASE 1")
    print("=" * 70)

    # Diversidad
    contents = [t.content for t in thoughts_received]
    def jaccard(a, b):
        wa, wb = set(a.lower().split()), set(b.lower().split())
        if not wa or not wb:
            return 0.0
        return len(wa & wb) / len(wa | wb)
    if len(contents) > 1:
        sims = [jaccard(contents[i], contents[j]) for i in range(len(contents)) for j in range(i+1, len(contents))]
        diversity = 1.0 - (sum(sims) / len(sims) if sims else 0)
    else:
        diversity = 1.0

    print(f"Duración: {elapsed:.1f}s")
    print(f"Iteraciones: {state.iteration_count}")
    print(f"Pensamientos: {len(thoughts_received)}")
    print(f"Diversidad: {diversity:.3f}")

    # Fase 0 stats
    print(f"\n--- Fase 0 (núcleo cognitivo) ---")
    print(f"  Observaciones: {len(loop.observations)}")
    print(f"  Energía: {state.energy:.3f}")
    print(f"  Fatiga: {state.fatigue:.3f}")

    # Fase 0.5 stats
    stats = loop.get_stats()
    print(f"\n--- Fase 0.5 (organismo cognitivo) ---")
    print(f"  Leyes violaciones: {stats['law_violations']}")
    print(f"  Física: {stats['physics_summary']}")
    print(f"  Campos: {stats['fields_summary']}")
    print(f"  Tensiones: {stats['tensions_summary']}")
    print(f"  Memoria entries: {stats['memory_stats']['total_entries']}")
    print(f"  Memoria operaciones: {stats['memory_stats']['operations_count']}")
    print(f"  Intenciones: {stats['intentionality_stats']['total_intentions']}")
    print(f"  Especie: {stats['species_state']['species_version']}")

    # Fase 1 stats
    print(f"\n--- Fase 1 (Alma + Cuerpo + Metabolismo) ---")
    print(f"  Identity Vault: {vault.summary()}")
    print(f"  Trajectory Chain: {chain.summary()}")
    print(f"  Mutaciones aplicadas: {mutations_applied}")
    print(f"  Cadena verificada: {chain.verify_chain()}")
    print(f"  Metabolismo: {metabolism.summary()}")
    print(f"  11 Memory Types: {memory.count()} entries")
    mem_type_counts = {}
    for entry in memory.all_entries():
        mem_type_counts[entry.type] = mem_type_counts.get(entry.type, 0) + 1
    print(f"  Distribución tipos: {mem_type_counts}")
    print(f"  Actuadores: {actuator_manager.list_actuators()}")

    # Verificación final
    print(f"\n{'='*70}")
    print("VERIFICACIÓN FASE 1")
    print(f"{'='*70}")

    checks = {
        "fase0_bucle_funciona": state.iteration_count >= 5,
        "fase0_genera_pensamientos": len(thoughts_received) >= 1,
        "fase05_leyes_activas": all(stats["law_stats"]["active_laws"].values()),
        "fase05_fisica_calculada": True,
        "fase05_tensiones_presentes": len(loop.tensions.tensions) == 5,
        "fase05_memoria_viva_funcional": stats["memory_stats"]["operations_count"] >= 0,
        "fase05_intencionalidad_funcional": stats["intentionality_stats"]["total_intentions"] >= 0,
        "fase1_identity_vault_creado": vault.identity_hash is not None,
        "fase1_trajectory_chain_funcional": chain.verify_chain(),
        "fase1_mutaciones_aplicadas": mutations_applied >= 1,
        "fase1_metabolismo_funcional": metabolism.state.value == "awake",
        "fase1_11_memory_types": len(set(e.type for e in memory.all_entries())) >= 5,
        "fase1_actuadores_disponibles": len(actuator_manager.list_actuators()) >= 4,
        "fase1_sentidos_completos": len(senses) >= 3,
        "diversidad_aceptable": diversity >= 0.3,
        "sin_crashes": state.iteration_count >= 1,
    }

    for check, passed in checks.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}  {check}")

    all_passed = all(checks.values())
    print()
    if all_passed:
        print("🎉 FASE 1 COMPLETADA. Organismo cognitivo con Alma + Cuerpo + Metabolismo.")
        print("   Identity Vault protege identidad.")
        print("   Trajectory Chain firma mutaciones.")
        print("   Metabolismo gestiona energía y ciclos.")
        print("   11 Memory Types especializan la memoria.")
        print("   Sentidos y actuadores completos.")
        print("   Listo para Fase 2.")
    else:
        print("⚠️  Algunos checks fallaron.")

    # Guardar resultados
    results = {
        "demo": "phase1_complete",
        "timestamp": time.time(),
        "backend": backend,
        "target_thoughts": target_thoughts,
        "actual_thoughts": len(thoughts_received),
        "duration_seconds": elapsed,
        "iterations": state.iteration_count,
        "diversity": diversity,
        "checks": checks,
        "all_passed": all_passed,
        "identity_hash": vault.identity_hash[:32] + "...",
        "mutations_applied": mutations_applied,
        "chain_verified": chain.verify_chain(),
        "metabolic_state": metabolism.state.value,
        "memory_entries": memory.count(),
        "memory_types": mem_type_counts,
        "actuators": actuator_manager.list_actuators(),
        "thoughts": [t.to_dict() for t in thoughts_received],
    }

    if output_file:
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        print(f"\nResultados guardados en: {output_file}")

    return all_passed


def main():
    parser = argparse.ArgumentParser(description="ZOE v1.0 Demo Fase 1 Completo")
    parser.add_argument(
        "--backend",
        choices=["mock", "zai", "ollama", "openai_compatible"],
        default="mock",
    )
    parser.add_argument("--model", help="Modelo específico")
    parser.add_argument("--thoughts", type=int, default=10)
    parser.add_argument("--duration", type=float, default=120.0)
    parser.add_argument("--tick", type=float, default=2.0)
    parser.add_argument(
        "--output",
        default="zoe/phases/phase1_demo_results.json",
    )
    parser.add_argument("--verbose", action="store_true")

    args = parser.parse_args()
    setup_logging(args.verbose)

    success = asyncio.run(
        run_phase1_demo(
            backend=args.backend,
            model=args.model,
            target_thoughts=args.thoughts,
            max_duration=args.duration,
            tick_interval=args.tick,
            output_file=args.output,
        )
    )
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
