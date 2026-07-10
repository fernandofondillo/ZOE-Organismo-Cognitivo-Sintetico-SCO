"""
ZOE V1.3 — Model Optimizer (Fase 7F)

Resuelve el problema de RAM limitada (8GB MacBook Air) permitiendo
usar modelos locales grandes vía memory-mapped files (mmap) desde
el pendrive, sin cargar el modelo completo en RAM.

Cómo funciona:
1. Detecta RAM disponible del sistema
2. Recibe el tamaño del modelo deseado
3. Decide estrategia:
   - RAM suficiente → carga normal (rápido)
   - RAM ajustada → mmap + GPU offload parcial (medio)
   - RAM insuficiente → mmap completo desde pendrive (lento pero funciona)
   - Imposible local → sugiere cloud API
4. Configura parámetros óptimos: n_gpu_layers, mmap, num_ctx, threads

Estrategia Cognitive Memory Paging:
- El modelo vive en el pendrive como archivo GGUF
- llama.cpp (motor de Ollama) con mmap lo memory-mapea
- El SO solo carga en RAM las capas activas (~2-4GB)
- El resto se queda en el pendrive hasta que se necesita
- Es como la paginación de un SO: no toda la "memoria" está en RAM

Combinado con ACD:
- L0/L1 (rápido, simple) → modelo pequeño en RAM (3B)
- L2 (estándar) → modelo medio en RAM (7B)
- L3 (profundo) → modelo grande vía mmap (14B-72B, lento pero calidad máxima)
"""

from __future__ import annotations

import logging
import os
import platform
import subprocess
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class ModelFitStrategy(str, Enum):
    FULL_RAM = "full_ram"
    MMAP_PARTIAL = "mmap_partial"
    MMAP_FULL = "mmap_full"
    CLOUD_FALLBACK = "cloud_fallback"


@dataclass
class ModelSpec:
    name: str
    params_b: float
    size_q4_gb: float
    size_q8_gb: float
    min_ram_gb: float
    mmap_ram_gb: float
    recommended_for: str
    ollama_tag: str
    # Fase 7G: cuantizaciones avanzadas (importance matrix)
    # IQ2_M = ~30% del tamaño Q4, mantiene ~95% calidad
    # IQ3_XS = ~40% del tamaño Q4, mantiene ~97% calidad
    size_iq2_m_gb: float = 0.0       # 0 = no disponible, se calcula si no se especifica
    size_iq3_xs_gb: float = 0.0


def _iq2_size(q4_size: float) -> float:
    """Estima el tamaño IQ2_M como ~30% del Q4_K_M."""
    return round(q4_size * 0.30, 2)


def _iq3_size(q4_size: float) -> float:
    """Estima el tamaño IQ3_XS como ~40% del Q4_K_M."""
    return round(q4_size * 0.40, 2)


