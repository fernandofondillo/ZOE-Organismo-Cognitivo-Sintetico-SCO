"""
ZOE — Prometheus Metrics Module

Módulo de métricas en formato Prometheus text exposition.
SOLO depende de la stdlib (threading.Lock).

Métricas expuestas:
- zoe_requests_total — Contador de requests por método/endpoint/status
- zoe_request_duration_seconds — Histograma de latencia de requests
- zoe_cognitive_loop_iterations_total — Contador de iteraciones del bucle
- zoe_memory_entries_total — Gauge de entradas en memoria
- zoe_metabolism_state — Gauge del estado metabólico
- zoe_llm_requests_total — Contador de requests al LLM por backend
- zoe_llm_request_duration_seconds — Histograma de latencia del LLM
- zoe_active_capsules — Gauge de cápsulas activas

Uso:
    from zoe.core.metrics import (
        inc_requests_total, observe_request_duration,
        inc_cognitive_loop_iterations, set_memory_entries,
        set_metabolism_state, inc_llm_requests, observe_llm_duration,
        set_active_capsules, generate_metrics,
    )
"""

from __future__ import annotations

import threading
import time
from collections import defaultdict
from typing import Dict, List, Tuple

# ============================================================================
# Thread-safe storage
# ============================================================================

_lock = threading.Lock()

# --- Counters: {label_tuple -> value} ---
_requests_total: Dict[Tuple[str, ...], int] = defaultdict(int)
_cognitive_loop_iterations_total: int = 0
_llm_requests_total: Dict[Tuple[str, ...], int] = defaultdict(int)

# --- Gauges: {label -> value} ---
_memory_entries_total: int = 0
_metabolism_state_value: int = 0  # 0=AWAKE, 1=DROWSY, 2=SLEEPING, 3=WAKING
_active_capsules_value: int = 0

# --- Histogram buckets (in seconds) ---
_BUCKETS = [0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, float("inf")]
_request_duration_buckets: Dict[Tuple[str, ...], List[int]] = defaultdict(lambda: [0] * len(_BUCKETS))
_llm_duration_buckets: Dict[Tuple[str, ...], List[int]] = defaultdict(lambda: [0] * len(_BUCKETS))

_request_duration_sum: Dict[Tuple[str, ...], float] = defaultdict(float)
_request_duration_count: Dict[Tuple[str, ...], int] = defaultdict(int)
_llm_duration_sum: Dict[Tuple[str, ...], float] = defaultdict(float)
_llm_duration_count: Dict[Tuple[str, ...], int] = defaultdict(int)

# --- Start time for process uptime ---
_start_time: float = time.time()

# ============================================================================
# Public API: increment/set/observe functions
# ============================================================================


def inc_requests_total(method: str, endpoint: str, status: str) -> None:
    """Incrementa el contador de requests."""
    key = (method, endpoint, status)
    with _lock:
        _requests_total[key] += 1


def observe_request_duration(method: str, endpoint: str, duration_seconds: float) -> None:
    """Registra la duración de un request en el histograma."""
    key = (method, endpoint)
    with _lock:
        _request_duration_sum[key] += duration_seconds
        _request_duration_count[key] += 1
        for i, bucket in enumerate(_BUCKETS):
            if duration_seconds <= bucket:
                _request_duration_buckets[key][i] += 1
                break


def inc_cognitive_loop_iterations(count: int = 1) -> None:
    """Incrementa el contador de iteraciones del cognitive loop."""
    global _cognitive_loop_iterations_total
    with _lock:
        _cognitive_loop_iterations_total += count


def set_memory_entries(count: int) -> None:
    """Establece el número de entradas en memoria."""
    global _memory_entries_total
    with _lock:
        _memory_entries_total = count


def set_metabolism_state(state: str) -> None:
    """
    Establece el estado metabólico como entero.
    0=AWAKE, 1=DROWSY, 2=SLEEPING, 3=WAKING
    """
    global _metabolism_state_value
    state_map = {
        "awake": 0,
        "drowsy": 1,
        "sleeping": 2,
        "waking": 3,
    }
    with _lock:
        _metabolism_state_value = state_map.get(state.lower(), 0)


def inc_llm_requests(backend: str) -> None:
    """Incrementa el contador de requests al LLM."""
    key = (backend,)
    with _lock:
        _llm_requests_total[key] += 1


def observe_llm_duration(backend: str, duration_seconds: float) -> None:
    """Registra la duración de un request al LLM."""
    key = (backend,)
    with _lock:
        _llm_duration_sum[key] += duration_seconds
        _llm_duration_count[key] += 1
        for i, bucket in enumerate(_BUCKETS):
            if duration_seconds <= bucket:
                _llm_duration_buckets[key][i] += 1
                break


def set_active_capsules(count: int) -> None:
    """Establece el número de cápsulas activas."""
    global _active_capsules_value
    with _lock:
        _active_capsules_value = count


# ============================================================================
# generate_metrics: Prometheus text exposition format
# ============================================================================


