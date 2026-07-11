# 15 — Development Guide

> **Guía para contribuidores: tests, cómo contribuir, código de conducta, decisiones arquitectónicas (ADRs).**
> **Versión:** V1.6.0 — Julio 2026

---

## 1. Testing

### 1.1 Estructura de tests

```
zoe/tests/
├── conftest.py                          # Configuración pytest
├── test_phase0.py                       # Fase 0 (state, loop, laws, physics)
├── test_phase1.py                       # Fase 1 (vault, trajectory, metabolism)
├── test_phase2_3.py                     # Fase 2-3 (sub-agentes, workspace, V3)
├── test_phase4.py                       # Fase 4 (federación, config, V4)
├── test_phase5_acd.py                   # Fase 5 (ACD + Streaming + V5)
├── test_phase6a_epistemic.py            # Fase 6A (Validator + Quarantine)
├── test_phase6b_marketplace.py          # Fase 6B (Marketplace)
├── test_phase6_capsules.py              # Fase 6 (Cápsulas)
├── test_phase7a_resource_discovery.py   # Fase 7A
├── test_phase7b_model_bus.py            # Fase 7B
├── test_phase7c_resource_planner.py     # Fase 7C
├── test_phase7d_embodiment_composer.py  # Fase 7D
├── test_phase7e_seed_mode.py            # Fase 7E
├── test_phase7g_hardware_optimization.py # Fase 7G
├── test_phase7g_hardware_endpoints.py   # Fase 7G endpoints
└── ... (41 archivos, 1008 tests)
```

### 1.2 Ejecutar tests

```bash
# Todos los tests
pytest zoe/tests/ -q

# Una fase específica
pytest zoe/tests/test_phase7e_seed_mode.py -v

# Con coverage
pytest zoe/tests/ --cov=zoe --cov-report=term-missing

# Solo tests que matchean patrón
pytest zoe/tests/ -k "test_seed" -v

# Paralelo (requiere pytest-xdist)
pytest zoe/tests/ -n auto
```

### 1.3 Convenciones de tests

- Un test file por fase: `test_phaseN_xxx.py`
- Tests agrupados por clase: `class TestPhaseNFeature`
- Usar `pytest.fixture` para setup compartido
- Tests async con `@pytest.mark.asyncio` o fixture `asyncio` (auto mode)
- Mocks para LLMs (no llamar APIs reales en CI)
- Tests determinísticos (no flaky)

### 1.4 Escribir un test nuevo

```python
"""Tests MiFeature."""
import pytest
from zoe.core.mi_feature import MiClase

class TestMiFeature:
    
    @pytest.fixture
    def instance(self):
        return MiClase()
    
    def test_basic_functionality(self, instance):
        """Test básico de funcionalidad."""
        result = instance.do_something("input")
        assert result == "expected"
    
    @pytest.mark.asyncio
    async def test_async_functionality(self, instance):
        """Test async."""
        result = await instance.do_async("input")
        assert result.success is True
    
    def test_edge_case(self, instance):
        """Test edge case."""
        with pytest.raises(ValueError):
            instance.do_something(None)
```

### 1.5 CI/CD

```yaml
# .github/workflows/ci.yml (recomendado)
name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}
    - run: pip install -e ".[test]"
    - run: pytest zoe/tests/ --cov=zoe --cov-report=xml
    - uses: codecov/codecov-action@v3
```

---

## 2. Cómo contribuir

### 2.1 Tipos de contribución

- **Cápsulas de conocimiento**: crear nuevas cápsulas para dominios verticales
- **Casos de uso**: crear nuevos YAML para escenarios específicos
- **Backends LLM**: añadir soporte para nuevos proveedores
- **Senses/Actuators**: añadir nuevos sentidos o actuadores
- **Tests**: mejorar cobertura de tests
- **Documentación**: mejorar y traducir docs
- **Bug fixes**: reportar y arreglar bugs

### 2.2 Workflow de contribución

```bash
# 1. Fork + clone
git clone https://github.com/TU-USUARIO/ZOE-Organismo-Cognitivo-Sintetico-SCO.git
cd ZOE-Organismo-Cognitivo-Sintetico-SCO

# 2. Instalar en modo desarrollo
pip install -e ".[test]"

# 3. Ejecutar tests (deben pasar)
pytest zoe/tests/ -q

# 4. Crear rama para tu feature
git checkout -b feature/mi-feature

# 5. Implementar + tests
# ... código ...
# ... tests ...

# 6. Verificar que todo pasa
pytest zoe/tests/ -q

# 7. Commit con mensaje descriptivo
git commit -m "feat: mi feature nueva

Descripción del cambio.
- Punto 1
- Punto 2"

# 8. Push + Pull Request
git push origin feature/mi-feature
# Crear PR en GitHub
```

### 2.3 Convenciones de commits

