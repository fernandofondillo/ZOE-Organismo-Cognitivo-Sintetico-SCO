# 12 — Integration Guide

> **Cómo integrar ZOE en sistemas externos: API REST, WebSocket, federación, SDK Python.**
> **Versión:** V1.6.0 — Julio 2026

---

## 1. Integración vía API REST

### Chat síncrono

```bash
curl -X POST http://localhost:8642/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hola ZOE"}'
```

### Python

```python
import requests

response = requests.post(
    "http://localhost:8642/chat",
    json={"message": "Hola ZOE"}
)
print(response.json()["response"])
```

### JavaScript

```javascript
const response = await fetch('http://localhost:8642/chat', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({message: 'Hola ZOE'})
});
const data = await response.json();
console.log(data.response);
```

---

## 2. Integración vía WebSocket

Para chat en tiempo real con streaming:

```javascript
const ws = new WebSocket('ws://localhost:8642/ws');

ws.onopen = () => {
    ws.send(JSON.stringify({cmd: 'chat', message: 'Hola ZOE'}));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'chat_token') {
        // Token de respuesta streaming
        console.log(data.token);
    } else if (data.type === 'chat_end') {
        // Respuesta completa
        console.log('Full:', data.full);
    } else if (data.type === 'state') {
        // Actualización de estado del organismo
        console.log('State:', data.state);
    }
};
```

### Eventos WebSocket

**Cliente → Servidor:**
- `{cmd: 'chat', message: '...'}` — enviar mensaje
- `{cmd: 'stats'}` — pedir stats
- `{cmd: 'memory'}` — pedir memoria
- `{cmd: 'sleep'}` — forzar sleep
- `{cmd: 'wake'}` — forzar wake

**Servidor → Cliente:**
- `{type: 'chat_token', token: '...'}` — token streaming
- `{type: 'chat_end', full: '...'}` — respuesta completa
- `{type: 'state', state: {...}}` — estado (cada 1s)
- `{type: 'thought', thought: '...'}` — pensamiento autónomo
- `{type: 'metabolism', state: '...'}` — cambio metabólico

---

## 3. SDK Python

ZOE se puede usar como librería Python:

```python
from zoe.cli_chat import ZoeChat

# Crear instancia
chat = ZoeChat(backend="ollama", model="qwen2.5:7b")
await chat.initialize()

# Enviar mensaje
response = await chat.send_message_acd("Hola ZOE")
print(response)

# Cambiar LLM
chat.switch_llm(backend="anthropic", model="claude-sonnet-4-20250514")

# Cargar cápsula
chat.capsule_manager.load("elder_care_knowledge")

# Ver stats
stats = chat.get_stats()
```

---

## 4. Integración con Ollama

```python
from zoe.peripherals.llm import OllamaPeripheral

# Crear backend Ollama
llm = OllamaPeripheral(model="qwen2.5:7b", base_url="http://localhost:11434")

# Generar
response = await llm.generate("Hola", max_tokens=100)

# Streaming
async for token in llm.generate_streaming("Cuéntame sobre..."):
    print(token, end='', flush=True)
```

---

## 5. Integración con OpenAI/Anthropic

```python
from zoe.peripherals.llm import OpenAICompatiblePeripheral, AnthropicPeripheral

# OpenAI
llm = OpenAICompatiblePeripheral(
    model="gpt-4o",
    api_key="sk-...",
    base_url="https://api.openai.com/v1"
)

# Anthropic
llm = AnthropicPeripheral(
    model="claude-sonnet-4-20250514",
    api_key="sk-ant-..."
)
```

---

## 6. Integración con federación

```python
from zoe.core.federation import FederationManager, FederationClient

# Registrar peer
client = FederationClient(organism_id="zoe_a", host="10.0.1.10", port=8642)
await client.register_with_peer("http://10.0.2.20:8642")

# Enviar voto
await client.send_vote("http://10.0.2.20:8642", mutation_id="...", vote="YES")

# Broadcast
await client.broadcast_to_peers({"event": "new_knowledge", "data": "..."})
```

---

## 7. Custom senses y actuators

### Crear sense custom

```python
from zoe.peripherals.senses import Sense
from zoe.core.cognitive_loop import Observation

class MyCustomSense(Sense):
    @property
    def name(self):
        return "my_custom"
    
    async def observe(self):
        return [Observation(
            timestamp=time.time(),
            source="my_custom",
            content="Custom observation",
            metadata={}
        )]
```

