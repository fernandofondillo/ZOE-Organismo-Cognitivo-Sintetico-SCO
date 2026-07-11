# 10 — Hardware Optimization

> **Optimización de rendimiento: modelos, mmap, P-cores, IQ2_M, flash attention, SSDs.**
> **Versión:** V1.6.0 — Julio 2026

---

## 1. Modelos soportados

16 modelos en `MODEL_CATALOG` (`zoe/core/model_optimizer.py`):

| Modelo | Params | Q4 (GB) | IQ2_M (GB) | Recomendado para |
|---|---|---|---|---|
| qwen2.5:3b | 3B | 2.0 | — | L0-L1 (recomendado default) |
| qwen2.5:7b | 7B | 4.5 | — | L2 |
| qwen2.5:14b | 14B | 8.0 | — | L3 |
| qwen2.5:32b | 32B | 18.0 | 5.4 | L3 (con IQ2_M en 8GB) |
| qwen2.5:72b | 72B | 40.0 | 12.0 | L3 (con IQ2_M) |
| llama3.1:8b | 8B | 4.9 | — | L2 |
| llama3.1:70b | 70B | 40.0 | 12.0 | L3 (con IQ2_M) |
| deepseek-r1:32b | 32B | 18.0 | 5.4 | L3 (con IQ2_M) |
| gemma2:27b | 27B | 16.0 | 4.8 | L3 (con IQ2_M) |

---

## 2. Cuantizaciones

| Cuantización | Tamaño vs Q4 | Calidad | Cuándo usar |
|---|---|---|---|
| Q4_K_M | 100% | 100% | Default |
| Q8 | ~150% | ~102% | RAM abundante |
| IQ3_XS | ~40% | ~97% | Q4 no cabe, buena calidad |
| IQ2_M | ~30% | ~95% | Q4 e IQ3 no caben. Última opción antes de cloud |

---

## 3. Estrategias de carga

| Estrategia | Cuándo | RAM usada | Velocidad |
|---|---|---|---|
| FULL_RAM | Modelo cabe en RAM | ~tamaño modelo | Rápida |
| MMAP_PARTIAL | Modelo 1-2.5x RAM | ~60% RAM | Media |
| MMAP_FULL | Modelo 2.5-10x RAM | ~40% RAM | Lenta |
| CLOUD_FALLBACK | Modelo >10x RAM | 0 | N/A (cloud) |

---

## 4. Cognitive Memory Paging (mmap)

El modelo se memory-mapea desde SSD. Solo las capas activas cargan en RAM (~2-4 GB). Como la paginación de memoria de un SO.

```python
from zoe.core.model_optimizer import ModelOptimizer

opt = ModelOptimizer()
result = opt.optimize("qwen2.5:32b", available_ram_gb=5.0)
# strategy: MMAP_PARTIAL, quantization: IQ3_XS, will_work: True
```

---

## 5. Detección de P-cores

Apple Silicon tiene P-cores (performance) y E-cores (efficiency). Usar E-cores DEGRADA el rendimiento.

```python
opt = ModelOptimizer()
p_cores = opt.detect_p_cores()  # hw.perflevel0.physicalcpu
e_cores = opt.detect_e_cores()  # hw.perflevel1.physicalcpu

# generate_ollama_env() configura automáticamente:
# OLLAMA_NUM_THREAD = P-cores (no total)
```

---

## 6. Flash Attention

Siempre activo desde V1.6.0 (Fase 7G). Reduce cómputo en contextos largos hasta 40%.

```python
env = opt.generate_ollama_env(result)
# env["OLLAMA_FLASH_ATTENTION"] = "1"  # siempre
```

---

## 7. Tabla de tokens/s esperados

MacBook Air M2/M3 8GB + SSD 2000 MB/s + cable USB-C correcto:

| Modelo | Cuantización | Tokens/s | Experiencia |
|---|---|---|---|
| Qwen 2.5 3B | Q4_K_M | 25-35 | ⚡ Más rápido de lo que lees |
| Qwen 2.5 7B | Q4_K_M | 12-18 | ✅ Similar a ChatGPT gratuito |
| Qwen 2.5 14B | Q4_K_M | 4-8 | 📖 Lectura pausada |
| Qwen 2.5 32B | IQ2_M | 3-6 | 🧠 Análisis profundo |
| Qwen 2.5 72B | IQ2_M | 1-3 | Lento pero funcional |

> Con pendrive USB normal (400 MB/s), divide entre 3-5.

---

## 8. SSDs portátiles recomendados

| Modelo | Velocidad | Precio | Recomendado |
|---|---|---|---|
| **Crucial X10 Pro** | 2100 MB/s | ~110€ | ✅ Por defecto |
| Kingston XS2000 | 2000 MB/s | ~100€ | Más económico |
| SanDisk PRO-BLADE | 2000 MB/s | ~160€ | Profesional |

---

## 9. Cable USB-C

> ⚠️ **Usa SIEMPRE el cable corto de la caja del SSD.** El cable de carga del Mac es USB 2.0 (60 MB/s). El cable corto es USB 3.2 Gen 2 (2000 MB/s). **10x impacto.**

**Síntomas:**
- Cable equivocado: ZOE tarda 10+ segundos en responder
- Cable correcto: ZOE responde en 1-2 segundos

---

## 10. ModelOptimizer API

```python
opt = ModelOptimizer()

# Info del sistema (con P-cores, E-cores)
info = opt.get_system_info()

# Optimizar modelo
result = opt.optimize("qwen2.5:32b", available_ram_gb=5.0)

# Recomendaciones por ACD
recs = opt.recommend_for_acd(ram_gb=5.0)

# Env vars para Ollama
env = opt.generate_ollama_env(result)

# APIs estáticas (UX)
ModelOptimizer.get_recommended_ssds()
ModelOptimizer.get_expected_token_rates()
ModelOptimizer.get_cable_warning()
```

---

## 11. Endpoints REST

| Endpoint | Descripción |
|---|---|
| `GET /api/hardware/ssds` | SSDs recomendados |
| `GET /api/hardware/token_rates` | Tabla tokens/s |
| `GET /api/hardware/cable_warning` | Warning cable USB-C |
| `GET /api/hardware/system` | Info hardware host |
| `GET /api/models/system_info` | Info con P-cores, E-cores |
| `GET /api/models/recommend` | Recomendaciones por ACD |
| `GET /api/models/catalog` | Catálogo modelos |
| `POST /api/models/optimize` | Optimizar modelo específico |

---

*ZOE V1.6.0 — Documento 10: Hardware Optimization*
*Julio 2026*
