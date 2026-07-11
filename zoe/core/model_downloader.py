"""
ZOE V1.8 — Model Downloader (Sprint 5.5)

Descarga modelos GGUF optimizados (IQ2_M, IQ3_XS) desde HuggingFace
automáticamente al SSD/pendrive, y los registra en Ollama vía Modelfile.

Sin deconstruir: es una capa NUEVA. No modifica ModelOptimizer, ni
OllamaPeripheral, ni el bucle cognitivo. Añade la capacidad de descargar
modelos optimizados que no están en el repositorio oficial de Ollama.

Fuentes soportadas:
- mradermacher (HuggingFace) — experto en cuantizaciones IQ
- bartowski (HuggingFace) — modelos actualizados rápido
- Repositorio oficial de Ollama (ollama pull)

Uso:
    from zoe.core.model_downloader import ModelDownloader
    
    downloader = ModelDownloader(models_dir="/Volumes/SSD/ZOE/models")
    
    # Descargar Qwen 2.5 32B IQ2_M (~12.5 GB)
    path = downloader.download_iq2_model("qwen2.5:32b")
    
    # Registrar en Ollama
    downloader.register_in_ollama("qwen2.5:32b-iq2", path)
    
    # Ahora ZOE puede usar: zoe-chat --backend ollama --model qwen2.5:32b-iq2
"""

from __future__ import annotations

import hashlib
import logging
import os
import shutil
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from enum import Enum

logger = logging.getLogger(__name__)


# ============================================================
# Catálogo de modelos optimizados en HuggingFace
# ============================================================

class ModelSource(str, Enum):
    """Fuentes de modelos GGUF."""
    HUGGINGFACE_MRADERMACHER = "mradermacher"
    HUGGINGFACE_BARTOWSKI = "bartowski"
    OLLAMA_OFFICIAL = "ollama"
    LOCAL = "local"


@dataclass
class OptimizedModel:
    """Un modelo GGUF optimizado disponible para descarga."""
    name: str                    # nombre ZOE (ej: "qwen2.5:32b")
    display_name: str            # nombre para mostrar
    params_b: float              # billones de parámetros
    quantization: str            # IQ2_M, IQ3_XS, Q4_K_M
    size_gb: float               # tamaño del archivo
    source: ModelSource          # fuente de descarga
    hf_repo: str                 # repo de HuggingFace (ej: "mradermacher/Qwen2.5-32B-Instruct-GGUF")
    hf_filename: str             # archivo exacto (ej: "Qwen2.5-32B-Instruct.IQ2_M.gguf")
    ollama_tag: str              # tag para Modelfile (ej: "qwen2.5-32b-iq2")
    recommended_ram_gb: float    # RAM mínima recomendada
    estimated_tokens_s: str      # velocidad estimada (ej: "3-6")
    description: str = ""


