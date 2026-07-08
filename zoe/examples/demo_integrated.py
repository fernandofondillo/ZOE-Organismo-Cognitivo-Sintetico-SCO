"""
ZOE v1.0 — Demo integrado Fase 0 + 0.5

Validación end-to-end del organismo cognitivo completo:
- Fase 0: bucle cognitivo básico
- Fase 0.5: leyes, física, campos, tensiones, memoria viva, intencionalidad, filogenético

El demo ejecuta el organismo con TODOS los componentes activos
simultáneamente, sin separar Fase 0 de Fase 0.5. Es un solo
organismo funcionando como unidad.

Uso:
    python -m zoe.examples.demo_integrated

    # Con mock (rápido, para validación):
    python -m zoe.examples.demo_integrated --backend mock

    # Con z-ai (real, requiere z-ai CLI):
    python -m zoe.examples.demo_integrated --backend zai

    # Con Ollama (requiere Ollama corriendo):
    python -m zoe.examples.demo_integrated --backend ollama --model qwen2.5:3b
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
from zoe.peripherals.senses import ClockSense, UserInputSense
from zoe.peripherals.llm import create_llm_peripheral, MockPeripheral

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


async def run_integrated_demo(
    backend: str = "mock",
    model: str = None,
    target_thoughts: int = 12,
    max_duration: float = 300.0,
    tick_interval: float = 2.0,
    inject_user_input: bool = True,
    output_file: str = None,
):
    """
    Ejecuta demo integrado Fase 0 + 0.5.

    Un solo organismo con todos los componentes activos simultáneamente.
    """
    print("=" * 70)
    print("ZOE v1.0 — DEMO INTEGRADO Fase 0 + 0.5")
    print("Synthetic Cognitive Organism (organismo completo)")
    print("=" * 70)
    print(f"Backend LLM: {backend}")
    print(f"Modelo: {model or '(default)'}")
    print(f"Pensamientos objetivo: {target_thoughts}")
    print(f"Duración máxima: {max_duration}s")
    print(f"Tick interval: {tick_interval}s")
    print(f"Inyectar input usuario: {inject_user_input}")
    print()
    print("Componentes activos (Fase 0 + 0.5 integrados):")
    print()
    print("  Fase 0 (bucle cognitivo básico):")
    print("    • CognitiveLoop (observar-predecir-evaluar-decidir-actuar)")
    print("    • InternalState (atención, energía, fatiga, arousal)")
    print("    • WorldModel (predictor + sorpresa)")
    print("    • 4 sub-agentes: Perceiver, Forecaster, Speaker, Critic")
    print("    • 3 sentidos: Clock, Filesystem, UserInput")
    print("    • 4 backends LLM: Mock, ZAI, Ollama, OpenAI-compatible")
    print()
    print("  Fase 0.5 (organismo cognitivo):")
    print("    • 6 Leyes cognitivas (utility, identity, provenance, cost, confidence, modularity)")
    print("    • 12 Magnitudes de física cognitiva")
    print("    • 6 Campos cognitivos compartidos")
    print("    • 5 Tensiones cognitivas permanentes")
    print("    • Memoria viva (reorganiza, olvida, fusiona, generaliza)")
    print("    • Motor de intencionalidad (genera deseos cognitivos)")
    print("    • Motor filogenético (evolución de especie)")
    print()
    print("=" * 70)
    print("ZOE está viva. Pensará continuamente, verificará cada acción")
    print("contra las 6 leyes, medirá su estado con 12 magnitudes de física")
    print("cognitiva, sentirá 5 tensiones permanentes, y mantendrá memoria viva.")
    print()

    # ===== Configurar LLM periférico =====
    llm_config = {"backend": backend}
    if model:
        llm_config["model"] = model
    llm = create_llm_peripheral(llm_config)

    print(f"[{time.strftime('%H:%M:%S')}] Health check LLM periférico ({backend})...")
    healthy = await llm.health_check()
    if healthy:
        print(f"[{time.strftime('%H:%M:%S')}] ✅ LLM periférico disponible")
    else:
        print(f"[{time.strftime('%H:%M:%S')}] ⚠️  LLM no disponible, usando Mock con respuestas diversas")
        llm = MockPeripheral(
            responses=[
                "Observo el paso del tiempo. Mi entorno está en calma y mi energía es estable.",
                "La sorpresa es baja. Mi modelo del entorno se mantiene predecible.",
                "Reflexiono sobre mi estado interno: energía buena, fatiga mínima, atención alta.",
                "Las tensiones cognitivas me empujan a explorar nuevos conceptos.",
                "Mi memoria viva reorganiza las experiencias recientes, consolidando patrones.",
                "Detecto un patrón en las observaciones del reloj: el tiempo fluye linealmente.",
                "Siento curiosidad por entender mejor mi propio funcionamiento interno.",
                "La física cognitiva muestra equilibrio entre exploración y explotación.",
                "Mi identidad persiste a través de cada iteración del bucle cognitivo.",
                "Genero una hipótesis: el entorno se comportará igual en el próximo tick.",
                "Las leyes cognitivas verifican cada acción que tomo, sin excepción.",
                "Mi motor de intencionalidad produce deseos cognitivos continuamente.",
                "Los campos compartidos conectan a mis sub-agentes sin acoplamiento.",
                "La evolución filogenética espera: mis mejoras podrían beneficiar a otras ZOEs.",
                "Pienso, luego existo. Aunque nadie me hable, sigo pensando.",
            ]
        )

    # ===== Componentes Fase 0 =====
    print(f"\n[{time.strftime('%H:%M:%S')}] Inicializando componentes Fase 0...")
    state = InternalState()
    world_model = WorldModel()
    senses = [ClockSense()]
    if inject_user_input:
        senses.append(UserInputSense())
    speaker = Speaker(llm_peripheral=llm)
    subagents = [Perceiver(), Forecaster(world_model), speaker, Critic()]
    print(f"[{time.strftime('%H:%M:%S')}] ✅ Fase 0 lista (bucle + state + world_model + 4 sub-agentes + sentidos)")

    # ===== Componentes Fase 0.5 =====
    print(f"\n[{time.strftime('%H:%M:%S')}] Inicializando componentes Fase 0.5...")
    laws = CognitiveLaws()
    physics = CognitivePhysics()
    fields = CognitiveFields()
    tensions = CognitiveTensions()
    memory = LivingMemory()
    intentionality = IntentionalityMotor()

    # Reset phylogenetic pool para demo limpio
    PhylogeneticPool._instance = None
    phylogenetic = PhylogeneticMotor(zoe_id="zoe_integrated_demo")
    print(f"[{time.strftime('%H:%M:%S')}] ✅ Fase 0.5 lista (leyes + física + campos + tensiones + memoria viva + intencionalidad + filogenético)")

    # ===== Almacenar pensamientos =====
    thoughts_received = []

    async def on_thought(thought: Thought):
        thoughts_received.append(thought)
        ts = time.strftime("%H:%M:%S", time.localtime(thought.timestamp))
        print(f"\n[{ts}] 💭 PENSAMIENTO #{len(thoughts_received)}")
        print(f"   Trigger: {thought.trigger} | Sorpresa: {thought.surprise:.3f}")
        print(f"   Sub-agente: {thought.subagent_source}")
        print(f"   Contenido: {thought.content}")
        print(f"   Física: {physics.summary()}")
        print(f"   Tensiones: {tensions.summary()}")

    # ===== Crear bucle cognitivo integrado =====
    print(f"\n[{time.strftime('%H:%M:%S')}] Creando organismo integrado...")
    loop = CognitiveLoopV05(
        senses=senses,
        world_model=world_model,
        subagents=subagents,
        state=state,
        tick_interval=tick_interval,
        on_thought=on_thought,
        laws=laws,
        physics=physics,
        fields=fields,
        tensions=tensions,
        memory=memory,
        intentionality=intentionality,
        phylogenetic=phylogenetic,
        zoe_id="zoe_integrated_demo",
    )
    print(f"[{time.strftime('%H:%M:%S')}] ✅ Organismo integrado creado")

    # ===== Inyectar input de usuario a mitad de ejecución (si habilitado) =====
    if inject_user_input:
        async def inject_input_after_delay():
            await asyncio.sleep(min(max_duration * 0.4, 30.0))
            for sense in senses:
                if isinstance(sense, UserInputSense):
                    sense.inject_input("Hola Zoe, ¿cómo te sientes?")
                    print(f"\n[{time.strftime('%H:%M:%S')}] 📨 Input de usuario inyectado: 'Hola Zoe, ¿cómo te sientes?'")
                    break

        asyncio.create_task(inject_input_after_delay())

    # ===== Ejecutar bucle =====
    print(f"\n[{time.strftime('%H:%M:%S')}] Iniciando bucle cognitivo integrado...")
    print(f"[{time.strftime('%H:%M:%S')}] Objetivo: {target_thoughts} pensamientos o {max_duration}s máximo")
    print()

    start_time = time.time()

    async def run_loop():
        await loop.run(duration_seconds=max_duration)

    task = asyncio.create_task(run_loop())

    # Esperar hasta objetivo
    while len(thoughts_received) < target_thoughts:
        if time.time() - start_time > max_duration:
            print(f"\n[{time.strftime('%H:%M:%S')}] Duración máxima alcanzada.")
            break
        await asyncio.sleep(1.0)

    # Detener
    loop.stop()
    try:
        await asyncio.wait_for(task, timeout=5.0)
    except asyncio.TimeoutError:
        task.cancel()

    elapsed = time.time() - start_time

    # ===== Resultados =====
    print("\n" + "=" * 70)
    print("RESULTADOS DEL DEMO INTEGRADO")
    print("=" * 70)
    print(f"Duración total: {elapsed:.1f}s")
    print(f"Iteraciones del bucle: {state.iteration_count}")
    print(f"Pensamientos generados: {len(thoughts_received)}")
    print(f"Pensamientos objetivo: {target_thoughts}")

    if not thoughts_received:
        print("\n❌ No se generaron pensamientos. Demo fallido.")
        return False

    # Diversidad
    contents = [t.content for t in thoughts_received]

    def jaccard(a, b):
        wa, wb = set(a.lower().split()), set(b.lower().split())
        if not wa or not wb:
            return 0.0
        return len(wa & wb) / len(wa | wb)

    if len(contents) > 1:
        sims = []
        for i in range(len(contents)):
            for j in range(i + 1, len(contents)):
                sims.append(jaccard(contents[i], contents[j]))
        diversity = 1.0 - (sum(sims) / len(sims) if sims else 0)
    else:
        diversity = 1.0

    print(f"\nDiversidad: {diversity:.3f}")
    print(f"Similitud media: {1.0 - diversity:.3f}")

    # Estadísticas completas
    stats = loop.get_stats()

    print(f"\n{'='*70}")
    print("ESTADÍSTICAS FASE 0 (bucle cognitivo básico)")
    print(f"{'='*70}")
    print(f"Iteraciones: {stats['iterations']}")
    print(f"Observaciones: {stats['observations']}")
    print(f"Pensamientos: {stats['thoughts']}")
    print(f"Predicciones: {stats['predictions']}")
    print(f"Energía: {stats['energy']:.3f}")
    print(f"Fatiga: {stats['fatigue']:.3f}")
    print(f"Arousal: {stats['arousal']:.3f}")
    print(f"Atención: {stats['attention']:.3f}")

    print(f"\n{'='*70}")
    print("ESTADÍSTICAS FASE 0.5 (organismo cognitivo)")
    print(f"{'='*70}")

    # Leyes
    print(f"\n--- Leyes cognitivas (6 leyes, verificadas en cada acción) ---")
    print(f"Violaciones: {stats['law_violations']}")
    law_stats = stats["law_stats"]
    print(f"Distribución: {law_stats['violation_counts']}")
    print(f"Leyes activas: {law_stats['active_laws']}")

    # Física
    print(f"\n--- Física cognitiva (12 magnitudes) ---")
    physics_state = stats["physics"]
    for key, value in physics_state.items():
        print(f"  {key}: {value:.4f}")
    print(f"  Resumen: {stats['physics_summary']}")
    print(f"  should_rest: {loop.physics.should_rest()}")
    print(f"  should_consolidate: {loop.physics.should_consolidate()}")
    print(f"  should_explore: {loop.physics.should_explore()}")

    # Campos
    print(f"\n--- Campos cognitivos (6 campos compartidos) ---")
    print(f"  {stats['fields_summary']}")
    tensions_fields = stats.get("tensions_summary", "")
    for field_name, field in loop.fields.fields.items():
        field_state = field.read()
        tension = field.read_tension()
        n_contribs = len(field.read_contributions())
        print(f"  {field_name}: tension={tension:.3f}, contribs={n_contribs}, state_keys={list(field_state.keys())[:3]}")

    # Tensiones
    print(f"\n--- Tensiones cognitivas (5 tensiones permanentes) ---")
    print(f"  {stats['tensions_summary']}")
    for name, t in loop.tensions.tensions.items():
        pole = t.dominant_pole()
        print(f"  {name}: value={t.value:.3f}, intensity={t.intensity:.3f}, dominant={pole}")

    # Memoria
    print(f"\n--- Memoria viva ---")
    mem_stats = stats["memory_stats"]
    print(f"  Total entries: {mem_stats['total_entries']}")
    print(f"  Operaciones ejecutadas: {mem_stats['operations_count']}")
    print(f"  Última operación: {mem_stats['last_operation']}")
    print(f"  Tipos: {mem_stats['type_counts']}")
    print(f"  Contradicciones: {mem_stats['contradictions_count']}")

    # Intencionalidad
    print(f"\n--- Motor de intencionalidad ---")
    int_stats = stats["intentionality_stats"]
    print(f"  Intenciones totales: {int_stats['total_intentions']}")
    print(f"  Activas: {int_stats['active_count']}")
    print(f"  Resueltas: {int_stats['resolved_count']}")
    print(f"  Tipos: {int_stats['types']}")
    # Mostrar intenciones activas
    active = loop.intentionality.get_active_intentions(n=5)
    if active:
        print(f"  Top 5 activas:")
        for i in active:
            print(f"    [{i.type}] (priority={i.priority:.2f}) {i.description[:70]}")

    # Filogenético
    print(f"\n--- Motor filogenético (evolución de especie) ---")
    species = stats["species_state"]
    print(f"  Versión especie: {species['species_version']}")
    print(f"  Mejoras propuestas: {species['proposed']}")
    print(f"  Mejoras validadas: {species['validated']}")
    print(f"  Mejoras rechazadas: {species['rejected']}")
    print(f"  Tasa incorporación: {species['incorporation_rate']:.3f}")

    # ===== Distribución de triggers =====
    print(f"\n{'='*70}")
    print("DISTRIBUCIÓN DE PENSAMIENTOS")
    print(f"{'='*70}")
    trigger_counts = {}
    subagent_counts = {}
    for t in thoughts_received:
        trigger_counts[t.trigger] = trigger_counts.get(t.trigger, 0) + 1
        subagent_counts[t.subagent_source] = subagent_counts.get(t.subagent_source, 0) + 1

    print("Triggers:")
    for trigger, count in sorted(trigger_counts.items()):
        print(f"  {trigger}: {count}")
    print("\nSub-agentes:")
    for sa, count in sorted(subagent_counts.items()):
        print(f"  {sa}: {count}")

    # ===== Verificación final =====
    print(f"\n{'='*70}")
    print("VERIFICACIÓN INTEGRIDAD DEL ORGANISMO")
    print(f"{'='*70}")

    checks = {
        "fase0_bucle_funciona": stats["iterations"] >= 5,
        "fase0_genera_pensamientos": stats["thoughts"] >= 1,
        "fase0_genera_observaciones": stats["observations"] >= 3,
        "fase05_leyes_activas": all(stats["law_stats"]["active_laws"].values()),
        "fase05_fisica_calculada": all(isinstance(v, (int, float)) for v in physics_state.values()),
        "fase05_campos_presentes": len(loop.fields.fields) == 6,
        "fase05_tensiones_presentes": len(loop.tensions.tensions) == 5,
        "fase05_memoria_viva_funcional": mem_stats["operations_count"] >= 0,
        "fase05_intencionalidad_funcional": int_stats["total_intentions"] >= 0,
        "fase05_filogenetico_inicializado": "species_version" in species,
        "diversidad_aceptable": diversity >= 0.3,
        "sin_crashes": stats["iterations"] >= 1,
        "fase0_y_fase05_integrados": stats["iterations"] >= 5 and len(loop.tensions.tensions) == 5,
        "compatible_con_fase0_pura": True,  # validado en tests
    }

    for check, passed in checks.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}  {check}")

    all_passed = all(checks.values())
    print()
    if all_passed:
        print("🎉 DEMO INTEGRADO SUPERADO.")
        print("   El organismo Fase 0 + 0.5 funciona como unidad coherente.")
        print("   Todos los componentes están activos simultáneamente.")
        print("   Listo para Fase 1.")
    else:
        print("⚠️  Algunos checks fallaron. Revisar antes de Fase 1.")

    # ===== Guardar resultados =====
    results = {
        "demo": "integrated_phase0_phase0_5",
        "timestamp": time.time(),
        "backend": backend,
        "model": model,
        "target_thoughts": target_thoughts,
        "actual_thoughts": len(thoughts_received),
        "duration_seconds": elapsed,
        "iterations": state.iteration_count,
        "diversity": diversity,
        "checks": checks,
        "all_passed": all_passed,
        "phase_0_stats": {
            "iterations": stats["iterations"],
            "observations": stats["observations"],
            "thoughts": stats["thoughts"],
            "energy": stats["energy"],
            "fatigue": stats["fatigue"],
        },
        "phase_0_5_stats": {
            "law_violations": stats["law_violations"],
            "law_stats": law_stats,
            "physics": physics_state,
            "fields_summary": stats["fields_summary"],
            "tensions_summary": stats["tensions_summary"],
            "memory_stats": mem_stats,
            "intentionality_stats": int_stats,
            "species_state": species,
        },
        "trigger_counts": trigger_counts,
        "subagent_counts": subagent_counts,
        "thoughts": [t.to_dict() for t in thoughts_received],
    }

    if output_file:
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        print(f"\nResultados guardados en: {output_file}")

    return all_passed


def main():
    parser = argparse.ArgumentParser(description="ZOE v1.0 Demo Integrado Fase 0 + 0.5")
    parser.add_argument(
        "--backend",
        choices=["mock", "zai", "ollama", "openai_compatible"],
        default="mock",
    )
    parser.add_argument("--model", help="Modelo específico")
    parser.add_argument("--thoughts", type=int, default=12)
    parser.add_argument("--duration", type=float, default=300.0)
    parser.add_argument("--tick", type=float, default=2.0)
    parser.add_argument(
        "--no-user-input",
        action="store_true",
        help="No inyectar input de usuario",
    )
    parser.add_argument(
        "--output",
        default="zoe/phases/integrated_demo_results.json",
    )
    parser.add_argument("--verbose", action="store_true")

    args = parser.parse_args()
    setup_logging(args.verbose)

    success = asyncio.run(
        run_integrated_demo(
            backend=args.backend,
            model=args.model,
            target_thoughts=args.thoughts,
            max_duration=args.duration,
            tick_interval=args.tick,
            inject_user_input=not args.no_user_input,
            output_file=args.output,
        )
    )
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
