"""
ZOE V1.3 — Resource Discovery Sense (Fase 7A)

Un nuevo sentido que descubre automáticamente qué recursos de cómputo
existen en el entorno: GPUs, CPUs, instancias Ollama en red, otros ZOEs,
cloud APIs configuradas, etc.

Construye un ResourceGraph que el metabolismo y el ModelOptimizer pueden
usar para decidir dónde ejecutar cada tarea cognitiva.

Sin desconstruir: es un sentido más, como ClockSense o NetworkSense.
No toca la arquitectura cognitiva.

Tipos de recursos que descubre:
1. Hardware local: CPU cores, RAM, Apple Silicon (Metal), NVIDIA GPU (CUDA)
2. Ollama instances: local (localhost:11434) y remotas en red local
3. Cloud APIs: OpenAI, Anthropic, DeepSeek, etc. (según env vars)
4. Otros ZOEs federados: vía federation peers
5. Almacenamiento: disco local, pendrive, NAS

El ResourceGraph se construye en segundos al iniciar ZOE y se actualiza
periódicamente.
"""

from __future__ import annotations

import asyncio
import logging
import os
import platform
import shutil
import subprocess
import time
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Set
from enum import Enum

logger = logging.getLogger(__name__)


class ResourceType(str, Enum):
    CPU = "cpu"
    GPU = "gpu"
    OLLAMA = "ollama"
    CLOUD_API = "cloud_api"
    ZOE_PEER = "zoe_peer"
    STORAGE = "storage"


@dataclass
class ResourceNode:
    """Un recurso descubierto en el entorno."""
    id: str
    type: ResourceType
    name: str
    address: str = ""  # IP:port o URL
    capabilities: Dict[str, Any] = field(default_factory=dict)
    available: bool = True
    last_seen: float = field(default_factory=time.time)
    latency_ms: Optional[float] = None
    cost_per_1k_tokens: float = 0.0  # EUR
    privacy_level: str = "local"  # local | network | cloud
    models: List[str] = field(default_factory=list)  # modelos disponibles

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ResourceGraph:
    """
    Grafo de recursos disponibles en el entorno.

    Mantiene un mapa de todos los recursos descubiertos y sus capacidades.
    El ModelOptimizer y el ResourcePlanner (futuro) lo usan para decidir
    dónde ejecutar cada tarea.
    """

    def __init__(self):
        self._nodes: Dict[str, ResourceNode] = {}
        self._last_scan: float = 0.0
        self._scan_count: int = 0

    def add_node(self, node: ResourceNode) -> None:
        self._nodes[node.id] = node
        logger.info(f"ResourceGraph: added {node.type.value} '{node.name}' at {node.address}")

    def remove_node(self, node_id: str) -> None:
        self._nodes.pop(node_id, None)

    def get_node(self, node_id: str) -> Optional[ResourceNode]:
        return self._nodes.get(node_id)

    def get_all(self) -> List[ResourceNode]:
        return list(self._nodes.values())

    def get_by_type(self, rtype: ResourceType) -> List[ResourceNode]:
        return [n for n in self._nodes.values() if n.type == rtype and n.available]

    def get_available_models(self) -> List[str]:
        """Devuelve todos los modelos disponibles en cualquier nodo."""
        models = set()
        for node in self._nodes.values():
            if node.available:
                models.update(node.models)
        return sorted(models)

    def get_ollama_nodes(self) -> List[ResourceNode]:
        return self.get_by_type(ResourceType.OLLAMA)

    def get_cloud_apis(self) -> List[ResourceNode]:
        return self.get_by_type(ResourceType.CLOUD_API)

    def get_local_hardware(self) -> List[ResourceNode]:
        return [n for n in self._nodes.values()
                if n.type in (ResourceType.CPU, ResourceType.GPU) and n.available]

    def get_zoe_peers(self) -> List[ResourceNode]:
        return self.get_by_type(ResourceType.ZOE_PEER)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodes": [n.to_dict() for n in self._nodes.values()],
            "node_count": len(self._nodes),
            "last_scan": self._last_scan,
            "scan_count": self._scan_count,
            "available_models": self.get_available_models(),
        }

    def get_stats(self) -> Dict[str, Any]:
        by_type = {}
        for node in self._nodes.values():
            by_type[node.type.value] = by_type.get(node.type.value, 0) + 1
        return {
            "total_nodes": len(self._nodes),
            "available_nodes": sum(1 for n in self._nodes.values() if n.available),
            "by_type": by_type,
            "available_models": len(self.get_available_models()),
            "last_scan": self._last_scan,
            "scan_count": self._scan_count,
        }