MODEL_CATALOG: List[ModelSpec] = [
    ModelSpec("qwen2.5:0.5b", 0.5, 0.5, 0.6, 1.0, 0.5, "L0", "qwen2.5:0.5b"),
    ModelSpec("qwen2.5:1.5b", 1.5, 1.2, 1.6, 2.0, 1.0, "L0-L1", "qwen2.5:1.5b"),
    ModelSpec("qwen2.5:3b", 3.0, 2.0, 3.2, 3.0, 1.5, "L0-L1", "qwen2.5:3b"),
    ModelSpec("qwen2.5:7b", 7.0, 4.5, 6.5, 6.0, 3.0, "L2", "qwen2.5:7b"),
    ModelSpec("qwen2.5:14b", 14.0, 8.0, 13.0, 10.0, 3.5, "L3", "qwen2.5:14b"),
    ModelSpec("qwen2.5:32b", 32.0, 18.0, 30.0, 20.0, 4.0, "L3", "qwen2.5:32b",
              size_iq2_m_gb=_iq2_size(18.0), size_iq3_xs_gb=_iq3_size(18.0)),
    ModelSpec("qwen2.5:72b", 72.0, 40.0, 72.0, 45.0, 5.0, "L3", "qwen2.5:72b",
              size_iq2_m_gb=_iq2_size(40.0), size_iq3_xs_gb=_iq3_size(40.0)),
    ModelSpec("llama3.2:1b", 1.0, 0.9, 1.2, 1.5, 0.8, "L0-L1", "llama3.2:1b"),
    ModelSpec("llama3.2:3b", 3.0, 2.0, 3.2, 3.0, 1.5, "L0-L1", "llama3.2:3b"),
    ModelSpec("llama3.1:8b", 8.0, 4.9, 7.5, 6.0, 3.0, "L2", "llama3.1:8b"),
    ModelSpec("llama3.1:70b", 70.0, 40.0, 70.0, 45.0, 5.0, "L3", "llama3.1:70b",
              size_iq2_m_gb=_iq2_size(40.0), size_iq3_xs_gb=_iq3_size(40.0)),
    ModelSpec("deepseek-r1:7b", 7.0, 4.5, 6.5, 6.0, 3.0, "L2", "deepseek-r1:7b"),
    ModelSpec("deepseek-r1:14b", 14.0, 8.0, 13.0, 10.0, 3.5, "L3", "deepseek-r1:14b"),
    ModelSpec("deepseek-r1:32b", 32.0, 18.0, 30.0, 20.0, 4.0, "L3", "deepseek-r1:32b",
              size_iq2_m_gb=_iq2_size(18.0), size_iq3_xs_gb=_iq3_size(18.0)),
    ModelSpec("phi4:14b", 14.0, 8.0, 13.0, 10.0, 3.5, "L3", "phi4:14b"),
    ModelSpec("gemma2:27b", 27.0, 16.0, 26.0, 18.0, 4.0, "L3", "gemma2:27b",
              size_iq2_m_gb=_iq2_size(16.0), size_iq3_xs_gb=_iq3_size(16.0)),
]


# Fase 7G: SSDs portátiles recomendados para el usuario final
RECOMMENDED_SSDS: List[Dict[str, Any]] = [
    {
        "model": "Crucial X10 Pro",
        "capacity_tb": 1,
        "read_speed_mbps": 2100,
        "price_eur": 110,
        "recommended": True,
        "why": "Equilibrado: pequeño, resistente, rápido. Recomendado por defecto.",
    },
    {
        "model": "Kingston XS2000",
        "capacity_tb": 1,
        "read_speed_mbps": 2000,
        "price_eur": 100,
        "recommended": False,
        "why": "El más económico, ultra compacto.",
    },
    {
        "model": "SanDisk PRO-BLADE Transport",
        "capacity_tb": 1,
        "read_speed_mbps": 2000,
        "price_eur": 160,
        "recommended": False,
        "why": "Línea profesional, diseño robusto.",
    },
]


# Fase 7G: Velocidades esperadas por modelo en MacBook Air M2/M3 8GB
# con SSD 2000 MB/s y cable USB-C correcto.
EXPECTED_TOKEN_RATES: List[Dict[str, Any]] = [
    {"model": "Qwen 2.5 3B", "quantization": "Q4_K_M", "ram_usage_gb": 2.5,
     "tokens_per_second_range": "25-35", "experience": "Más rápido de lo que lees", "strategy": "full_ram"},
    {"model": "Qwen 2.5 7B", "quantization": "Q4_K_M", "ram_usage_gb": 4.5,
     "tokens_per_second_range": "12-18", "experience": "Similar a ChatGPT gratuito", "strategy": "mmap_partial"},
    {"model": "Qwen 2.5 14B", "quantization": "Q4_K_M", "ram_usage_gb": 3.5,
     "tokens_per_second_range": "4-8", "experience": "Lectura pausada, ideal análisis", "strategy": "mmap_partial"},
    {"model": "Qwen 2.5 32B", "quantization": "IQ2_M", "ram_usage_gb": 3.0,
     "tokens_per_second_range": "3-6", "experience": "Análisis profundo en background", "strategy": "mmap_full"},
    {"model": "Qwen 2.5 72B", "quantization": "IQ2_M", "ram_usage_gb": 4.0,
     "tokens_per_second_range": "1-3", "experience": "Lento pero funcional", "strategy": "mmap_full"},
    {"model": "Llama 3.1 70B", "quantization": "IQ2_M", "ram_usage_gb": 4.0,
     "tokens_per_second_range": "1-3", "experience": "Lento pero funcional", "strategy": "mmap_full"},
]


