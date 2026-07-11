# 07 — Marketplace Guide

> **Marketplace de cápsulas: modelo de negocio, guía de autor, guía de comprador, API.**
> **Versión:** V1.6.0 — Julio 2026

---

## 1. Modelo del marketplace

El marketplace es el **modelo de negocio recurrente** de ZOE. Similar a la App Store pero para conocimiento experto:

- **Autores** crean cápsulas de conocimiento experto
- **Compradores** compran e instalan cápsulas
- **ZOE** toma 30% de comisión (revenue split 70/30)
- **Validación**: ZOE team revisa cápsulas antes de publicar

**Ubicación:** `zoe/marketplace/core.py` (425 LOC)

---

## 2. 5 tipos de licencia

| Licencia | Uso permitido | Precio típico | Badge color |
|---|---|---|---|
| **FREE** | Cualquiera, sin restricciones | €0 | 🟢 Verde |
| **OPENSOURCE** | MIT, Apache, GPL | €0 | 🔵 Azul |
| **RESEARCH** | Uso académico solo | €0-50 | 🟣 Morado |
| **PAID** | One-time purchase | €10-100 | 🟠 Naranja |
| **SUBSCRIPTION** | Pago mensual con actualizaciones | €5-50/mes | 🔴 Rojo |

---

## 3. Revenue split

- **70% para el autor** de la cápsula
- **30% para ZOE** (mantenimiento, validación, distribución, payment processing)

---

## 4. Guía del autor

### Crear cápsula
Ver [`06_CAPSULES_GUIDE.md`](06_CAPSULES_GUIDE.md) para guía completa de creación.

### Empaquetar y subir

```python
from zoe.marketplace.core import CapsulePackager, MarketplaceUploader

packager = CapsulePackager()
package_path = packager.package_capsule("mi_capsula")

uploader = MarketplaceUploader()
uploader.upload_capsule(package_path, {
    "author": "Fernando Fondillo",
    "license": "paid",
    "price": 25.00,
})
```

### Precio recomendado

| Tipo | Precio | Ejemplos |
|---|---|---|
| Cápsula básica | €10-30 | Comunicación, psicología |
| Cápsula especializada | €30-80 | Farmacología, legal |
| Cápsula enterprise | €80-500 | Regulación médica EU |
| Subscription | €5-20/mes | Actualizaciones mensuales |

---

## 5. Guía del comprador

### Navegar e instalar

```bash
# Listar disponibles
curl http://localhost:8642/api/marketplace/capsules

# Instalar
curl -X POST http://localhost:8642/api/marketplace/download/mi_capsula \
  -d '{"license_key": "tu-key"}'

# Desde Dashboard: 🏪 Marketplace → [⬇ Instalar]
```

### Gestionar licencias

```python
from zoe.marketplace.core import LicenseChecker

checker = LicenseChecker()
result = checker.can_use("mi_capsula", user_id="fernando")
# {"allowed": True, "license_type": "paid", "expires": null}
```

---

## 6. API del marketplace

### Clases principales (`zoe/marketplace/core.py`)

- `MarketplaceCatalog` — catálogo de cápsulas y casos de uso
- `CapsulePackager` — empaqueta cápsulas para distribución
- `MarketplaceUploader` — sube cápsulas al marketplace
- `MarketplaceDownloader` — descarga cápsulas del marketplace
- `LicenseChecker` — verifica licencias

### Endpoints REST

| Endpoint | Método | Descripción |
|---|---|---|
| `/api/marketplace/capsules` | GET | Lista cápsulas marketplace |
| `/api/marketplace/upload` | POST | Subir cápsula |
| `/api/marketplace/download/{name}` | POST | Descargar cápsula |
| `/api/marketplace/use_cases` | GET | Lista casos de uso |
| `/api/marketplace/upload_use_case` | POST | Subir caso de uso |

---

## 7. Casos de uso YAML en marketplace

Además de cápsulas, el marketplace soporta **casos de uso YAML**: configuraciones completas de ZOE para un escenario específico.

```bash
curl -X POST http://localhost:8642/api/marketplace/upload_use_case \
  -F "file=@cuidado_personas_mayores.yaml" \
  -F "author=Fernando Fondillo" \
  -F "license=paid" \
  -F "price=15.00"
```

---

## 8. Certificación de autores

**Estado:** En roadmap (Q4 2026)

- Curso online de creación de cápsulas
- Examen de certificación
- Badge "ZOE Certified Author"
- Cápsulas de autores certificados tienen prioridad en marketplace

---

*ZOE V1.6.0 — Documento 07: Marketplace Guide*
*Julio 2026*
