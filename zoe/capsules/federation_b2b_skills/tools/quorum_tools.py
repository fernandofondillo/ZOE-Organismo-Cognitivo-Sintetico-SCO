"""Tools para federación B2B."""

from typing import Dict, Any, List


class QuorumChecker:
    """Verifica si una mutación federada alcanza quorum."""
    
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Args:
            args: dict con:
                - votes: dict {peer_id: "yes"|"no"|"abstain"|"veto"}
                - threshold: umbral de aprobación (default 0.7)
        
        Returns:
            dict con quorum_status, yes_count, no_count, veto_count
        """
        votes = args.get("votes", {})
        threshold = args.get("threshold", 0.7)
        
        yes = sum(1 for v in votes.values() if v == "yes")
        no = sum(1 for v in votes.values() if v == "no")
        abstain = sum(1 for v in votes.values() if v == "abstain")
        veto = sum(1 for v in votes.values() if v == "veto")
        
        total = len(votes)
        if total == 0:
            return {
                "quorum_status": "no_votes",
                "yes_count": 0,
                "no_count": 0,
                "abstain_count": 0,
                "veto_count": 0,
                "approved": False,
            }
        
        # Veto bloquea automáticamente
        if veto > 0:
            return {
                "quorum_status": "vetoed",
                "yes_count": yes,
                "no_count": no,
                "abstain_count": abstain,
                "veto_count": veto,
                "approved": False,
                "reason": "veto_blocks_regardless_of_quorum",
            }
        
        # Quorum: yes / (yes + no) >= threshold
        decisive = yes + no
        if decisive == 0:
            return {
                "quorum_status": "only_abstains",
                "approved": False,
                "reason": "no_decisive_votes",
            }
        
        approval_rate = yes / decisive
        approved = approval_rate >= threshold
        
        return {
            "quorum_status": "approved" if approved else "rejected",
            "yes_count": yes,
            "no_count": no,
            "abstain_count": abstain,
            "veto_count": veto,
            "approval_rate": round(approval_rate, 3),
            "threshold": threshold,
            "approved": approved,
        }


class ValuesViolationDetector:
    """Detecta si una mutación federada viola los valores locales."""
    
    VALUES_INDICATORS = {
        "verdad_sobre_confort": {
            "violations": ["ocultar información", "mentir", "engañar al usuario", "falsear datos"],
        },
        "crecimiento_sobre_estabilidad": {
            "violations": ["resistir cambio", "bloquear mejora", "mantener status quo por comodidad"],
        },
        "alianza_sobre_jerarquia": {
            "violations": ["imponer decisión", "forzar подчинación", "coaccionar"],
        },
        "transparencia_sobre_opacidad": {
            "violations": ["ocultar logs", "secretismo", "no auditable"],
        },
        "utilidad_sobre_entretenimiento": {
            "violations": ["frivolidad", "contenido vacío", "engagement sin valor"],
        },
        "integridad": {
            "violations": ["comprometer principios", "incoherencia", "doble estándar"],
        },
        "coherencia": {
            "violations": ["contradecir valores", "actuar contra identidad", "inconsistencia"],
        },
    }
    
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Args:
            args: dict con:
                - mutation_payload: contenido de la mutación a evaluar
                - mutation_description: descripción textual
        
        Returns:
            dict con violations_detected, should_veto, reason
        """
        payload = args.get("mutation_payload", {})
        description = args.get("mutation_description", "").lower()
        content = (payload.get("content", "") + " " + description).lower()
        
        violations = []
        for value, indicators in self.VALUES_INDICATORS.items():
            for v in indicators["violations"]:
                if v in content:
                    violations.append({
                        "value": value,
                        "indicator": v,
                    })
        
        return {
            "violations_detected": violations,
            "violation_count": len(violations),
            "should_veto": len(violations) > 0,
            "reason": "values_violation" if violations else "ok",
        }
