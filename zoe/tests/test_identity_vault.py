"""Tests para Identity Vault (Fase 1)."""

import pytest
import time

from zoe.alma.identity_vault import (
    IdentityVault,
    NINE_VECTORS,
    SEVEN_VALUES,
    PURPOSE,
)


def test_vault_initialization():
    """Vault se inicializa con 9 vectores + 7 valores + propósito."""
    vault = IdentityVault()
    assert len(vault.vectors) == 9
    assert len(vault.values) == 7
    assert vault.purpose
    assert vault.name == "Zoe"


def test_vault_has_hash():
    """Vault tiene hash criptográfico."""
    vault = IdentityVault()
    assert vault.identity_hash
    assert len(vault.identity_hash) == 64  # SHA-256 hex


def test_vault_hash_deterministic():
    """Mismos invariantes → mismo hash."""
    v1 = IdentityVault(birth_timestamp=1000.0)
    v2 = IdentityVault(birth_timestamp=1000.0)
    assert v1.identity_hash == v2.identity_hash


def test_vault_hash_changes_if_vectors_change():
    """Vectores distintos → hash distinto."""
    v1 = IdentityVault(birth_timestamp=1000.0)
    v2 = IdentityVault(vectors=["different"], birth_timestamp=1000.0)
    assert v1.identity_hash != v2.identity_hash


def test_vault_hash_changes_if_values_change():
    """Valores distintos → hash distinto."""
    v1 = IdentityVault(birth_timestamp=1000.0)
    v2 = IdentityVault(values=["different"], birth_timestamp=1000.0)
    assert v1.identity_hash != v2.identity_hash


def test_vault_verify_non_mutation_action():
    """Acciones que no son mutaciones siempre preservan identidad."""
    vault = IdentityVault()
    ok, reason = vault.verify({"type": "think"})
    assert ok is True


def test_vault_verify_mutation_allows_safe_target():
    """Mutación a target seguro preserva identidad."""
    vault = IdentityVault()
    ok, reason = vault.verify({
        "type": "mutate",
        "subtype": "add_memory",
        "target": "memory_episodic",
        "preserves_identity": True,
    })
    assert ok is True


def test_vault_verify_mutation_rejects_identity_target():
    """Mutación a target de identidad es rechazada."""
    vault = IdentityVault()
    ok, reason = vault.verify({
        "type": "mutate",
        "target": "vectors",
    })
    assert ok is False
    assert "forbidden" in reason.lower()


def test_vault_verify_mutation_rejects_explicit_break():
    """Mutación marcada como que rompe identidad es rechazada."""
    vault = IdentityVault()
    ok, reason = vault.verify({
        "type": "mutate",
        "preserves_identity": False,
    })
    assert ok is False


def test_vault_verify_proposed_state_coherent():
    """Estado propuesto coherente pasa."""
    vault = IdentityVault()
    ok, reason = vault.verify_proposed_state({
        "vectors": vault.vectors,
        "values": vault.values,
        "purpose": vault.purpose,
    })
    assert ok is True


def test_vault_verify_proposed_state_missing_vector():
    """Estado propuesto con vector faltante falla."""
    vault = IdentityVault()
    ok, reason = vault.verify_proposed_state({
        "vectors": vault.vectors[:-1],  # falta uno
        "values": vault.values,
        "purpose": vault.purpose,
    })
    assert ok is False
    assert "vectors" in reason.lower()


def test_vault_verify_proposed_state_different_purpose():
    """Estado propuesto con propósito distinto falla."""
    vault = IdentityVault()
    ok, reason = vault.verify_proposed_state({
        "vectors": vault.vectors,
        "values": vault.values,
        "purpose": "different purpose",
    })
    assert ok is False
    assert "purpose" in reason.lower()


def test_vault_to_dict_roundtrip():
    """to_dict / from_dict roundtrip."""
    vault = IdentityVault(birth_timestamp=1000.0)
    d = vault.to_dict()
    restored = IdentityVault.from_dict(d)
    assert restored.identity_hash == vault.identity_hash
    assert restored.vectors == vault.vectors
    assert restored.values == vault.values


def test_vault_from_dict_hash_verification():
    """from_dict verifica hash."""
    vault = IdentityVault(birth_timestamp=1000.0)
    d = vault.to_dict()
    # Alterar hash
    d["identity_hash"] = "fake_hash"
    with pytest.raises(ValueError):
        IdentityVault.from_dict(d)


def test_vault_is_compatible_with():
    """Dos vaults con mismos invariantes son compatibles."""
    v1 = IdentityVault(birth_timestamp=1000.0)
    v2 = IdentityVault(birth_timestamp=1000.0)
    assert v1.is_compatible_with(v2)

    v3 = IdentityVault(vectors=["different"], birth_timestamp=1000.0)
    assert not v1.is_compatible_with(v3)


def test_vault_summary():
    """summary() devuelve string legible."""
    vault = IdentityVault()
    s = vault.summary()
    assert "IdentityVault" in s
    assert "Zoe" in s


def test_nine_vectors_complete():
    """Los 9 vectores están definidos."""
    assert len(NINE_VECTORS) == 9
    assert "emancipacion_coherencia_cognitiva" in NINE_VECTORS
    assert "curiosidad" in NINE_VECTORS


def test_seven_values_complete():
    """Los 7 valores están definidos."""
    assert len(SEVEN_VALUES) == 7
    assert "verdad_sobre_confort" in SEVEN_VALUES
    assert "coherencia" in SEVEN_VALUES


def test_purpose_defined():
    """El propósito está definido."""
    assert PURPOSE
    assert "mejora" in PURPOSE.lower()
