# 16 — ZOE Format (.zoe)

> **El formato .zoe: un organismo cognitivo completo en un archivo portable.**
> **Audiencia:** todos (usuarios, desarrolladores, CTO, directivos).
> **Versión:** V1.7.0 — Julio 2026

---

## Tabla de contenidos

1. [Qué es un .zoe](#1-qué-es-un-zoe)
2. [Qué contiene por dentro](#2-qué-contiene-por-dentro)
3. [Los 3 modos de funcionamiento](#3-los-3-modos-de-funcionamiento)
4. [Variantes de .zoe](#4-variantes-de-zoe)
5. [Cómo se crea un .zoe](#5-cómo-se-crea-un-zoe)
6. [Caso de uso completo: descarga → instalación → uso](#6-caso-de-uso-completo)
7. [Capacidades que mantiene](#7-capacidades-que-mantiene)
8. [Distribución y descarga](#8-distribución-y-descarga)
9. [Sprint 3.5 — Runtime mínimo](#9-sprint-35--runtime-mínimo)
10. [Sprint 3.6 — Enhanced PatternSpeaker](#10-sprint-36--enhanced-patternspeaker)

---

## 1. Qué es un .zoe

Un archivo `.zoe` es un **tarball comprimido** que contiene **todo lo necesario para que un organismo ZOE funcione en cualquier ordenador**, sin instalar Python, sin instalar Ollama, sin clonar repositorios, sin configurar nada.

Es el equivalente a un `.exe` portable para Windows, pero para un organismo cognitivo completo.

### Analogía

Piensa en un `.zoe` como una **semilla de roble**. La semilla contiene:
- El ADN del árbol (Identity Vault + Trajectory Chain)
- Nutrientes para arrancar (memoria + cápsulas + patrones)
- Instrucciones para germinar (runtime mínimo)

Al plantar la semilla en cualquier suelo (cualquier ordenador con Python), el árbol crece con su identidad intacta.

---

## 2. Qué contiene por dentro

```
mi_zoe.zoe (archivo comprimido, 50MB - 5GB según configuración)
│
├── manifest.json              ← Metadata: versión, organismo_id, fecha, tamaño
│
├── identity_vault.json        ← Alma de ZOE (hash SHA-256, 9 vectores, 7 valores)
├── trajectory_chain.json      ← Historial de mutaciones firmadas (blockchain)
│
├── memory.db                  ← SQLite con TODA la memoria (11 tipos)
│
├── capsules/                  ← Cápsulas de conocimiento instaladas
│   ├── zoe_basal_knowledge/   ← Cargada siempre
│   ├── base_ethics/           ← Ética general
│   ├── elder_care_knowledge/  ← Cuidado geriátrico (si el .zoe es para mayores)
│   ├── language_patterns/     ← Patrones para PatternSpeaker (sin LLM)
│   └── ... (hasta 15+ cápsulas)
│
├── language_patterns/         ← Patrones de respuesta (para funcionar sin LLM)
│   ├── response_templates.jsonl
│   ├── dialogue_patterns.jsonl
│   └── intent_classifiers.jsonl
│
├── config.yaml                ← Configuración del organismo
│
├── zoe_runtime.py             ← Runtime mínimo (Sprint 3.5) — ejecuta sin pip install
│
└── embedded_model.gguf        ← (OPCIONAL) Modelo tiny para L2/L3 sin red
```

### Tamaños según configuración

| Tipo de .zoe | Tamaño | Contenido | Cuándo usar |
|---|---|---|---|
| **.zoe Lite** | ~50 MB | Sin modelo embebido. Usa PatternSpeaker. | Máxima portabilidad |
| **.zoe Standard** | ~550 MB | Con Qwen 0.5B embebido. L2/L3 básico. | Portabilidad + calidad |
| **.zoe Pro** | ~2-5 GB | Con Qwen 3B embebido. L2/L3 decente. | Calidad media offline |
| **.zoe Cloud** | ~50 MB | Sin modelo. Configurado para cloud API. | Calidad máxima con red |

---

## 3. Los 3 modos de funcionamiento

### Modo 1: Sin LLM (PatternSpeaker puro)

El host no tiene Ollama, no tiene internet, no tiene API keys.

```
Usuario escribe → classify_intent (<1ms) → buscar en memoria → template → respuesta
```

**Calidad:** Suficiente para L0-L1. L2-L3 más simple pero coherente.
**Ventaja:** Funciona en CUALQUIER ordenador. Sin red, sin GPU, sin dependencias.

### Modo 2: Con modelo embebido (offline con IA)

El .zoe incluye `embedded_model.gguf` (Qwen 0.5B o 3B).

```
L0/L1 → PatternSpeaker (instantáneo)
L2/L3 → EmbeddedModelPeripheral (Qwen desde el .zoe, offline)
```

**Calidad:** Depende del modelo embebido (0.5B básica, 3B decente).
**Ventaja:** IA real offline. Sin red, sin Ollama instalado.

### Modo 3: Con LLM externo (calidad máxima)

El host tiene Ollama o API key de OpenAI/Anthropic.

```
L0/L1 → PatternSpeaker (instantáneo, gratis)
L2    → Ollama 7B local (gratis, calidad media)
L3    → GPT-4o/Claude cloud (calidad máxima, ~€0.05)
```

**Calidad:** Máxima. Igual que ZOE con instalación completa.
**Ventaja:** Aprovecha el hardware del host.

### Transición automática

ZOE detecta automáticamente qué tiene disponible y elige el mejor modo. **El usuario no configura nada.**

---

## 4. Variantes de .zoe

### Por caso de uso

| .zoe | Cápsulas incluidas | Modelo embebido | Tamaño | Precio |
|---|---|---|---|---|
| `zoe_cuidador_mayores.zoe` | zoe_basal, base_ethics, basic_psychology, elder_care_knowledge, elder_care_skills, pharmacy_interactions | Qwen 3B | ~2.5 GB | €150 |
| `zoe_compañia_soledad.zoe` | zoe_basal, base_ethics, basic_psychology, communication_skills, company_loneliness_knowledge | Qwen 3B | ~2.5 GB | €100 |
| `zoe_vigilancia_devops.zoe` | zoe_basal, base_ethics, vigilance_devops_knowledge, research_methodology | Qwen 7B | ~5 GB | €200 |
| `zoe_investigacion.zoe` | zoe_basal, base_ethics, research_methodology | Sin embebido | ~50 MB | €50 |
| `zoe_federacion_b2b.zoe` | zoe_basal, base_ethics, federation_b2b_skills | Qwen 7B | ~5 GB | €500 |
| `zoe_asistente_personal.zoe` | zoe_basal, base_ethics, basic_psychology, b2c_assistant_growth, communication_skills | Qwen 3B | ~2.5 GB | €80 |
| `zoe_heredable.zoe` | zoe_basal, base_ethics, ia_heredable_legal | Sin embebido | ~50 MB | €200 |
| `zoe_lite.zoe` | zoe_basal, base_ethics, language_patterns | Sin embebido | ~50 MB | Gratis |

### Por nivel de LLM

| Variante | Modelo embebido | Calidad offline | Tamaño |
|---|---|---|---|
| **.zoe Lite** | Ninguno (PatternSpeaker) | Básica (patrones) | ~50 MB |
| **.zoe Micro** | Qwen 0.5B | Baja pero funcional | ~550 MB |
| **.zoe Standard** | Qwen 3B | Decente | ~2.5 GB |
| **.zoe Pro** | Qwen 7B | Buena | ~5 GB |
| **.zoe Cloud** | Ninguno (usa cloud API) | Máxima (con red) | ~50 MB |
| **.zoe Ultimate** | Qwen 14B (IQ2_M) | Alta | ~10 GB |

---

## 5. Cómo se crea un .zoe

### Desde Python

```python
from zoe.core.zoe_packager import ZoePackager

packager = ZoePackager()

# .zoe Lite (sin modelo)
packager.package(
    output_path="zoe_cuidador.zoe",
    organism_id="zoe_cuidador_v1",
    memory_db="zoe_data/memory.db",
    capsules_dir="zoe/capsules",
    config_path="zoe/config/production.yaml",
    description="ZOE Cuidador de Mayores",
)

# .zoe Pro (con modelo embebido)
packager.package(
    output_path="zoe_cuidador_pro.zoe",
    organism_id="zoe_cuidador_v1",
    memory_db="zoe_data/memory.db",
    capsules_dir="zoe/capsules",
    embedded_model_path="models/qwen2.5:3b.gguf",
    description="ZOE Cuidador Pro - con IA offline",
)
```

### Inspeccionar sin desempaquetar

```python
manifest = packager.inspect("zoe_cuidador.zoe")
print(f"Organismo: {manifest.organism_id}")
print(f"Cápsulas: {manifest.capsule_count}")
print(f"Memoria: {manifest.memory_entries} entries")
print(f"Modelo embebido: {manifest.has_embedded_model}")
```

---

## 6. Caso de uso completo

### Escenario: Fernando compra "ZOE Cuidador de Mayores Pro"

#### Paso 1: Descarga (5 min)
- Compra en marketplace/web → descarga `zoe_cuidador_mayores_pro.zoe` (~2.5 GB)

#### Paso 2: Verificación (1 min)
```bash
python -c "
from zoe.core.zoe_packager import ZoePackager
m = ZoePackager().inspect('zoe_cuidador_mayores_pro.zoe')
print(f'Organismo: {m.organism_id}, Cápsulas: {m.capsule_count}, Modelo: {m.has_embedded_model}')
"
```

#### Paso 3: Instalación (2 min)
```bash
# En SSD portátil
python -c "
from zoe.core.zoe_packager import ZoePackager
ZoePackager().unpackage('zoe_cuidador_mayores_pro.zoe', '/Volumes/Mi-SSD/ZOE')
"
```

#### Paso 4: Ejecución (30 seg)
```bash
cd /Volumes/Mi-SSD/ZOE
python zoe_runtime.py
# ZOE despierta con su identidad, memoria y cápsulas intactas
```

#### Paso 5: Uso
```
zoe> Hola, ¿quién eres?
[L0_REFLEX] <50ms (PatternSpeaker)
ZOE: Soy ZOE, un organismo cognitivo sintético...

zoe> Mi madre tiene 78 años y vive sola.
[L3_DEEP] 8s (Qwen 3B embebido)
ZOE: Entiendo tu preocupación. Que tu madre viva sola a los 78...
```

#### Paso 6: Si instala Ollama después
ZOE detecta automáticamente Ollama y mejora L2/L3 a Qwen 7B. Sin reconfigurar nada.

---

## 7. Capacidades que mantiene

### SIEMPRE mantiene (en cualquier modo)

| Capacidad | .zoe Lite | .zoe Pro | .zoe Cloud |
|---|---|---|---|
| Identidad criptográfica (SHA-256) | ✅ | ✅ | ✅ |
| Memoria persistente (11 tipos) | ✅ | ✅ | ✅ |
| Bucle cognitivo continuo | ✅ | ✅ | ✅ |
| 12 sub-agentes (Society of Mind) | ✅ | ✅ | ✅ |
| Global Workspace (competición) | ✅ | ✅ | ✅ |
| Meta-cognición (System 1/2) | ✅ | ✅ | ✅ |
| Active Inference (Friston) | ✅ | ✅ | ✅ |
| Metabolismo (4 estados) | ✅ | ✅ | ✅ |
| Validación epistémica | ✅ | ✅ | ✅ |
| Trajectory Chain (firmada) | ✅ | ✅ | ✅ |
| Cápsulas de conocimiento | ✅ | ✅ | ✅ |
| ACD (4 niveles) | ✅ | ✅ | ✅ |
| Idiomas (ES/EN/FR/DE) | ✅ | ✅ | ✅ |
| Federación B2B | ✅ | ✅ | ✅ |
| Marketplace | ✅ | ✅ | ✅ |

### Depende del modo

| Capacidad | .zoe Lite | .zoe Pro | .zoe + Ollama |
|---|---|---|---|
| L0-L1 (rápido) | ✅ Patrones | ✅ Patrones | ✅ Patrones |
| L2 (estándar) | 🟡 Limitado | ✅ Qwen 3B | ✅ Ollama 7B |
| L3 (profundo) | 🟡 Básico | ✅ Qwen 3B | ✅ Cloud GPT-4o |
| Visión (VLM) | ❌ | 🟡 Si modelo soporta | ✅ Si LLaVA |
| Voz (STT/TTS) | ✅ Si instalados | ✅ Si instalados | ✅ Si instalados |

**Lo único que cambia es la calidad del lenguaje generado.** El cerebro de ZOE funciona igual en todos los modos.

---

## 8. Distribución y descarga

### Modelos de distribución

1. **Marketplace de ZOE** — compra y descarga directa
2. **Web de ZOE** — catálogo con compra Stripe
3. **Distribución directa** — email (Lite), USB, cloud storage
4. **Creación propia** — cualquier usuario empaqueta su ZOE

---

## 9. Sprint 3.5 — Runtime mínimo

El `zoe_runtime.py` es el runtime que se incluye dentro del .zoe. Permite ejecutar ZOE **sin instalar nada** (solo Python 3.10+ en el host).

### Características

- Solo usa Python stdlib (sin pip install)
- Carga memory.db desde SQLite
- Inicializa PatternSpeaker como backend
- Si detecta embedded_model.gguf, lo carga
- Si detecta Ollama en el host, lo usa
- Ejecuta bucle cognitivo simplificado
- Expone Dashboard web en localhost:8642

### Uso

```bash
# Después de desempaquetar el .zoe:
cd /path/to/ZOE
python zoe_runtime.py

# O con opciones:
python zoe_runtime.py --port 8642 --backend pattern
python zoe_runtime.py --dashboard  # abre Dashboard web
```

---

## 10. Sprint 3.6 — Enhanced PatternSpeaker

El Sprint 3.6 mejora el PatternSpeaker para que ZOE sea **mucho más capaz sin LLM**:

### 3 mejoras clave

#### A. Response Distillation (destilación de respuestas)

Antes de empaquetar un .zoe, se ejecuta ZOE con GPT-4o durante un tiempo. Las mejores respuestas se capturan y almacenan en `distilled_responses.jsonl`. El PatternSpeaker las recupera cuando el input es similar.

```python
# Proceso de destilación (antes de empaquetar .zoe):
# 1. Ejecutar ZOE con GPT-4o
# 2. Por cada respuesta buena, almacenar: {input, response, intent, quality}
# 3. Al empaquetar .zoe, incluir distilled_responses.jsonl
# 4. PatternSpeaker busca en destiladas PRIMERO, antes de templates
```

#### B. Retrieval-Augmented Patterns (patrones aumentados por memoria)

PatternSpeaker busca en TODA la memoria de ZOE (no solo la última respuesta), recupera knowledge relevante de las cápsulas, y lo incorpora a la respuesta.

```python
# En vez de solo templates:
# 1. Buscar en memory.db entries relevantes al input
# 2. Buscar en capsules/ knowledge relevante
# 3. Componer respuesta combinando: template + memoria + cápsula
```

#### C. Dashboard sin Ollama (PatternSpeaker como backend)

El Dashboard puede funcionar con PatternSpeaker como único backend. No necesita Ollama ni cloud API. El usuario abre el Dashboard, escribe, y ZOE responde desde patrones + memoria + destilación.

```bash
# Dashboard con PatternSpeaker (sin Ollama, sin cloud):
zoe-dashboard --backend pattern
# → http://localhost:8642
# → ZOE responde desde patrones + memoria destilada
```

### Resultado

Un .zoe con Enhanced PatternSpeaker puede:
- Responder con calidad cercana a L2 sin ningún LLM
- Usar conocimiento de las cápsulas en sus respuestas
- Recordar y reutilizar respuestas buenas del pasado
- Funcionar desde el Dashboard sin instalar Ollama
- Mantener conversación coherente de múltiples turnos

---

## 11. Sprint 5 — Cognitive Optimization Layer en .zoe

El Cognitive Optimization Layer (COL) funciona dentro del .zoe de forma transparente:

### Con .zoe Lite (sin modelo embebido)

```
Usuario escribe → CPL evalúa:
  ¿L0/L1? → PatternSpeaker responde (instantáneo, sin LLM)
  ¿L2/L3? → Enhanced PatternSpeaker + destiladas + cápsulas
             (si no hay destiladas, responde con lo mejor posible)
```

### Con .zoe Pro (con modelo embebido)

```
Usuario escribe → CPL evalúa:
  ¿L0/L1? → PatternSpeaker responde (no carga el modelo, ahorra RAM)
  ¿L2/L3? → CPL pre-carga modelo embebido + .zmap optimiza capas
             → Modelo genera respuesta (offline, sin red)
```

### Con .zoe + Ollama detectado en el host

```
Usuario escribe → CPL evalúa:
  ¿L0/L1? → PatternSpeaker responde (no toca Ollama)
  ¿L2/L3? → CPL pre-carga modelo en Ollama (warmup)
             + .zmap optimiza qué capas cargar
             + TPE predice qué capas necesitará
             → Ollama genera respuesta (mejor calidad que embebido)
```

### Con .zoe + Cloud API detectada

```
Usuario escribe → CPL evalúa:
  ¿L0/L1? → PatternSpeaker responde (no gasta API)
  ¿L2/L3? → CPL pre-construye contexto enriquecido
             (system prompt + memoria + cápsulas ya recuperadas)
             → Cloud API genera respuesta (máxima calidad)
```

### Beneficio para el usuario

**El usuario no necesita entender nada de esto.** ZOE detecta qué tiene disponible y elige la mejor opción automáticamente. El .zoe funciona en cualquier escenario:

| Escenario | L0/L1 (simple) | L2/L3 (complejo) |
|---|---|---|
| Solo .zoe | PatternSpeaker instantáneo | PatternSpeaker + destiladas |
| .zoe + Ollama | PatternSpeaker (no toca Ollama) | CPL pre-carga + .zmap + Ollama |
| .zoe + Cloud API | PatternSpeaker (no gasta API) | CPL pre-construye + API |
| .zoe + modelo embebido | PatternSpeaker (no carga modelo) | CPL + modelo embebido offline |

---

*ZOE V1.8.0 — Documento 16: ZOE Format (.zoe)*
*Julio 2026*
