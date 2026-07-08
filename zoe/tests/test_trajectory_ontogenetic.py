"""Tests para Trajectory Chain y Ontogenetic Motor (Fase 1)."""

import pytest
import time

from zoe.alma.trajectory_chain import TrajectoryChain, Mutation
from zoe.alma.identity_vault import IdentityVault
from zoe.alma.ontogenetic_motor import OntogeneticMotor, VALID_MUTATION_TYPES
from zoe.core.cognitive_laws import CognitiveLaws


# ===== TrajectoryChain =====


def test_chain_initial_state():
    """Cadena empieza vacía."""
    chain = TrajectoryChain(organism_id="test_zoe")
    assert len(chain._mutations) == 0
    assert chain._last_hash is None


def test_chain_commit():
    """Commit añade mutación a la cadena."""
    chain = TrajectoryChain(organism_id="test_zoe")
    mutation = Mutation(
        id="mut_1",
        type="add_memory",
        target="episodic",
        payload={"content": "test"},
        justification="test",
        provenance="test",
        cost=0.1,
        confidence=0.5,
    )
    commit_hash = chain.commit(mutation)
    assert commit_hash
    assert len(chain._mutations) == 1
    assert chain._last_hash == commit_hash


def test_chain_verify_integrity():
    """Cadena íntegra pasa verificación."""
    chain = TrajectoryChain(organism_id="test_zoe")
    for i in range(5):
        mutation = Mutation(
            id=f"mut_{i}",
            type="add_memory",
            target="episodic",
            payload={"content": f"test {i}"},
            justification=f"test {i}",
            provenance="test",
            cost=0.1,
            confidence=0.5,
        )
        chain.commit(mutation)

    assert chain.verify_chain() is True


def test_chain_links_correctly():
    """Cada mutación se enlaza con la anterior."""
    chain = TrajectoryChain(organism_id="test_zoe")
    hashes = []
    for i in range(3):
        mutation = Mutation(
            id=f"mut_{i}",
            type="add_memory",
            target="episodic",
            payload={"content": f"test {i}"},
            justification="test",
            provenance="test",
            cost=0.1,
            confidence=0.5,
        )
        h = chain.commit(mutation)
        hashes.append(h)

    # Primera mutación: prev_hash = None
    assert chain._mutations[0].prev_hash is None
    # Segunda: prev_hash = hash de primera
    assert chain._mutations[1].prev_hash == hashes[0]
    # Tercera: prev_hash = hash de segunda
    assert chain._mutations[2].prev_hash == hashes[1]


def test_chain_rollback():
    """Rollback marca mutación como revertida y añade mutación de rollback."""
    chain = TrajectoryChain(organism_id="test_zoe")
    mutation = Mutation(
        id="mut_1",
        type="add_memory",
        target="episodic",
        payload={"content": "test"},
        justification="test",
        provenance="test",
        cost=0.1,
        confidence=0.5,
    )
    chain.commit(mutation)

    success, reason = chain.rollback("mut_1")
    assert success is True
    # La mutación original está marcada como revertida
    assert chain._mutations[0].rolled_back is True
    # Se añadió una mutación de rollback
    assert len(chain._mutations) == 2
    assert chain._mutations[1].type == "rollback_previous"


def test_chain_rollback_not_found():
    """Rollback de mutación inexistente falla."""
    chain = TrajectoryChain(organism_id="test_zoe")
    success, reason = chain.rollback("nonexistent")
    assert success is False


def test_chain_get_history():
    """get_history devuelve historial."""
    chain = TrajectoryChain(organism_id="test_zoe")
    for i in range(3):
        mutation = Mutation(
            id=f"mut_{i}",
            type="add_memory",
            target="episodic",
            payload={"content": f"test {i}"},
            justification="test",
            provenance="test",
            cost=0.1,
            confidence=0.5,
        )
        chain.commit(mutation)

    history = chain.get_history()
    assert len(history) == 3

    history_limited = chain.get_history(n=2)
    assert len(history_limited) == 2


def test_chain_get_active_mutations():
    """get_active_mutations excluye revertidas."""
    chain = TrajectoryChain(organism_id="test_zoe")
    mutation = Mutation(
        id="mut_1",
        type="add_memory",
        target="episodic",
        payload={"content": "test"},
        justification="test",
        provenance="test",
        cost=0.1,
        confidence=0.5,
    )
    chain.commit(mutation)

    assert len(chain.get_active_mutations()) == 1
    chain.rollback("mut_1")
    # Tras rollback, mut_1 no está activa; la de rollback tampoco
    assert len(chain.get_active_mutations()) == 0


def test_chain_get_stats():
    """get_stats devuelve estadísticas."""
    chain = TrajectoryChain(organism_id="test_zoe")
    mutation = Mutation(
        id="mut_1",
        type="add_memory",
        target="episodic",
        payload={"content": "test"},
        justification="test",
        provenance="test",
        cost=0.1,
        confidence=0.5,
    )
    chain.commit(mutation)

    stats = chain.get_stats()
    assert stats["total_mutations"] == 1
    assert stats["active_mutations"] == 1
    assert stats["chain_verified"] is True


def test_chain_summary():
    """summary() devuelve string legible."""
    chain = TrajectoryChain(organism_id="test_zoe")
    s = chain.summary()
    assert "TrajectoryChain" in s
    assert "test_zoe" in s