def _format_labels(label_names: List[str], label_values: Tuple[str, ...]) -> str:
    """Formatea labels como {name1=\"val1\",name2=\"val2\"}."""
    if not label_names:
        return ""
    pairs = [f'{name}="{value}"' for name, value in zip(label_names, label_values)]
    return "{" + ",".join(pairs) + "}"


def generate_metrics() -> str:
    """
    Genera un string con todas las métricas en formato Prometheus text.

    Returns:
        String en formato Prometheus exposition (text/plain).
    """
    lines: List[str] = []

    with _lock:
        # --- process uptime ---
        uptime = time.time() - _start_time
        lines.append(f"# HELP zoe_process_uptime_seconds Total process uptime in seconds")
        lines.append(f"# TYPE zoe_process_uptime_seconds gauge")
        lines.append(f"zoe_process_uptime_seconds {uptime:.3f}")
        lines.append("")

        # --- zoe_requests_total ---
        lines.append("# HELP zoe_requests_total Total HTTP requests")
        lines.append("# TYPE zoe_requests_total counter")
        if _requests_total:
            for (method, endpoint, status), value in sorted(_requests_total.items()):
                labels = _format_labels(["method", "endpoint", "status"], (method, endpoint, status))
                lines.append(f"zoe_requests_total{labels} {value}")
        else:
            lines.append("zoe_requests_total 0")
        lines.append("")

        # --- zoe_request_duration_seconds (histogram) ---
        lines.append("# HELP zoe_request_duration_seconds HTTP request latency")
        lines.append("# TYPE zoe_request_duration_seconds histogram")
        for key in sorted(_request_duration_buckets.keys()):
            method, endpoint = key
            labels_base = _format_labels(["method", "endpoint"], (method, endpoint))
            for i, bucket in enumerate(_BUCKETS):
                if bucket == float("inf"):
                    bucket_labels = f'{{method="{method}",endpoint="{endpoint}",le="+Inf"}}'
                else:
                    bucket_labels = f'{{method="{method}",endpoint="{endpoint}",le="{bucket}"}}'
                lines.append(f"zoe_request_duration_seconds_bucket{bucket_labels} {_request_duration_buckets[key][i]}")
            lines.append(f"zoe_request_duration_seconds_sum{labels_base} {_request_duration_sum[key]:.6f}")
            lines.append(f"zoe_request_duration_seconds_count{labels_base} {_request_duration_count[key]}")
        lines.append("")

        # --- zoe_cognitive_loop_iterations_total ---
        lines.append("# HELP zoe_cognitive_loop_iterations_total Total cognitive loop iterations")
        lines.append("# TYPE zoe_cognitive_loop_iterations_total counter")
        lines.append(f"zoe_cognitive_loop_iterations_total {_cognitive_loop_iterations_total}")
        lines.append("")

        # --- zoe_memory_entries_total ---
        lines.append("# HELP zoe_memory_entries_total Current memory entries")
        lines.append("# TYPE zoe_memory_entries_total gauge")
        lines.append(f"zoe_memory_entries_total {_memory_entries_total}")
        lines.append("")

        # --- zoe_metabolism_state ---
        lines.append("# HELP zoe_metabolism_state Current metabolic state (0=AWAKE,1=DROWSY,2=SLEEPING,3=WAKING)")
        lines.append("# TYPE zoe_metabolism_state gauge")
        lines.append(f"zoe_metabolism_state {_metabolism_state_value}")
        lines.append("")

        # --- zoe_llm_requests_total ---
        lines.append("# HELP zoe_llm_requests_total Total LLM requests")
        lines.append("# TYPE zoe_llm_requests_total counter")
        if _llm_requests_total:
            for (backend,), value in sorted(_llm_requests_total.items()):
                labels = _format_labels(["backend"], (backend,))
                lines.append(f"zoe_llm_requests_total{labels} {value}")
        else:
            lines.append("zoe_llm_requests_total 0")
        lines.append("")

        # --- zoe_llm_request_duration_seconds (histogram) ---
        lines.append("# HELP zoe_llm_request_duration_seconds LLM request latency")
        lines.append("# TYPE zoe_llm_request_duration_seconds histogram")
        for key in sorted(_llm_duration_buckets.keys()):
            (backend,) = key
            labels_base = _format_labels(["backend"], (backend,))
            for i, bucket in enumerate(_BUCKETS):
                if bucket == float("inf"):
                    bucket_labels = f'{{backend="{backend}",le="+Inf"}}'
                else:
                    bucket_labels = f'{{backend="{backend}",le="{bucket}"}}'
                lines.append(f"zoe_llm_request_duration_seconds_bucket{bucket_labels} {_llm_duration_buckets[key][i]}")
            lines.append(f"zoe_llm_request_duration_seconds_sum{labels_base} {_llm_duration_sum[key]:.6f}")
            lines.append(f"zoe_llm_request_duration_seconds_count{labels_base} {_llm_duration_count[key]}")
        lines.append("")

        # --- zoe_active_capsules ---
        lines.append("# HELP zoe_active_capsules Currently active capsules")
        lines.append("# TYPE zoe_active_capsules gauge")
        lines.append(f"zoe_active_capsules {_active_capsules_value}")
        lines.append("")

    return "\n".join(lines)
