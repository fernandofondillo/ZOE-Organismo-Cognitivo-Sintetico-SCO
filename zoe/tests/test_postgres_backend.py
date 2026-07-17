"""
Tests unitarios de PostgreSQLBackend con AsyncMock.

No requiere PostgreSQL real. Simula asyncpg.Pool y verifica
que todos los metodos funcionan correctamente.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# Sprint 5.13 B8 — Fix skipif detection.
# Antes: el try/except capturaba la importacion del MODULO postgres_backend,
# que SI importa correctamente (asyncpg = None cuando no instalado).
# Pero PostgreSQLBackend.__init__ lanza ImportError al instanciar.
# Por eso HAS_ASYNCpg = True pero los tests fallaban al instanciar.
# Ahora: verificamos directamente si asyncpg esta disponible.
try:
    import asyncpg as _asyncpg_check
    HAS_ASYNCPG = _asyncpg_check is not None
except ImportError:
    HAS_ASYNCPG = False

# Solo importar PostgreSQLBackend si asyncpg esta disponible (evita errores)
if HAS_ASYNCPG:
    from zoe.storage.postgres_backend import PostgreSQLBackend


pytestmark = pytest.mark.skipif(not HAS_ASYNCPG, reason="asyncpg not installed")


class TestPostgreSQLBackend:
    """Tests unitarios de PostgreSQLBackend con pool mockeado."""

    @pytest.fixture
    def mock_pool(self):
        """Crea un pool mockeado con fetch y execute async."""
        pool = AsyncMock()
        pool.fetch = AsyncMock(return_value=[])
        pool.fetchrow = AsyncMock(return_value=None)
        pool.fetchval = AsyncMock(return_value=0)
        pool.execute = AsyncMock(return_value="INSERT 0 1")
        pool.close = AsyncMock()
        pool.acquire = MagicMock()
        pool.acquire.__aenter__ = AsyncMock(return_value=pool)
        pool.acquire.__aexit__ = AsyncMock(return_value=False)
        pool.get_size = MagicMock(return_value=5)
        pool.get_free_size = MagicMock(return_value=3)
        return pool

    @pytest.fixture
    def backend(self, mock_pool):
        """Crea un PostgreSQLBackend con pool mockeado."""
        b = PostgreSQLBackend(
            host="localhost", port=5432, database="zoe_test",
            user="zoe", password="test",
        )
        b._pool = mock_pool
        b._initialized = True
        return b

    @pytest.mark.asyncio
    async def test_save_memory(self, backend, mock_pool):
        """save_memory debe ejecutar INSERT correctamente."""
        mock_pool.fetchrow = AsyncMock(return_value={"id": 42})

        entry_id = await backend.save_memory(
            "episodic",
            {
                "content": "Test content",
                "confidence": 0.8,
                "provenance": "test",
            },
        )

        assert entry_id == 42
        mock_pool.fetchrow.assert_called_once()
        sql = mock_pool.fetchrow.call_args[0][0]
        assert "INSERT" in sql.upper()

    @pytest.mark.asyncio
    async def test_get_memory(self, backend, mock_pool):
        """get_memory debe retornar la entry correcta."""
        mock_pool.fetchrow = AsyncMock(return_value={
            "id": 42,
            "entry_id": "episodic_12345",
            "type": "episodic",
            "content": "Test content",
            "confidence": 0.8,
            "salience": 0.5,
            "provenance": "test",
            "timestamp": 12345.0,
            "last_access": 12345.0,
            "access_count": 0,
            "merged_from": [],
            "contradictions": [],
            "metadata": {},
            "extra_data": {},
            "created_at": None,
        })

        entry = await backend.get_memory(42)

        assert entry is not None
        assert entry["content"] == "Test content"
        assert entry["type"] == "episodic"

    @pytest.mark.asyncio
    async def test_search_memory(self, backend, mock_pool):
        """search_memory debe retornar lista de resultados."""
        mock_pool.fetch = AsyncMock(return_value=[
            {"id": 1, "entry_id": "e1", "type": "episodic",
             "content": "Hello", "confidence": 0.9, "salience": 0.5,
             "provenance": "", "timestamp": 0.0, "last_access": 0.0,
             "access_count": 0, "merged_from": [], "contradictions": [],
             "metadata": {}, "extra_data": {}, "created_at": None},
            {"id": 2, "entry_id": "e2", "type": "episodic",
             "content": "World", "confidence": 0.7, "salience": 0.5,
             "provenance": "", "timestamp": 0.0, "last_access": 0.0,
             "access_count": 0, "merged_from": [], "contradictions": [],
             "metadata": {}, "extra_data": {}, "created_at": None},
        ])

        results = await backend.search_memory("episodic", "hello", limit=5)

        assert len(results) == 2
        mock_pool.fetch.assert_called_once()
        sql = mock_pool.fetch.call_args[0][0]
        assert "ILIKE" in sql.upper()

    @pytest.mark.asyncio
    async def test_delete_memory(self, backend, mock_pool):
        """delete_memory debe ejecutar DELETE."""
        mock_pool.execute = AsyncMock(return_value="DELETE 1")

        result = await backend.delete_memory(42)

        assert result is True
        mock_pool.execute.assert_called_once()
        sql = mock_pool.execute.call_args[0][0]
        assert "DELETE" in sql.upper()

    @pytest.mark.asyncio
    async def test_save_identity(self, backend, mock_pool):
        """save_identity debe almacenar el vault."""
        mock_pool.execute = AsyncMock(return_value="INSERT 0 1")

        await backend.save_identity(
            {"name": "Zoe", "identity_hash": "abc123", "vectors": ["v1"]},
        )

        mock_pool.execute.assert_called_once()
        sql = mock_pool.execute.call_args[0][0]
        assert "INSERT" in sql.upper()
        assert "identity" in sql.lower()

    @pytest.mark.asyncio
    async def test_health_check(self, backend, mock_pool):
        """health_check debe ejecutar SELECT 1."""
        mock_pool.fetchrow = AsyncMock(return_value={"alive": 1})

        healthy = await backend.health_check()

        assert healthy is True
        mock_pool.fetchrow.assert_called_once()
        sql = mock_pool.fetchrow.call_args[0][0]
        assert "SELECT 1" in sql

    @pytest.mark.asyncio
    async def test_health_check_fails_when_no_pool(self, backend):
        """health_check debe retornar False si no hay pool."""
        backend._pool = None
        healthy = await backend.health_check()
        assert healthy is False

    @pytest.mark.asyncio
    async def test_health_check_fails_on_exception(self, backend, mock_pool):
        """health_check debe retornar False si la query falla."""
        mock_pool.fetchrow = AsyncMock(side_effect=Exception("DB error"))

        healthy = await backend.health_check()
        assert healthy is False

    @pytest.mark.asyncio
    async def test_list_by_type(self, backend, mock_pool):
        """list_by_type debe retornar entries filtradas por tipo."""
        mock_pool.fetch = AsyncMock(return_value=[
            {"id": 1, "entry_id": "e1", "type": "semantic",
             "content": "Fact A", "confidence": 0.9, "salience": 0.5,
             "provenance": "", "timestamp": 0.0, "last_access": 0.0,
             "access_count": 0, "merged_from": [], "contradictions": [],
             "metadata": {}, "extra_data": {}, "created_at": None},
        ])

        results = await backend.list_by_type("semantic", limit=10)

        assert len(results) == 1
        assert results[0]["content"] == "Fact A"
        mock_pool.fetch.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_memory(self, backend, mock_pool):
        """update_memory debe ejecutar UPDATE correctamente."""
        mock_pool.execute = AsyncMock(return_value="UPDATE 1")

        result = await backend.update_memory(
            42,
            {"content": "Updated content", "confidence": 0.95},
        )

        assert result is True
        mock_pool.execute.assert_called_once()
        sql = mock_pool.execute.call_args[0][0]
        assert "UPDATE" in sql.upper()

    @pytest.mark.asyncio
    async def test_get_identity(self, backend, mock_pool):
        """get_identity debe retornar el vault almacenado."""
        mock_pool.fetchrow = AsyncMock(return_value={
            "name": "Zoe",
            "vectors": '["v1", "v2"]',
            "values": '["val1"]',
            "purpose": "Test purpose",
            "birth_timestamp": 12345.0,
            "identity_hash": "abc123",
            "updated_at": None,
        })

        identity = await backend.get_identity()

        assert identity is not None
        assert identity["name"] == "Zoe"
        assert identity["identity_hash"] == "abc123"

    @pytest.mark.asyncio
    async def test_save_trajectory(self, backend, mock_pool):
        """save_trajectory debe insertar una mutacion."""
        mock_pool.execute = AsyncMock(return_value="INSERT 0 1")

        await backend.save_trajectory({
            "id": "mut_1",
            "type": "test_mutation",
            "target": "memory",
            "payload": {"key": "value"},
        })

        mock_pool.execute.assert_called_once()
        sql = mock_pool.execute.call_args[0][0]
        assert "INSERT" in sql.upper()
        assert "trajectory" in sql.lower()

    @pytest.mark.asyncio
    async def test_get_trajectory(self, backend, mock_pool):
        """get_trajectory debe retornar la lista de mutaciones."""
        mock_pool.fetch = AsyncMock(return_value=[
            {
                "mutation_id": "mut_1",
                "mutation_type": "test",
                "target": "mem",
                "payload": '{}',
                "justification": "",
                "provenance": "",
                "cost": 0.0,
                "confidence": 0.5,
                "mutation_timestamp": 0.0,
                "signature": "",
                "prev_hash": "",
                "mutation_hash": "",
                "applied": True,
                "rolled_back": False,
            },
        ])

        results = await backend.get_trajectory()

        assert len(results) == 1
        assert results[0]["id"] == "mut_1"

    @pytest.mark.asyncio
    async def test_get_stats(self, backend, mock_pool):
        """get_stats debe retornar estadisticas del backend."""
        mock_pool.fetchval = AsyncMock(side_effect=[100, 50, 1])
        mock_pool.fetch = AsyncMock(return_value=[
            {"type": "episodic", "c": 40},
            {"type": "semantic", "c": 60},
        ])

        stats = await backend.get_stats()

        assert stats["backend"] == "postgresql"
        assert stats["connected"] is True
        assert stats["total_entries"] == 100

    @pytest.mark.asyncio
    async def test_search_memory_fulltext(self, backend, mock_pool):
        """search_memory_fulltext debe buscar con ILIKE."""
        mock_pool.fetch = AsyncMock(return_value=[
            {"id": 1, "entry_id": "e1", "type": "episodic",
             "content": "Hello world", "confidence": 0.9, "salience": 0.5,
             "provenance": "", "timestamp": 0.0, "last_access": 0.0,
             "access_count": 0, "merged_from": [], "contradictions": [],
             "metadata": {}, "extra_data": {}, "created_at": None},
        ])

        results = await backend.search_memory_fulltext("hello", limit=5)

        assert len(results) == 1
        mock_pool.fetch.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_memory_jsonb(self, backend, mock_pool):
        """search_memory_jsonb debe buscar en metadata JSONB."""
        mock_pool.fetch = AsyncMock(return_value=[])

        results = await backend.search_memory_jsonb("source", "test", limit=5)

        assert len(results) == 0
        mock_pool.fetch.assert_called_once()
        sql = mock_pool.fetch.call_args[0][0]
        assert "@>" in sql

    @pytest.mark.asyncio
    async def test_disconnect(self, backend, mock_pool):
        """disconnect debe cerrar el pool y limpiar estado."""
        await backend.disconnect()

        mock_pool.close.assert_called_once()
        assert backend._pool is None
        assert backend._initialized is False

    @pytest.mark.asyncio
    async def test_connect_creates_pool(self, mock_pool):
        """connect debe crear el pool si no existe."""
        backend = PostgreSQLBackend(
            host="localhost", port=5432, database="zoe_test",
            user="zoe", password="test",
        )

        with patch("asyncpg.create_pool", new_callable=AsyncMock, return_value=mock_pool):
            await backend.connect()

        assert backend._pool is not None
        assert backend._initialized is True

    @pytest.mark.asyncio
    async def test_connect_skips_if_already_connected(self, backend, mock_pool):
        """connect no debe hacer nada si ya hay pool."""
        with patch("asyncpg.create_pool", new_callable=AsyncMock) as mock_create:
            await backend.connect()
            mock_create.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_memory_not_found(self, backend, mock_pool):
        """get_memory debe retornar None si no existe."""
        mock_pool.fetchrow = AsyncMock(return_value=None)

        entry = await backend.get_memory(999)

        assert entry is None

    @pytest.mark.asyncio
    async def test_delete_memory_not_found(self, backend, mock_pool):
        """delete_memory debe retornar False si la entry no existe."""
        mock_pool.execute = AsyncMock(return_value="DELETE 0")

        result = await backend.delete_memory(999)

        assert result is False

    @pytest.mark.asyncio
    async def test_update_memory_no_allowed_fields(self, backend, mock_pool):
        """update_memory debe retornar False si no hay campos permitidos."""
        result = await backend.update_memory(42, {"invalid_field": "value"})

        assert result is False

    @pytest.mark.asyncio
    async def test_get_stats_disconnected(self, backend):
        """get_stats debe retornar estado desconectado si no hay pool."""
        backend._pool = None

        stats = await backend.get_stats()

        assert stats["connected"] is False

    @pytest.mark.asyncio
    async def test_health_check_fetchrow_returns_none(self, backend, mock_pool):
        """health_check debe retornar False si fetchrow retorna None."""
        mock_pool.fetchrow = AsyncMock(return_value=None)

        healthy = await backend.health_check()
        assert healthy is False

    @pytest.mark.asyncio
    async def test_health_check_fetchrow_returns_wrong_value(self, backend, mock_pool):
        """health_check debe retornar False si alive no es 1."""
        mock_pool.fetchrow = AsyncMock(return_value={"alive": 0})

        healthy = await backend.health_check()
        assert healthy is False

    @pytest.mark.asyncio
    async def test_get_schema_version(self, backend, mock_pool):
        """get_schema_version debe retornar la version almacenada."""
        mock_pool.fetchrow = AsyncMock(return_value={
            "value": '{"version": "1.2.3"}',
        })

        version = await backend.get_schema_version()

        assert version == "1.2.3"

    @pytest.mark.asyncio
    async def test_set_schema_version(self, backend, mock_pool):
        """set_schema_version debe persistir la version."""
        mock_pool.execute = AsyncMock(return_value="INSERT 0 1")

        await backend.set_schema_version("2.0.0")

        mock_pool.execute.assert_called_once()
        sql = mock_pool.execute.call_args[0][0]
        assert "storage_metadata" in sql.lower()

    @pytest.mark.asyncio
    async def test_get_identity_not_found(self, backend, mock_pool):
        """get_identity debe retornar None si no hay vault."""
        mock_pool.fetchrow = AsyncMock(return_value=None)

        identity = await backend.get_identity()

        assert identity is None
