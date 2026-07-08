"""Tests para IntentionalityMotor y PhylogeneticMotor (Fase 0.5)."""

import pytest
import time

from zoe.core.intentionality_motor import IntentionalityMotor, Intention
from zoe.core.phylogenetic_motor import (
    PhylogeneticMotor,
    PhylogeneticPool,
    ArchitecturalImprovement,
)
from zoe.core.cognitive_tensions import CognitiveTensions
from zoe.core.cognitive_physics import CognitivePhysics
from zoe.core.living_memory import LivingMemory
from zoe.core.cognitive_loop import Observation


# ===== IntentionalityMotor =====

def test_intentionality_initial_state():
    """Motor empieza sin intenciones."""
    motor = IntentionalityMotor()
    assert len(motor.get_active_intentions()) == 0


def test_intentionality_generate_from_tensions():
    """Genera intenciones desde tensiones."""
    motor = IntentionalityMotor()
    tensions = CognitiveTensions()
    # Alta fatiga → tensión rest_vs_productivity
    tensions.update_from_state(energy=0.1, fatigue=0.9, arousal=0.1, surprise=0.1)

    new = motor.generate(tensions=tensions, physics=None, memory=None, observations=[])
    # Debería generar al menos 1 intención (desde tensión)
    assert len(new) >= 1


def test_intentionality_generate_from_uncertainty():
    """Genera intención de entender con incertidumbre alta."""
    motor = IntentionalityMotor()
    physics = CognitivePhysics()
    physics.uncertainty_pressure = 0.7

    new = motor.generate(tensions=None, physics=physics, memory=None, observations=[])
    understand_intentions = [i for i in new if i.type == "understand"]
    assert len(understand_intentions) >= 1


def test_intentionality_generate_from_user_input():
    """Genera intención de comunicar con input de usuario."""
    motor = IntentionalityMotor()
    # Forzar que haya pasado tiempo desde última comunicación
    motor._last_communication = time.time() - 100
    obs = [Observation(timestamp=time.time(), source="user", content="Hola")]

    new = motor.generate(tensions=None, physics=None, memory=None, observations=obs)
    communicate_intentions = [i for i in new if i.type == "communicate"]
    assert len(communicate_intentions) >= 1


def test_intentionality_generate_from_memory_size():
    """Genera intención de consolidar con memoria grande."""
    motor = IntentionalityMotor()
    memory = LivingMemory()
    for i in range(10):
        memory.add(content=f"test {i}", provenance="test")

    # Forzar tiempo desde última consolidación
    motor._last_consolidation = time.time() - 100

    new = motor.generate(tensions=None, physics=None, memory=memory, observations=[])
    consolidate_intentions = [i for i in new if i.type == "consolidate"]
    assert len(consolidate_intentions) >= 1


def test_intentionality_get_active_intentions():
    """get_active_intentions() devuelve las de mayor prioridad."""
    motor = IntentionalityMotor()
    motor._intentions = [
        Intention(id="1", description="a", type="explore", priority=0.3, source="test"),
        Intention(id="2", description="b", type="understand", priority=0.8, source="test"),
        Intention(id="3", description="c", type="consolidate", priority=0.5, source="test"),
    ]
    active = motor.get_active_intentions(n=2)
    assert len(active) == 2
    assert active[0].priority == 0.8


def test_intentionality_resolve():
    """resolve() marca intención como resuelta."""
    motor = IntentionalityMotor()
    intention = Intention(id="1", description="test", type="explore", priority=0.5, source="test")
    motor._intentions.append(intention)
    assert motor.resolve("1") is True
    assert motor._intentions[0].resolved is True
    assert motor._intentions[0].active is False


def test_intentionality_avoids_duplicates():
    """No genera intenciones duplicadas."""
    motor = IntentionalityMotor()
    tensions = CognitiveTensions()
    tensions.update_from_state(energy=0.1, fatigue=0.9, arousal=0.1, surprise=0.1)

    new1 = motor.generate(tensions=tensions, physics=None, memory=None, observations=[])
    new2 = motor.generate(tensions=tensions, physics=None, memory=None, observations=[])

    # La segunda llamada no debería duplicar la primera
    descriptions1 = {i.description for i in new1}
    descriptions2 = {i.description for i in new2}
    assert descriptions1.isdisjoint(descriptions2) or len(new2) == 0


def test_intentionality_get_stats():
    """get_stats() funciona."""
    motor = IntentionalityMotor()
    motor._intentions = [
        Intention(id="1", description="a", type="explore", priority=0.5, source="test"),
    ]
    stats = motor.get_stats()
    assert stats["active_count"] == 1
    assert stats["total_intentions"] == 1


# ===== PhylogeneticMotor =====

def test_phylogenetic_pool_singleton():
    """PhylogeneticPool es singleton."""
    pool1 = PhylogeneticPool.get_instance()
    pool2 = PhylogeneticPool.get_instance()
    assert pool1 is pool2