### Crear actuator custom

```python
from zoe.peripherals.actuators import Actuator, ActionResult

class MyCustomActuator(Actuator):
    @property
    def name(self):
        return "my_custom"
    
    async def execute(self, action):
        return ActionResult(success=True, output="Done")
```

---

## 8. Multi-modal (Sprint 2)

### Visión (VLM)

```python
from zoe.peripherals.multimodal import VLMPeripheral, VisionSense

# Crear VLM
vlm = VLMPeripheral(backend="openai_compatible", model="gpt-4o")

# Crear sense de visión
vision = VisionSense(vlm=vlm)

# Inyectar imagen
vision.inject_image(image_bytes, "¿Qué ves en esta imagen?")

# El bucle cognitivo la procesará en el próximo tick
```

### Voz (STT + TTS)

```python
from zoe.peripherals.multimodal import VoiceInputSense, VoiceActuator

# STT con Whisper
voice_input = VoiceInputSense(engine="whisper", model="base")
await voice_input.start_listening(duration=5.0)

# TTS con Piper
voice_output = VoiceActuator(engine="piper", voice="es_ES-davefx-medium")
await voice_output.execute({"type": "voice", "payload": "Hola, soy ZOE"})
```

---

## 9. Voice-first mode (Sprint 4)

```python
from zoe.peripherals.voice_first import VoiceFirstMode, VoiceConfig

# Configurar
config = VoiceConfig(
    wake_word="hey zoe",
    stt_model="base",
    tts_voice="es_ES-davefx-medium",
    enable_interruption=True,
)

# Crear y ejecutar
mode = VoiceFirstMode(zoe_url="http://localhost:8642", config=config)
await mode.initialize()
await mode.run()
```

O desde CLI:
```bash
python -m zoe.peripherals.voice_first --zoe-url http://localhost:8642
```

---

## 10. PatternSpeaker (sin LLM) — Sprint 3

```python
from zoe.peripherals.pattern_speaker import PatternPeripheral

# PatternSpeaker básico
llm = PatternPeripheral(memory=living_memory)
response = await llm.generate("Hola, ¿quién eres?")
```

### Enhanced PatternSpeaker — Sprint 3.6

```python
from zoe.peripherals.enhanced_pattern_speaker import EnhancedPatternPeripheral

# Con destilación + retrieval + dialog state
llm = EnhancedPatternPeripheral(
    memory=living_memory,
    distilled_responses_path="distilled_responses.jsonl",
    capsules_dir="zoe/capsules",
)
response = await llm.generate("Mi madre toma paracetamol, ¿puede con alcohol?")
# Respuesta enriquecida con knowledge de cápsulas + respuestas destiladas
```

### Destilar respuestas de LLM

```python
from zoe.peripherals.enhanced_pattern_speaker import ResponseDistiller

distiller = ResponseDistiller("distilled_responses.jsonl")

# Después de una buena respuesta de GPT-4o:
distiller.distill(
    input_text="¿Qué es la paracetamol?",
    response_text="La paracetamol es un analgésico...",
    source="gpt-4o",
    quality_score=0.95,
)
# Esta respuesta se reutilizará sin necesidad de GPT-4o en el futuro
```

---

## 11. Formato .zoe (Sprint 3)

```python
from zoe.core.zoe_packager import ZoePackager

packager = ZoePackager()

# Empaquetar organismo completo
packager.package(
    output_path="mi_zoe.zoe",
    organism_id="zoe_fernando",
    memory_db="zoe_data/memory.db",
    capsules_dir="zoe/capsules",
    embedded_model_path="models/qwen2.5:3b.gguf",  # opcional
)

# Inspeccionar sin desempaquetar
manifest = packager.inspect("mi_zoe.zoe")

# Desempaquetar
packager.unpackage("mi_zoe.zoe", "/path/to/output")
# cd /path/to/output && python zoe_runtime.py
```

---

## 12. Webhooks (en roadmap)

ZOE podrá enviar webhooks a sistemas externos:
- `on_thought` — cuando ZOE genera pensamiento autónomo
- `on_mutation` — cuando ZOE firma mutación
- `on_quarantine` — cuando conocimiento entra a cuarentena
- `on_metabolism_change` — cuando cambia estado metabólico

**Estado:** En roadmap Q4 2026.

---

*ZOE V1.6.0 — Documento 12: Integration Guide*
*Julio 2026*
