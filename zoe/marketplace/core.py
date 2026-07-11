"""
ZOE v1.2 — Marketplace Core

Implementación del marketplace de cápsulas y casos de uso.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import shutil
import time
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)


# ============================================================
# Licencias y monetización
# ============================================================

class LicenseType:
    FREE = "free"
    PAID = "paid"
    SUBSCRIPTION = "subscription"
    OPENSOURCE = "opensource"
    RESEARCH = "research"


@dataclass
class CapsuleLicense:
    """Licencia de una cápsula o caso de uso."""
    type: str = LicenseType.FREE
    price: float = 0.0
    currency: str = "EUR"
    subscription_period: Optional[str] = None
    trial_days: int = 0
    commercial_use: bool = True
    attribution_required: bool = True
    redistribution_allowed: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "price": self.price,
            "currency": self.currency,
            "subscription_period": self.subscription_period,
            "trial_days": self.trial_days,
            "commercial_use": self.commercial_use,
            "attribution_required": self.attribution_required,
            "redistribution_allowed": self.redistribution_allowed,
        }


@dataclass
class MarketplaceEntry:
    """Entrada del marketplace."""
    name: str
    version: str
    description: str
    author: str
    author_url: Optional[str] = None
    type: str = "capsule"
    domain: str = ""
    trust_level: str = "community"
    license: CapsuleLicense = field(default_factory=CapsuleLicense)
    tags: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    downloads: int = 0
    rating: float = 0.0
    rating_count: int = 0
    content_hash: Optional[str] = None
    file_path: Optional[str] = None
    size_bytes: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "author_url": self.author_url,
            "type": self.type,
            "domain": self.domain,
            "trust_level": self.trust_level,
            "license": self.license.to_dict(),
            "tags": self.tags,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "downloads": self.downloads,
            "rating": self.rating,
            "rating_count": self.rating_count,
            "content_hash": self.content_hash,
            "size_bytes": self.size_bytes,
        }


class MarketplaceCatalog:
    """Catálogo local/remote de cápsulas y casos de uso disponibles."""
    
    def __init__(self, catalog_dir: Optional[Path] = None):
        if catalog_dir is None:
            catalog_dir = Path.home() / ".zoe" / "marketplace"
        self.catalog_dir = Path(catalog_dir)
        self.catalog_dir.mkdir(parents=True, exist_ok=True)
        (self.catalog_dir / "capsules").mkdir(exist_ok=True)
        (self.catalog_dir / "use_cases").mkdir(exist_ok=True)
        (self.catalog_dir / "metadata").mkdir(exist_ok=True)
        
        self._entries: Dict[str, MarketplaceEntry] = {}
        self._load_catalog()
    
    def _load_catalog(self) -> None:
        meta_dir = self.catalog_dir / "metadata"
        for meta_file in meta_dir.glob("*.json"):
            try:
                with open(meta_file, "r") as f:
                    data = json.load(f)
                license_data = data.pop("license", {})
                license = CapsuleLicense(**license_data)
                entry = MarketplaceEntry(license=license, **data)
                self._entries[entry.name] = entry
            except Exception as e:
                logger.warning(f"Failed to load catalog entry {meta_file}: {e}")
    
    def list_all(self, entry_type: Optional[str] = None) -> List[MarketplaceEntry]:
        if entry_type:
            return [e for e in self._entries.values() if e.type == entry_type]
        return list(self._entries.values())
    
    def list_capsules(self) -> List[MarketplaceEntry]:
        return self.list_all("capsule")
    
    def list_use_cases(self) -> List[MarketplaceEntry]:
        return self.list_all("use_case")
    
    def get(self, name: str) -> Optional[MarketplaceEntry]:
        return self._entries.get(name)
    
    def search(self, query: str, entry_type: Optional[str] = None) -> List[MarketplaceEntry]:
        query_lower = query.lower()
        results = []
        for entry in self._entries.values():
            if entry_type and entry.type != entry_type:
                continue
            text = f"{entry.name} {entry.description} {entry.domain} {' '.join(entry.tags)}".lower()
            if query_lower in text:
                results.append(entry)
        return results
    
    def add(self, entry: MarketplaceEntry) -> bool:
        self._entries[entry.name] = entry
        self._save_entry(entry)
        logger.info(f"Marketplace: added {entry.type} '{entry.name}' v{entry.version}")
        return True
    
    def remove(self, name: str) -> bool:
        if name not in self._entries:
            return False
        entry = self._entries[name]
        if entry.file_path and Path(entry.file_path).exists():
            Path(entry.file_path).unlink()
        meta_file = self.catalog_dir / "metadata" / f"{name}.json"
        if meta_file.exists():
            meta_file.unlink()
        del self._entries[name]
        return True
    
    def increment_downloads(self, name: str) -> None:
        if name in self._entries:
            self._entries[name].downloads += 1
            self._save_entry(self._entries[name])
    
    def add_rating(self, name: str, rating: float) -> None:
        if name not in self._entries:
            return
        entry = self._entries[name]
        total = entry.rating * entry.rating_count
        entry.rating_count += 1
        entry.rating = (total + rating) / entry.rating_count
        self._save_entry(entry)
    
    def _save_entry(self, entry: MarketplaceEntry) -> None:
        meta_file = self.catalog_dir / "metadata" / f"{entry.name}.json"
        with open(meta_file, "w") as f:
            json.dump(entry.to_dict(), f, indent=2, default=str)
    
    def get_stats(self) -> Dict[str, Any]:
        total = len(self._entries)
        capsules = sum(1 for e in self._entries.values() if e.type == "capsule")
        use_cases = sum(1 for e in self._entries.values() if e.type == "use_case")
        by_license = {}
        for e in self._entries.values():
            by_license[e.license.type] = by_license.get(e.license.type, 0) + 1
        total_downloads = sum(e.downloads for e in self._entries.values())
        avg_rating = sum(e.rating for e in self._entries.values()) / max(1, total)
        return {
            "total": total,
            "capsules": capsules,
            "use_cases": use_cases,
            "by_license": by_license,
            "total_downloads": total_downloads,
            "avg_rating": round(avg_rating, 2),
        }


class CapsulePackager:
    """Empaqueta y desempaqueta cápsulas y casos de uso."""
    
    @staticmethod
    def package_capsule(capsule_dir: Path, output_path: Path) -> str:
        if not capsule_dir.exists():
            raise FileNotFoundError(f"Capsule dir not found: {capsule_dir}")
        
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(capsule_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(capsule_dir.parent)
                    zf.write(file_path, arcname)
        
        h = hashlib.sha256()
        with open(output_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return f"sha256:{h.hexdigest()}"
    
    @staticmethod
    def package_use_case(yaml_path: Path, output_path: Path) -> str:
        if not yaml_path.exists():
            raise FileNotFoundError(f"YAML not found: {yaml_path}")
        
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.write(yaml_path, yaml_path.name)
            readme = yaml_path.parent / f"{yaml_path.stem}_README.md"
            if readme.exists():
                zf.write(readme, readme.name)
        
        h = hashlib.sha256()
        with open(output_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return f"sha256:{h.hexdigest()}"
    
    @staticmethod
    def unpackage(zcap_path: Path, target_dir: Path) -> bool:
        try:
            with zipfile.ZipFile(zcap_path, "r") as zf:
                zf.extractall(target_dir)
            return True
        except Exception as e:
            logger.error(f"Failed to unpackage {zcap_path}: {e}")
            return False


class MarketplaceUploader:
    """Sube cápsulas y casos de uso al marketplace."""
    
    def __init__(self, catalog: MarketplaceCatalog, capsules_dir: Path, use_cases_dir: Path):
        self.catalog = catalog
        self.capsules_dir = capsules_dir
        self.use_cases_dir = use_cases_dir
    
    def upload_capsule(
        self,
        capsule_name: str,
        author: str,
        description: str,
        license_data: Dict[str, Any],
        tags: List[str] = None,
        author_url: str = None,
    ) -> Tuple[bool, str]:
        cap_dir = self.capsules_dir / capsule_name
        if not cap_dir.exists():
            return False, f"capsule_not_found: {capsule_name}"
        
        import yaml
        yaml_path = cap_dir / "capsule.yaml"
        if not yaml_path.exists():
            return False, "capsule.yaml not found"
        
        with open(yaml_path) as f:
            data = yaml.safe_load(f)
        if "capsule" in data and "name" not in data:
            data = data["capsule"]
        
        output_path = self.catalog.catalog_dir / "capsules" / f"{capsule_name}-{data.get('version', '0.1.0')}.zcap"
        content_hash = CapsulePackager.package_capsule(cap_dir, output_path)
        
        license = CapsuleLicense(**license_data)
        entry = MarketplaceEntry(
            name=capsule_name,
            version=data.get("version", "0.1.0"),
            description=description or data.get("description", ""),
            author=author,
            author_url=author_url,
            type="capsule",
            domain=data.get("domain", ""),
            trust_level=data.get("trust_level", "community"),
            license=license,
            tags=tags or [],
            content_hash=content_hash,
            file_path=str(output_path),
            size_bytes=output_path.stat().st_size,
        )
        
        self.catalog.add(entry)
        return True, content_hash
    
    def upload_use_case(
        self,
        use_case_name: str,
        author: str,
        description: str,
        license_data: Dict[str, Any],
        tags: List[str] = None,
        author_url: str = None,
    ) -> Tuple[bool, str]:
        yaml_path = self.use_cases_dir / f"{use_case_name}.yaml"
        if not yaml_path.exists():
            return False, f"use_case_not_found: {use_case_name}"
        
        output_path = self.catalog.catalog_dir / "use_cases" / f"{use_case_name}.zyaml"
        content_hash = CapsulePackager.package_use_case(yaml_path, output_path)
        
        license = CapsuleLicense(**license_data)
        entry = MarketplaceEntry(
            name=use_case_name,
            version="1.0.0",
            description=description,
            author=author,
            author_url=author_url,
            type="use_case",
            license=license,
            tags=tags or [],
            content_hash=content_hash,
            file_path=str(output_path),
            size_bytes=output_path.stat().st_size,
        )
        
        self.catalog.add(entry)
        return True, content_hash


class MarketplaceDownloader:
    """Descarga e instala cápsulas y casos de uso."""
    
    def __init__(self, catalog: MarketplaceCatalog, capsules_dir: Path, use_cases_dir: Path):
        self.catalog = catalog
        self.capsules_dir = capsules_dir
        self.use_cases_dir = use_cases_dir
    
    def download_capsule(self, name: str) -> Tuple[bool, str]:
        entry = self.catalog.get(name)
        if not entry or entry.type != "capsule":
            return False, f"capsule_not_in_marketplace: {name}"
        
        if not entry.file_path or not Path(entry.file_path).exists():
            return False, "packaged_file_not_found"
        
        target = self.capsules_dir / name
        if target.exists():
            shutil.rmtree(target)
        target.mkdir(parents=True)
        
        ok = CapsulePackager.unpackage(Path(entry.file_path), target)
        if not ok:
            return False, "unpackage_failed"
        
        self.catalog.increment_downloads(name)
        return True, f"installed: {name} v{entry.version}"
    
    def download_use_case(self, name: str) -> Tuple[bool, str]:
        entry = self.catalog.get(name)
        if not entry or entry.type != "use_case":
            return False, f"use_case_not_in_marketplace: {name}"
        
        if not entry.file_path or not Path(entry.file_path).exists():
            return False, "packaged_file_not_found"
        
        ok = CapsulePackager.unpackage(Path(entry.file_path), self.use_cases_dir)
        if not ok:
            return False, "unpackage_failed"
        
        self.catalog.increment_downloads(name)
        return True, f"installed: {name}"


class LicenseChecker:
    """Verifica licencias de uso."""
    
    @staticmethod
    def can_use(entry: MarketplaceEntry, user_has_paid: bool = False) -> Tuple[bool, str]:
        if entry.license.type in (LicenseType.FREE, LicenseType.OPENSOURCE, LicenseType.RESEARCH):
            return True, "ok"
        
        if entry.license.type == LicenseType.PAID:
            if user_has_paid:
                return True, "ok"
            return False, "payment_required"
        
        if entry.license.type == LicenseType.SUBSCRIPTION:
            if user_has_paid:
                return True, "ok"
            return False, "subscription_required"
        
        return False, "unknown_license"
    
    @staticmethod
    def get_payment_info(entry: MarketplaceEntry) -> Dict[str, Any]:
        return {
            "license_type": entry.license.type,
            "price": entry.license.price,
            "currency": entry.license.currency,
            "subscription_period": entry.license.subscription_period,
            "trial_days": entry.license.trial_days,
            "author": entry.author,
            "author_url": entry.author_url,
        }