def test_phylogenetic_publish_improvement():
    """Publicar mejora la añade al pool."""
    # Reset pool para test
    PhylogeneticPool._instance = None
    pool = PhylogeneticPool.get_instance()

    motor_a = PhylogeneticMotor(zoe_id="zoe_a", pool=pool)
    imp_id = motor_a.publish_improvement(
        description="nuevo sub-agente de creatividad",
        change_type="add_module",
        payload={"module": "creativity_engine"},
        metrics_before={"efficiency": 0.5},
    )

    assert imp_id
    assert len(pool._improvements) == 1


def test_phylogenetic_get_pending():
    """Otras ZOEs ven mejoras pendientes."""
    PhylogeneticPool._instance = None
    pool = PhylogeneticPool.get_instance()

    motor_a = PhylogeneticMotor(zoe_id="zoe_a", pool=pool)
    motor_b = PhylogeneticMotor(zoe_id="zoe_b", pool=pool)

    motor_a.publish_improvement(
        description="test mejora",
        change_type="add_module",
        payload={"module": "test"},
        metrics_before={"efficiency": 0.5},
    )

    pending_b = motor_b.get_pending_improvements()
    assert len(pending_b) == 1


def test_phylogenetic_try_improvement_pass():
    """Probar mejora con test_function que pasa."""
    PhylogeneticPool._instance = None
    pool = PhylogeneticPool.get_instance()

    motor_a = PhylogeneticMotor(zoe_id="zoe_a", pool=pool)
    motor_b = PhylogeneticMotor(zoe_id="zoe_b", pool=pool)

    imp_id = motor_a.publish_improvement(
        description="test",
        change_type="add_module",
        payload={"module": "test"},
        metrics_before={"efficiency": 0.5},
    )

    def test_fn(payload, metrics_before):
        return True, {"efficiency": 0.7}, ""

    pending = motor_b.get_pending_improvements()
    result = motor_b.try_improvement(pending[0], test_fn)
    assert result["passed"] is True


def test_phylogenetic_try_improvement_fail():
    """Probar mejora con test_function que falla."""
    PhylogeneticPool._instance = None
    pool = PhylogeneticPool.get_instance()

    motor_a = PhylogeneticMotor(zoe_id="zoe_a", pool=pool)
    motor_b = PhylogeneticMotor(zoe_id="zoe_b", pool=pool)

    motor_a.publish_improvement(
        description="test",
        change_type="add_module",
        payload={"module": "test"},
        metrics_before={"efficiency": 0.5},
    )

    def test_fn(payload, metrics_before):
        return False, {"efficiency": 0.3}, "degraded performance"

    pending = motor_b.get_pending_improvements()
    result = motor_b.try_improvement(pending[0], test_fn)
    assert result["passed"] is False


def test_phylogenetic_validated_after_two_tests():
    """Mejora validada tras 2 ZOEs que pasan."""
    PhylogeneticPool._instance = None
    pool = PhylogeneticPool.get_instance()

    motor_a = PhylogeneticMotor(zoe_id="zoe_a", pool=pool)
    motor_b = PhylogeneticMotor(zoe_id="zoe_b", pool=pool)
    motor_c = PhylogeneticMotor(zoe_id="zoe_c", pool=pool)

    motor_a.publish_improvement(
        description="test",
        change_type="add_module",
        payload={"module": "test"},
        metrics_before={"efficiency": 0.5},
    )

    def test_fn(payload, metrics_before):
        return True, {"efficiency": 0.7}, ""

    # zoe_b prueba
    pending_b = motor_b.get_pending_improvements()
    motor_b.try_improvement(pending_b[0], test_fn)

    # zoe_c prueba
    pending_c = motor_c.get_pending_improvements()
    motor_c.try_improvement(pending_c[0], test_fn)

    # Ahora debería estar validada
    validated = pool.get_validated()
    assert len(validated) >= 1


def test_phylogenetic_incorporate_validated():
    """ZOEs pueden incorporar mejoras validadas."""
    PhylogeneticPool._instance = None
    pool = PhylogeneticPool.get_instance()

    motor_a = PhylogeneticMotor(zoe_id="zoe_a", pool=pool)
    motor_b = PhylogeneticMotor(zoe_id="zoe_b", pool=pool)
    motor_c = PhylogeneticMotor(zoe_id="zoe_c", pool=pool)
    motor_d = PhylogeneticMotor(zoe_id="zoe_d", pool=pool)

    motor_a.publish_improvement(
        description="test",
        change_type="add_module",
        payload={"module": "test"},
        metrics_before={"efficiency": 0.5},
    )

    def test_fn(payload, metrics_before):
        return True, {"efficiency": 0.7}, ""

    motor_b.try_improvement(motor_b.get_pending_improvements()[0], test_fn)
    motor_c.try_improvement(motor_c.get_pending_improvements()[0], test_fn)

    # zoe_d incorpora
    incorporated = motor_d.incorporate_validated()
    assert len(incorporated) >= 1


def test_phylogenetic_species_state():
    """get_species_state() devuelve métricas de especie."""
    PhylogeneticPool._instance = None
    pool = PhylogeneticPool.get_instance()

    motor = PhylogeneticMotor(zoe_id="zoe_a", pool=pool)
    motor.publish_improvement(
        description="test",
        change_type="add_module",
        payload={},
        metrics_before={},
    )

    state = motor.get_species_state()
    assert state["total_improvements"] == 1
    assert state["proposed"] == 1
    assert "species_version" in state
