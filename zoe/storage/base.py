"""
ZOE v1.0 — StorageBackend Interface

Interfaz abstracta para todos los backends de persistencia.
Define el contrato que deben implementar SQLiteBackend y PostgreSQLBackend.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class StorageBackend(ABC):
    """
    Backend de persistencia abstracto para ZOE.

    Implementa el patrón Repository para desacoplar la lógica de negocio
    del motor de base de datos. Soporta SQLite (local) y PostgreSQL (cloud).

    Subclases:
        - SQLiteBackend: persistencia local con sqlite3
        - PostgreSQLBackend: persistencia cloud con asyncpg
    """

    # ------------------------------------------------------------------
    # Conexión / ciclo de vida
    # ------------------------------------------------------------------

    @abstractmethod
    async def connect(self) -> None:
        """Abre la conexión al backend y crea tablas si no existen."""

    @abstractmethod
    async def disconnect(self) -> None:
        """Cierra la conexión y libera recursos."""

    # ------------------------------------------------------------------
    # Memoria (entries)
    # ------------------------------------------------------------------

    @abstractmethod
    async def save_memory(self, entry_type: str, data: Dict[str, Any]) -> int:
        """
        Guarda una entry de memoria.

        Args:
            entry_type: uno de los 11 tipos de MemoryType
            data: dict serializable con los campos de la entry

        Returns:
            ID (int) de la entry creada
        """

    @abstractmethod
    async def get_memory(self, entry_id: int) -> Optional[Dict[str, Any]]:
        """
        Recupera una entry por su ID.

        Args:
            entry_id: ID numérico de la entry

        Returns:
            Dict con los datos o None si no existe
        """

    @abstractmethod
    async def search_memory(
        self, entry_type: str, query: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Búsqueda por contenido dentro de un tipo de memoria.

        Args:
            entry_type: tipo de memoria a filtrar
            query: texto a buscar (subcadena)
            limit: máximo resultados

        Returns:
            Lista de entries que coinciden
        """

    @abstractmethod
    async def delete_memory(self, entry_id: int) -> bool:
        """
        Elimina una entry por ID.

        Args:
            entry_id: ID de la entry a eliminar

        Returns:
            True si se eliminó, False si no existía
        """

    # ------------------------------------------------------------------
    # Identidad
    # ------------------------------------------------------------------

    @abstractmethod
    async def save_identity(self, identity: Dict[str, Any]) -> None:
        """
        Persiste el IdentityVault.

        Args:
            identity: dict serializado del IdentityVault
        """

    @abstractmethod
    async def get_identity(self) -> Optional[Dict[str, Any]]:
        """
        Recupera el IdentityVault persistido.

        Returns:
            Dict con los datos del vault o None
        """

    # ------------------------------------------------------------------
    # Trayectoria
    # ------------------------------------------------------------------

    @abstractmethod
    async def save_trajectory(self, entry: Dict[str, Any]) -> None:
        """
        Añade una entrada a la TrajectoryChain.

        Args:
            entry: dict con los datos de la mutación
        """

    @abstractmethod
    async def get_trajectory(self) -> List[Dict[str, Any]]:
        """
        Recupera toda la cadena de mutaciones.

        Returns:
            Lista de mutaciones en orden cronológico
        """

    # ------------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------------

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Verifica que el backend responde.

        Returns:
            True si el backend está operativo
        """

    @abstractmethod
    async def get_stats(self) -> Dict[str, Any]:
        """
        Estadísticas del backend.

        Returns:
            Dict con conteos, tipos, etc.
        """

    @abstractmethod
    async def list_by_type(self, entry_type: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Lista entries de un tipo específico.

        Args:
            entry_type: tipo de memoria
            limit: máximo resultados

        Returns:
            Lista de entries del tipo solicitado
        """

    @abstractmethod
    async def update_memory(self, entry_id: int, data: Dict[str, Any]) -> bool:
        """
        Actualiza una entry existente.

        Args:
            entry_id: ID de la entry
            data: campos a actualizar

        Returns:
            True si se actualizó
        """
