"""
ZOE V1.8 — Model Profile Router (Sprint 5.6)

Asigna automáticamente cada modelo del SSD al nivel ACD correcto.
ZOE no usa el mismo modelo para todo — usa el modelo óptimo para cada tipo
de pensamiento.

Con 4 modelos en un SSD de 1TB cubrimos todo el espectro:

  L0/L1 (reflejo/rápido)  → Gemma 2 9B (3.5GB, 15-25 t/s)
  L2 (estándar)           → Agents-A1 MoE (11.7GB, 5-10 t/s)
  L3 (profundo)           → QwQ-32B (12.5GB, 3-6 t/s, razonamiento)
  L3 máximo (calidad)     → Qwen 2.5 72B (25GB, 1-3 t/s)
  L4 (reflexión autónoma) → DeepSeek-R1 32B Q4_K_M (18GB, 2-4 t/s, solo SLEEPING)

Total: ~52.7 GB en SSD de 1TB — sobra espacio para cápsulas y memoria.

ZOE elige automáticamente:
- "Hola" → Gemma 2 9B (instantáneo)
- "Resume este artículo" → Agents-A1 MoE (rápido y capaz)
- "Analiza las causas profundas de esta depresión" → QwQ-32B (razonamiento)
- "Compara estos 3 contratos jurídicamente" → Qwen 2.5 72B (máxima calidad)

Sin deconstruir: usa ModelBus existente. Solo añade la lógica de routing.

Uso:
    from zoe.core.model_profile_router import ModelProfileRouter, ModelProfile
    
    router = ModelProfileRouter()
    
    # Detectar qué modelos hay instalados en el SSD
    router.detect_installed_models(models_dir="/Volumes/SSD/ZOE/models")
    
    # Crear perfil óptimo con los modelos disponibles
    profile = router.create_optimal_profile()
    
    # ZOE usa el perfil para decidir qué modelo cargar
    model = router.get_model_for_acd("L3_DEEP", profile)
    # → "qwq-32b-iq2" (si está disponible)
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class ACDLevel(str, Enum):
    """Niveles de Adaptive Cognitive Depth."""
    L0_REFLEX = "L0_REFLEX"
    L1_FAST = "L1_FAST"
    L2_STANDARD = "L2_STANDARD"
    L3_DEEP = "L3_DEEP"
    L3_MAXIMUM = "L3_MAXIMUM"  # máxima calidad cuando es crítico


@dataclass
class ModelAssignment:
    """Asignación de un modelo a un nivel ACD."""
    acd_level: str
    model_tag: str          # tag de Ollama (ej: "gemma2-9b-iq2")
    model_key: str          # clave en OPTIMIZED_MODELS (ej: "gemma-2-9b-iq2")
    reason: str             # por qué se eligió este modelo
    fallback: str = "pattern"  # fallback si el modelo no está disponible


@dataclass
class ModelProfile:
    """
    Perfil de modelos asignados a cada nivel ACD.
    
    Define qué modelo usa ZOE para cada tipo de pensamiento.
    Un SSD de 1TB puede tener varios modelos y ZOE elige el óptimo.
    """
    name: str = "default"
    description: str = ""
    assignments: Dict[str, ModelAssignment] = field(default_factory=dict)
    
    def get_model(self, acd_level: str) -> Optional[ModelAssignment]:
        """Devuelve la asignación para un nivel ACD."""
        # L3_MAXIMUM usa L3_DEEP si no hay asignación específica
        if acd_level == ACDLevel.L3_MAXIMUM.value:
            return self.assignments.get(acd_level) or self.assignments.get(ACDLevel.L3_DEEP.value)
        return self.assignments.get(acd_level)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "assignments": {k: asdict(v) for k, v in self.assignments.items()},
        }


class ModelProfileRouter:
    """
    Router que asigna modelos del SSD a niveles ACD de ZOE.
    
    Detecta qué modelos están instalados en el SSD/pendrive y crea
    un perfil óptimo que asigna cada modelo al nivel ACD donde brilla.
    
    Sin deconstruir: usa ModelBus existente. Solo añade lógica de routing.
    """
    
    # Asignaciones preferidas por defecto (cuando todos los modelos están disponibles)
    DEFAULT_ASSIGNMENTS = {
        "L0_REFLEX": {
            "preferred": "gemma-2-9b-iq2",
            "reason": "Ultra rápido (15-25 t/s), solo 3.5GB. Ideal para respuestas reflejo.",
            "fallback": "pattern",
        },
        "L1_FAST": {
            "preferred": "gemma-2-9b-iq2",
            "reason": "Mismo modelo que L0 — rápido y eficiente para preguntas sencillas.",
            "fallback": "pattern",
        },
        "L2_STANDARD": {
            "preferred": "agents-a1-iq2",
            "reason": "MoE más rápido (5-10 t/s) para conversación normal. Activa solo expertos relevantes.",
            "fallback": "qwen2.5:32b-iq2",
        },
        "L3_DEEP": {
            "preferred": "qwq-32b-iq2",
            "reason": "Modelo de razonamiento profundo. Muestra árbol de pensamientos antes de responder.",
            "fallback": "qwen2.5:32b-iq2",
        },
        "L3_MAXIMUM": {
            "preferred": "qwen2.5:72b-iq2",
            "reason": "Máxima calidad offline. 72B ultra-comprimido. Lento pero potente.",
            "fallback": "qwq-32b-iq2",
        },
        "L4_REFLECTION": {
            "preferred": "deepseek-r1:32b-iq2",
            "reason": "DeepSeek-R1-Distill-Qwen-32B IQ2_M (~12.5GB). Cuantización ultra-ligera optimizada para MacBook Air M3 8GB. Preserva ~93% de calidad. Reflexión autónoma durante SLEEPING sin swap destructivo. NO para interacción en tiempo real — solo ciclo SLEEPING. Si tienes 16GB+ RAM, el bootstrap instala Q4_K_M automáticamente.",
            "fallback": "qwq-32b-iq2",
        },
    }
    
    # Orden de preferencia por nivel ACD (si el preferido no está, prueba estos)
    FALLBACK_CHAINS = {
        "L0_REFLEX": ["gemma-2-9b-iq2", "pattern"],
        "L1_FAST": ["gemma-2-9b-iq2", "qwen2.5:32b-iq2", "pattern"],
        "L2_STANDARD": ["agents-a1-iq2", "qwen2.5:32b-iq2", "deepseek-r1:32b-iq2", "gemma-2-9b-iq2", "pattern"],
        "L3_DEEP": ["qwq-32b-iq2", "deepseek-r1:32b-iq2", "qwen2.5:32b-iq2", "agents-a1-iq2", "pattern"],
        "L3_MAXIMUM": ["qwen2.5:72b-iq2", "llama3.1:70b-iq2", "qwq-32b-iq2", "deepseek-r1:32b-iq2", "qwen2.5:32b-iq2", "pattern"],
        "L4_REFLECTION": ["deepseek-r1:32b-iq2", "deepseek-r1:32b-q4km", "qwq-32b-iq2", "qwen2.5:32b-iq2"],
    }
    
    def __init__(self):
        from .model_downloader import OPTIMIZED_MODELS
        self._optimized_models = OPTIMIZED_MODELS
        self._installed_models: List[str] = []
        self._profiles_created = 0
    
    def detect_installed_models(self, models_dir: str) -> List[str]:
        """
        Detecta qué modelos optimizados están instalados en el SSD.
        
        Verifica:
        1. Archivos .gguf en el directorio
        2. Modelos registrados en Ollama (ollama list)
        
        Returns:
            Lista de claves de modelos instalados
        """
        installed = []
        models_path = Path(models_dir)
        
        # 1. Verificar archivos .gguf en el directorio
        for key, model in self._optimized_models.items():
            gguf_path = models_path / model.hf_filename
            if gguf_path.exists():
                installed.append(key)
                logger.info(f"ModelProfileRouter: found {key} at {gguf_path}")
        
        # 2. Verificar modelos registrados en Ollama
        try:
            import subprocess
            result = subprocess.run(
                ["ollama", "list"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                for key, model in self._optimized_models.items():
                    if model.ollama_tag in result.stdout and key not in installed:
                        installed.append(key)
                        logger.info(f"ModelProfileRouter: found {key} in Ollama")
        except (subprocess.SubprocessError, OSError) as e:
            logger.warning(f"Ollama model detection failed: {e}")
        
        self._installed_models = installed
        logger.info(f"ModelProfileRouter: {len(installed)} models detected: {installed}")
        return installed
    
    def create_optimal_profile(self, installed_models: List[str] = None, ram_gb: float = None) -> ModelProfile:
        """
        Crea el perfil óptimo con los modelos disponibles.
        
        Asigna cada modelo al nivel ACD donde es mejor, usando
        fallbacks si el preferido no está disponible.
        
        Si ram_gb >= 16.0 y deepseek-r1:32b-q4km está disponible,
        L4_REFLECTION usa Q4_K_M para máxima calidad.
        
        Args:
            installed_models: lista de claves instaladas (si None, usa self._installed_models)
            ram_gb: RAM disponible en GB (si None, no ajusta L4_REFLECTION)
            
        Returns:
            ModelProfile con asignaciones óptimas
        """
        available = installed_models or self._installed_models
        
        # Ajustar cadena de fallback para L4_REFLECTION según RAM disponible
        if ram_gb is not None and ram_gb >= 16.0 and "deepseek-r1:32b-q4km" in available:
            # RAM alta + q4km disponible: preferir calidad máxima
            self.FALLBACK_CHAINS["L4_REFLECTION"] = [
                "deepseek-r1:32b-q4km", "deepseek-r1:32b-iq2", "qwq-32b-iq2", "qwen2.5:32b-iq2"
            ]
        else:
            # Por defecto: preferir iq2 (más ligero, sin swap)
            self.FALLBACK_CHAINS["L4_REFLECTION"] = [
                "deepseek-r1:32b-iq2", "deepseek-r1:32b-q4km", "qwq-32b-iq2", "qwen2.5:32b-iq2"
            ]
        
        if not available:
            # Sin modelos instalados — todo a PatternSpeaker
            profile = ModelProfile(
                name="pattern_only",
                description="Sin modelos LLM. ZOE usa PatternSpeaker para todo.",
            )
            for acd in ACDLevel:
                profile.assignments[acd.value] = ModelAssignment(
                    acd_level=acd.value,
                    model_tag="pattern",
                    model_key="pattern",
                    reason="No hay modelos LLM instalados. PatternSpeaker responde desde patrones.",
                    fallback="pattern",
                )
            self._profiles_created += 1
            return profile
        
        profile = ModelProfile(
            name="auto_optimal",
            description=f"Perfil automático con {len(available)} modelos: {', '.join(available)}",
        )
        
        # Para cada nivel ACD, encontrar el mejor modelo disponible
        for acd_level in ACDLevel:
            chain = self.FALLBACK_CHAINS.get(acd_level.value, [])
            
            assigned = False
            for model_key in chain:
                if model_key == "pattern":
                    # PatternSpeaker siempre disponible
                    profile.assignments[acd_level.value] = ModelAssignment(
                        acd_level=acd_level.value,
                        model_tag="pattern",
                        model_key="pattern",
                        reason="PatternSpeaker (sin LLM necesario)",
                        fallback="pattern",
                    )
                    assigned = True
                    break
                elif model_key in available:
                    model = self._optimized_models.get(model_key)
                    if model:
                        default = self.DEFAULT_ASSIGNMENTS.get(acd_level.value, {})
                        reason = default.get("reason", f"Mejor modelo disponible para {acd_level.value}")
                        fallback = default.get("fallback", "pattern")
                        
                        # Si el modelo preferido no está, usar fallback de la cadena
                        if model_key != default.get("preferred"):
                            reason = f"Modelo {model_key} asignado a {acd_level.value} (preferido no disponible)"
                        
                        profile.assignments[acd_level.value] = ModelAssignment(
                            acd_level=acd_level.value,
                            model_tag=model.ollama_tag,
                            model_key=model_key,
                            reason=reason,
                            fallback=fallback,
                        )
                        assigned = True
                        break
            
            if not assigned:
                profile.assignments[acd_level.value] = ModelAssignment(
                    acd_level=acd_level.value,
                    model_tag="pattern",
                    model_key="pattern",
                    reason="Sin modelo disponible — PatternSpeaker",
                    fallback="pattern",
                )
        
        self._profiles_created += 1
        logger.info(f"ModelProfileRouter: created profile '{profile.name}'")
        return profile
    
    def get_model_for_acd(self, acd_level: str, profile: ModelProfile = None) -> Optional[ModelAssignment]:
        """
        Devuelve el modelo asignado a un nivel ACD.
        
        Args:
            acd_level: "L0_REFLEX", "L1_FAST", "L2_STANDARD", "L3_DEEP", "L3_MAXIMUM"
            profile: perfil a usar (si None, crea uno automáticamente)
            
        Returns:
            ModelAssignment con el modelo y razón
        """
        if profile is None:
            profile = self.create_optimal_profile()
        
        return profile.get_model(acd_level)
    
    def get_recommended_setup(self, ssd_capacity_gb: float = 1000) -> Dict[str, Any]:
        """
        Recomienda qué modelos instalar en un SSD de N GB.
        
        Cubre todo el espectro ACD con el mínimo de modelos.
        """
        setups = {
            # Setup mínimo (1 modelo, ~4GB)
            "minimal": {
                "models": ["gemma-2-9b-iq2"],
                "total_gb": 3.5,
                "coverage": "L0/L1/L2 (Gemma para todo). L3 limitado.",
                "description": "Mínimo viable. Gemma 2 9B para todo. Calidad limitada en L3.",
            },
            # Setup equilibrado (2 modelos, ~16GB)
            "balanced": {
                "models": ["gemma-2-9b-iq2", "qwq-32b-iq2"],
                "total_gb": 16.0,
                "coverage": "L0/L1 rápido (Gemma) + L2/L3 razonamiento (QwQ)",
                "description": "Equilibrado. Gemma para rápido, QwQ para profundo. Recomendado para 8GB RAM.",
            },
            # Setup completo (3 modelos, ~28GB)
            "complete": {
                "models": ["gemma-2-9b-iq2", "agents-a1-iq2", "qwq-32b-iq2"],
                "total_gb": 27.7,
                "coverage": "L0/L1 (Gemma) + L2 (MoE) + L3 (QwQ razonamiento)",
                "description": "Cobertura completa sin modelo de 72B. Ideal para SSD 128GB+.",
            },
            # Setup máximo (4 modelos, ~53GB)
            "maximum": {
                "models": ["gemma-2-9b-iq2", "agents-a1-iq2", "qwq-32b-iq2", "qwen2.5:72b-iq2"],
                "total_gb": 52.7,
                "coverage": "Todo el espectro: L0/L1 (Gemma) + L2 (MoE) + L3 (QwQ) + L3 máx (72B)",
                "description": "Máximo espectro. Los 4 modelos cubren todo. Ideal para SSD 1TB.",
            },
        }
        
        # Filtrar por capacidad
        for name, setup in setups.items():
            setup["fits_in_ssd"] = setup["total_gb"] <= ssd_capacity_gb
            setup["setup_name"] = name
        
        return setups
    
    def create_full_spectrum_profile(self) -> ModelProfile:
        """
        Crea el perfil de espectro completo (4 modelos).
        
        Este es el perfil recomendado para SSD de 1TB:
        - L0/L1: Gemma 2 9B (ultra rápido)
        - L2: Agents-A1 MoE (ágil)
        - L3: QwQ-32B (razonamiento)
        - L3 máximo: Qwen 2.5 72B (calidad máxima)
        """
        profile = ModelProfile(
            name="full_spectrum",
            description="Espectro completo: 4 modelos cubren todo el rango cognitivo de ZOE",
        )
        
        for acd_level, config in self.DEFAULT_ASSIGNMENTS.items():
            model_key = config["preferred"]
            model = self._optimized_models.get(model_key)
            
            if model:
                profile.assignments[acd_level] = ModelAssignment(
                    acd_level=acd_level,
                    model_tag=model.ollama_tag,
                    model_key=model_key,
                    reason=config["reason"],
                    fallback=config["fallback"],
                )
            else:
                profile.assignments[acd_level] = ModelAssignment(
                    acd_level=acd_level,
                    model_tag="pattern",
                    model_key="pattern",
                    reason="Modelo no disponible — PatternSpeaker",
                    fallback="pattern",
                )
        
        self._profiles_created += 1
        return profile
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            "installed_models": len(self._installed_models),
            "installed_model_keys": self._installed_models,
            "profiles_created": self._profiles_created,
            "available_catalog_models": len(self._optimized_models),
        }