# Catálogo de modelos optimizados disponibles en HuggingFace
OPTIMIZED_MODELS: Dict[str, OptimizedModel] = {
    "qwen2.5:32b-iq2": OptimizedModel(
        name="qwen2.5:32b-iq2",
        display_name="Qwen 2.5 32B (IQ2_M)",
        params_b=32.0,
        quantization="IQ2_M",
        size_gb=12.5,
        source=ModelSource.HUGGINGFACE_MRADERMACHER,
        hf_repo="mradermacher/Qwen2.5-32B-Instruct-GGUF",
        hf_filename="Qwen2.5-32B-Instruct.IQ2_M.gguf",
        ollama_tag="qwen2.5-32b-iq2",
        recommended_ram_gb=8.0,
        estimated_tokens_s="3-6",
        description="Modelo de 32B ultra-comprimido. Calidad ~95%. Ideal para análisis profundo en Mac 8GB con SSD.",
    ),
    "qwen2.5:32b-iq3": OptimizedModel(
        name="qwen2.5:32b-iq3",
        display_name="Qwen 2.5 32B (IQ3_XS)",
        params_b=32.0,
        quantization="IQ3_XS",
        size_gb=16.0,
        source=ModelSource.HUGGINGFACE_MRADERMACHER,
        hf_repo="mradermacher/Qwen2.5-32B-Instruct-GGUF",
        hf_filename="Qwen2.5-32B-Instruct.IQ3_XS.gguf",
        ollama_tag="qwen2.5-32b-iq3",
        recommended_ram_gb=8.0,
        estimated_tokens_s="2-5",
        description="Modelo de 32B con mejor calidad (~97%). Más grande pero más preciso.",
    ),
    "qwen2.5:72b-iq2": OptimizedModel(
        name="qwen2.5:72b-iq2",
        display_name="Qwen 2.5 72B (IQ2_M)",
        params_b=72.0,
        quantization="IQ2_M",
        size_gb=25.0,
        source=ModelSource.HUGGINGFACE_MRADERMACHER,
        hf_repo="mradermacher/Qwen2.5-72B-Instruct-GGUF",
        hf_filename="Qwen2.5-72B-Instruct.IQ2_M.gguf",
        ollama_tag="qwen2.5-72b-iq2",
        recommended_ram_gb=8.0,
        estimated_tokens_s="1-3",
        description="Modelo de 72B ultra-comprimido. Máxima calidad offline. Lento pero potente.",
    ),
    "llama3.1:70b-iq2": OptimizedModel(
        name="llama3.1:70b-iq2",
        display_name="Llama 3.1 70B (IQ2_M)",
        params_b=70.0,
        quantization="IQ2_M",
        size_gb=25.0,
        source=ModelSource.HUGGINGFACE_MRADERMACHER,
        hf_repo="mradermacher/Meta-Llama-3.1-70B-Instruct-GGUF",
        hf_filename="Meta-Llama-3.1-70B-Instruct.IQ2_XS.gguf",
        ollama_tag="llama3.1-70b-iq2",
        recommended_ram_gb=8.0,
        estimated_tokens_s="1-3",
        description="Llama 3.1 70B ultra-comprimido. Alternativa a Qwen 72B.",
    ),
    "deepseek-r1:32b-iq2": OptimizedModel(
        name="deepseek-r1:32b-iq2",
        display_name="DeepSeek R1 32B (IQ2_M)",
        params_b=32.0,
        quantization="IQ2_M",
        size_gb=12.5,
        source=ModelSource.HUGGINGFACE_MRADERMACHER,
        hf_repo="mradermacher/DeepSeek-R1-Distill-Qwen-32B-GGUF",
        hf_filename="DeepSeek-R1-Distill-Qwen-32B.IQ2_M.gguf",
        ollama_tag="deepseek-r1-32b-iq2",
        recommended_ram_gb=8.0,
        estimated_tokens_s="3-6",
        description="DeepSeek R1 destilado a 32B. Especializado en razonamiento.",
    ),
}