@dataclass
class OptimizationResult:
    model_name: str
    strategy: ModelFitStrategy
    available_ram_gb: float
    model_size_gb: float
    estimated_ram_usage_gb: float
    n_gpu_layers: int
    use_mmap: bool
    num_threads: int
    num_ctx: int
    quantization: str
    will_work: bool
    estimated_speed: str
    warning: Optional[str] = None
    cloud_fallback_recommended: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_name": self.model_name,
            "strategy": self.strategy.value,
            "available_ram_gb": round(self.available_ram_gb, 1),
            "model_size_gb": round(self.model_size_gb, 1),
            "estimated_ram_usage_gb": round(self.estimated_ram_usage_gb, 1),
            "n_gpu_layers": self.n_gpu_layers,
            "use_mmap": self.use_mmap,
            "num_threads": self.num_threads,
            "num_ctx": self.num_ctx,
            "quantization": self.quantization,
            "will_work": self.will_work,
            "estimated_speed": self.estimated_speed,
            "warning": self.warning,
            "cloud_fallback_recommended": self.cloud_fallback_recommended,
        }


class ModelOptimizer:
    """
    Analiza el hardware disponible y recomienda la configuración óptima
    para cargar un modelo LLM, especialmente en sistemas con RAM limitada.
    """

    def __init__(self, models_dir: Optional[str] = None):
        self.models_dir = models_dir
        self._cached_ram = None
        self._cached_total_ram = None
        self._cached_cpu = None

    def detect_available_ram_gb(self) -> float:
        if self._cached_ram is not None:
            return self._cached_ram
        try:
            system = platform.system()
            if system == "Darwin":
                result = subprocess.run(["vm_stat"], capture_output=True, text=True, timeout=5)
                lines = result.stdout.strip().split("\n")
                for line in lines:
                    if "free" in line.lower() or "available" in line.lower():
                        num = int(line.split(":")[1].strip().rstrip("."))
                        self._cached_ram = (num * 4096) / (1024**3)
                        return self._cached_ram
                self._cached_ram = self.detect_total_ram_gb() * 0.6
                return self._cached_ram
            elif system == "Linux":
                with open("/proc/meminfo") as f:
                    for line in f:
                        if line.startswith("MemAvailable:"):
                            kb = int(line.split(":")[1].strip().split()[0])
                            self._cached_ram = kb / (1024**2)
                            return self._cached_ram
        except Exception as e:
            logger.warning(f"ModelOptimizer: RAM detection failed: {e}")
        self._cached_ram = 4.0
        return self._cached_ram

    def detect_total_ram_gb(self) -> float:
        if self._cached_total_ram is not None:
            return self._cached_total_ram
        try:
            system = platform.system()
            if system == "Darwin":
                result = subprocess.run(["sysctl", "-n", "hw.memsize"], capture_output=True, text=True, timeout=5)
                self._cached_total_ram = int(result.stdout.strip()) / (1024**3)
                return self._cached_total_ram
            elif system == "Linux":
                with open("/proc/meminfo") as f:
                    for line in f:
                        if line.startswith("MemTotal:"):
                            kb = int(line.split(":")[1].strip().split()[0])
                            self._cached_total_ram = kb / (1024**2)
                            return self._cached_total_ram
        except Exception:
            pass
        self._cached_total_ram = 8.0
        return self._cached_total_ram

    def detect_cpu_cores(self) -> int:
        if self._cached_cpu is not None:
            return self._cached_cpu
        try:
            self._cached_cpu = os.cpu_count() or 4
        except Exception:
            self._cached_cpu = 4
        return self._cached_cpu

    # ============================================================
    # Fase 7G: Detección de P-cores y E-cores en Apple Silicon
    # ============================================================

    def detect_p_cores(self) -> int:
        """
        Detecta el número de núcleos de rendimiento (P-cores) en Apple Silicon.

        En Apple Silicon (M1/M2/M3/M4), los cores se dividen en:
        - P-cores (performance, perflevel0): alta velocidad, alta potencia
        - E-cores (efficiency, perflevel1): baja velocidad, baja potencia

        Para LLM inference, usar E-cores DEGRADA el rendimiento porque
        los P-cores tienen que esperar a los E-cores más lentos.

        Por eso es CRÍTICO configurar OLLAMA_NUM_THREAD = P-cores (no total).

        Returns:
            Número de P-cores. En hardware sin distinción (Intel, AMD, Linux),
            devuelve el total de cores.
        """
        try:
            system = platform.system()
            if system == "Darwin":
                # macOS: hw.perflevel0 = P-cores, hw.perflevel1 = E-cores
                result = subprocess.run(
                    ["sysctl", "-n", "hw.perflevel0.physicalcpu"],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    p_cores = int(result.stdout.strip())
                    if p_cores > 0:
                        return p_cores
            # Linux/Intel/AMD: no hay distinción, devolver total
            return self.detect_cpu_cores()
        except Exception as e:
            logger.debug(f"ModelOptimizer: P-core detection failed: {e}")
            return self.detect_cpu_cores()

    def detect_e_cores(self) -> int:
        """
        Detecta el número de núcleos de eficiencia (E-cores) en Apple Silicon.

        Returns:
            Número de E-cores. En hardware sin distinción, devuelve 0.
        """
        try:
            system = platform.system()
            if system == "Darwin":
                result = subprocess.run(
                    ["sysctl", "-n", "hw.perflevel1.physicalcpu"],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    return int(result.stdout.strip())
            return 0
        except Exception:
            return 0

    def is_apple_silicon(self) -> bool:
        try:
            result = subprocess.run(["sysctl", "-n", "machdep.cpu.brand_string"], capture_output=True, text=True, timeout=5)
            brand = result.stdout.strip().lower()
            return any(chip in brand for chip in ["apple m", "m1", "m2", "m3", "m4"])
        except Exception:
            return False

    def get_model_spec(self, model_name: str) -> Optional[ModelSpec]:
        for spec in MODEL_CATALOG:
            if spec.name == model_name or spec.ollama_tag == model_name:
                return spec
        return None

    def list_models_for_ram(self, ram_gb: Optional[float] = None) -> List[Dict[str, Any]]:
        if ram_gb is None:
            ram_gb = self.detect_available_ram_gb()
        results = []
        for spec in MODEL_CATALOG:
            result = self.optimize(spec.name, ram_gb)
            if result.will_work:
                results.append({
                    "model": spec.name, "params": f"{spec.params_b}B",
                    "size_gb": spec.size_q4_gb, "strategy": result.strategy.value,
                    "speed": result.estimated_speed, "recommended_for": spec.recommended_for,
                    "ram_usage": round(result.estimated_ram_usage_gb, 1),
                })
        return results

    def optimize(self, model_name: str, available_ram_gb: Optional[float] = None) -> OptimizationResult:
        """
        Analiza el modelo + hardware y recomienda la configuración óptima.

        Fase 7G: añade soporte para cuantizaciones IQ2_M / IQ3_XS (importance
        matrix) cuando Q4_K_M no quepa pero la versión IQ sí. También usa
        P-cores (no total cores) para OLLAMA_NUM_THREAD en Apple Silicon.
        """
        if available_ram_gb is None:
            available_ram_gb = self.detect_available_ram_gb()
        spec = self.get_model_spec(model_name)
        if not spec:
            return self._optimize_unknown(model_name, available_ram_gb)

        # Fase 7G: usar P-cores en Apple Silicon (no total de cores)
        # En hardware sin distinción, detect_p_cores() devuelve el total.
        cpu_cores = self.detect_p_cores()
        is_apple = self.is_apple_silicon()
        quantization = "Q8" if available_ram_gb > spec.size_q8_gb * 2 else "Q4_K_M"
        model_size = spec.size_q8_gb if quantization == "Q8" else spec.size_q4_gb

        # FULL_RAM
        if model_size <= available_ram_gb * 0.8:
            return OptimizationResult(model_name, ModelFitStrategy.FULL_RAM, available_ram_gb,
                model_size, model_size, -1 if is_apple else 0, True, min(cpu_cores, 4),
                4096, quantization, True, "fast")

        # MMAP_PARTIAL
        if model_size <= available_ram_gb * 2.5:
            gpu_layers = int((available_ram_gb * 0.6) / model_size * 100)
            return OptimizationResult(model_name, ModelFitStrategy.MMAP_PARTIAL, available_ram_gb,
                model_size, available_ram_gb * 0.7, max(10, gpu_layers), True, min(cpu_cores, 6),
                2048, quantization, True, "medium",
                warning=f"Modelo {model_size:.1f}GB excede RAM ({available_ram_gb:.1f}GB). Usando mmap. Velocidad reducida.")

        # Fase 7G: si Q4_K_M no quepa pero IQ3_XS o IQ2_M sí, usarlas
        # IQ3_XS = ~40% del Q4, mantiene ~97% calidad
        # IQ2_M = ~30% del Q4, mantiene ~95% calidad
        iq3_size = spec.size_iq3_xs_gb if spec.size_iq3_xs_gb > 0 else _iq3_size(spec.size_q4_gb)
        iq2_size = spec.size_iq2_m_gb if spec.size_iq2_m_gb > 0 else _iq2_size(spec.size_q4_gb)

        # Intentar IQ3_XS primero (mejor calidad)
        if iq3_size > 0 and iq3_size <= available_ram_gb * 2.5 and iq3_size < model_size:
            return OptimizationResult(model_name, ModelFitStrategy.MMAP_PARTIAL, available_ram_gb,
                iq3_size, available_ram_gb * 0.7, max(10, int((available_ram_gb * 0.6) / iq3_size * 100)),
                True, min(cpu_cores, 6), 2048, "IQ3_XS", True, "medium",
                warning=f"Modelo {model_size:.1f}GB (Q4) no cabe. Usando IQ3_XS ({iq3_size:.1f}GB). ~97% calidad. mmap parcial.")

        # Intentar IQ2_M (más comprimido)
        if iq2_size > 0 and iq2_size <= available_ram_gb * 5 and iq2_size < model_size:
            speed = "slow" if iq2_size <= available_ram_gb * 2.5 else "very_slow"
            strategy = ModelFitStrategy.MMAP_PARTIAL if iq2_size <= available_ram_gb * 2.5 else ModelFitStrategy.MMAP_FULL
            return OptimizationResult(model_name, strategy, available_ram_gb,
                iq2_size, available_ram_gb * 0.6, max(5, int(available_ram_gb * 0.4 / iq2_size * 100)),
                True, min(cpu_cores, 8), 1024, "IQ2_M", True, speed,
                warning=f"Modelo {model_size:.1f}GB (Q4) no cabe. Usando IQ2_M ({iq2_size:.1f}GB). ~95% calidad. mmap.",
                cloud_fallback_recommended="openai_compatible" if iq2_size > 20 else None)

        # MMAP_FULL con Q4_K_M
        if model_size <= available_ram_gb * 10:
            speed = "slow" if model_size <= available_ram_gb * 5 else "very_slow"
            return OptimizationResult(model_name, ModelFitStrategy.MMAP_FULL, available_ram_gb,
                model_size, available_ram_gb * 0.6,
                max(5, int(available_ram_gb * 0.4 / model_size * 100)), True, min(cpu_cores, 8),
                1024, "Q4_K_M", True, speed,
                warning=f"Modelo {model_size:.1f}GB es {model_size/available_ram_gb:.1f}x tu RAM. Funciona vía paging pero será LENTO.",
                cloud_fallback_recommended="openai_compatible" if model_size > 20 else None)

        # CLOUD_FALLBACK
        return OptimizationResult(model_name, ModelFitStrategy.CLOUD_FALLBACK, available_ram_gb,
            model_size, 0, 0, False, cpu_cores, 4096, "Q4_K_M", False, "impossible",
            warning=f"Modelo {model_size:.1f}GB demasiado grande para {available_ram_gb:.1f}GB RAM. Usa cloud API.",
            cloud_fallback_recommended="openai_compatible")

    def _optimize_unknown(self, model_name: str, ram_gb: float) -> OptimizationResult:
        import re
        match = re.search(r'(\d+(?:\.\d+)?)b', model_name.lower())
        size_q4 = float(match.group(1)) * 0.6 if match else 5.0
        if size_q4 <= ram_gb * 0.8:
            return OptimizationResult(model_name, ModelFitStrategy.FULL_RAM, ram_gb, size_q4, size_q4,
                -1 if self.is_apple_silicon() else 0, True, min(self.detect_cpu_cores(), 4), 2048, "Q4_K_M", True, "fast")
        elif size_q4 <= ram_gb * 2.5:
            return OptimizationResult(model_name, ModelFitStrategy.MMAP_PARTIAL, ram_gb, size_q4, ram_gb * 0.7,
                10, True, min(self.detect_cpu_cores(), 6), 2048, "Q4_K_M", True, "medium",
                warning=f"Modelo estimado {size_q4:.1f}GB. mmap parcial.")
        elif size_q4 <= ram_gb * 10:
            return OptimizationResult(model_name, ModelFitStrategy.MMAP_FULL, ram_gb, size_q4, ram_gb * 0.6,
                5, True, min(self.detect_cpu_cores(), 8), 1024, "Q4_K_M", True, "slow",
                warning=f"Modelo estimado {size_q4:.1f}GB. mmap completo. Lento.")
        return OptimizationResult(model_name, ModelFitStrategy.CLOUD_FALLBACK, ram_gb, size_q4, 0,
            0, False, self.detect_cpu_cores(), 4096, "Q4_K_M", False, "impossible",
            warning="Demasiado grande. Usar cloud API.", cloud_fallback_recommended="openai_compatible")

    def recommend_for_acd(self, ram_gb: Optional[float] = None) -> Dict[str, Any]:
        if ram_gb is None:
            ram_gb = self.detect_available_ram_gb()
        recommendations = {}
        for level in ["L0", "L1", "L2", "L3"]:
            best = None
            best_score = -1
            for spec in MODEL_CATALOG:
                if level == "L0" and spec.recommended_for not in ("L0", "L0-L1"): continue
                if level == "L1" and spec.recommended_for not in ("L1", "L0-L1"): continue
                if level == "L2" and spec.recommended_for != "L2": continue
                if level == "L3" and spec.recommended_for != "L3": continue
                result = self.optimize(spec.name, ram_gb)
                if result.will_work:
                    score = spec.params_b + (10 if result.estimated_speed == "fast" else 5 if result.estimated_speed == "medium" else 1)
                    if score > best_score:
                        best_score = score
                        best = {"model": spec.name, "params": f"{spec.params_b}B", "strategy": result.strategy.value,
                                "speed": result.estimated_speed, "ram_usage": round(result.estimated_ram_usage_gb, 1)}
            recommendations[level] = best or {"model": "cloud_api", "params": "N/A", "strategy": "cloud_fallback", "speed": "fast (network)", "ram_usage": 0}
        return {"available_ram_gb": round(ram_gb, 1), "total_ram_gb": round(self.detect_total_ram_gb(), 1),
                "is_apple_silicon": self.is_apple_silicon(), "cpu_cores": self.detect_cpu_cores(), "recommendations": recommendations}

    def generate_ollama_env(self, result: OptimizationResult) -> Dict[str, str]:
        """
        Genera variables de entorno óptimas para Ollama según el resultado.

        Fase 7G: OLLAMA_FLASH_ATTENTION=1 siempre activo (no solo MMAP_FULL),
        y OLLAMA_NUM_THREAD configurado a P-cores en Apple Silicon.
        """
        env = {}
        if self.models_dir:
            env["OLLAMA_MODELS"] = self.models_dir
        env["OLLAMA_MAX_LOADED_MODELS"] = "1"
        env["OLLAMA_NUM_PARALLEL"] = "1"

        # Fase 7G: Flash Attention SIEMPRE activo (mejora rendimiento en
        # contextos largos, sin downside en contextos cortos)
        env["OLLAMA_FLASH_ATTENTION"] = "1"

        # Fase 7G: número de threads = P-cores en Apple Silicon
        # (usar total de cores DEGRADA rendimiento porque E-cores más lentos
        # obligan a P-cores a esperar)
        p_cores = self.detect_p_cores()
        if p_cores > 0:
            env["OLLAMA_NUM_THREAD"] = str(p_cores)

        if result.strategy == ModelFitStrategy.MMAP_PARTIAL:
            env["OLLAMA_KEEP_ALIVE"] = "30m"
        elif result.strategy == ModelFitStrategy.MMAP_FULL:
            env["OLLAMA_KEEP_ALIVE"] = "60m"

        return env

    def get_system_info(self) -> Dict[str, Any]:
        """
        Info del sistema con detalles Fase 7G (P-cores, E-cores).
        """
        return {
            "platform": platform.system(),
            "machine": platform.machine(),
            "is_apple_silicon": self.is_apple_silicon(),
            "total_ram_gb": round(self.detect_total_ram_gb(), 1),
            "available_ram_gb": round(self.detect_available_ram_gb(), 1),
            "cpu_cores": self.detect_cpu_cores(),
            # Fase 7G
            "p_cores": self.detect_p_cores(),
            "e_cores": self.detect_e_cores(),
        }

    # ============================================================
    # Fase 7G: APIs de información para usuarios finales
    # ============================================================

    @staticmethod
    def get_recommended_ssds() -> List[Dict[str, Any]]:
        """
        Devuelve la lista de SSDs portátiles recomendados para el usuario final.

        Estos son SSDs comerciales "todo en uno" de fábrica, con velocidades
        de 2000 MB/s vía USB-C, ideales para ejecutar modelos LLM grandes
        desde un MacBook Air de 8GB vía mmap.
        """
        return list(RECOMMENDED_SSDS)

    @staticmethod
    def get_expected_token_rates() -> List[Dict[str, Any]]:
        """
        Devuelve la tabla de velocidades esperadas (tokens/segundo) por modelo
        en un MacBook Air M2/M3 8GB con SSD de 2000 MB/s y cable USB-C correcto.

        Útil para gestionar expectativas del usuario antes de instalar un modelo.
        """
        return list(EXPECTED_TOKEN_RATES)

    @staticmethod
    def get_cable_warning() -> Dict[str, str]:
        """
        Devuelve el warning sobre el cable USB-C que DEBE usar el usuario.

        El cable de carga del MacBook Air es USB 2.0 (480 Mbps) y limita el
        SSD a 60 MB/s. El cable corto que viene en la caja del SSD es
        USB 3.2 Gen 2 (10 Gbps) y permite los 2000 MB/s reales.
        """
        return {
            "title": "Usa SIEMPRE el cable corto que viene en la caja del SSD",
            "problem": "El cable largo de carga del MacBook Air es USB 2.0 (480 Mbps) y limita el SSD a ~60 MB/s.",
            "solution": "Usa el cable corto USB 3.2 Gen 2 (10 Gbps) que viene dentro de la caja del SSD.",
            "symptom_slow": "ZOE tarda 10+ segundos en responder y la primera palabra aparece muy lenta.",
            "symptom_fast": "ZOE responde en 1-2 segundos y el texto fluye rápido.",
            "impact_factor": "10x",  # el cable equivocado es 10x más lento
        }
