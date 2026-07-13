"""
ZOE v1.2 — Marketplace de Cápsulas y Casos de Uso

Permite que cualquiera pueda aportar y monetizar cápsulas de conocimiento
y casos de uso YAML nuevos.

Modelo:
- Autores crean cápsulas/casos con scaffold CLI
- Las suben al marketplace (local o remoto)
- Otros usuarios las descubren, descargan e instalan
- Sistema de monetización con licencias (free, paid, subscription)

Componentes:
- MarketplaceCatalog: catálogo local/remote de cápsulas y casos disponibles
- CapsuleLicense: licencia de uso (free, paid, subscription)
- MarketplaceUploader: sube cápsulas al marketplace
- MarketplaceDownloader: descarga e instala cápsulas
- LicenseChecker: verifica licencias de uso
"""

from .core import (
    MarketplaceCatalog, MarketplaceEntry, CapsuleLicense, LicenseType,
    CapsulePackager, MarketplaceUploader, MarketplaceDownloader, LicenseChecker,
)

__all__ = [
    "MarketplaceCatalog", "MarketplaceEntry", "CapsuleLicense", "LicenseType",
    "CapsulePackager", "MarketplaceUploader", "MarketplaceDownloader", "LicenseChecker",
]