# ===== OntogeneticMotor =====


def test_motor_initialization():
    """Motor se inicializa con Vault y Chain."""
    vault = IdentityVault(birth_timestamp=1000.0)
    chain = TrajectoryChain(organism_id="test")
    motor = OntogeneticMotor(
        identity_vault=vault,
        trajectory_chain=chain,
        organism_id="test",
    )
    assert motor.identity_vault is vault
    assert motor.trajectory_chain is chain


def test_motor_propose_mutation():
    """Propose crea mutación sin aplicarla."""
    vault = IdentityVault(birth_timestamp=1000.0)
    motor = OntogeneticMotor(identity_vault=vault, organism_id="test")

    mutation = motor.propose_mutation(
        type="add_memory",
        target="episodic",
        payload={"content": "test"},
        justification="test",
    )
    assert mutation.type == "add_memory"
    assert mutation.id
    # No se ha aplicado todavía
    assert len(motor.trajectory_chain._mutations) == 0


def test_motor_apply_mutation():
    """Apply verifica leyes + identidad + firma en cadena."""
    vault = IdentityVault(birth_timestamp=1000.0)
    laws = CognitiveLaws()
    motor = OntogeneticMotor(
        identity_vault=vault,
        laws=laws,
        organism_id="test",
    )

    mutation = motor.propose_mutation(
        type="add_memory",
        target="episodic",
        payload={"content": "test"},
        justification="test",
        provenance="test",
        cost=0.1,
        confidence=0.5,
    )

    success, reason = motor.apply_mutation(mutation)
    assert success is True
    assert len(motor.trajectory_chain._mutations) == 1


def test_motor_apply_rejects_identity_breaking():
    """Apply rechaza mutación que rompe identidad."""
    vault = IdentityVault(birth_timestamp=1000.0)
    motor = OntogeneticMotor(identity_vault=vault, organism_id="test")

    mutation = motor.propose_mutation(
        type="add_memory",
        target="vectors",  # target prohibido
        payload={"content": "test"},
        justification="test",
    )

    success, reason = motor.apply_mutation(mutation)
    assert success is False
    assert "identity" in reason.lower()


def test_motor_apply_rejects_law_violation():
    """Apply rechaza mutación que viola leyes."""
    vault = IdentityVault(birth_timestamp=1000.0)
    laws = CognitiveLaws()
    motor = OntogeneticMotor(
        identity_vault=vault,
        laws=laws,
        organism_id="test",
    )

    mutation = motor.propose_mutation(
        type="add_memory",
        target="episodic",
        payload={"content": "test"},
        justification="test",
        # sin provenance → viola 3ra ley
        cost=0.1,
        confidence=0.5,
    )
    mutation.provenance = ""  # forzar violación

    success, reason = motor.apply_mutation(mutation)
    assert success is False
    assert "law" in reason.lower() or "provenance" in reason.lower()


def test_motor_rollback():
    """Rollback revierte mutación."""
    vault = IdentityVault(birth_timestamp=1000.0)
    motor = OntogeneticMotor(identity_vault=vault, organism_id="test")

    mutation = motor.propose_mutation(
        type="add_memory",
        target="episodic",
        payload={"content": "test"},
        justification="test",
        provenance="test",
    )
    motor.apply_mutation(mutation)

    success, reason = motor.rollback(mutation.id)
    assert success is True
    # La mutación está revertida
    assert motor.trajectory_chain._mutations[0].rolled_back is True


def test_motor_verify_integrity():
    """verify_integrity verifica la cadena."""
    vault = IdentityVault(birth_timestamp=1000.0)
    motor = OntogeneticMotor(identity_vault=vault, organism_id="test")

    for i in range(3):
        mutation = motor.propose_mutation(
            type="add_memory",
            target="episodic",
            payload={"content": f"test {i}"},
            justification="test",
            provenance="test",
        )
        motor.apply_mutation(mutation)

    assert motor.verify_integrity() is True


def test_motor_get_stats():
    """get_stats devuelve estadísticas completas."""
    vault = IdentityVault(birth_timestamp=1000.0)
    motor = OntogeneticMotor(identity_vault=vault, organism_id="test")

    mutation = motor.propose_mutation(
        type="add_memory",
        target="episodic",
        payload={"content": "test"},
        justification="test",
        provenance="test",
    )
    motor.apply_mutation(mutation)

    stats = motor.get_stats()
    assert "identity_vault" in stats
    assert "trajectory_chain" in stats
    assert stats["total_mutations_proposed"] >= 1


def test_motor_invalid_type_rejected():
    """Tipo de mutación inválido lanza error."""
    vault = IdentityVault(birth_timestamp=1000.0)
    motor = OntogeneticMotor(identity_vault=vault, organism_id="test")

    with pytest.raises(ValueError):
        motor.propose_mutation(
            type="invalid_type",
            target="episodic",
            payload={},
            justification="test",
        )


def test_motor_all_valid_types():
    """Todos los tipos válidos funcionan."""
    vault = IdentityVault(birth_timestamp=1000.0)
    motor = OntogeneticMotor(identity_vault=vault, organism_id="test")

    for mutation_type in VALID_MUTATION_TYPES:
        mutation = motor.propose_mutation(
            type=mutation_type,
            target="test_target",
            payload={"content": "test"},
            justification=f"test {mutation_type}",
            provenance="test",
        )
        assert mutation.type == mutation_type
