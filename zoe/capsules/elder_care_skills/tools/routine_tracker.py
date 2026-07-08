"""Tool: Routine Tracker — detecta desviaciones de rutina en personas mayores."""

from typing import Dict, Any, List
from datetime import datetime, timedelta
import math


class RoutineTracker:
    """Detecta desviaciones significativas en la rutina de un usuario."""
    
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Args:
            args: dict con:
                - current_events: lista de eventos recientes (tipo, timestamp)
                - historical_pattern: patrón histórico (lista de eventos típicos por franja horaria)
                - threshold: umbral de desviación (default 0.3)
        
        Returns:
            dict con deviation_score, detected_anomalies, recommendation
        """
        current = args.get("current_events", [])
        pattern = args.get("historical_pattern", [])
        threshold = args.get("threshold", 0.3)
        
        if not pattern:
            return {
                "deviation_score": 0.0,
                "detected_anomalies": [],
                "recommendation": "insufficient_historical_data",
            }
        
        # Calcular desviación: comparar eventos actuales con patrón esperado
        expected_types = {e["type"] for e in pattern}
        current_types = {e["type"] for e in current}
        
        # Tipos esperados no presentes
        missing = expected_types - current_types
        # Tipos presentes no esperados
        unexpected = current_types - expected_types
        
        # Desviación temporal: comparar timestamps
        time_deviations = []
        for curr in current:
            for pat in pattern:
                if curr["type"] == pat["type"]:
                    # Comparar horas del día
                    curr_hour = curr.get("hour", 0)
                    pat_hour = pat.get("hour", 0)
                    diff = abs(curr_hour - pat_hour)
                    if diff > 12:
                        diff = 24 - diff
                    time_deviations.append(diff)
        
        avg_time_dev = sum(time_deviations) / max(1, len(time_deviations))
        type_deviation = (len(missing) + len(unexpected)) / max(1, len(expected_types))
        
        deviation_score = min(1.0, (avg_time_dev / 6.0) * 0.5 + type_deviation * 0.5)
        
        anomalies = []
        if missing:
            anomalies.append(f"missing_expected_events: {missing}")
        if unexpected:
            anomalies.append(f"unexpected_events: {unexpected}")
        if avg_time_dev > 2:
            anomalies.append(f"temporal_shift_hours: {avg_time_dev:.1f}")
        
        recommendation = "no_action_needed"
        if deviation_score >= threshold:
            if deviation_score >= 0.7:
                recommendation = "alert_family_check_in"
            elif deviation_score >= 0.5:
                recommendation = "proactive_contact_user"
            else:
                recommendation = "monitor_closely"
        
        return {
            "deviation_score": round(deviation_score, 3),
            "detected_anomalies": anomalies,
            "recommendation": recommendation,
            "missing_events": list(missing),
            "unexpected_events": list(unexpected),
            "avg_temporal_shift_hours": round(avg_time_dev, 2),
        }


class FallRiskAssessor:
    """Evalúa riesgo de caída basado en factores conocidos."""
    
    RISK_FACTORS = {
        "edad_>=_80": 0.3,
        "polimedicacion_>=_5": 0.25,
        "psicofarmaco_activo": 0.3,
        "caida_previa_6m": 0.4,
        "deterioro_cognitivo": 0.25,
        "deficit_visual": 0.2,
        "deficit_auditivo": 0.1,
        "incontinencia": 0.15,
        "depresion": 0.2,
        "marcha_lenta": 0.3,
    }
    
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Args:
            args: dict con keys booleanas para cada factor de riesgo
        
        Returns:
            dict con risk_score, risk_level, recommendations
        """
        score = 0.0
        active_factors = []
        for factor, weight in self.RISK_FACTORS.items():
            if args.get(factor, False):
                score += weight
                active_factors.append(factor)
        
        score = min(1.0, score)
        
        if score >= 0.7:
            level = "high"
            recs = [
                "valoracion geriátrica integral en <2 semanas",
                "revisar medicación con médico (desprescripción si procede)",
                "evaluación de marcha y equilibrio",
                "adaptaciones ambientales (barras, alfombras, iluminación)",
            ]
        elif score >= 0.4:
            level = "moderate"
            recs = [
                "valoración geriátrica en próxima visita",
                "revisar medicación",
                "ejercicio de equilibrio si es factible",
            ]
        else:
            level = "low"
            recs = ["mantener seguimiento rutinario"]
        
        return {
            "risk_score": round(score, 3),
            "risk_level": level,
            "active_factors": active_factors,
            "recommendations": recs,
        }


class MedicationChecker:
    """Verifica interacciones farmacológicas básicas en polimedicación."""
    
    HIGH_RISK_COMBOS = {
        frozenset(["benzodiacepina", "opioide"]): "riesgo depresión respiratoria",
        frozenset(["benzodiacepina", "antihipertensivo"]): "riesgo caídas aumentado",
        frozenset(["aines", "anticoagulante"]): "riesgo hemorragia",
        frozenset(["aines", "ieca"]): "riesgo insuficiencia renal aguda",
        frozenset(["opioide", "antihistaminico_sedante"]): "riesgo sedación excesiva",
        frozenset(["diuretico", "digoxina"]): "riesgo toxicidad digitálica por hipokalemia",
    }
    
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Args:
            args: dict con:
                - medications: lista de nombres de medicamentos
                - patient_age: edad del paciente
        """
        meds = args.get("medications", [])
        age = args.get("patient_age", 70)
        
        meds_lower = [m.lower() for m in meds]
        
        # Detectar combos de alto riesgo
        detected_interactions = []
        for combo, risk in self.HIGH_RISK_COMBOS.items():
            # Heurística simple: buscar categoría del fármaco en el nombre
            for med in meds_lower:
                if any(c in med for c in combo):
                    for med2 in meds_lower:
                        if med2 != med and any(c in med2 for c in combo):
                            if {med, med2} not in [i.get("meds") for i in detected_interactions]:
                                detected_interactions.append({
                                    "meds": [med, med2],
                                    "risk": risk,
                                })
        
        # Polimedicación
        polymedication = len(meds) >= 5
        
        # Ajustes por edad
        age_warnings = []
        if age >= 80:
            age_warnings.append("mayor de 80: revisar benzodiacepinas y anticolinérgicos")
        if age >= 75 and polymedication:
            age_warnings.append("polimedicación en >75: aumentar vigilancia caídas")
        
        risk_level = "low"
        if detected_interactions:
            risk_level = "high" if len(detected_interactions) >= 2 else "moderate"
        elif polymedication:
            risk_level = "moderate"
        
        return {
            "medications_count": len(meds),
            "polymedication": polymedication,
            "detected_interactions": detected_interactions,
            "age_warnings": age_warnings,
            "risk_level": risk_level,
            "recommendation": "consultar_con_medico_para_revision" if risk_level != "low" else "seguimiento_rutinario",
            "disclaimer": "ZOE no sustituye valoración farmacéutica profesional",
        }
