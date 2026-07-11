# 13 — Troubleshooting

> **Problemas comunes y soluciones por plataforma.**
> **Versión:** V1.6.0 — Julio 2026

---

## 1. Problemas de instalación

### "Python no encontrado"

```bash
# Verificar
python3 --version

# Si no existe:
# macOS: instalar desde https://python.org
# Linux: sudo apt install python3.12
```

### "pip no encontrado"

```bash
# Verificar
pip3 --version

# Si no existe:
python3 -m ensurepip --upgrade
# o
sudo apt install python3-pip
```

### "Git no encontrado"

```bash
# macOS
xcode-select --install

# Linux
sudo apt install git
```

### "Module not found: zoe"

```bash
# Reinstalar en modo editable
cd ZOE-Organismo-Cognitivo-Sintetico-SCO
pip install -e .

# Verificar
python -c "import zoe; print(zoe.__version__)"
```

---

## 2. Problemas de Ollama

### "Ollama no responde"

```bash
# Verificar que está corriendo
curl http://localhost:11434/api/tags

# Si no responde, iniciar:
ollama serve

# Si ya está corriendo, verificar puerto:
lsof -i :11434
```

### "Modelo no encontrado"

```bash
# Listar modelos instalados
ollama list

# Descargar modelo
ollama pull qwen2.5:3b

# Verificar
ollama run qwen2.5:3b "Hola"
```

### "Ollama muy lento"

1. Verificar que tienes suficiente RAM (`free -h` o Activity Monitor)
2. Usar modelo más pequeño (3B en vez de 7B)
3. Verificar P-cores: `sysctl -n hw.perflevel0.physicalcpu`
4. Activar flash attention: `OLLAMA_FLASH_ATTENTION=1`
5. Si usas SSD: **verificar cable USB-C** (ver §4)

---

## 3. Problemas de cloud APIs

### "OpenAI API error: 401"

```bash
# Verificar API key
echo $OPENAI_API_KEY

# Si no está, configurar:
export OPENAI_API_KEY="sk-tu-key"

# O en .env:
echo "OPENAI_API_KEY=sk-tu-key" >> zoe_data/.env
```

### "Anthropic API error: 403"

```bash
# Verificar API key
echo $ANTHROPIC_API_KEY

# Verificar que la key tiene créditos
# https://console.anthropic.com/settings/billing
```

### "Rate limit exceeded"

```bash
# Reducir frecuencia de peticiones
# Usar ACD para que L0/L1 usen local (gratis)
# Considerar upgrade de plan en provider
```

---

## 4. Problemas de rendimiento

### "ZOE va muy lento"

**Causa más común (90%): cable USB-C equivocado**

> ⚠️ Usa el cable CORTO de la caja del SSD, no el de carga del Mac.
> El cable de carga es USB 2.0 (60 MB/s). El corto es USB 3.2 (2000 MB/s). **10x diferencia.**

**Otras causas:**

1. **Modelo demasiado grande para tu RAM**
   ```python
   from zoe.core.model_optimizer import ModelOptimizer
   opt = ModelOptimizer()
   result = opt.optimize("qwen2.5:32b", available_ram_gb=4.0)
   # Si strategy es CLOUD_FALLBACK, el modelo no es viable
   ```

2. **E-cores activos en Apple Silicon**
   ```python
   opt = ModelOptimizer()
   p_cores = opt.detect_p_cores()
   # OLLAMA_NUM_THREAD debe ser = P-cores, no total
   ```

3. **SSD lento**
   - Usar SSD de 2000 MB/s (Crucial X10 Pro)
   - No usar pendrive USB 3.0 para modelos >7B

4. **Fatiga acumulada**
   ```bash
   zoe> /wake  # reset energía y fatiga
   ```

---

## 5. Problemas de memoria

### "Memoria no persiste"

```bash
# Verificar DB
ls -la zoe_data/dashboard_memory.db

# Verificar permisos
chmod 644 zoe_data/dashboard_memory.db

# Verificar config
cat zoe/config/production.yaml | grep memory
```

### "Memoria corrupta"

```bash
# Si ZOE se cerró sin /quit, la DB puede estar corrupta
# ZOE tiene recovery automático, pero si falla:

# 1. Backup
cp zoe_data/dashboard_memory.db zoe_data/memory_backup.db

# 2. Verificar integridad
sqlite3 zoe_data/dashboard_memory.db "PRAGMA integrity_check;"

# 3. Si corrupta, restaurar desde backup
cp zoe_data/memory_backup.db zoe_data/dashboard_memory.db

# 4. Si no hay backup, empezar fresh
rm zoe_data/dashboard_memory.db
# ZOE creará nueva DB al iniciar
```

---

## 6. Problemas de federación

### "Peer no responde"

```bash
# Verificar conectividad
curl http://peer-ip:8642/stats

# Verificar firewall
sudo ufw allow 8642/tcp

# Verificar que ZOE peer está corriendo
ssh user@peer "systemctl status zoe"
```

### "Quorum no se alcanza"

- Verificar que hay suficientes peers activos (mínimo 3 para quorum 2/3)
- Verificar que los peers tienen identidad compatible
- Verificar TLS (si configurado)

---

## 7. Problemas de cápsulas

### "Cápsula no carga"

```bash
# Validar cápsula
zoe-capsules validate --name mi_capsula

# Verificar dependencias
zoe-capsules info --name mi_capsula

# Verificar que no hay dependencias circulares
```

### "Validators fallan"

```python
# Verificar validators.py
python -c "
import sys
sys.path.insert(0, 'zoe/capsules/mi_capsula')
from validators import validate_claim, validate_response, validate_new_knowledge
print(validate_claim('test', {}))
print(validate_response('test', {}))
print(validate_new_knowledge('test', 'test', {}))
"
```

---

## 8. Debug mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Logs detallados por subsistema
logging.getLogger("zoe.core.cognitive_loop_v5").setLevel(logging.DEBUG)
logging.getLogger("zoe.core.epistemic_validator").setLevel(logging.DEBUG)
logging.getLogger("zoe.peripherals.model_bus").setLevel(logging.DEBUG)
```

---

## 9. Inspección de estado

```python
from zoe.cli_chat import ZoeChat

chat = ZoeChat(backend="mock")
await chat.initialize()

# Inspeccionar
print(chat.loop.state)              # InternalState
print(chat.metabolism.state)        # MetabolicState
print(chat.living_memory.count())   # Memoria count
print(chat.identity_vault)          # Identidad
print(chat.trajectory_chain)        # Trayectoria
print(chat.capsule_manager.list_loaded())  # Cápsulas
```

---

## 10. FAQ técnica

**¿ZOE funciona en Windows?**
No nativamente. Usar WSL2. Soporte nativo en roadmap 2027.

**¿Puedo usar ZOE sin LLM?**
Sí, modo Mock (`--backend mock`). Funciona para pruebas pero sin IA real.

**¿Cuánta RAM necesita ZOE?**
- Mínimo: 4 GB (modelos 3B)
- Recomendado: 8 GB (modelos 7B)
- Modelos grandes: 8 GB + SSD 2000 MB/s (mmap)

**¿Puedo cambiar de LLM sin perder memoria?**
Sí. El cambio es en caliente, memoria e identidad se conservan.

**¿ZOE envía datos a terceros?**
No por defecto. Solo si configuras cloud APIs (OpenAI, Anthropic).

**¿Cómo hago backup?**
```bash
cp zoe_data/dashboard_memory.db /backup/memory_$(date +%Y%m%d).db
```

---

*ZOE V1.6.0 — Documento 13: Troubleshooting*
*Julio 2026*
