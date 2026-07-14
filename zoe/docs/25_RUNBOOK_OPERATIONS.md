# ZOE Operations Runbook — v2.1.2

> Guía de operaciones para despliegue, monitoring, debugging y recuperación de ZOE en producción.

---

## 1. Despliegue

### 1.1 Despliegue en Kubernetes

```bash
# 1. Crear namespace
kubectl apply -f k8s/namespace.yaml

# 2. Crear secrets (copiar template primero)
cp k8s/secret.yaml.example k8s/secret.yaml
# Editar k8s/secret.yaml con passwords reales
kubectl apply -f k8s/secret.yaml

# 3. Desplegar configuración y RBAC
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/rbac.yaml

# 4. Desplegar PostgreSQL + Ollama
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/postgres-service.yaml
kubectl apply -f k8s/ollama-deployment.yaml
kubectl apply -f k8s/ollama-service.yaml

# 5. Desplegar ZOE
kubectl apply -f k8s/pvc.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# 6. Networking + Observabilidad
kubectl apply -f k8s/networkpolicy.yaml
kubectl apply -f k8s/ingress.yaml
kubectl apply -f k8s/prometheus-rules.yaml
kubectl apply -f k8s/service-monitor.yaml
kubectl apply -f k8s/pod-disruption-budget.yaml
kubectl apply -f k8s/horizontal-pod-autoscaler.yaml
```

### 1.2 Verificar despliegue

```bash
kubectl get pods -n zoe
kubectl exec -n zoe deployment/zoe -- curl -s http://localhost:8080/health | jq .
```

### 1.3 Despliegue en SSD (macOS)

```bash
bash <(curl -sL https://raw.githubusercontent.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO/main/zoe/scripts/zoe-bootstrap.sh)
# Doble click en INICIAR-DASHBOARD.command
```

---

## 2. Monitoring

### 2.1 Endpoints de salud

| Endpoint | Propósito | Status codes |
|----------|-----------|-------------|
| `/health` | Liveness + readiness | 200/503 |
| `/ready` | Ready para tráfico | 200/503 |
| `/live` | Liveness real (CPU, memory, disk, loop) | 200/503 |
| `/metrics` | Prometheus metrics | 200 |

### 2.2 Alertas Prometheus

| Alerta | Severidad | Acción |
|--------|-----------|--------|
| `ZoeDown` | Critical | Verificar pod, revisar logs |
| `ZoeHighMemory` | Warning | Escalar pods o aumentar limits |
| `ZoeHighDiskUsage` | Warning | Limpiar datos, expandir PVC |
| `ZoeCognitiveLoopStalled` | Critical | Reiniciar pod, revisar LLM |
| `ZoeHighErrorRate` | Warning | Revisar logs, verificar dependencias |
| `ZoeLLMUnavailable` | Warning | Verificar Ollama, verificar API keys |

---

## 3. Debugging

### 3.1 ZOE no responde
```bash
kubectl get pod -n zoe -l app.kubernetes.io/name=zoe
kubectl logs -n zoe -l app.kubernetes.io/name=zoe --tail=50
kubectl exec -n zoe deployment/zoe -- curl -s http://localhost:8080/health | jq .checks
```

### 3.2 Dashboard devuelve 401
```bash
kubectl exec -n zoe deployment/zoe -- cat /data/zoe/dashboard_token.txt
curl -H "Authorization: Bearer TOKEN" http://localhost:8642/stats
```

### 3.3 Cognitive loop estancado
```bash
kubectl exec -n zoe deployment/zoe -- curl -s http://localhost:8080/live | jq .checks
kubectl delete pod -n zoe -l app.kubernetes.io/name=zoe  # reiniciar
```

---

## 4. Backup y Recovery

### 4.1 Backup manual
```bash
kubectl exec -n zoe deployment/zoe -- tar czf - /data/zoe/ > zoe_full_backup.tar.gz
```

### 4.2 Restore
```bash
kubectl scale deployment zoe -n zoe --replicas=0
kubectl cp zoe_full_backup.tar.gz zoe/POD_NAME:/tmp/
kubectl exec -n zoe deployment/zoe -- tar xzf /tmp/zoe_full_backup.tar.gz -C /
kubectl scale deployment zoe -n zoe --replicas=1
```

---

## 5. Rollback

```bash
kubectl rollout undo deployment/zoe -n zoe
kubectl rollout status deployment/zoe -n zoe
```

---

## 6. Seguridad

### 6.1 Rotar auth token
```bash
NEW_TOKEN=$(openssl rand -base64 32)
kubectl set env deployment/zoe -n zoe ZOE_AUTH_TOKEN=$NEW_TOKEN
```

### 6.2 Rotar API keys
```bash
kubectl edit secret zoe-secrets -n zoe
kubectl rollout restart deployment/zoe -n zoe
```

---

## 7. Contacto

- **Repositorio**: https://github.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO
- **Manual de usuario**: `zoe/docs/22_MANUAL_COMPLETO_USUARIO_v2.1.1.md`
