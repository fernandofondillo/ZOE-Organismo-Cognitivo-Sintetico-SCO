"""
Sprint 5.18 F4.1-F4.5 — Tests de Fase 4 (hardening k8s).

F4.1: PodDisruptionBudget
F4.2: HorizontalPodAutoscaler
F4.3: ServiceMonitor
F4.4: NetworkPolicy endurecida
F4.5: readOnlyRootFilesystem + seccompProfile en todos los deployments
"""

import yaml
from pathlib import Path

import pytest


_K8S_DIR = Path(__file__).parent.parent.parent / "k8s"


def _load_yaml(filename):
    """Carga un YAML y devuelve lista de documentos."""
    path = _K8S_DIR / filename
    if not path.exists():
        return []
    with open(path) as f:
        return list(yaml.safe_load_all(f))


# ============================================================
# F4.1: PodDisruptionBudget
# ============================================================

class TestF41PodDisruptionBudget:
    """Sprint 5.18 F4.1 — PDB para ZOE, Ollama y PostgreSQL."""

    def test_pdb_yaml_exists(self):
        """k8s/pod-disruption-budget.yaml existe."""
        assert (_K8S_DIR / "pod-disruption-budget.yaml").exists()

    def test_pdb_for_zoe_exists(self):
        """Hay un PDB para zoe con minAvailable: 1."""
        docs = _load_yaml("pod-disruption-budget.yaml")
        zoe_pdbs = [d for d in docs if d and d.get("kind") == "PodDisruptionBudget"
                     and d.get("metadata", {}).get("name") == "zoe-pdb"]
        assert len(zoe_pdbs) == 1
        assert zoe_pdbs[0]["spec"]["minAvailable"] == 1

    def test_pdb_for_ollama_exists(self):
        """Hay un PDB para ollama."""
        docs = _load_yaml("pod-disruption-budget.yaml")
        ollama_pdbs = [d for d in docs if d and d.get("kind") == "PodDisruptionBudget"
                        and d.get("metadata", {}).get("name") == "zoe-ollama-pdb"]
        assert len(ollama_pdbs) == 1

    def test_pdb_for_postgres_exists(self):
        """Hay un PDB para postgres."""
        docs = _load_yaml("pod-disruption-budget.yaml")
        pg_pdbs = [d for d in docs if d and d.get("kind") == "PodDisruptionBudget"
                    and d.get("metadata", {}).get("name") == "zoe-postgres-pdb"]
        assert len(pg_pdbs) == 1


# ============================================================
# F4.2: HorizontalPodAutoscaler
# ============================================================

class TestF42HorizontalPodAutoscaler:
    """Sprint 5.18 F4.2 — HPA para ZOE."""

    def test_hpa_yaml_exists(self):
        """k8s/horizontal-pod-autoscaler.yaml existe."""
        assert (_K8S_DIR / "horizontal-pod-autoscaler.yaml").exists()

    def test_hpa_targets_zoe_deployment(self):
        """El HPA tiene scaleTargetRef a Deployment/zoe."""
        docs = _load_yaml("horizontal-pod-autoscaler.yaml")
        hpas = [d for d in docs if d and d.get("kind") == "HorizontalPodAutoscaler"]
        assert len(hpas) == 1
        assert hpas[0]["spec"]["scaleTargetRef"]["kind"] == "Deployment"
        assert hpas[0]["spec"]["scaleTargetRef"]["name"] == "zoe"

    def test_hpa_has_cpu_metric(self):
        """El HPA tiene metrica de CPU."""
        docs = _load_yaml("horizontal-pod-autoscaler.yaml")
        hpa = docs[0]
        metrics = hpa["spec"]["metrics"]
        cpu_metrics = [m for m in metrics if m["type"] == "Resource" and m["resource"]["name"] == "cpu"]
        assert len(cpu_metrics) == 1

    def test_hpa_has_memory_metric(self):
        """El HPA tiene metrica de memoria."""
        docs = _load_yaml("horizontal-pod-autoscaler.yaml")
        hpa = docs[0]
        metrics = hpa["spec"]["metrics"]
        mem_metrics = [m for m in metrics if m["type"] == "Resource" and m["resource"]["name"] == "memory"]
        assert len(mem_metrics) == 1

    def test_hpa_has_scale_up_down_behavior(self):
        """El HPA tiene behavior de scale up y scale down."""
        docs = _load_yaml("horizontal-pod-autoscaler.yaml")
        hpa = docs[0]
        behavior = hpa["spec"]["behavior"]
        assert "scaleUp" in behavior
        assert "scaleDown" in behavior


