# 05 — Epistemic Validation

> **Cómo ZOE valida el conocimiento: EpistemicValidator, Quarantine, CrossValidator, Federación epistémica.**
> **Audiencia:** desarrolladores, investigadores.
> **Versión:** V1.8.0 — Julio 2026

---

## Tabla de contenidos

1. [El problema epistémico](#1-el-problema-epistémico)
2. [EpistemicValidator](#2-epistemicvalidator)
3. [KnowledgeQuarantine](#3-knowledgequarantine)
4. [CrossValidator](#4-crossvalidator)
5. [EpistemicFederation](#5-epistemicfederation)
6. [Flujo completo de validación](#6-flujo-completo-de-validación)
7. [Dashboard de Cuarentena](#7-dashboard-de-cuarentena)
8. [Configuración avanzada](#8-configuración-avanzada)

---

## 1. El problema epistémico

Los LLMs (GPT-4, Claude, etc.) tienen un problema fundamental: **alucinan con seguridad**. Cuando no saben algo, lo inventan con la misma confianza que cuando sí saben. No distinguen "sé" de "creo" de "no sé".

ZOE resuelve esto con un **sistema epistémico de 4 capas**:

1. **EpistemicValidator** — valida todo conocimiento nuevo
2. **KnowledgeQuarantine** — cuarentena activa para conocimiento no validado
3. **CrossValidator** — triple verificación multi-fuente
4. **EpistemicFederation** — revisión por pares entre ZOEs

---

## 2. EpistemicValidator

**Archivo:** `zoe/core/epistemic_validator.py` (399 LOC)

### 2.1 Fuentes categorizadas

ZOE asigna confianza base según la fuente del conocimiento:

```python
SOURCE_TRUST = {
    # Cápsulas (conocimiento empaquetado)
    "capsule:verified": 0.95,      # Validado por expertos
    "capsule:curated": 0.80,       # Curado por expertos
    "capsule:community": 0.55,     # Comunidad
    "capsule:experimental": 0.40,  # Experimental
    
    # LLMs (modelos de lenguaje)
    "llm:gpt-4o": 0.50,            # GPT-4o
    "llm:claude": 0.50,            # Claude
    "llm:qwen-7b": 0.40,           # Qwen local
    "llm:qwen-3b": 0.30,           # Qwen pequeño
    
    # Científico
    "scientific:pubmed": 0.95,     # PubMed
    "scientific:arxiv": 0.85,      # arXiv
    "scientific:cochrane": 0.95,   # Cochrane reviews
    "scientific:who": 0.95,        # OMS
    
    # Web
    "web:general": 0.30,           # Web general
    "web:wikipedia": 0.50,         # Wikipedia
    
    # Federación
    "federation:peer": 0.70,       # Otra ZOE
    "federation:quorum": 0.85,     # Quorum de ZOEs
}
```

### 2.2 Dominios sensibles

5 dominios requieren **triple verificación**:

```python
SENSITIVE_DOMAINS = [
    "medical",        # Todo lo médico
    "psychological",  # Todo lo psicológico
    "legal",          # Todo lo legal
    "safety",         # Seguridad física
    "financial",      # Consejos financieros
]
```

### 2.3 Cap de confianza

ZOE limita cuánta confianza puede tener en conocimiento según su origen:

| Origen | Confianza máxima |
|---|---|
| Auto-aprendido (Learner) | 0.50 |
| Triple-verificado (CrossValidator) | 0.75 |
| Federativo (quorum de ZOEs) | 0.85 |
| Cápsula verified | 0.95 |

### 2.4 API

```python
class EpistemicValidator:
    def validate_new_knowledge(self, claim: str, source: str, 
                                domain: str = None) -> ValidationResult:
        """Valida un claim nuevo."""
        # 1. Detectar dominio
        # 2. Verificar confianza de fuente
        # 3. Si dominio sensible, requerir triple verificación
        # 4. Verificar contradicción con conocimiento existente
        # 5. Aplicar cap de confianza
        # Returns: ValidationResult(status, confidence, reason)
```

---

## 3. KnowledgeQuarantine

**Archivo:** `zoe/core/knowledge_quarantine.py` (284 LOC)

La cuarentena activa mantiene conocimiento no validado **separado** del conocimiento confiable.

### 3.1 Ciclo de vida

```
Conocimiento nuevo
    ↓
EpistemicValidator valida
    ↓
¿Pasa validación?
├── SÍ → Entra a memoria con confianza asignada
└── NO → Va a QUARANTINE
            ↓
    ¿Confirmado por 2+ fuentes?
    ├── SÍ → PROMOTE (sale de cuarentena, confianza 0.75)
    ├── NO (30 días) → EXPIRE (se olvida)
    └── Contradicción → REJECT (se rechaza)
```

### 3.2 API

```python
class KnowledgeQuarantine:
    def add(self, claim: str, source: str, domain: str = None) -> str:
        """Añade claim a cuarentena. Devuelve entry_id."""
    
    def filter_safe(self, critical_context: bool = False) -> List[QuarantineEntry]:
        """Filtra entries seguras para usar."""
        # Si critical_context=True, solo devuelve verified
        # Si False, devuelve verified + quarantined (para brainstorming)
    
    def promote(self, entry_id: str, second_source: str) -> bool:
        """Promueve claim a conocimiento confiable."""
        # Requiere 2 fuentes confirmándolo
    
    def reject(self, entry_id: str, reason: str) -> bool:
        """Rechaza claim."""
    
    def cleanup_expired(self) -> int:
        """Elimina entries expiradas (default 30 días)."""
```

### 3.3 Cuándo se usa cuarentena vs memoria

| Contexto | Usa cuarentena | Usa memoria |
|---|---|---|
| Decisión crítica (médica, legal) | ❌ | ✅ (solo verified) |
| Brainstorming, hipótesis | ✅ | ✅ |
| Respuesta al usuario L3_DEEP | ❌ | ✅ (solo verified) |
| Respuesta al usuario L1_FAST | ⚠️ (con disclaimer) | ✅ |
| Aprendizaje autónomo | ✅ (en cuarentena) | ✅ (si promovido) |

---

## 4. CrossValidator

**Archivo:** `zoe/core/cross_validator.py` (325 LOC)

Triple verificación consultando 3 fuentes independientes.

### 4.1 Cómo funciona

```python
class CrossValidator:
    async def verify_triple(self, claim: str, 
                             sources: List[str]) -> CrossVerificationResult:
        """Verifica claim con 3 fuentes."""
        # 1. Consultar 3 fuentes en paralelo
        #    - LLM-A (ej: GPT-4o)
        #    - LLM-B (ej: Claude)
        #    - Cápsula o tercera fuente
        # 2. Comparar respuestas con similitud léxica (Jaccard)
        # 3. Resultado:
        #    - 3/3 coinciden → confianza 0.75 (sale de cuarentena)
        #    - 2/3 coinciden → confianza 0.65 o 0.80 si cápsula en mayoría
        #    - Divergencia total → rechazo
```

### 4.2 Similitud léxica

```python
def _lexical_similarity(self, text_a: str, text_b: str) -> float:
    """Similitud Jaccard entre dos textos."""
    tokens_a = set(text_a.lower().split())
    tokens_b = set(text_b.lower().split())
    intersection = tokens_a & tokens_b
    union = tokens_a | tokens_b
    return len(intersection) / len(union) if union else 0.0
```

### 4.3 Resultados

| Coincidencia | Confianza | Acción |
|---|---|---|
| 3/3 fuentes | 0.75 | Promueve de cuarentena |
| 2/3 + cápsula en mayoría | 0.80 | Promueve de cuarentena |
| 2/3 sin cápsula | 0.65 | Mantiene en cuarentena |
| 1/3 | 0.30 | Mantiene en cuarentena |
| 0/3 (divergencia) | 0.0 | Rechaza |

---

## 5. EpistemicFederation

**Archivo:** `zoe/core/epistemic_federation.py` (329 LOC)

Revisión por pares entre ZOEs vía HTTP.

### 5.1 Cómo funciona

```
ZOE A descubre claim nuevo
    ↓
ZOE A envía KnowledgeValidationRequest a peers (ZOE B, ZOE C)
    ↓
ZOE B y C responden: confirmed | contradicted | unknown
    ↓
ZOE A evalúa:
├── ≥2 confirmaciones → confianza sube a 0.85 (sale de cuarentena)
├── ≥1 contradicción → rechazo federativo
└── Respuestas insuficientes → mantiene en cuarentena
```

### 5.2 API

```python
class EpistemicFederation:
    async def request_validation(self, claim: str, domain: str) -> str:
        """Pide a peers que validen el claim."""
    
    async def receive_validation_request(self, request) -> KnowledgeValidationResponse:
        """Recibe request de otra ZOE."""
        # 1. Buscar en memoria local si conoce el claim
        # 2. Responder: confirmed | contradicted | unknown
    
    async def receive_validation_response(self, response):
        """Recibe respuesta de un peer."""
        # Acumular respuestas
        # Si ≥2 confirmaciones → promover
        # Si ≥1 contradicción → rechazar
```

### 5.3 Endpoint HTTP

```python
# zoe/core/epistemic_federation_server.py (351 LOC)
class EpistemicFederationServer:
    """Servidor HTTP para federación epistémica."""
    
    # Endpoints:
    # POST /federation/epistemic/validate       — validar claim
    # GET  /federation/epistemic/knowledge/{hash}  — obtener conocimiento
    # POST /federation/epistemic/register       — registrar peer
    # GET  /federation/epistemic/peers          — listar peers
    # GET  /federation/epistemic/stats          — stats federación
```

---

## 6. Flujo completo de validación

```
ZOE detecta gap de conocimiento (ScientificEngine o Learner)
    ↓
EpistemicValidator valida el claim nuevo
    ↓
¿Dominio sensible (medical, psychological, legal, safety, financial)?
├── SÍ → NEEDS_TRIPLE_VALIDATION → cuarentena
└── NO → continúa
    ↓
¿Fuente confiable (confidence ≥ 0.50)?
├── SÍ → entra a memoria con confianza asignada
└── NO → cuarentena
    ↓
[Si en cuarentena]
CrossValidator consulta 3 fuentes (LLM-A + LLM-B + cápsula)
    ↓
3/3 coinciden → promueve a confianza 0.75
2/3 coinciden → confianza 0.65, sigue en cuarentena
Divergencia → rechazo
    ↓
EpistemicFederation envía a peers para validación adicional
    ↓
≥2 peers confirman → confianza sube a 0.85
≥1 peer contradice → rechazo federativo
    ↓
Si después de 30 días no se valida → Curator poda (olvida)
    ↓
Todo queda firmado en TrajectoryChain
```

---

## 7. Dashboard de Cuarentena

Desde el Dashboard web, clic en 🔒 **Cuarentena** del panel izquierdo.

### 7.1 Stats visuales

- **Total** — todas las entries en cuarentena
- **Activas** (amarillo) — pendientes de validación
- **Verificadas** (verde) — promovidas a memoria
- **Rechazadas** (rojo) — rechazadas
- **Expiradas** (gris) — eliminadas por timeout

### 7.2 Lista de entries activas

Cada entry muestra:
- Claim (truncado)
- Dominio
- Source
- Confianza actual
- Razón de cuarentena
- Confirmaciones y contradicciones
- Botones: [✓ Promover] [✗ Rechazar]

### 7.3 Acciones

- **Promover**: marca como validado, sale de cuarentena
- **Rechazar**: elimina de cuarentena, no entra a memoria
- Recarga automática tras cada acción

---

## 8. Configuración avanzada

### 8.1 Dominios sensibles custom

```python
from zoe.core.epistemic_validator import EpistemicValidator

validator = EpistemicValidator()
validator.SENSITIVE_DOMAINS.append("aviation")  # añadir dominio custom
```

### 8.2 Fuentes custom

```python
validator.SOURCE_TRUST["scientific:nasa"] = 0.95
validator.SOURCE_TRUST["web:mi_org"] = 0.70
```

### 8.3 Timeout de cuarentena

```python
from zoe.core.knowledge_quarantine import KnowledgeQuarantine

quarantine = KnowledgeQuarantine(default_timeout_days=60)  # 60 días en vez de 30
```

### 8.4 Endpoints REST

```bash
# Listar cuarentena
curl http://localhost:8642/api/quarantine

# Stats
curl http://localhost:8642/api/quarantine/stats

# Promover
curl -X POST http://localhost:8642/api/quarantine/{entry_id}/promote \
  -H "Content-Type: application/json" \
  -d '{"second_source": "scientific:pubmed"}'

# Rechazar
curl -X POST http://localhost:8642/api/quarantine/{entry_id}/reject \
  -H "Content-Type: application/json" \
  -d '{"reason": "Contradicted by 2 sources"}'
```

---

## Cierre

El sistema epistémico es lo que hace que ZOE **no alucine con seguridad**. Conocimiento nuevo va a cuarentena, se valida con múltiples fuentes, y solo cuando está confirmado entra a memoria confiable. Esto es crítico para:
- Datos médicos (no dar consejo médico incorrecto)
- Datos legales (no dar consejo legal incorrecto)
- Cualquier dominio sensible

**Documentos relacionados:**
- [04_MEMORY_AND_LEARNING.md](04_MEMORY_AND_LEARNING.md) — dónde se almacena el conocimiento validado
- [11_SECURITY_COMPLIANCE.md](11_SECURITY_COMPLIANCE.md) — cumplimiento normativo
- [02_ARCHITECTURE.md](02_ARCHITECTURE.md) — arquitectura del subsistema epistémico

---

*ZOE V1.8.0 — Documento 05: Epistemic Validation*
*Julio 2026*
