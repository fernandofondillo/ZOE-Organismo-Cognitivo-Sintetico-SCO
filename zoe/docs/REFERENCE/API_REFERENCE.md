# API Reference

> **50+ endpoints REST de ZOE documentados.**
> **Versión:** V1.6.0 — Julio 2026

---

## Core

### POST /chat
Chat síncrono.
```bash
curl -X POST http://localhost:8642/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hola ZOE"}'
```
**Response:** `{"response": "...", "acd_level": "L2_STANDARD", "duration_ms": 3200}`

### GET /ws
WebSocket para chat en tiempo real. Ver [Integration Guide](../12_INTEGRATION_GUIDE.md).

### POST /feed
Subir archivo a memoria.
```bash
curl -X POST http://localhost:8642/feed -F "file=@archivo.txt"
```

### GET /stats
Stats del organismo.
```bash
curl http://localhost:8642/stats
```

### GET /memory
Memoria viva.
### GET /identity
Identity Vault.
### GET /state
InternalState.
### POST /sleep
Forzar SLEEPING.
### POST /wake
Forzar AWAKE.
### POST /llm
Cambiar LLM en caliente.
```bash
curl -X POST http://localhost:8642/llm \
  -d '{"backend": "anthropic", "model": "claude-sonnet-4-20250514"}'
```
### GET /history
Histórico de conversaciones.
### GET /federation
Estado de federación.

---

## Cápsulas (6B)

| Endpoint | Método | Descripción |
|---|---|---|
| `/api/capsules` | GET | Lista cápsulas disponibles |
| `/api/capsules/loaded` | GET | Cápsulas cargadas |
| `/api/capsules/load` | POST | Cargar cápsula |
| `/api/capsules/unload` | POST | Descargar cápsula |
| `/api/capsules/{name}/info` | GET | Info de cápsula |
| `/api/capsules/{name}/validate` | POST | Validar cápsula |
| `/api/capsules/create` | POST | Crear nueva cápsula |

---

## Epistémico (6A)

| Endpoint | Método | Descripción |
|---|---|---|
| `/federation/epistemic/validate` | POST | Validar claim |
| `/federation/epistemic/knowledge/{hash}` | GET | Obtener conocimiento |
| `/federation/epistemic/register` | POST | Registrar peer |
| `/federation/epistemic/peers` | GET | Listar peers |
| `/federation/epistemic/stats` | GET | Stats federación |
| `/federation/epistemic/request_validation` | POST | Pedir validación |

---

## Cuarentena (6A)

| Endpoint | Método | Descripción |
|---|---|---|
| `/api/quarantine` | GET | Lista cuarentena |
| `/api/quarantine/stats` | GET | Stats cuarentena |
| `/api/quarantine/{id}/promote` | POST | Promover |
| `/api/quarantine/{id}/reject` | POST | Rechazar |

---

## Marketplace (6B)

| Endpoint | Método | Descripción |
|---|---|---|
| `/api/marketplace/capsules` | GET | Lista marketplace |
| `/api/marketplace/upload` | POST | Subir cápsula |
| `/api/marketplace/download/{name}` | POST | Descargar cápsula |
| `/api/marketplace/use_cases` | GET | Lista casos de uso |
| `/api/marketplace/upload_use_case` | POST | Subir caso de uso |

---

## Mentor (6C)

| Endpoint | Método | Descripción |
|---|---|---|
| `/api/mentor` | GET | Config mentor |
| `/api/mentor` | POST | Actualizar mentor |
| `/api/mentor/stats` | GET | Stats mentor |

---

## Model Optimizer (7F + 7G)

| Endpoint | Método | Descripción |
|---|---|---|
| `/api/models/system_info` | GET | Info hardware (con p_cores, e_cores) |
| `/api/models/recommend` | GET | Recomendaciones por ACD |
| `/api/models/catalog` | GET | Catálogo modelos |
| `/api/models/optimize` | POST | Optimizar modelo específico |

---

## Hardware (7G)

| Endpoint | Método | Descripción |
|---|---|---|
| `/api/hardware/ssds` | GET | SSDs recomendados |
| `/api/hardware/token_rates` | GET | Tabla tokens/s |
| `/api/hardware/cable_warning` | GET | Warning cable USB-C |
| `/api/hardware/system` | GET | Info hardware host |

---

## Resource Discovery (7A)

| Endpoint | Método | Descripción |
|---|---|---|
| `/api/resources` | GET | Grafo recursos |
| `/api/resources/stats` | GET | Stats recursos |
| `/api/resources/scan` | POST | Ejecutar scan |

---

## Model Bus (7B)

| Endpoint | Método | Descripción |
|---|---|---|
| `/api/modelbus` | GET | Lista backends |
| `/api/modelbus/stats` | GET | Stats bus |
| `/api/modelbus/select` | POST | Seleccionar backend |

---

## Resource Planner (7C)

| Endpoint | Método | Descripción |
|---|---|---|
| `/api/planner/plan` | POST | Generar plan |
| `/api/planner/stats` | GET | Stats planner |
| `/api/planner/recommend` | GET | Recomendaciones |

---

## Embodiment Composer (7D)

| Endpoint | Método | Descripción |
|---|---|---|
| `/api/embodiment/compose` | POST | Componer desde plan |
| `/api/embodiment/bootstrap` | POST | Pipeline completo |
| `/api/embodiment/status` | GET | Estado composer |
| `/api/embodiment/list` | GET | Lista embodiments |
| `/api/embodiment/tear_down` | POST | Detener embodiment |
| `/api/embodiment/log` | GET | Log composiciones |

---

## Seed Mode (7E)

| Endpoint | Método | Descripción |
|---|---|---|
| `/api/seed/detect` | GET | Detectar semilla |
| `/api/seed/inspect` | GET | Inspeccionar semilla |
| `/api/seed/create` | POST | Crear semilla |
| `/api/seed/germinate` | POST | Germinar semilla |
| `/api/seed/stats` | GET | Stats ZOESeed |
| `/api/seed/last_report` | GET | Último reporte |

---

## PWA (Sprint 1)

| Endpoint | Método | Descripción |
|---|---|---|
| `/manifest.json` | GET | PWA manifest para instalación en móvil |

---

**Total: 50+ endpoints REST**

---

*ZOE V1.7.0 — API Reference*
*Julio 2026*