# ============================================================
# F4.3: ServiceMonitor
# ============================================================

class TestF43ServiceMonitor:
    """Sprint 5.18 F4.3 — ServiceMonitor para Prometheus."""

    def test_service_monitor_yaml_exists(self):
        """k8s/service-monitor.yaml existe."""
        assert (_K8S_DIR / "service-monitor.yaml").exists()

    def test_service_monitor_targets_zoe(self):
        """El ServiceMonitor selecciona pods de ZOE."""
        docs = _load_yaml("service-monitor.yaml")
        sms = [d for d in docs if d and d.get("kind") == "ServiceMonitor"]
        assert len(sms) == 1
        assert sms[0]["spec"]["selector"]["matchLabels"]["app.kubernetes.io/name"] == "zoe"

    def test_service_monitor_scrapes_metrics_endpoint(self):
        """El ServiceMonitor scrapea /metrics."""
        docs = _load_yaml("service-monitor.yaml")
        sm = docs[0]
        endpoints = sm["spec"]["endpoints"]
        metrics_endpoints = [e for e in endpoints if e.get("path") == "/metrics"]
        assert len(metrics_endpoints) >= 1

    def test_service_monitor_has_interval(self):
        """El ServiceMonitor tiene interval configurado."""
        docs = _load_yaml("service-monitor.yaml")
        sm = docs[0]
        for ep in sm["spec"]["endpoints"]:
            assert "interval" in ep, "Each endpoint must have interval"


# ============================================================
# F4.4: NetworkPolicy endurecida
# ============================================================

class TestF44NetworkPolicyHardened:
    """Sprint 5.18 F4.4 — NetworkPolicy con deny-all default."""

    def test_network_policy_has_deny_all(self):
        """Hay una politica default-deny-all."""
        docs = _load_yaml("networkpolicy.yaml")
        deny_all = [d for d in docs if d and d.get("kind") == "NetworkPolicy"
                     and d.get("metadata", {}).get("name") == "default-deny-all"]
        assert len(deny_all) == 1
        assert "Ingress" in deny_all[0]["spec"]["policyTypes"]
        assert "Egress" in deny_all[0]["spec"]["policyTypes"]

    def test_network_policy_has_deny_inter_pod(self):
        """Sprint 5.18: Hay deny-inter-pod-default."""
        docs = _load_yaml("networkpolicy.yaml")
        deny_inter = [d for d in docs if d and d.get("kind") == "NetworkPolicy"
                       and d.get("metadata", {}).get("name") == "deny-inter-pod-default"]
        assert len(deny_inter) == 1

    def test_network_policy_allows_ingress_to_zoe(self):
        """Hay allow-ingress-to-zoe."""
        docs = _load_yaml("networkpolicy.yaml")
        allow_ingress = [d for d in docs if d and d.get("kind") == "NetworkPolicy"
                          and d.get("metadata", {}).get("name") == "allow-ingress-to-zoe"]
        assert len(allow_ingress) == 1

    def test_network_policy_allows_zoe_to_postgres(self):
        """Hay zoe-to-postgres."""
        docs = _load_yaml("networkpolicy.yaml")
        zoe_pg = [d for d in docs if d and d.get("kind") == "NetworkPolicy"
                   and d.get("metadata", {}).get("name") == "zoe-to-postgres"]
        assert len(zoe_pg) == 1

    def test_network_policy_allows_zoe_egress_internet(self):
        """Hay zoe-egress-internet con DNS + HTTPS."""
        docs = _load_yaml("networkpolicy.yaml")
        egress = [d for d in docs if d and d.get("kind") == "NetworkPolicy"
                   and d.get("metadata", {}).get("name") == "zoe-egress-internet"]
        assert len(egress) == 1
        # Debe permitir DNS (53) y HTTPS (443)
        ports = []
        for rule in egress[0]["spec"]["egress"]:
            for p in rule.get("ports", []):
                ports.append(p["port"])
        assert 53 in ports, "Must allow DNS (port 53)"
        assert 443 in ports, "Must allow HTTPS (port 443)"


