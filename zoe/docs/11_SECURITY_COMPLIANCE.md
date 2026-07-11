# 11 — Security & Compliance

> **Seguridad, hardening, GDPR, HIPAA, EU AI Act, modelo de amenazas.**
> **Versión:** V1.6.0 — Julio 2026

---

## 1. Modelo de amenazas

| Amenaza | Vector | Mitigación |
|---|---|---|
| Robo de identidad | Alguien se hace pasar por tu ZOE | Identity Vault con SHA-256 |
| Manipulación de trayectoria | Modificar mutaciones pasadas | Trajectory Chain (blockchain) |
| Inyección de conocimiento falso | Convencer a ZOE de algo falso | Quarantine + CrossValidator |
| Exfiltración de datos | Cloud API envía datos a terceros | Modo offline, cloud opt-in |
| Federación maliciosa | Peer propone mutaciones dañinas | Veto por valores, quorum 2/3 |
| Prompt injection | Extraer system prompt | Validators en Speaker, EthicalMotor |

---

## 2. Identity Vault

- Hash SHA-256 de 9 vectores + 7 valores
- Inmutable (cualquier cambio invalida el hash)
- Soberana (no depende de terceros)
- `verify(action)` comprueba compatibilidad antes de ejecutar

---

## 3. Trajectory Chain

- Cadena de mutaciones firmadas (blockchain-style)
- Cada mutación contiene hash de la anterior
- Inmutable: modificar una invalida todas las posteriores
- `get_history()` permite auditoría completa
- `rollback()` añade mutación de rollback (no elimina original)

---

## 4. Privacidad por diseño

ZOE puede funcionar **100% offline**:
- Sin cloud APIs (modo Ollama local)
- Sin telemetría (ZOE no reporta a terceros)
- Datos no salen del dispositivo
- Usuario controla 100% sus datos

---

## 5. GDPR compliance

**Por arquitectura:**
- Datos no salen del dispositivo (modo offline)
- Sin telemetría a terceros
- Derecho al olvido: `rm -rf zoe_data/`
- Portabilidad: ZOE Seed Mode (SSD portátil)
- Consentimiento explícito para cloud APIs

---

## 6. HIPAA compatibility

Para datos médicos:
- Modo 100% offline
- Sin cloud APIs
- Cápsulas específicas (`pharmacy_interactions`, `elder_care_knowledge`)
- Audit log completo (Trajectory Chain)
- Restrictions: no diagnosis, no medication modification

---

## 7. EU AI Act 2024

ZOE cumple requisitos para "Trustworthy AI":
- **Transparencia**: Trajectory Chain auditable
- **Human oversight**: humano en el loop
- **Technical robustness**: 1008 tests, validación epistémica
- **Privacy**: GDPR compliant por diseño
- **Accountability**: identidad criptográfica, firma de mutaciones
- **Societal well-being**: veto por valores en federación

---

## 8. Gestión de API keys

### Almacenamiento seguro

```bash
# Pendrive (chmod 600)
echo "OPENAI_API_KEY=sk-..." > /Volumes/SSD/ZOE/data/.env
chmod 600 /Volumes/SSD/ZOE/data/.env

# VPS (systemd env vars)
[Service]
Environment="OPENAI_API_KEY=sk-..."
```

### Rotación
1. Generar nueva key en provider
2. Actualizar `.env` o systemd
3. Reiniciar ZOE
4. Revocar key antigua

---

## 9. Hardening checklist

### Pendrive macOS
- [ ] API key en `ZOE/data/.env` con `chmod 600`
- [ ] `/quit` antes de desconectar SSD
- [ ] Backup encriptado del SSD

### VPS Linux
- [ ] API keys en env vars (no en código)
- [ ] `chmod 600` en `zoe_data/*.json`
- [ ] Firewall: solo puertos 22, 80, 443
- [ ] TLS con Nginx + Let's Encrypt
- [ ] Rate limiting en `/chat`
- [ ] Authentication para dashboard
- [ ] Backup automático diario
- [ ] Monitoring con alertas

### Docker
- [ ] API keys en Docker secrets
- [ ] Volúmenes encriptados
- [ ] Network isolation
- [ ] Image scanning

### Kubernetes
- [ ] Secrets en K8s Secrets
- [ ] RBAC estricto
- [ ] Network policies
- [ ] Audit logging

---

## 10. Veto por valores

En federación B2B, cualquier ZOE puede vetar mutaciones que violen valores:

```python
federation_manager.cast_vote(
    mutation_id="...",
    vote="VETO",
    reason="Viola valor: truth_over_comfort"
)
# Mutación rechazada automáticamente
```

---

*ZOE V1.6.0 — Documento 11: Security & Compliance*
*Julio 2026*