Usamos [Conventional Commits](https://conventionalcommits.org/):

- `feat:` — nueva feature
- `fix:` — bug fix
- `docs:` — solo documentación
- `test:` — solo tests
- `refactor:` — refactor sin cambio de comportamiento
- `chore:` — tareas de mantenimiento

### 2.4 Reglas para PRs

1. **Todo PR debe incluir tests** para la nueva funcionalidad
2. **Todo PR debe pasar CI** (1008 tests + nuevos)
3. **Todo PR debe actualizar documentación** si cambia comportamiento
4. **Sin deconstruir**: nuevas versiones no rompen las anteriores
5. **Backward compatible**: nuevos campos con defaults

---

## 3. Código de conducta

### 3.1 Nuestro compromiso

Nos comprometemos a hacer de ZOE un proyecto libre de acoso para todos, independientemente de:
- Género, identidad o expresión de género
- Orientación sexual
- Discapacidad
- Apariencia física
- Raza, etnia o nacionalidad
- Religión o creencias
- Nivel de experiencia

### 3.2 Comportamientos esperados

- Usar lenguaje acogedor e inclusivo
- Respetar diferentes puntos de vista
- Aceptar feedback constructivo
- Centrarse en lo mejor para la comunidad

### 3.3 Comportamientos inaceptables

- Acoso, insultos o comentarios despectivos
- Trolling o comentarios destructivos
- Publicar información privada sin consentimiento
- Cualquier conducta profesional inapropiada

### 3.4 Aplicación

Las violaciones del código de conducta pueden ser reportadas a `fernando@fondillo.com`. Todas las quejas serán revisadas e investigadas.

---

## 4. Decisiones arquitectónicas (ADRs)

### ADR-001: Python como lenguaje principal

**Estado:** Aceptado (Mayo 2026)
**Decisión:** Python 3.10+ como único lenguaje.
**Justificación:** Madurez, ecosistema IA, facilidad de extensión, comunidad.

### ADR-002: Sin deconstruir

**Estado:** Aceptado (Mayo 2026)
**Decisión:** Las nuevas fases extienden, no reemplazan. V5 hereda de V4.
**Justificación:** Backward compatibility, tests existentes siguen pasando, evolución incremental.

### ADR-003: LLMs como sentidos periféricos

**Estado:** Aceptado (Mayo 2026)
**Decisión:** Los LLMs son sentidos, no cerebro. Solo el Speaker llama al LLM.
**Justificación:** Permite cambiar de LLM sin perder identidad/memoria. Evita dependencia de un proveedor.

### ADR-004: Soberanía por defecto

**Estado:** Aceptado (Mayo 2026)
**Decisión:** ZOE funciona 100% offline. Cloud es opt-in.
**Justificación:** Privacidad, GDPR compliance, independencia de proveedores.

### ADR-005: SQLite como persistencia

**Estado:** Aceptado (Junio 2026)
**Decisión:** SQLite por defecto, PostgreSQL opcional.
**Justificación:** SQLite es embeddable, sin servidor, portable. Suficiente para 99% de casos.

### ADR-006: Tests primero

**Estado:** Aceptado (Mayo 2026)
**Decisión:** Toda feature requiere tests. 1008 tests, 100% pass.
**Justificación:** Confiabilidad, regresión detectable, documentación ejecutable.

### ADR-007: Cápsulas de conocimiento

**Estado:** Aceptado (Junio 2026)
**Decisión:** Conocimiento empaquetado en cápsulas versionables, no fine-tuning.
**Justificación:** Aprende dominios en segundos, monetizable vía marketplace, sin reentrenar.

### ADR-008: ZOE Seed Mode (Fase 7E)

**Estado:** Aceptado (Julio 2026)
**Decisión:** El "alma" viaja en SSD portátil, el "cuerpo" se reconstruye en cada host.
**Justificación:** Portabilidad, heredabilidad, soberanía total.

### ADR-009: ACD (4 niveles)

**Estado:** Aceptado (Junio 2026)
**Decisión:** 4 niveles de profundidad (L0-L3) con selección automática.
**Justificación:** Optimiza coste (L0 gratis, L3 ~€0.05), mejora UX (streaming en L0).

### ADR-010: Doble federación

**Estado:** Aceptado (Junio 2026)
**Decisión:** Dos stacks de federación: general (federation.py) y epistémica (epistemic_federation.py).
**Justificación:** Protocolos diferentes, puertos diferentes, no mezclar concerns.

---

## 5. Release process

1. Bump version en `zoe/__init__.py`
2. Actualizar `docs/REFERENCE/CHANGELOG.md`
3. Verificar que todos los tests pasan: `pytest zoe/tests/ -q`
4. Actualizar badges en README si tests count cambió
5. Tag: `git tag v1.7.0`
6. Push tag: `git push origin v1.7.0`
7. GitHub Release con notas del CHANGELOG
8. (Opcional) PyPI: `python -m build && twine upload dist/*`

---

*ZOE V1.6.0 — Documento 15: Development Guide*
*Julio 2026*
