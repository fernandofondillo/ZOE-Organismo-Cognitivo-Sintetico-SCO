"""Tests para Senses."""

import asyncio
import os
import tempfile
import time
import pytest

from zoe.peripherals.senses import ClockSense, FilesystemSense, UserInputSense
from zoe.core.cognitive_loop import Observation


# ===== CLOCK SENSE =====

@pytest.mark.asyncio
async def test_clock_sense_observe():
    """ClockSense produce observación."""
    clock = ClockSense()
    obs = await clock.observe()
    assert obs is not None
    assert obs.source == "clock"
    assert "tick" in obs.content.lower() or "hora" in obs.content.lower()


@pytest.mark.asyncio
async def test_clock_sense_increments_iteration():
    """ClockSense incrementa iteración."""
    clock = ClockSense()
    obs1 = await clock.observe()
    obs2 = await clock.observe()
    assert obs1.metadata["iteration"] == 1
    assert obs2.metadata["iteration"] == 2


@pytest.mark.asyncio
async def test_clock_sense_metadata():
    """ClockSense incluye metadata correcta."""
    clock = ClockSense()
    obs = await clock.observe()
    assert "hour" in obs.metadata
    assert "minute" in obs.metadata
    assert "period" in obs.metadata
    assert obs.metadata["period"] in ["morning", "afternoon", "evening", "night"]


# ===== FILESYSTEM SENSE =====

@pytest.mark.asyncio
async def test_filesystem_sense_no_dir():
    """FilesystemSense con directorio inexistente devuelve None."""
    fs = FilesystemSense(watch_dir="/nonexistent/path")
    obs = await fs.observe()
    assert obs is None


@pytest.mark.asyncio
async def test_filesystem_sense_detects_new_file():
    """FilesystemSense detecta archivos nuevos."""
    with tempfile.TemporaryDirectory() as tmpdir:
        fs = FilesystemSense(watch_dir=tmpdir, interval=0.1)

        # Primera observación: sin archivos
        obs1 = await fs.observe()
        # Puede ser None (sin cambios) o "no_change"

        # Crear archivo
        with open(os.path.join(tmpdir, "test.txt"), "w") as f:
            f.write("test")

        # Esperar para que pase el interval
        await asyncio.sleep(0.15)

        # Observar de nuevo: debe detectar el archivo nuevo
        obs2 = await fs.observe()
        assert obs2 is not None

        # Puede ser Observation o List[Observation]
        if isinstance(obs2, list):
            contents = " ".join(o.content for o in obs2)
        else:
            contents = obs2.content
        assert "nuevo" in contents.lower() or "test.txt" in contents


@pytest.mark.asyncio
async def test_filesystem_sense_detects_modification():
    """FilesystemSense detecta archivos modificados."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Crear archivo inicial
        filepath = os.path.join(tmpdir, "test.txt")
        with open(filepath, "w") as f:
            f.write("v1")

        fs = FilesystemSense(watch_dir=tmpdir, interval=0.1)

        # Primera observación
        await fs.observe()

        # Esperar
        await asyncio.sleep(0.15)

        # Modificar archivo
        time.sleep(0.1)  # asegurar mtime distinto
        with open(filepath, "w") as f:
            f.write("v2")

        # Observar de nuevo
        obs = await fs.observe()
        assert obs is not None
        if isinstance(obs, list):
            contents = " ".join(o.content for o in obs)
        else:
            contents = obs.content
        assert "modificado" in contents.lower() or "test.txt" in contents


# ===== USER INPUT SENSE =====

@pytest.mark.asyncio
async def test_user_input_sense_no_input():
    """UserInputSense sin input devuelve None."""
    user = UserInputSense()
    obs = await user.observe()
    assert obs is None


@pytest.mark.asyncio
async def test_user_input_sense_with_input():
    """UserInputSense procesa input inyectado."""
    user = UserInputSense()
    user.inject_input("Hola Zoe")
    obs = await user.observe()
    assert obs is not None
    assert obs.source == "user"
    assert "Hola Zoe" in obs.content


@pytest.mark.asyncio
async def test_user_input_sense_multiple_inputs():
    """UserInputSense procesa múltiples inputs en orden."""
    user = UserInputSense()
    user.inject_input("primero")
    user.inject_input("segundo")

    obs1 = await user.observe()
    obs2 = await user.observe()
    obs3 = await user.observe()  # debe ser None

    assert "primero" in obs1.content
    assert "segundo" in obs2.content
    assert obs3 is None
