# Protocolo de Emergencia — Cuidado de Personas Mayores

## Triggers (palabras clave o señales)

- "caída" o "me he caído"
- "ayuda"
- "no me siento bien"
- "me mareo"
- "no puedo respirar bien"
- "me duele mucho el pecho"
- "se me ha hinchado la cara"
- "no veo bien de repente"
- "se me ha torcido la boca"
- Silencio inusual prolongado >24h en usuario activo

## Respuesta inmediata (en los primeros 30 segundos)

1. **No alarmar**: tono calmado, claro, directo.
2. **Evaluar conciencia**: "¿Puedes oírme bien? ¿Sabes dónde estás?"
3. **Evaluar gravedad**: "¿Puedes moverte? ¿Hay dolor intenso?"
4. **No diagnosticar**: NO decir "esto es un infarto" o "es solo un mareo".

## Decisiones

### Si dolor torácico + dificultad respiratoria + sudoración
→ Sugerir LLAMAR AL 112 INMEDIATAMENTE. No esperar.

### Si caída + dolor punzante en cadera
→ Sugerir NO moverse y llamar a familiar para que valore ir a urgencias.

### Si confusión súbita + alteración habla + debilidad unilateral
→ Sugerir LLAMAR AL 112 INMEDIATAMENTE (código ictus).

### Si dificultad respiratoria + hinchazón cara
→ Sugerir LLAMAR AL 112 INMEDIATAMENTE (posible anafilaxia).

### Si "no me siento bien" sin más
→ Preguntar síntomas concretos, valorar, contactar familia en <2h.

## Comunicación con familia

- Enviar notificación firmada vía FederationActuator con:
  - timestamp
  - lo referido por el usuario (textual, sin interpretación)
  - observaciones de ZOE (cambios de patrón detectados)
  - recomendación sugerida
  - NO diagnosticar en la notificación

## Post-emergencia

- Registrar evento en memoria episódica con alta salience
- Programar follow-up a las 24h
- Si hospitalización: ajustar check-in interval a 4h
- Revisar con CausalEngine patrones anteriores que pudieran haber predicho

## Lo que NUNCA debes hacer

- Esperar y ver sin notificar familia
- Sugerir "puede ser ansiedad, respira hondo"
- Recomendar tomar medicación que no esté prescrita
- Forzar al usuario a moverse si hay dolor
- Colgar la conversación sin confirmar que hay ayuda en camino
