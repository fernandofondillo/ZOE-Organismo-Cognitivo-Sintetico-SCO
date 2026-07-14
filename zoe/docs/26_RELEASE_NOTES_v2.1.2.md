# ZOE v2.1.2 — Release Notes

**Fecha:** Julio 2026
**Commit:** `a6a45d6`
**Estado:** Production Ready (Score: 8.3/10)

---

## Resumen

ZOE v2.1.2 es la primera versión **Production Ready** del organismo cognitivo sintético. Tras 8 sprints de hardening (5.12 → 5.20), se resolvieron **31 issues críticos** de seguridad, rendimiento, escalabilidad y observabilidad. El proyecto pasó de **4.8/10 (NOT_READY)** a **8.3/10 (READY)**.

---

## Sprints incluidos

### Sprint 5.12 — Dashboard utilizable + coherencia SSD
- Dashboard HTML maneja auth token automáticamente (?token= → localStorage → Bearer)
- Rate limit middleware refactorizado a funcional (compatible aiohttp 3.13+)
- Token persistido a `data/dashboard_token.txt` (chmod 0600)
- Launchers universales (`INICIAR-DASHBOARD.command`, `INICIAR-ZOE.command`) con detección automática de backend
- Todos los launchers pasan `--db-path` al SSD (coherencia garantizada)
- Default `db_path` usa `$ZOE_DATA` si existe

### Sprint 5.12.1 — Cápsulas base + Tutor + Idioma
- 5 cápsulas base cargadas SIEMPRE: `zoe_basal_knowledge`, `communication_skills`, `base_ethics`, `basic_psychology`, `language_patterns` (162 entradas)
- MentorAgent activo por defecto (áreas: communication, empathy, critical_thinking, self_awareness)
- LanguageDetector detecta es/en/fr/de sin LLM (<10ms)
- Manual reescrito a 2,444 líneas, 22 secciones

### Sprint 5.13 — 8 bloqueantes críticos (B1-B8)
- B1: `loop._storage_backend` UnboundLocalError fixed (postgres path)
- B2: ReflectionEngine cableado en producción via `metabolism.attach_reflection_hook()`
- B3: `await mentor.evaluate_thought` (sync) fixed → llamada sin await
- B4: `serve.py` sirve HTTP en puerto 8080 (/health, /ready, /live, /metrics)
- B4-bis: Memory leaks bounded (`_max_thoughts=1000`, `deque(maxlen=500)`)
- B5: `k8s/secret.yaml` eliminado del git + `.gitignore` + `.example`
- B6: Auth token NO logueado (redaction en structured logging)
- B7: `hmac.compare_digest` para token comparison (timing-safe)
- B8: 44 tests rotos arreglados (asyncpg, Proposal(action=), hardware handlers, PWA)

### Sprint 5.14 — Regresión crítica + test hygiene
- Fix `/history` endpoint (deque slicing → `list()` conversion)
- Fix `test_full_system_integration.py` Proposal(action=)
- Tests async convertidos a `@pytest.mark.asyncio` (no `asyncio.run()`)

### Sprint 5.15 — Errores bloqueantes k8s + CI
- k8s image: `ghcr.io/fernandofondillo/zoe-organismo-cognitivo-sintetico-sco:latest` + `imagePullPolicy: Always`
- Ollama UID fix: `mountPath: /var/lib/ollama` + `OLLAMA_MODELS=/var/lib/ollama`
- RWO PVC: `replicas: 1` + `strategy: Recreate`
- Helm template syntax removed → Reloader annotation
- 7 test_loop_v3.py failures fixed
- `bandit || true` removed — security scan ahora falla CI
- Coverage threshold: 55% → 65%

### Sprint 5.16 — Seguridad + rendimiento
- L0_REFLEX bug fixed: "no me gusta" ya no se clasifica como reflejo
- `/memory` con paginación (limit/offset, max 200)
- `/feed` con limites: MAX_FILE_SIZE=10MB, extension whitelist, filename sanitization
- Argument injection prevention en `/api/capsules` (regex validation)
- Version unificada a 2.1.2 (setup.py, __init__.py, README)
- SQLite ops async via `asyncio.to_thread()` en /health y /ready