# ============================================================
# F4.5: readOnlyRootFilesystem + seccompProfile
# ============================================================

class TestF45SecurityContextHardening:
    """Sprint 5.18 F4.5 — readOnlyRootFilesystem + seccompProfile en todos los deployments."""

    def test_zoe_deployment_has_readonly_root_fs(self):
        """ZOE container tiene readOnlyRootFilesystem: true."""
        docs = _load_yaml("deployment.yaml")
        deploy = docs[0]
        for container in deploy["spec"]["template"]["spec"]["containers"]:
            if container["name"] == "zoe":
                sc = container.get("securityContext", {})
                assert sc.get("readOnlyRootFilesystem") is True, \
                    "zoe container must have readOnlyRootFilesystem: true"

    def test_zoe_deployment_has_seccomp_profile(self):
        """ZOE pod tiene seccompProfile RuntimeDefault."""
        docs = _load_yaml("deployment.yaml")
        deploy = docs[0]
        pod_sc = deploy["spec"]["template"]["spec"].get("securityContext", {})
        assert pod_sc.get("seccompProfile", {}).get("type") == "RuntimeDefault", \
            "zoe pod must have seccompProfile RuntimeDefault"

    def test_zoe_deployment_drops_all_capabilities(self):
        """ZOE container drops ALL capabilities."""
        docs = _load_yaml("deployment.yaml")
        deploy = docs[0]
        for container in deploy["spec"]["template"]["spec"]["containers"]:
            if container["name"] == "zoe":
                caps = container.get("securityContext", {}).get("capabilities", {})
                assert "ALL" in caps.get("drop", []), \
                    "zoe container must drop ALL capabilities"

    def test_ollama_deployment_has_readonly_root_fs(self):
        """Sprint 5.18: Ollama container tiene readOnlyRootFilesystem: true."""
        docs = _load_yaml("ollama-deployment.yaml")
        deploy = docs[0]
        for container in deploy["spec"]["template"]["spec"]["containers"]:
            if container["name"] == "ollama":
                sc = container.get("securityContext", {})
                assert sc.get("readOnlyRootFilesystem") is True, \
                    "ollama container must have readOnlyRootFilesystem: true"

    def test_ollama_deployment_has_seccomp_profile(self):
        """Sprint 5.18: Ollama pod tiene seccompProfile RuntimeDefault."""
        docs = _load_yaml("ollama-deployment.yaml")
        deploy = docs[0]
        pod_sc = deploy["spec"]["template"]["spec"].get("securityContext", {})
        assert pod_sc.get("seccompProfile", {}).get("type") == "RuntimeDefault", \
            "ollama pod must have seccompProfile RuntimeDefault"

    def test_all_deployments_run_as_non_root(self):
        """Todos los deployments tienen runAsNonRoot: true."""
        for filename in ["deployment.yaml", "ollama-deployment.yaml", "postgres-deployment.yaml"]:
            docs = _load_yaml(filename)
            deploy = docs[0]
            pod_sc = deploy["spec"]["template"]["spec"].get("securityContext", {})
            assert pod_sc.get("runAsNonRoot") is True, \
                f"{filename} must have runAsNonRoot: true"
