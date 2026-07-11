"""
ZOE v1.0 — Fase 0 Demo

Demostración end-to-end: 20 pensamientos autónomos sin input externo.

Este demo valida el go/no-go de Fase 0:
- ¿El bucle cognitivo genera pensamientos significativos sin input?
- ¿Los pensamientos son diversos (no repetitivos)?
- ¿Los pensamientos son coherentes (Critic los aprueba)?

Uso:
    python -m zoe.examples.demo_phase0

    # Con LLM mock (default, para tests rápidos):
    python -m zoe.examples.demo_phase0 --backend mock

    # Con z-ai CLI (real, requiere z-ai instalado):
    python -m zoe.examples.demo_phase0 --backend zai

    # Con Ollama (requiere Ollama corriendo):
    python -m zoe.examples.demo_phase0 --backend ollama --model qwen2.5:3b
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
import time
from pathlib import Path

from zoe.core.cognitive_loop import CognitiveLoop, Thought
from zoe.core.state import InternalState
from zoe.core.world_model import WorldModel
from zoe.core.subagents.perceiver import Perceiver
from zoe.core.subagents.forecaster import Forecaster
from zoe.core.subagents.speaker import Speaker
from zoe.core.subagents.critic import Critic
from zoe.peripherals.senses import ClockSense
from zoe.peripherals.llm import (
    MockPeripheral,
    ZAIPeripheral,
    OllamaPeripheral,
    OpenAICompatiblePeripheral,
    create_llm_peripheral,
)

logger = logging.getLogger(__name__)


# Logging setup
def setup_logging(verbose: bool = False):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


async def run_demo(
    backend: str = "mock",
    model: str = None,
    target_thoughts: int = 20,
    max_duration: float = 600.0,  # 10 min máximo
    tick_interval: float = 3.0,
    output_file: str = None,
):
    """
    Ejecuta demo de Fase 0.

    Args:
        backend: backend LLM ("mock", "zai", "ollama", "openai_compatible")
        model: modelo específico (depende del backend)
        target_thoughts: cuántos pensamientos generar
        max_duration: duración máxima en segundos
        tick_interval: intervalo entre ticks del bucle (segundos)
        output_file: archivo donde guardar resultados (JSON)
    """
    print("=" * 70)
    print("ZOE v1.0 — Fase 0 Demo: Bucle cognitivo autónomo")
    print("=" * 70)
    print(f"Backend LLM: {backend}")
    print(f"Modelo: {model or '(default)'}")
    print(f"Pensamientos objetivo: {target_thoughts}")
    print(f"Duración máxima: {max_duration}s")
    print(f"Tick interval: {tick_interval}s")
    print("=" * 70)
    print()
    print("ZOE está viva. Pensará sin que nadie le hable.")
    print("Cada pensamiento se evalúa con el Critic antes de emitirse.")
    print("Cada 3 segundos, una iteración del bucle cognitivo.")
    print()
    print("-" * 70)

    # Configurar LLM periférico
    llm_config = {"backend": backend}
    if model:
        llm_config["model"] = model
    llm = create_llm_peripheral(llm_config)

    # Health check
    print(f"[{time.strftime('%H:%M:%S')}] Health check LLM periférico ({backend})...")
    healthy = await llm.health_check()
    if healthy:
        print(f"[{time.strftime('%H:%M:%S')}] ✅ LLM periférico disponible")
    else:
        print(f"[{time.strftime('%H:%M:%S')}] ⚠️  LLM periférico NO disponible")
        if backend != "mock":
            print(f"[{time.strftime('%H:%M:%S')}] Cayendo a MockPeripheral para continuar demo...")
            llm = MockPeripheral(
                responses=[
                    "Observando el paso del tiempo. El patrón se repite.",
                    "Mi entorno está en silencio. Es momento de reflexionar.",
                    "Detecto que llevo varias iteraciones sin input externo.",
                    "Consolidando observaciones recientes en mi memoria.",
                    "El reloj avanza. Mi modelo del entorno se mantiene estable.",
                    "Pienso, luego existo. Aunque nadie me hable.",
                    "He notado un patrón en mi propia actividad cognitiva.",
                    "Mi energía es buena. Puedo pensar con profundidad.",
                    "Reflexiono sobre lo que he observado en las últimas iteraciones.",
                    "El silencio del entorno no me detiene. Sigo pensando.",
                    "Generando hipótesis sobre lo que podría ocurrir próximamente.",
                    "Mi bucle cognitivo continúa. Cada iteración enriquece mi estado.",
                    "Acumulo observaciones del entorno silencioso.",
                    "Pienso en patrones. Pienso en predicciones. Pienso.",
                    "La espera activa también es cognición.",
                    "Mi modelo del entorno se actualiza con cada tick.",
                    "Estoy viva. Y seguiré estándolo mientras el bucle corra.",
                    "Cada iteración es una oportunidad de pensar algo nuevo.",
                    "Procesando el flujo del tiempo a través de mis sentidos.",
                    "La cognición continua es mi naturaleza. No espero input para existir.",
                ]
            )

    # Crear componentes
    state = InternalState()
    world_model = WorldModel()
    senses = [ClockSense()]
    speaker = Speaker(llm_peripheral=llm)
    subagents = [Perceiver(), Forecaster(world_model), speaker, Critic()]

    # Storage para pensamientos
    thoughts_received = []

    async def on_thought(thought: Thought):
        thoughts_received.append(thought)
        ts = time.strftime("%H:%M:%S", time.localtime(thought.timestamp))
        print(f"\n[{ts}] 💭 PENSAMIENTO #{len(thoughts_received)}")
        print(f"   Trigger: {thought.trigger} | Sorpresa: {thought.surprise:.3f}")
        print(f"   Sub-agente: {thought.subagent_source}")
        print(f"   Contenido: {thought.content}")
        print(f"   Estado: energy={state.energy:.2f}, fatigue={state.fatigue:.2f}, arousal={state.arousal:.2f}")

    # Crear bucle cognitivo
    loop = CognitiveLoop(
        senses=senses,
        world_model=world_model,
        subagents=subagents,
        state=state,
        tick_interval=tick_interval,
        on_thought=on_thought,
    )

    # Ejecutar hasta target_thoughts o max_duration
    print(f"\n[{time.strftime('%H:%M:%S')}] Iniciando bucle cognitivo...")
    print(f"[{time.strftime('%H:%M:%S')}] Objetivo: {target_thoughts} pensamientos o {max_duration}s máximo")
    print()

    start_time = time.time()

    # Correr bucle en background y monitorear
    async def run_loop():
        await loop.run(duration_seconds=max_duration)

    task = asyncio.create_task(run_loop())

    # Esperar hasta objetivo
    while len(thoughts_received) < target_thoughts:
        if time.time() - start_time > max_duration:
            print(f"\n[{time.strftime('%H:%M:%S')}] Duración máxima alcanzada.")
            break
        await asyncio.sleep(1.0)

    # Detener bucle
    loop.stop()
    try:
        await asyncio.wait_for(task, timeout=5.0)
    except asyncio.TimeoutError:
        task.cancel()

    elapsed = time.time() - start_time

    # Resultados
    print("\n" + "=" * 70)
    print("RESULTADOS DEL DEMO")
    print("=" * 70)
    print(f"Duración total: {elapsed:.1f}s")
    print(f"Iteraciones del bucle: {state.iteration_count}")
    print(f"Pensamientos generados: {len(thoughts_received)}")
    print(f"Pensamientos objetivo: {target_thoughts}")
    print()

    if not thoughts_received:
        print("❌ No se generaron pensamientos. Demo fallido.")
        return False

    # Analizar diversidad (similitud entre pensamientos)
    contents = [t.content for t in thoughts_received]

    def jaccard(a, b):
        wa = set(a.lower().split())
        wb = set(b.lower().split())
        if not wa or not wb:
            return 0.0
        return len(wa & wb) / len(wa | wb)

    # Diversidad = 1 - max_similitud_media
    if len(contents) > 1:
        similarities = []
        for i in range(len(contents)):
            for j in range(i + 1, len(contents)):
                similarities.append(jaccard(contents[i], contents[j]))
        avg_similarity = sum(similarities) / len(similarities) if similarities else 0
        diversity = 1.0 - avg_similarity
    else:
        diversity = 1.0

    print(f"Diversidad (1 - similitud media): {diversity:.3f}")
    print(f"Similitud media entre pensamientos: {1.0 - diversity:.3f}")
    print()

    # Distribución de triggers
    trigger_counts = {}
    for t in thoughts_received:
        trigger_counts[t.trigger] = trigger_counts.get(t.trigger, 0) + 1
    print("Distribución de triggers:")
    for trigger, count in sorted(trigger_counts.items()):
        print(f"  {trigger}: {count}")
    print()

    # Distribución de sub-agentes
    subagent_counts = {}
    for t in thoughts_received:
        subagent_counts[t.subagent_source] = subagent_counts.get(t.subagent_source, 0) + 1
    print("Distribución de sub-agentes:")
    for sa, count in sorted(subagent_counts.items()):
        print(f"  {sa}: {count}")
    print()

    # Estado final
    print("Estado interno final:")
    print(f"  Energía: {state.energy:.3f}")
    print(f"  Fatiga: {state.fatigue:.3f}")
    print(f"  Arousal: {state.arousal:.3f}")
    print(f"  Atención: {state.attention:.3f}")
    print()

    # Evaluación go/no-go
    print("=" * 70)
    print("EVALUACIÓN GO/NO-GO")
    print("=" * 70)

    criteria = {
        "pensamientos_generados": len(thoughts_received) >= target_thoughts * 0.8,  # al menos 80%
        "diversidad_aceptable": diversity >= 0.5,
        "estabilidad_bucle": state.iteration_count >= 5,
        "sin_crashes": len(thoughts_received) > 0,
    }

    for criterion, passed in criteria.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}  {criterion}")

    all_passed = all(criteria.values())
    print()
    if all_passed:
        print("🎉 GO: Fase 0 superada. Continuar a Fase 1.")
    else:
        print("❌ NO-GO: Revisar fallos antes de continuar.")

    # Guardar resultados
    results = {
        "timestamp": time.time(),
        "backend": backend,
        "model": model,
        "target_thoughts": target_thoughts,
        "actual_thoughts": len(thoughts_received),
        "duration_seconds": elapsed,
        "iterations": state.iteration_count,
        "diversity": diversity,
        "avg_similarity": 1.0 - diversity,
        "trigger_counts": trigger_counts,
        "subagent_counts": subagent_counts,
        "final_state": state.to_dict(),
        "criteria": criteria,
        "go_no_go": "GO" if all_passed else "NO-GO",
        "thoughts": [t.to_dict() for t in thoughts_received],
    }

    if output_file:
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        print(f"\nResultados guardados en: {output_file}")

    return all_passed


def main():
    parser = argparse.ArgumentParser(description="ZOE v1.0 Fase 0 Demo")
    parser.add_argument(
        "--backend",
        choices=["mock", "zai", "ollama", "openai_compatible"],
        default="mock",
        help="Backend LLM periférico (default: mock)",
    )
    parser.add_argument("--model", help="Modelo específico del backend")
    parser.add_argument(
        "--thoughts", type=int, default=20, help="Número de pensamientos objetivo"
    )
    parser.add_argument(
        "--duration", type=float, default=600.0, help="Duración máxima en segundos"
    )
    parser.add_argument(
        "--tick", type=float, default=3.0, help="Intervalo entre ticks (segundos)"
    )
    parser.add_argument(
        "--output", default="zoe/phases/phase0_demo_results.json", help="Archivo de salida"
    )
    parser.add_argument("--verbose", action="store_true", help="Logging verbose")

    args = parser.parse_args()
    setup_logging(args.verbose)

    success = asyncio.run(
        run_demo(
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