class ModelDownloader:
    """
    Descarga modelos GGUF optimizados desde HuggingFace y los registra en Ollama.
    
    Sin deconstruir: capa aditiva. No modifica ModelOptimizer ni OllamaPeripheral.
    """

    def __init__(self, models_dir: str = None):
        self.models_dir = Path(models_dir) if models_dir else Path("models")
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self._downloads = 0
        self._registrations = 0

    def list_available(self) -> List[Dict[str, Any]]:
        """Lista todos los modelos optimizados disponibles para descarga."""
        result = []
        for key, model in OPTIMIZED_MODELS.items():
            # Verificar si ya está descargado
            local_path = self.models_dir / model.hf_filename
            downloaded = local_path.exists()

            # Verificar si está registrado en Ollama
            registered = self._is_registered_in_ollama(model.ollama_tag)

            result.append({
                "key": key,
                "display_name": model.display_name,
                "params_b": model.params_b,
                "quantization": model.quantization,
                "size_gb": model.size_gb,
                "source": model.source.value,
                "recommended_ram_gb": model.recommended_ram_gb,
                "estimated_tokens_s": model.estimated_tokens_s,
                "description": model.description,
                "downloaded": downloaded,
                "registered_in_ollama": registered,
                "local_path": str(local_path) if downloaded else None,
            })
        return result

    def get_model_info(self, model_key: str) -> Optional[OptimizedModel]:
        """Devuelve info de un modelo específico."""
        return OPTIMIZED_MODELS.get(model_key)

    def download(
        self,
        model_key: str,
        progress_callback: Callable[[float, str], None] = None,
    ) -> Optional[str]:
        """
        Descarga un modelo GGUF desde HuggingFace.
        
        Args:
            model_key: clave del modelo (ej: "qwen2.5:32b-iq2")
            progress_callback: función llamada con (porcentaje, mensaje)
            
        Returns:
            Path del archivo descargado, o None si falla
        """
        model = OPTIMIZED_MODELS.get(model_key)
        if not model:
            logger.error(f"ModelDownloader: unknown model '{model_key}'")
            return None

        local_path = self.models_dir / model.hf_filename

        # Si ya existe, no descargar
        if local_path.exists():
            size_gb = local_path.stat().st_size / (1024**3)
            logger.info(f"ModelDownloader: {model_key} already downloaded ({size_gb:.1f} GB)")
            if progress_callback:
                progress_callback(100.0, f"Ya descargado ({size_gb:.1f} GB)")
            return str(local_path)

        if progress_callback:
            progress_callback(0.0, f"Descargando {model.display_name} ({model.size_gb:.1f} GB)...")

        # Construir URL de HuggingFace
        url = f"https://huggingface.co/{model.hf_repo}/resolve/main/{model.hf_filename}"

        logger.info(f"ModelDownloader: downloading {model_key} from {url}")

        # Descargar con curl (muestra progreso nativo)
        try:
            cmd = [
                "curl", "-L", "--progress-bar",
                "-o", str(local_path),
                url,
            ]

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            # Esperar a que termine
            stdout, stderr = process.communicate()

            if process.returncode == 0:
                size_gb = local_path.stat().st_size / (1024**3)
                self._downloads += 1
                logger.info(f"ModelDownloader: downloaded {model_key} ({size_gb:.1f} GB)")
                if progress_callback:
                    progress_callback(100.0, f"Descarga completa ({size_gb:.1f} GB)")
                return str(local_path)
            else:
                logger.error(f"ModelDownloader: curl failed: {stderr.decode()}")
                # Limpiar archivo parcial
                if local_path.exists():
                    local_path.unlink()
                if progress_callback:
                    progress_callback(0.0, "Error en descarga")
                return None

        except FileNotFoundError:
            logger.error("ModelDownloader: curl not found")
            if progress_callback:
                progress_callback(0.0, "curl no encontrado. Instala curl.")
            return None
        except Exception as e:
            logger.error(f"ModelDownloader: download error: {e}")
            if progress_callback:
                progress_callback(0.0, f"Error: {e}")
            return None

    def register_in_ollama(
        self,
        model_key: str,
        gguf_path: str = None,
    ) -> bool:
        """
        Registra un GGUF en Ollama usando Modelfile.
        
        Esto permite usar `ollama run qwen2.5-32b-iq2` con un GGUF
        descargado de HuggingFace que no está en el repositorio oficial.
        
        Args:
            model_key: clave del modelo (ej: "qwen2.5:32b-iq2")
            gguf_path: path al GGUF (si None, usa el path por defecto)
            
        Returns:
            True si se registró correctamente
        """
        model = OPTIMIZED_MODELS.get(model_key)
        if not model:
            logger.error(f"ModelDownloader: unknown model '{model_key}'")
            return False

        # Determinar path del GGUF
        if gguf_path is None:
            gguf_path = str(self.models_dir / model.hf_filename)

        if not os.path.exists(gguf_path):
            logger.error(f"ModelDownloader: GGUF not found at {gguf_path}")
            return False

        # Si ya está registrado, no hacer nada
        if self._is_registered_in_ollama(model.ollama_tag):
            logger.info(f"ModelDownloader: {model.ollama_tag} already registered in Ollama")
            return True

        # Crear Modelfile
        modelfile_content = self._generate_modelfile(model, gguf_path)
        modelfile_path = self.models_dir / f"Modelfile.{model.ollama_tag}"
        with open(modelfile_path, "w") as f:
            f.write(modelfile_content)

        # Ejecutar ollama create
        try:
            result = subprocess.run(
                ["ollama", "create", model.ollama_tag, "-f", str(modelfile_path)],
                capture_output=True, text=True, timeout=120,
            )

            if result.returncode == 0:
                self._registrations += 1
                logger.info(f"ModelDownloader: registered {model.ollama_tag} in Ollama")
                # Limpiar Modelfile temporal
                modelfile_path.unlink()
                return True
            else:
                logger.error(f"ModelDownloader: ollama create failed: {result.stderr}")
                return False

        except FileNotFoundError:
            logger.error("ModelDownloader: ollama not found")
            return False
        except Exception as e:
            logger.error(f"ModelDownloader: registration error: {e}")
            return False

    def _generate_modelfile(self, model: OptimizedModel, gguf_path: str) -> str:
        """Genera el contenido del Modelfile para Ollama."""
        return f"""# Modelfile para {model.display_name}
# Generado automáticamente por ZOE ModelDownloader

# Indicar a Ollama dónde está el archivo GGUF
FROM {gguf_path}

# Parámetros críticos para Mac 8GB RAM
PARAMETER num_ctx 2048
PARAMETER num_predict 512
PARAMETER num_parallel 1

# Plantilla de chat para Qwen 2.5
TEMPLATE "{{{{ if .System }}}}<|im_start|>system
{{{{ .System }}}}<|im_end|>
{{{{ end }}}}{{{{ if .Prompt }}}}<|im_start|>user
{{{{ .Prompt }}}}<|im_end|>
{{{{ end }}}}<|im_start|>assistant
{{{{ .Response }}}}<|im_end|>"

SYSTEM "Eres ZOE, un organismo cognitivo sintético."
"""

    def _is_registered_in_ollama(self, tag: str) -> bool:
        """Verifica si un modelo está registrado en Ollama."""
        try:
            result = subprocess.run(
                ["ollama", "list"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                return tag in result.stdout
        except:
            pass
        return False

    def download_and_register(
        self,
        model_key: str,
        progress_callback: Callable[[float, str], None] = None,
    ) -> bool:
        """
        Descarga un modelo Y lo registra en Ollama en un solo paso.
        
        Returns:
            True si todo fue bien
        """
        # 1. Descargar
        if progress_callback:
            progress_callback(0.0, "Iniciando descarga...")

        path = self.download(model_key, progress_callback)
        if not path:
            return False

        # 2. Registrar en Ollama
        if progress_callback:
            progress_callback(90.0, "Registrando en Ollama...")

        return self.register_in_ollama(model_key, path)

    def recommend_for_ram(self, ram_gb: float) -> List[Dict[str, Any]]:
        """
        Recomienda modelos optimizados según RAM disponible.
        
        Returns:
            Lista de modelos recomendados ordenados por calidad
        """
        recommended = []
        for key, model in OPTIMIZED_MODELS.items():
            if model.recommended_ram_gb <= ram_gb:
                local_path = self.models_dir / model.hf_filename
                recommended.append({
                    "key": key,
                    "display_name": model.display_name,
                    "size_gb": model.size_gb,
                    "estimated_tokens_s": model.estimated_tokens_s,
                    "downloaded": local_path.exists(),
                    "registered": self._is_registered_in_ollama(model.ollama_tag),
                    "description": model.description,
                })

        # Ordenar por tamaño (más pequeño = más rápido primero)
        recommended.sort(key=lambda x: x["size_gb"])
        return recommended

    def get_stats(self) -> Dict[str, Any]:
        """Stats del downloader."""
        return {
            "downloads": self._downloads,
            "registrations": self._registrations,
            "models_dir": str(self.models_dir),
            "available_models": len(OPTIMIZED_MODELS),
            "downloaded_models": sum(
                1 for m in OPTIMIZED_MODELS.values()
                if (self.models_dir / m.hf_filename).exists()
            ),
        }
