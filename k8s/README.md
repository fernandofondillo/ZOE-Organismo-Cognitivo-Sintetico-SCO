# ZOE - Kubernetes Deployment Guide

Este directorio contiene todos los manifiestos Kubernetes para desplegar ZOE en un cluster, incluyendo PostgreSQL y Ollama.

## Arquitectura

```
                    [ Ingress :443 ]
                          |
                    [ Service :8642 ]
                          |
              +-----------+-----------+
              |                       |
      [ ZOE Pod ]              [ ZOE Pod ]
      (replica 1)              (replica 2)
              |                       |
      +-------+------+       +------+-------+
      |              |       |              |
 [Postgres]    [Ollama]  [Postgres]   [Ollama]
   :5432        :11434    :5432        :11434
```

## Requisitos Previos

- Kubernetes 1.25+
- kubectl configurado
- Kustomize (incluido en kubectl)
- Ingress Controller (NGINX recomendado)
- cert-manager (para TLS con Let's Encrypt)
- StorageClass disponible (para PVCs)

## Instalacion Rapida

```bash
# 1. Desplegar todo con Kustomize
kubectl apply -k k8s/

# 2. Verificar que todo esta corriendo
kubectl get all -n zoe

# 3. Ver logs de ZOE
kubectl logs -n zoe -l app.kubernetes.io/name=zoe --tail=100

# 4. Port-forward para acceso local
kubectl port-forward -n zoe svc/zoe 8642:8642
```

## Estructura de Manifiestos

| Archivo | Descripcion |
|---|---|
| `namespace.yaml` | Namespace `zoe` con Pod Security Standards (restricted) |
| `configmap.yaml` | Configuracion de ZOE, PostgreSQL y Ollama |
| `secret.yaml` | Secrets (passwords, API keys). **Cambiar en produccion** |
| `pvc.yaml` | PersistentVolumeClaims para datos persistentes |
| `rbac.yaml` | ServiceAccount, Role y RoleBinding (principio de minimo privilegio) |
| `postgres-deployment.yaml` | PostgreSQL 15 StatefulSet |
| `postgres-service.yaml` | Service ClusterIP para PostgreSQL |
| `ollama-deployment.yaml` | Ollama StatefulSet para modelos LLM |
| `ollama-service.yaml` | Service ClusterIP para Ollama |
| `deployment.yaml` | Deployment de ZOE (2 replicas, rolling updates) |
| `service.yaml` | Service ClusterIP para ZOE (puerto 8642) |
| `ingress.yaml` | Ingress con TLS (Let's Encrypt) |
| `networkpolicy.yaml` | NetworkPolicies (zero-trust por defecto) |
| `kustomization.yaml` | Kustomize base para gestion declarativa |

## Seguridad

### Politicas de Seguridad Implementadas

1. **Pod Security Standards (Restricted)**: Enforce en el namespace
2. **Non-root containers**: Todos los contenedores corren como usuario no-root
3. **Read-only root filesystem**: `readOnlyRootFilesystem: true`
4. **Drop ALL capabilities**: Sin privilegios de Linux
5. **No privilege escalation**: `allowPrivilegeEscalation: false`
6. **Network Policies**: Default deny-all, solo trafico permitido explicitamente
7. **RBAC**: ServiceAccount con minimo privilegio (solo lectura de su configmap)
8. **Resource limits**: CPU y memoria limitados para todos los pods

### Secrets

**IMPORTANTE**: El archivo `secret.yaml` contiene valores de ejemplo. En produccion:

```bash
# Opcion 1: Editar el secret directamente (no recomendado para git)
kubectl create secret generic zoe-secrets \
  --from-literal=POSTGRES_PASSWORD=$(openssl rand -base64 32) \
  -n zoe --dry-run=client -o yaml | kubectl apply -f -

# Opcion 2: Usar un gestor de secretos externo
# Ver comentarios en secret.yaml para External Secrets Operator
```

## Cambiar entre SQLite y PostgreSQL

Por defecto, el ConfigMap usa `ZOE_STORAGE_TYPE=postgres`. Para usar SQLite:

```bash
# Editar el configmap
kubectl patch configmap zoe-config -n zoe --type merge \
  -p '{"data":{"ZOE_STORAGE_TYPE":"sqlite"}}'

# Reiniciar el deployment
kubectl rollout restart deployment/zoe -n zoe
```

O editar directamente `k8s/configmap.yaml` antes de aplicar.

## Personalizar el Despliegue

### Con Kustomize Overlays

```bash
# Crear overlay para staging
mkdir -p k8s/overlays/staging

cat > k8s/overlays/staging/kustomization.yaml << 'EOF'
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
  - ../../base

namespace: zoe-staging

patchesStrategicMerge:
  - replicas.yaml
  - resources.yaml
EOF

cat > k8s/overlays/staging/replicas.yaml << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: zoe
spec:
  replicas: 1
EOF

# Aplicar overlay
kubectl apply -k k8s/overlays/staging/
```

### Variables de Entorno Importantes

| Variable | Descripcion | Default |
|---|---|---|
| `ZOE_STORAGE_TYPE` | Tipo de backend: sqlite/postgres | `sqlite` |
| `POSTGRES_HOST` | Host de PostgreSQL | `zoe-postgres` |
| `POSTGRES_DB` | Nombre de la base de datos | `zoe` |
| `POSTGRES_USER` | Usuario PostgreSQL | `zoe` |
| `POSTGRES_PASSWORD` | Password (desde secret) | - |
| `OLLAMA_HOST` | URL de Ollama | `http://zoe-ollama:11434` |

## Monitoreo y Health Checks

### Endpoints de Salud

| Endpoint | Puerto | Proposito |
|---|---|---|
| `/health` | 8080 | Startup probe |
| `/live` | 8080 | Liveness probe |
| `/ready` | 8080 | Readiness probe |

### Metricas Prometheus

```bash
# Port-forward al health port
kubectl port-forward -n zoe svc/zoe 8080:8080

# Ver metricas
curl http://localhost:8080/metrics
```

### Ver Estado

```bash
# Pods
kubectl get pods -n zoe -o wide

# Servicios
kubectl get svc -n zoe

# PVCs
kubectl get pvc -n zoe

# Eventos
kubectl get events -n zoe --sort-by=.lastTimestamp

# Logs
kubectl logs -n zoe -l app.kubernetes.io/name=zoe --tail=500 -f
kubectl logs -n zoe -l app.kubernetes.io/name=zoe-postgres --tail=100
kubectl logs -n zoe -l app.kubernetes.io/name=zoe-ollama --tail=100
```

## Escalamiento

### Escalar ZOE

```bash
# Aumentar replicas de ZOE
kubectl scale deployment zoe --replicas=3 -n zoe

# Escalar recursos
kubectl patch deployment zoe -n zoe --type=json \
  -p='[{"op": "replace", "path": "/spec/template/spec/containers/0/resources/limits/memory", "value": "8Gi"}]'
```

### Alta Disponibilidad PostgreSQL

Para produccion, considerar:
- Cloud SQL (GCP)
- Amazon RDS para PostgreSQL
n- Azure Database for PostgreSQL
- PostgreSQL HA con Patroni

Modificar `configmap.yaml` para apuntar a la instancia externa:
```yaml
POSTGRES_HOST: "my-production-db.cloudprovider.com"
```

### GPU para Ollama

Para usar GPU con Ollama:

```bash
# Verificar que el cluster tiene GPU
kubectl get nodes -o json | grep nvidia

# Aplicar patch para GPU
kubectl patch statefulset zoe-ollama -n zoe --type=json \
  -p='[{"op": "add", "path": "/spec/template/spec/containers/0/resources/limits/nvidia.com~1gpu", "value": "1"}]'
```

## Backup y Recuperacion

### Backup PostgreSQL

```bash
# Crear backup
kubectl exec -n zoe zoe-postgres-0 -- pg_dump -U zoe zoe > backup_$(date +%Y%m%d).sql

# Restaurar
kubectl exec -i -n zoe zoe-postgres-0 -- psql -U zoe zoe < backup_20240101.sql
```

### Backup PVC

```bash
# Con velero (recomendado)
velero backup create zoe-backup --include-namespaces zoe

# O manualmente con snapshots (depende del proveedor de cloud)
```

## Troubleshooting

| Problema | Solucion |
|---|---|
| Pods en `Pending` | Verificar storage class: `kubectl get sc` |
| PostgreSQL no inicia | Verificar PVC: `kubectl describe pvc zoe-postgres-data -n zoe` |
| ZOE no conecta a Postgres | Verificar NetworkPolicy: `kubectl describe networkpolicy -n zoe` |
| Ollama timeout | Aumentar startupProbe failureThreshold o verificar recursos |
| Ingress no funciona | Verificar ingress controller y cert-manager |
| Secret invalido | Regenerar: `kubectl create secret generic zoe-secrets ...` |

## Actualizaciones

```bash
# Actualizar imagen de ZOE
kubectl set image deployment/zoe zoe=zoe:v1.1 -n zoe

# Ver rollout
kubectl rollout status deployment/zoe -n zoe

# Rollback si hay problemas
kubectl rollout undo deployment/zoe -n zoe
```

## Limpieza

```bash
# Eliminar todo
kubectl delete -k k8s/

# O eliminar el namespace (borra todo)
kubectl delete namespace zoe
```
