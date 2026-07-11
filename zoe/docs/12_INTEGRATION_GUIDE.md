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
        # Ejecutar acción
        return ActionResult(success=True, output="Done")
```

---

## 8. Webhooks (en roadmap)

ZOE podrá enviar webhooks a sistemas externos:
- `on_thought` — cuando ZOE genera pensamiento autónomo
- `on_mutation` — cuando ZOE firma mutación
- `on_quarantine` — cuando conocimiento entra a cuarentena
- `on_metabolism_change` — cuando cambia estado metabólico

**Estado:** En roadmap Q4 2026.

---

*ZOE V1.6.0 — Documento 12: Integration Guide*
*Julio 2026*