class ResourceDiscoverySense:
    """
    Sentido que descubre recursos de cómputo en el entorno.

    Ejecuta un scan al inicializar y luego scans periódicos.
    Los resultados se almacenan en un ResourceGraph.

    Uso:
        sense = ResourceDiscoverySense()
        graph = await sense.observe()  # devuelve ResourceGraph
    """

    DEFAULT_OLLAMA_PORTS = [11434]
    SCAN_INTERVAL = 60  # segundos entre scans automáticos

    def __init__(self, scan_interval: int = None):
        self.scan_interval = scan_interval or self.SCAN_INTERVAL
        self.graph = ResourceGraph()
        self._last_scan_time = 0.0
        self._scans_performed = 0

    async def observe(self) -> List[Any]:
        """
        Ejecuta un scan completo y devuelve observaciones.

        Returns:
            Lista de Observation objects (compatibles con el bucle cognitivo)
        """
        from ..core.cognitive_loop import Observation

        observations = []
        scan_start = time.time()

        # 1. Hardware local
        hw_results = self._scan_hardware()
        for node in hw_results:
            self.graph.add_node(node)

        # 2. Ollama local
        ollama_local = self._scan_ollama_local()
        if ollama_local:
            self.graph.add_node(ollama_local)

        # 3. Cloud APIs configuradas
        cloud_results = self._scan_cloud_apis()
        for node in cloud_results:
            self.graph.add_node(node)

        # 4. Almacenamiento
        storage_results = self._scan_storage()
        for node in storage_results:
            self.graph.add_node(node)

        self.graph._last_scan = time.time()
        self.graph._scan_count += 1
        self._scans_performed += 1
        self._last_scan_time = time.time()

        scan_duration = time.time() - scan_start

        # Crear observación
        obs = Observation(
            timestamp=time.time(),
            source="resource_discovery",
            content=f"Resource scan complete: {self.graph.get_stats()['total_nodes']} nodes found, "
                   f"{len(self.graph.get_available_models())} models available. "
                   f"Scan took {scan_duration:.2f}s.",
            metadata={
                "scan_duration_s": scan_duration,
                "node_count": self.graph.get_stats()['total_nodes'],
                "available_models": self.graph.get_available_models(),
            }
        )
        observations.append(obs)

        return observations

    def _scan_hardware(self) -> List[ResourceNode]:
        """Descubre hardware local: CPU, RAM, GPU."""
        nodes = []
        system = platform.system()

        # CPU
        try:
            cpu_cores = os.cpu_count() or 4
            nodes.append(ResourceNode(
                id="local_cpu",
                type=ResourceType.CPU,
                name=f"Local CPU ({cpu_cores} cores)",
                capabilities={"cores": cpu_cores, "platform": system},
                privacy_level="local",
            ))
        except Exception as e:
            logger.debug(f"CPU scan failed: {e}")

        # GPU / Apple Silicon
        try:
            if system == "Darwin":
                result = subprocess.run(
                    ["sysctl", "-n", "machdep.cpu.brand_string"],
                    capture_output=True, text=True, timeout=5
                )
                brand = result.stdout.strip()
                is_apple = any(chip in brand.lower() for chip in ["apple m", "m1", "m2", "m3", "m4"])

                if is_apple:
                    # Apple Silicon = Metal GPU + Neural Engine
                    ram_result = subprocess.run(
                        ["sysctl", "-n", "hw.memsize"],
                        capture_output=True, text=True, timeout=5
                    )
                    ram_gb = int(ram_result.stdout.strip()) / (1024**3)
                    nodes.append(ResourceNode(
                        id="local_gpu_apple",
                        type=ResourceType.GPU,
                        name=f"Apple Silicon ({brand})",
                        capabilities={
                            "type": "apple_silicon",
                            "ram_gb": round(ram_gb, 1),
                            "metal": True,
                            "neural_engine": True,
                        },
                        privacy_level="local",
                    ))
                else:
                    # Intel Mac - verificar GPU externa
                    nodes.append(ResourceNode(
                        id="local_gpu_intel",
                        type=ResourceType.GPU,
                        name=f"Intel Mac GPU ({brand})",
                        capabilities={"type": "intel", "metal": True},
                        privacy_level="local",
                    ))

            elif system == "Linux":
                # Verificar NVIDIA GPU
                if shutil.which("nvidia-smi"):
                    result = subprocess.run(
                        ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"],
                        capture_output=True, text=True, timeout=5
                    )
                    if result.returncode == 0:
                        for line in result.stdout.strip().split("\n"):
                            parts = line.split(", ")
                            if len(parts) >= 2:
                                name = parts[0]
                                vram = parts[1]
                                nodes.append(ResourceNode(
                                    id=f"local_gpu_nvidia_{name.lower().replace(' ', '_')}",
                                    type=ResourceType.GPU,
                                    name=f"NVIDIA {name} ({vram})",
                                    capabilities={
                                        "type": "nvidia",
                                        "vram": vram,
                                        "cuda": True,
                                    },
                                    privacy_level="local",
                                ))
        except Exception as e:
            logger.debug(f"GPU scan failed: {e}")

        return nodes

    def _scan_ollama_local(self) -> Optional[ResourceNode]:
        """Descubre instancia local de Ollama y sus modelos."""
        try:
            import aiohttp
        except ImportError:
            # Sin aiohttp, verificar si el puerto responde
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            try:
                result = sock.connect_ex(("localhost", 11434))
                if result != 0:
                    return None
            except Exception:
                return None
            finally:
                sock.close()

            # Puerto abierto pero no podemos verificar modelos
            return ResourceNode(
                id="ollama_local",
                type=ResourceType.OLLAMA,
                name="Ollama (local)",
                address="http://localhost:11434",
                capabilities={"streaming": True},
                models=[],
                privacy_level="local",
                latency_ms=1.0,
            )

        # Con aiohttp: hacer petición real (async)
        # Pero observe() es async, así que esto se hace fuera
        # Por ahora, verificamos sincrónicamente
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        try:
            result = sock.connect_ex(("localhost", 11434))
            if result != 0:
                return None
        except Exception:
            return None
        finally:
            sock.close()

        # Puerto abierto, intentar obtener modelos
        try:
            import urllib.request
            import json
            with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=5) as resp:
                data = json.loads(resp.read().decode())
                models = [m.get("name", "") for m in data.get("models", [])]
                return ResourceNode(
                    id="ollama_local",
                    type=ResourceType.OLLAMA,
                    name="Ollama (local)",
                    address="http://localhost:11434",
                    capabilities={"streaming": True, "mmap": True},
                    models=models,
                    privacy_level="local",
                    latency_ms=1.0,
                )
        except Exception as e:
            logger.debug(f"Ollama local models fetch failed: {e}")
            return ResourceNode(
                id="ollama_local",
                type=ResourceType.OLLAMA,
                name="Ollama (local, port open)",
                address="http://localhost:11434",
                models=[],
                privacy_level="local",
            )

    def _scan_cloud_apis(self) -> List[ResourceNode]:
        """Descubre cloud APIs configuradas según variables de entorno."""
        nodes = []

        api_configs = [
            ("openai", "OPENAI_API_KEY", "OpenAI", "https://api.openai.com/v1",
             ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "o1", "o1-mini"]),
            ("anthropic", "ANTHROPIC_API_KEY", "Anthropic Claude", "https://api.anthropic.com",
             ["claude-sonnet-4-20250514", "claude-opus-4-20250514", "claude-3-5-haiku-20241022"]),
            ("deepseek", "DEEPSEEK_API_KEY", "DeepSeek", "https://api.deepseek.com/v1",
             ["deepseek-chat", "deepseek-reasoner"]),
            ("groq", "GROQ_API_KEY", "Groq", "https://api.groq.com/openai/v1",
             ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]),
            ("moonshot", "MOONSHOT_API_KEY", "Kimi/Moonshot", "https://api.moonshot.cn/v1",
             ["moonshot-v1-8k", "moonshot-v1-32k"]),
            ("minimax", "MINIMAX_API_KEY", "MiniMax", "https://api.minimax.chat/v1",
             ["abab6.5-chat"]),
        ]

        for env_name, env_var, display_name, base_url, models in api_configs:
            api_key = os.environ.get(env_var)
            if api_key:
                cost = 0.01 if "mini" in env_name or "haiku" in env_name or "instant" in env_name else 0.03
                nodes.append(ResourceNode(
                    id=f"cloud_{env_name}",
                    type=ResourceType.CLOUD_API,
                    name=display_name,
                    address=base_url,
                    capabilities={"streaming": True, "api_key_configured": True},
                    models=models,
                    privacy_level="cloud",
                    cost_per_1k_tokens=cost,
                    latency_ms=500.0,  # estimación
                ))

        return nodes

    def _scan_storage(self) -> List[ResourceNode]:
        """Descubre opciones de almacenamiento."""
        nodes = []

        # Pendrive (si ZOE está en uno)
        system = platform.system()
        if system == "Darwin":
            for vol in os.listdir("/Volumes"):
                if vol == "Macintosh HD" or vol == "MacintoshHD":
                    continue
                vol_path = f"/Volumes/{vol}"
                if os.path.isdir(vol_path):
                    # Verificar si tiene ZOE
                    zoe_path = os.path.join(vol_path, "ZOE")
                    has_zoe = os.path.isdir(zoe_path)
                    nodes.append(ResourceNode(
                        id=f"storage_{vol}",
                        type=ResourceType.STORAGE,
                        name=f"Pendrive: {vol}",
                        address=vol_path,
                        capabilities={"has_zoe": has_zoe},
                        privacy_level="local",
                    ))

        # Windows: detectar drives D: a Z:
        if system == "Windows":
            import string
            for letter in string.ascii_uppercase:
                drive_path = f"{letter}:\\"
                if os.path.exists(drive_path):
                    zoe_path = os.path.join(drive_path, "ZOE")
                    has_zoe = os.path.isdir(zoe_path)
                    if letter != "C":  # No reportar disco del sistema
                        nodes.append(ResourceNode(
                            id=f"storage_{letter}",
                            type=ResourceType.STORAGE,
                            name=f"Drive {letter}:",
                            address=drive_path,
                            capabilities={"has_zoe": has_zoe},
                            privacy_level="local",
                        ))

        # Disco local
        nodes.append(ResourceNode(
            id="storage_local",
            type=ResourceType.STORAGE,
            name="Local disk",
            address=os.path.expanduser("~"),
            privacy_level="local",
        ))

        return nodes

    def add_zoe_peer(self, peer_id: str, address: str, models: List[str] = None) -> None:
        """Añade un peer ZOE descubierto vía federación."""
        self.graph.add_node(ResourceNode(
            id=f"zoe_peer_{peer_id}",
            type=ResourceType.ZOE_PEER,
            name=f"ZOE peer: {peer_id}",
            address=address,
            capabilities={"federation": True},
            models=models or [],
            privacy_level="network",
        ))

    def get_graph(self) -> ResourceGraph:
        return self.graph

    def get_stats(self) -> Dict[str, Any]:
        return {
            "scans_performed": self._scans_performed,
            "last_scan_time": self._last_scan_time,
            **self.graph.get_stats(),
        }