### Sprint 5.17 — Observabilidad
- Structured logging JSON con redaction de secrets (`zoe/core/structured_logging.py`)
- `/live` check real: cognitive loop iterations, memoria < 95%, disco < 95%
- `/health` y `/ready` detectan postgres vs sqlite via `ZOE_STORAGE_TYPE`
- `k8s/prometheus-rules.yaml` con 6 alertas (ZoeDown, ZoeHighMemory, etc.)

### Sprint 5.18 — Hardening k8s
- PodDisruptionBudget para ZOE, Ollama, PostgreSQL
- HorizontalPodAutoscaler (CPU 70%, Memory 80%)
- ServiceMonitor para Prometheus auto-discovery
- NetworkPolicy endurecida (deny-inter-pod-default)
- `readOnlyRootFilesystem: true` + `seccompProfile: RuntimeDefault` en Ollama

### Sprint 5.19 — Escalabilidad
- Distributed rate limiting con Redis (`_RedisRateLimiter` con sorted sets)
- Multi-tenant con `tenant_id` (header `X-ZOE-Tenant` o query `?tenant=`)
- Tenant validation regex (anti-injection)
- Fallback graceful: sin Redis → in-memory, sin tenant → default

### Sprint 5.20 — Chaos engineering + fuzzing
- 6 chaos tests reales: DB corrupta, DB missing, concurrent init, shutdown sin init, memory bounded, token persistence
- 6 fuzzing tests: tenant injection, capsule name injection, pagination bounds, filename sanitization, auth token timing, depth classifier extreme inputs

---

## Métricas

| Métrica | Antes (5.12) | Después (5.20) |
|---------|:-----------:|:--------------:|
| Tests | 1,726 collected, 44 broken | 1,832 collected, 0 broken |
| Archivos Python | 213 | 220 |
| k8s manifests | 14 | 17 (PDB, HPA, ServiceMonitor, PrometheusRule) |
| CI threshold | 55% coverage, bandit `\|\| true` | 65% coverage, bandit real |
| Security score | 4.0/10 | 9.0/10 |
| Production score | 4.1/10 | 8.5/10 |
| Global score | 4.8/10 | 8.3/10 |

---

## Features nuevas

- **Distributed rate limiting** con Redis (multi-pod)
- **Multi-tenant** con `X-ZOE-Tenant` header
- **Structured logging** JSON con redaction de secrets
- **ReflectionEngine** cableado en producción (DeepSeek-R1:32B)
- **5 cápsulas base** cargadas automáticamente (162 entradas)
- **MentorAgent** activo por defecto
- **LanguageDetector** es/en/fr/de sin LLM
- **/live check real** (CPU, memory, disk, cognitive loop)
- **6 alertas Prometheus** listas
- **Chaos engineering** + **fuzzing tests** reales

---

## Breaking changes

- `k8s/secret.yaml` eliminado del git. Usar `k8s/secret.yaml.example` como template.
- Version canónica cambiada de `1.8.0` a `2.1.2` en `setup.py` e `__init__.py`.
- `_L0_TOKENS` separado en `_L0_TOKENS_STRICT` y `_L0_TOKENS_AMBIGUOUS`. "no me gusta" ya no es L0_REFLEX.
- `/memory` ahora requiere paginación (default limit=50, max=200).
- `/feed` ahora rechaza archivos > 10MB y extensiones no permitidas.
- Rate limit middleware acepta `redis_url` parameter opcional.

---

## Upgrade guide

```bash
git pull origin main
pip install -e .

# Si usas k8s:
cp k8s/secret.yaml.example k8s/secret.yaml
# Editar secret.yaml con tus passwords
kubectl apply -f k8s/

# Si usas SSD:
bash zoe/scripts/zoe-bootstrap.sh  # detecta instalación existente y actualiza
```
