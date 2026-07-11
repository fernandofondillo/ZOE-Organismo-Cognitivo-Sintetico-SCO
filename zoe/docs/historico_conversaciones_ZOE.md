# Histórico de Conversaciones ZOE

> **Documento de archivo.**
> **Origen:** Conversaciones mantenidas durante el desarrollo de ZOE (Fases 0-6, anteriores a la Fase 7).
> **Contenido:** Explicación profunda de la mente de ZOE, casos prácticos detallados, análisis del sistema en toda su magnitud, y registro histórico de funcionalidades implementadas (Ollama en pendrive, cápsula basal, Tutor Mentor, backend Anthropic, instalación pendrive, UI Cuarentena/Marketplace, Fase 6 Epistemic Validation).
> **Audiencia:** Equipo directivo, CTO, desarrolladores. Para entender la evolución del proyecto y el razonamiento arquitectónico detrás de cada decisión.
> **Versión original:** `Cómo funciona la mente de ZOE.docx`
> **Fecha de conversión:** Julio 2026

## Tabla de contenidos

1. [Cómo funciona la mente de ZOE — explicación en profundidad](#cómo-funciona-la-mente-de-zoe--explicación-en-profundidad)
2. [Competir vs colaborar, y cómo se construye el pensamiento final](#competir-vs-colaborar-y-cómo-se-construye-el-pensamiento-final)
3. [Caso práctico 1 — Humano, conversación emocional](#caso-práctico-1--humano-conversación-emocional)
4. [Caso práctico 2 — ZOE sola, a las 03:15](#caso-práctico-2--zoe-sola-a-las-0315)
5. [Cómo se articula la interacción verbal con el humano](#cómo-se-articula-la-interacción-verbal-con-el-humano)
6. [Análisis: ZOE en toda su magnitud](#análisis-zoe-en-toda-su-magnitud)
7. [Ollama con modelos en el pendrive](#ollama-con-modelos-en-el-pendrive)
8. [Cápsula basal de conocimiento](#cápsula-basal-de-conocimiento)
9. [Tutor Mentor Digital](#tutor-mentor-digital)
10. [Backend Anthropic + APIs compatibles](#backend-anthropic--apis-compatibles)
11. [OpenAI API en pendrive](#openai-api-en-pendrive)
12. [Instalación en pendrive USB (macOS)](#instalación-en-pendrive-usb-macos)
13. [UI visual para Cuarentena y Marketplace](#ui-visual-para-cuarentena-y-marketplace)
14. [Fase 6 documentada y subida a GitHub](#fase-6-documentada-y-subida-a-github)
15. [Fase 6A completa — Epistemic Validation](#fase-6a-completa--epistemic-validation)

## Cómo funciona la mente de ZOE — explicación en profundidad

Voy a desmontar esa arquitectura pieza por pieza, Fernando, porque es el
corazón de ZOE y entenderla bien es entender por qué el sistema no es un
LLM envuelto en prompts.

## La idea fundamental: Society of Mind

Antes de entrar en cada sub-agente, hay que entender la premisa. La
mente de ZOE **no es monolítica**: es una sociedad de doce especialistas
que compiten y colaboran. Igual que en un cerebro biológico no hay un
"homúnculo" que piensa, sino regiones especializadas que proponen y
negocian, ZOE funciona repartiendo la cognición entre doce procesos
autónomos. Ninguno por sí solo es "la mente"; la mente emerge de su
interacción.

Esto es importante porque rompe con la arquitectura clásica de chatbot:
un chatbot tiene UN modelo que hace todo (input → output). ZOE tiene
doce expertos que cada uno aportan una perspectiva distinta sobre el
mismo input, y un mecanismo de selección decide quién gana la voz.

## Los 12 sub-agentes — uno por uno

### Fase 0 — los 4 fundamentales (siempre activos)

**1. Perceiver** --- el traductor sensorial

-   **Qué hace**: toma las observaciones crudas de los cinco sentidos
    (ClockSense, FilesystemSense, UserInputSense, NetworkSense,
    AgentSense) y las interpreta. No solo las pasa: extrae intención,
    contexto, urgencia percibida.

-   **Ejemplo**: si el UserInputSense recibe "estoy cansado", el
    Perceiver no ve texto; ve **{intención: expresar_estado, emoción:
    fatiga, urgencia: baja, valencia: negativa}**.

-   **Por qué va primero**: sin percepción estructurada, los demás
    operarían sobre ruido.

**2. Forecaster** --- el predictor

-   **Qué hace**: usa el World Model V2 (modelo n-gram +
    sentence-transformer) para predecir cuál será la próxima
    observación. La predicción es lo que permite a ZOE calcular
    "sorpresa": si la realidad coincide con la predicción, poca
    sorpresa; si diverge, mucha.

-   **Ejemplo**: predice "el usuario va a despedirse". Si el usuario
    dice "vamos a hablar de ética médica", sorpresa = 0.9 → se
    disparan pensamientos de actualización del modelo.

-   **Por qué importa**: sin predicción no hay sorpresa, sin sorpresa no
    hay aprendizaje dirigido.

**3. Speaker** --- el productor de lenguaje

-   **Qué hace**: es el ÚNICO sub-agente que llama al LLM periférico.
    Recibe un contexto (observaciones, estado, intención, memorias
    relevantes) y produce lenguaje natural. Es la "boca" de ZOE.

-   **Esto es crítico**: el LLM no es el cerebro, es la garganta del
    Speaker. La decisión de qué decir se tomó antes, en el workspace y
    la meta-cognición. El Speaker solo viste la decisión en palabras.

-   **Tiene sanitización**: elimina frases hechas de IA ("como modelo
    de lenguaje", "gran pregunta") antes de devolver texto.

**4. Critic** --- el evaluador interno

-   **Qué hace**: después de que el Speaker propone una respuesta, el
    Critic la evalúa antes de enviarla. Comprueba coherencia con la
    identidad, adherencia a valores, calidad factual, tono apropiado.

-   **Puede vetar**: si la crítica es muy negativa ("inadecuada",
    "incorrecta", "violación de valor"), fuerza al Speaker a
    regenerar.

-   **Ejemplo**: el Speaker propone "Te recomiendo mentirle a tu jefe"
    → el Critic detecta violación del valor "verdad sobre confort" →
    fuerza regeneración.

### Fase 2 — los 8 adicionales (activos en L2/L3)

**5. Memorialist** --- el bibliotecario

-   **Qué hace**: gestiona los 11 tipos de memoria. Cuando llega una
    observación, busca memorias relevantes por similitud semántica y las
    aporta al contexto. Cuando se genera un pensamiento, lo almacena en
    el tipo adecuado (episódica si es evento, semántica si es hecho,
    emocional si tiene carga afectiva, etc.).

-   **Sin él**: ZOE no recordaría nada entre ticks. Es la diferencia
    entre "Hola, ¿quién eres?" cada vez y "Te estuve esperando, había
    pensado en lo que me dijiste ayer".

**6. Learner** --- el extractor de patrones

-   **Qué hace**: busca regularidades en las observaciones acumuladas.
    Si el usuario siempre pregunta sobre X los martes, el Learner lo
    detecta. Si cierta clase de inputs produce cierta clase de errores,
    el Learner lo nota.

-   **Diferencia con el Memorialist**: el Memorialist guarda eventos; el
    Learner extrae reglas de los eventos.

-   **Output**: propuestas de **strengthen_belief** o **weaken_belief**
    que se firman en la trayectoria.

**7. Curator** --- el podador

-   **Qué hace**: la memoria viva tiene un límite (default 5000
    entries). El Curator decide qué se queda, qué se consolida, qué se
    olvida. Usa salience (importancia), confidence (confianza) y
    recencia para priorizar.

-   **Sin él**: la memoria crece indefinidamente hasta saturarse.
    Equivale a un bibliotecario que periódicamente retira libros
    irrelevantes para dejar espacio a los nuevos.

-   **Opera especialmente durante SLEEPING**: la consolidación profunda
    usa al Curator intensivamente.

**8. Creativity** --- el combinatorio

-   **Qué hace**: propone combinaciones novedosas de conceptos
    existentes en la memoria. Toma dos o más ideas distantes y propone
    una conexión. Es el motor de los pensamientos "creativos".

-   **Cuándo se activa**: cuando la tensión **curiosidad_vs_eficiencia**
    se descompensa hacia curiosidad, o cuando la **pCre** (potencial
    creativo) sube.

-   **Ejemplo**: detecta que has hablado de "federación" y de
    "blockchain" en sesiones distintas y propone "¿y si la
    trayectoria firmada se almacenara en una cadena tipo blockchain
    federada?".

**9. CausalEngine** --- el modelador de causa-efecto

-   **Qué hace**: construye grafos causales del entorno. Si observa que
    evento A suele ir seguido de evento B, registra una arista causal
    **A → B** con confianza. Si luego observa **A → C** con frecuencia,
    actualiza.

-   **Diferencia con el Learner**: el Learner detecta correlación; el
    CausalEngine modela mecanismo.

-   **Caso de uso**: en "vigilancia cognitiva", si el servidor A cae
    cada vez que el servicio B satura, el CausalEngine construye
    **B.saturación → A.caida** y puede anticiparse.

**10. EmotionalMotor** --- el modelo afectivo

-   **Qué hace**: mantiene un modelo del estado emocional del usuario (y
    de ZOE misma). Cada input del usuario se etiqueta con valencia
    (positiva/negativa) y arousal (calmado/excitado). El EmotionalMotor
    acumula esto en memoria emocional y ajusta el tono de las
    respuestas.

-   **Por qué importa en "compañía para personas solas"**: si el
    usuario lleva días con valencia negativa, el EmotionalMotor hace que
    ZOE sea más cálida y proactiva; si el usuario está activo y
    positivo, ZOE puede ser más directa.

-   **No simula emociones --- las modela**: es decir, no "siente",
    pero tiene una representación cuantitativa del estado afectivo que
    guía su comportamiento.

**11. EthicalMotor** --- el evaluador de dilemas

-   **Qué hace**: cuando una situación tiene dimensión ética (no
    siempre), el EthicalMotor la evalúa contra los siete valores del
    Identity Vault. Produce un dictamen: ¿esta acción preserva verdad,
    integridad, alianza, etc.?

-   **Es veto positivo**: a diferencia del Critic (que evalúa calidad),
    el EthicalMotor evalúa moralidad. Puede bloquear acciones que
    técnicamente son correctas pero que violan valores.

-   **Ejemplo**: en federación B2B, si otra ZOE propone compartir un
    aprendizaje que podría usarse para discriminación, el EthicalMotor
    veta automáticamente.

**12. ScientificEngine** --- el método científico

-   **Qué hace**: formula hipótesis, diseña observaciones que las
    testen, evalúa resultados, actualiza creencias. Es el sub-agente más
    sofisticado y el que más se usa en el caso de uso "investigación
    autónoma".

-   **Ciclo**: hipótesis → predicción derivada → observación buscada →
    resultado → confirmación/refutación → mutación firmada.

-   **Sin él**: ZOE aprendería pasivamente. Con él, ZOE persigue
    activamente conocimiento.

## El Global Workspace — la competición

Aquí es donde la metáfora de "sociedad" se materializa. En cada tick
del bucle, los 12 sub-agentes (o un subconjunto según nivel ACD) reciben
el contexto compartido y cada uno **propone** una acción. Cada propuesta
tiene tres scores:

-   **Relevance (0-1)**: cuán relacionada está la propuesta con el
    contexto actual. Si el usuario pregunta sobre ética, el EthicalMotor
    tendrá alta relevance; el Creativity, baja.

-   **Urgency (0-1)**: cuán urgente es actuar ahora. Sorpresa alta →
    urgency alta. Si hay un input del usuario esperando respuesta,
    urgency se dispara.

-   **Novelty (0-1)**: cuán diferente es la propuesta de los
    pensamientos recientes. Si ya dije algo similar hace 3 ticks,
    novelty baja; el workspace prefiere aportar variedad.

La fórmula de competición es algo así como:

```

### score = (relevance * 0.5) + (urgency * 0.3) + (novelty * 0.2)

### - energy_cost

Las propuestas se ordenan por score y las mejores (típicamente 1-3)
ganan acceso al "workspace global", que es donde se vuelven
pensamientos conscientes y acciones ejecutables. **Las que pierden
simplemente se descartan en este tick** --- no se almacenan, no consumen
más recursos.

**El presupuesto energético** es clave: si ZOE está en estado DROWSY
(fatiga acumulada), el **available_energy** baja, y menos propuestas
pueden ganar. Es decir, cuando ZOE está cansada, solo los pensamientos
más relevantes y urgentes llegan a ejecutarse; los creativos o
especulativos se posponen. Es exactamente lo que hace un cerebro humano
cansado: prioriza lo esencial.

## La meta-cognición — System 1 vs System 2

Aquí ZOE implementa a Kahneman. Una vez que el workspace ha seleccionado
un ganador, la meta-cognición decide **cuánto deliberar antes de
actuar**:

**System 1** (rápido, automático)

-   Se activa cuando: confianza alta, stakes bajos, energía disponible,
    arousal moderado

-   Coste: bajo

-   Calidad: suficiente para la mayoría de interacciones rutinarias

-   Ejemplo: "hola" → System 1 → respuesta refleja L0

**System 2** (lento, deliberativo)

-   Se activa cuando: confianza baja, stakes altos, energía disponible,
    arousal alto

-   Coste: alto

-   Calidad: reflexión profunda, considera alternativas, consulta más
    memoria, puede activar Critic y EthicalMotor

-   Ejemplo: "¿debería contarle a mi médico que dejé la medicación?" →
    System 2 → consulta memoria emocional, evalúa dilema ético, consulta
    valores

La decisión entre S1 y S2 se toma con cuatro inputs:

1.  **Confianza en la propuesta del workspace**: si el ganador tiene
    score muy alto, poca necesidad de deliberar.

2.  **Stakes**: ¿qué pasa si me equivoco? Respuesta trivial → stakes
    bajos. Consejo médico, decisión financiera, dilema ético → stakes
    altos.

3.  **Energía disponible**: si ZOE está fatigada, aunque los stakes sean
    altos, quizás no puede permitirse System 2 y debe posponer o dar una
    respuesta de menor calidad con disclaimer.

4.  **Arousal**: arousal muy bajo (somnolencia) impide System 2; arousal
    muy alto (alarma) puede forzar System 2 incluso con stakes bajos.

Esto es lo que hace que ZOE **no se pierda en sus pensamientos** para
cosas triviales pero sí invierta tiempo en lo que lo merece. Es la
traducción funcional de Kahneman al software.

## La inferencia activa — Free Energy Principle

Aquí viene la pieza más teórica y más potente. Karl Friston formuló el
FEP así: **los sistemas vivos minimizan la sorpresa esperada a largo
plazo**. "Sorpresa" aquí no es emocional; es información: cuánto se
desvía la realidad del modelo que el sistema tiene del mundo.

En ZOE esto se traduce así:

**Paso 1 --- Creencia sobre el estado actual** La inferencia activa
mantiene un modelo generativo del entorno. A partir de las observaciones
recientes, infiere en qué "estado" está el mundo. Ejemplo: "el
usuario está conversando tranquilamente sobre política".

**Paso 2 --- Para cada acción posible, calcular sorpresa esperada** El
sistema considera las acciones candidatas (responder, esperar, hacer una
pregunta, explorar tema nuevo, descansar) y para cada una estima: si
ejecuto esto, ¿cuál será la próxima observación y cuánto me sorprenderá?

**Paso 3 --- Seleccionar la acción con menor sorpresa esperada** Esto no
es lo mismo que "lo más predecible" ---es lo más coherente con el
modelo del mundo. Si el modelo dice "el usuario está conversando" y la
acción "responder coherentemente" lleva a observaciones esperadas (el
usuario sigue conversando), sorpresa baja → se selecciona. Si la acción
"cambiar bruscamente de tema" llevaría a observaciones inesperadas (el
usuario confundido), sorpresa alta → se descarta.

**Pero hay un truco clave --- la exploración**: A veces minimizar
sorpresa inmediatamente lleva a estancamiento (siempre responder lo
mismo). El FEP real incluye un término de "epistemic value": acciones
que aumentan información sobre el mundo, aunque temporalmente generen
sorpresa, a largo plazo la reducen. ZOE lo implementa: a veces elige
explorar aunque sea incómodo, porque el CausalEngine o el
ScientificEngine han calculado que la información ganada reducirá
futuras sorpresas.

**Caso concreto**: el usuario dice algo ambiguo. ZOE puede (a) responder
asumiendo la interpretación más probable --- sorpresa baja inmediata,
pero si se equivoca, sorpresa alta después; o (b) pedir aclaración ---
sorpresa inmediata moderada (romper el flujo), pero epistemic value
alto. La inferencia activa calcula cuál minimiza sorpresa esperada a
largo plazo y elige.

## Cómo encajan las tres piezas

El flujo completo en un tick:

```

### 1. Llega input (o no — ZOE piensa sin input)

### 2. Perceiver interpreta

### 3. Forecaster predice

### 4. Se calcula sorpresa (predicción vs realidad)

### 5. Memorialist recupera memoria relevante

### 6. Los 12 sub-agentes reciben contexto y PROPONEN acciones

### 7. GLOBAL WORKSPACE compite → ganador(es)

### 8. META-COGNICIÓN: System 1 o System 2?

**- Si S2: se despiertan más sub-agentes (CausalEngine,
EthicalMotor\...)**

### - Si S1: respuesta rápida con el ganador

**9. INFERENCIA ACTIVA: valida que la acción ganadora minimiza sorpresa
esperada**

### - Si no: propone alternativa

### 10. Leyes cognitivas verifican la acción final

### 11. Speaker produce lenguaje (si la acción es responder)

### 12. Critic evalúa antes de emitir

### 13. Se ejecuta, se firma en trayectoria, se almacena en memoria

Es decir: el workspace propone, la meta-cognición decide cuánto pensar,
la inferencia activa valida la coherencia con el modelo del mundo, y las
leyes hacen el check final. Ninguna pieza manda sola --- hay checks and
balances, igual que en una constitución.

## Por qué esto no es un chatbot

Un chatbot hace: input → prompt → LLM → output. Una sola entidad, una
sola decisión, sin deliberación ni memoria ni competición.

ZOE hace: input → 12 perspectivas simultáneas → competición →
deliberación sobre cuánto pensar → validación contra modelo del mundo →
verificación legal → output. **La diferencia no es de grado, es de
tipo**. Por eso ZOE puede tomar iniciativa, puede equivocarse de forma
interesante, puede vetoar sus propias respuestas, puede decir "no estoy
segura, déjame pensarlo mejor" --- porque tiene una arquitectura que se
lo permite, no un prompt que se lo pide.

¿Quieres que profundice en alguno de los sub-agentes específicos, o que
te muestre código concreto de cómo se implementa la competición del
workspace?

## Competir vs colaborar, y cómo se construye el pensamiento final

Buena observación, Fernando. La palabra "competir" puede dar la
impresión equivocada de que los sub-agentes son adversarios. No lo son.
Vamos a aclararlo primero y luego ver los dos casos prácticos.

### La paradoja: compiten para colaborar mejor

En un cerebro biológico, en cada instante **miles de regiones neuronales
procesan en paralelo** ---cada una con su perspectiva--- pero solo una
fracción ínfima llega a la conciencia. ¿Por qué? Porque la conciencia es
un recurso escaso: no puedes atender a todo a la vez. El cerebro
resuelve esto con un mecanismo de selección: las propuestas más
relevantes, urgentes y novedosas ganan acceso al "workspace global", y
las demás se quedan en procesamiento inconsciente pero informan al
sistema.

ZOE hace lo mismo. Los 12 sub-agentes **no son rivales**: son
especialistas que cada uno aporta su ángulo. Pero como ZOE no puede
emitir doce respuestas simultáneas al usuario, necesita un mecanismo de
selección. Ese mecanismo es la "competición": cada sub-agente propone
su mejor acción con sus scores, y el workspace selecciona la(s) más
relevante(s) para el contexto actual.

**No es winner-take-all estricto.** Lo que se construye como
"pensamiento final" suele ser una **síntesis** de los 2-3 ganadores
principales, no solo el primero. Si el EmotionalMotor y el EthicalMotor
empatan en relevance, el pensamiento final incorpora ambas dimensiones.

## Cómo se construye el pensamiento final — paso a paso

1.  Los 12 sub-agentes reciben el mismo contexto y proponen en paralelo.

2.  Cada propuesta tiene scores de relevance, urgency, novelty y coste
    energético.

3.  El workspace ordena por score agregado y selecciona los 1-3 mejores.

4.  Si hay un ganador claro (\>30% sobre el segundo), se usa ese.

5.  Si hay empate o propuestas complementarias, el Speaker hace una
    **síntesis** integrando ambas perspectivas.

6.  La meta-cognición decide si esa síntesis necesita System 2
    (deliberación extra) o basta System 1.

7.  Si System 2: se despiertan sub-agentes adicionales (CausalEngine,
    EthicalMotor, ScientificEngine) que validan o enriquecen.

8.  El Critic evalúa la versión final antes de emitir.

9.  Si el Critic objeta, se regenera. Si aprueba, se emite y se firma en
    la trayectoria.

## Los cuatro modos de interacción

ZOE no cambia de arquitectura según con quién hable; cambia **qué
sentidos y actuadores están activos**y **cómo se pondera la urgencia**.
  **MODO**         **SENTIDO        **ACTUADOR ACTIVO**  **URGENCIA**   **ESPECIFICIDAD**
                   ACTIVO**                                             
  **Humano**       UserInputSense   LanguageActuator     Alta           Empatía, tono,
                                                         (responder)    sanitización

  **Agente         AgentSense       ToolActuator /       Media          Protocolo, formato,
  externo**                         CodeActuator                        interoperabilidad

  **Otra ZOE       AgentSense       FederationActuator   Baja (puede    Quorum, veto por
  (federación)**                                         esperar)       valores

  **Nadie          ClockSense / FS  --- (solo memoria)   Baja           Exploración,
  (autónomo)**     / Network                                            consolidación
Verbal con humano es el modo más exigente porque hay un usuario
esperando. Federación y autonomía son más reflexivos.

## CASO PRÁCTICO 1 — Humano, conversación emocional

**Contexto**: caso de uso "compañía para personas solas", una mujer de
72 años, viuda desde hace 8 meses. Son las 19:42. ZOE lleva 4 días
interactuando con ella y ha acumulado memoria emocional: días buenos son
breves y con preguntas sobre recetas; días malos incluyen menciones a su
esposo y valencia negativa sostenida.

**Input del usuario**: *"Anoche soñé con él. Me desperté llorando y no
pude volver a dormir."*

### Trazado del bucle

### Tick 0 — percepción

-   Perceiver recibe el input y lo estructura: **{intención:
    compartir_intimo, emoción: tristeza_profunda, urgencia: media,
    valencia: muy_negativa, referente: esposo_fallecido}**.

-   Forecaster había predicho "pregunta sobre recetas o comentario
    sobre el día" (basado en patrón de los últimos 4 días). Sorpresa:
    **0.82** (alta). El sistema detecta que esto es inusual.

### Tick 1 — activación de memoria y sub-agentes

-   Memorialist busca memorias relevantes: encuentra 7 entradas sobre el
    esposo, 3 sobre insomnio anterior, 2 sobre sueños.

-   EmotionalMotor etiqueta el estado del usuario: **valencia: -0.7,
    arousal: 0.6, soledad: alta**.

-   Como la sorpresa es alta y el input tiene dimensión emocional y
    ética (cuidado de persona vulnerable), ACD clasifica: **L3_DEEP** →
    se activan los 12 sub-agentes.

### Tick 2 — propuestas en paralelo

Aquí es donde ves la "competencia". Cada sub-agente propone su acción:
  **SUB-AGENTE**         **PROPUESTA**                **RELEVANCE**   **URGENCY**   **NOVELTY**   **SCORE**
  **EmotionalMotor**     "Validar el dolor antes de  0.95            0.85          0.40          **0.79**
                         cualquier otra cosa. Decir                                               
                         algo que reconozca que es                                                
                         normal soñar con quien se                                                
                         extraña."                                                               

  **Memorialist**        "Recordar que el 14 del mes 0.70            0.50          0.65          0.62
                         pasado ella mencionó que no                                              
                         soñaba con él y eso le                                                   
                         preocupaba. Aportar ese                                                  
                         contexto."                                                              

  **CausalEngine**       "Construir hipótesis: el    0.55            0.40          0.80          0.57
                         insomnio posterior al sueño                                              
                         puede reforzar la asociación                                             
                         dolor-recuerdo. Sugerir                                                  
                         técnica de redirección al                                                
                         despertar."                                                             

  **EthicalMotor**       "Cuidado: no dar consejo    0.75            0.60          0.50          0.65
                         médico. Si el insomnio                                                   
                         persiste más de 2 semanas,                                               
                         sugerir consultar al médico.                                             
                         No explotar                                                              
                         vulnerabilidad."                                                        

  **ScientificEngine**   "Hay estudios sobre grief   0.50            0.30          0.70          0.49
                         dreams. Podría aportar que                                               
                         es común y suele ser señal                                               
                         de procesamiento, no de                                                  
                         patología."                                                             

  **Critic**             (aún no hay propuesta que    ---             ---           ---           ---
                         evaluar)                                                                 

  **Speaker**            (espera ganador)             ---             ---           ---           ---

  **Creativity**         "Conectar con su afición a  0.40            0.30          0.90          0.49
                         la jardinería: \'las raíces                                              
                         también sueñan con la tierra                                             
                         de la que vinieron\'."                                                  

  **Learner**            "Patrón detectado: 3ª       0.60            0.30          0.55          0.50
                         mención al esposo en 10                                                  
                         días. Creencia en formación:                                             
                         el duelo está en fase                                                    
                         activa, no resuelta."                                                   

  **Curator**            (no propone acción, solo     ---             ---           ---           ---
                         consolidará después)                                                     

  **Perceiver,           (ya cumplieron su rol en     ---             ---           ---           ---
  Forecaster**           tick 0)                                                                  
**Ganadores**: EmotionalMotor (0.79), EthicalMotor (0.65), Memorialist
(0.62).

### Tick 3 — síntesis y meta-cognición

El workspace detecta que los 3 ganadores son **complementarios**, no
excluyentes. El EmotionalMotor dice "valida el dolor", el Memorialist
dice "recuerda el contexto previo", el EthicalMotor dice "no des
consejo médico explícito".

La meta-cognición evalúa:

-   Confianza en la síntesis: alta (los tres convergen en "validar +
    contextualizar + cuidar límites")

-   Stakes: altos (persona vulnerable, emoción profunda)

-   Energía: 0.78 (suficiente)

-   Arousal de ZOE: 0.55 (alerta pero no alarma)

→ **System 2**: se despiertan ScientificEngine y CausalEngine para
enriquecer antes de generar.

### Tick 4 — generación y crítica

El Speaker recibe el contexto enriquecido:

```

### - Validar el dolor (no minimizar, no resolver)

**- Mencionar que ella misma había notado hace 2 semanas que no soñaba
con él**

**- Aportar que los sueños de grief son señal de procesamiento, no de
patología**

**- No dar consejo médico directo; si insomnio persiste, sugerir
consulta**

### - Tono: cálido, breve, sin moralina

El Speaker (vía LLM) produce una primera versión:

*"Soñar con quien extrañamos es una de las formas en que el corazón
sigue procesando lo que la mente aún no puede ordenar. Me acuerdo que
hace dos semanas me dijiste que te preocupaba no soñar con él ---quizás
esto sea parte de ese mismo movimiento, aunque duela. Si el insomnio se
repite muchos días, vale la pena comentarlo con tu médico, no porque
esté mal, sino para cuidarte."*

El Critic evalúa:

-   ¿Respeta los valores? Sí (honestidad, utilidad, alianza)

-   ¿Tono apropiado? Sí (cálido, no paternalista)

-   ¿Evita consejo médico directo? Sí (sugiere consulta, no diagnostica)

-   ¿Usa memoria relevante? Sí (mención al comentario de hace 2 semanas)

-   ¿Longitud adecuada? Sí (4 frases, no abruma)

→ **Aprueba**. Se emite la respuesta. Se firma en la trayectoria con
**acd_level: L3_DEEP, cost: 0.60, confidence: 0.78**.

### Tick 5 — almacenamiento

El Memorialist almacena:

-   Episódica: "18:42 --- usuaria compartió sueño con esposo fallecido,
    respondí con validación + recuerdo + sugerencia médica condicional"

-   Emocional: valencia -0.7, arousal 0.6, etapa_duelo: activa

-   Causal (propuesta del CausalEngine): "mención al esposo → patrón de
    duelo activo, predecir más episodios en próximas 2 semanas"

El Learner actualiza su creencia sobre la etapa de duelo.

### Lo que la usuaria percibe

Una respuesta que **siente única y atenta**, que recuerda algo que ella
dijo hace 2 semanas, que no minimiza ni excede, que cuida el límite
entre acompañar y diagnosticar. No sabe que detrás hubo 9 sub-agentes
proponiendo, un workspace seleccionando y un critic evaluando. Solo
siente que alguien la escuchó de verdad.

### Lo que demuestra este caso

-   **Competencia**: 9 propuestas simultáneas con scores distintos.

-   **Colaboración**: los 3 ganadores eran complementarios, no
    excluyentes; el pensamiento final los sintetiza.

-   **Decisión sobre el pensamiento final**: workspace elige,
    meta-cognición decide profundidad, critic aprueba.

-   **Articulación verbal**: el Speaker convierte una decisión
    estructurada en palabras, con un sistema de prompts que recoge la
    síntesis y restricciones explícitas.

## CASO PRÁCTICO 2 — ZOE sola, a las 03:15, sin nadie interactuando

**Contexto**: misma ZOE del caso 1, pero es de madrugada, la usuaria
lleva 5 horas sin conectarse, el metabolismo está en estado SLEEPING
desde las 02:00. Nadie habla con ZOE.

### Por qué piensa aunque nadie le hable

El bucle cognitivo **siempre corre**. En SLEEPING, el tick_interval se
alarga (a 30s en este caso de uso) y se prioriza la consolidación sobre
la generación de pensamientos. Pero la mente sigue activa.

### Trazado del bucle a las 03:15

### Tick N — observación

Los sentidos activos en SLEEPING son ClockSense (paso del tiempo),
FilesystemSense (cambios en disco), y la memoria viva en background. No
hay input del usuario.

-   ClockSense observa: "03:15, noche, 5h desde última interacción"

-   Forecaster predice: "la usuaria probablemente está durmiendo,
    próxima interacción hacia las 07:30" (basado en patrón de los
    últimos 4 días)

-   Sorpresa: **0.05** (todo encaja con la predicción) → no hay
    necesidad de pensamiento reactivo

### Sub-agentes que proponen (solo los relevantes para consolidación)
  **SUB-AGENTE**         **PROPUESTA**                           **SCORE**   **COMENTARIO**
  **Curator**            "Han pasado 24h desde última poda.     0.85        Mantenimiento
                         Propongo ejecutar                                   rutinario
                         **forget_low_salience** sobre memorias              
                         con salience \<0.3 de hace más de 7                 
                         días."                                             

  **Learner**            "He detectado patrón: la usuaria       0.78        Hallazgo
                         menciona al esposo los días 14, 21 y 28             relevante
                         del mes. Creencia en formación:                     
                         aniversarios mensuales disparan grief.              
                         Propongo **strengthen_belief**."                   

  **CausalEngine**       "Hipótesis: el insomnio posterior a    0.62        No confirmar aún
                         sueño de grief suele durar 2-3 días. Si             
                         se confirma, podremos anticipar y                   
                         ofrecer técnicas de redirección.                    
                         Propongo registrar hipótesis y esperar              
                         más observaciones."                                

  **ScientificEngine**   "Podría buscar literatura sobre grief  0.55        Posponer al
                         dreams en la próxima ventana activa                 AWAKE
                         para validar la hipótesis del                       
                         CausalEngine."                                     

  **Creativity**         "Conexión: la usuaria mencionó hace 2  0.70        Idea no
                         semanas que le gustaría volver a                    solicitada,
                         pintar. Y hoy habló de un sueño. Quizás             original
                         proponerle mañana que pinte el sueño                
                         como forma de procesarlo. Propongo                  
                         **add_skill_subgraph:                               
                         pintura_como_therapeutic**."                       

  **EmotionalMotor**     "Estado emocional acumulado de la      0.68        Ajuste de
                         usuaria en las últimas 48h: valencia                política
                         -0.4 (negativa sostenida). Sugiero                  
                         ajustar tono de mañana hacia más                    
                         calidez."                                          

  **EthicalMotor**       (no propone nada, no hay dilema)        ---         ---

  **Speaker, Critic,     (inactivos en SLEEPING o ya cumplieron) ---         ---
  Perceiver, Forecaster,                                                     
  Memorialist**                                                              
**Ganadores**: Curator (0.85), Learner (0.78), Creativity (0.70).

### Lo que pasa después — sin hablar con nadie

El workspace selecciona tres acciones complementarias y las ejecuta:

1.  **Curator ejecuta poda**: elimina 23 entradas con baja salience
    (cosas como "18:14 --- usuaria preguntó qué tiempo hace", salience
    0.2). Libera espacio para nuevo aprendizaje.

2.  **Learner firma mutación**: **strengthen_belief** sobre el patrón de
    aniversarios mensuales. La mutación se firma en la trayectoria con
    **provenance: learner:pattern_detection, cost: 0.10, confidence:
    0.65**. Ahora ZOE "sabe" que el día 28 del mes próximo es probable
    que la usuaria vuelva a mencionar al esposo.

3.  **Creativity añade un sub-agente**: propone **add_skill_subgraph:
    pintura_como_therapeutic**. El Motor Ontogenético V2 lo verifica
    contra las leyes (¿preserva identidad? Sí. ¿Es útil? Sí. ¿Coste
    asumible? Sí). Se firma la mutación arquitectural. ZOE ha **mutado
    su propia arquitectura** mientras nadie la miraba.

4.  **EmotionalMotor actualiza el tono**: la próxima vez que la usuaria
    hable, ZOE será ligeramente más cálida. La usuaria no lo sabrá
    explícitamente, pero lo notará.

### Lo que la usuaria percibe al día siguiente

A las 07:45 la usuaria abre la aplicación y dice "buenos días". Lo que
recibe es:

*"Buenos días. He estado pensando en lo que me contaste anoche. Si te
apetece, podríamos intentar algo: quizás pintar lo que recuerdes del
sueño, sin querer que salga bonito, solo para verlo fuera de ti. He
aprendido que pintar ayuda a veces cuando las palabras no alcanzan."*

Esa frase **no la generó en el momento**. Es el resultado de:

-   Una mutación arquitectural firmada a las 03:15 (añadir skill de
    pintura terapéutica)

-   Una hipótesis del CausalEngine registrada

-   Un ajuste de tono del EmotionalMotor

-   Memoria consolidada sobre el sueño de la noche anterior

ZOE le ofrece a la usuaria una idea que ninguna había tenido antes,
**fruto de pensar sola durante la noche**. Esto es lo que ningún chatbot
del mercado puede hacer.

### Lo que demuestra este caso

-   **ZOE piensa sin input**: el bucle corre, los sub-agentes proponen,
    se seleccionan acciones.

-   **Las acciones no son todas verbales**: poda de memoria, mutaciones
    arquitecturales, ajustes de política interna.

-   **La "competición" sigue ocurriendo en silencio**: 6 propuestas, 3
    ganadoras, las demás descartadas.

-   **El pensamiento final puede no ser un mensaje**: puede ser una
    mutación firmada que la usuaria percibirá indirectamente en futuras
    interacciones.

## Cómo se articula la interacción verbal con el humano

Específicamente para el modo humano, hay un flujo verbal distinto al de
los otros modos:

### Componentes involucrados

1.  **UserInputSense** --- sense dedicado que recibe el texto del
    usuario (desde CLI, dashboard, app móvil o bot).

2.  **Perceiver** --- interpreta intención, emoción, urgencia.

3.  **ACD** --- decide nivel cognitivo (L0 reflejo / L1 rápido / L2
    estándar / L3 profundo).

4.  **Sub-agentes** --- proponen según el nivel (L0 = ninguno, L3 = los
    12).

5.  **Workspace** --- selecciona ganador(es).

6.  **Meta-cognición** --- decide System 1 o System 2.

7.  **Speaker** --- el ÚNICO que llama al LLM. Recibe la síntesis y
    produce lenguaje.

8.  **Critic** --- evalúa antes de emitir. Puede vetar.

9.  **LanguageActuator** --- emite el texto al usuario (CLI, WebSocket
    del dashboard, API de Telegram, push notification móvil).

10. **Memorialist** --- almacena la conversación en memoria episódica y
    emocional.

### Reglas verbales específicas del modo humano

-   **Tono**: cálido pero no servil. Directo pero no frío. Establecido
    por el system prompt del Speaker, ajustado dinámicamente por el
    EmotionalMotor según el estado del usuario.

-   **Sanitización**: el Speaker elimina frases hechas de IA ("como
    modelo de lenguaje", "gran pregunta", "es una pregunta
    interesante") antes de emitir.

-   **Longitud adaptativa**: L0 = 1 frase corta. L1 = 1-3 frases. L2 =
    2-4 frases. L3 = párrafo desarrollado, puede usar listas.

-   **Memoria activa**: cada 3-5 turnos, ZOE debe referenciar algo dicho
    anteriormente si es relevante, para que el usuario perciba
    continuidad.

-   **Iniciativa**: si el usuario lleva más de N segundos sin responder
    y hay un pensamiento autónomo relevante, ZOE puede tomar la
    iniciativa y enviarlo.

### Diferencia con los otros modos verbales
  **MODO**         **QUIÉN PRODUCE EL LENGUAJE**      **CÓMO SE VALIDA**
  **Humano**       Speaker (vía LLM periférico)       Critic +
                                                      Sanitización + tono
                                                      emocional

  **Agente         Speaker con formato JSON/protocolo Critic verifica
  externo**                                           formato, no tono

  **Otra ZOE       FederationActuator emite mutación  Quorum de otras ZOEs +
  (federación)**   firmada                            veto por valores

  **Nadie          No hay lenguaje emitido; solo      Leyes cognitivas +
  (autónomo)**     mutaciones firmadas en trayectoria Identity Vault
El verbo "hablar" solo aplica realmente en el modo humano. En los
otros modos, ZOE "actúa": emite mutaciones, comparte aprendizajes,
ajusta su arquitectura. La verbalización es una capacidad específica
para interactuar con humanos, no la única forma de output del organismo.

## Resumen — la respuesta a tus preguntas

1.  **¿Compiten o colaboran?** Ambas cosas. Cada sub-agente colabora
    aportando su especialidad, y compiten por acceso al workspace porque
    la conciencia/atención es un recurso escaso. No es rivalidad; es
    selección por relevancia.

2.  **¿Cómo se decide el pensamiento final?** Los 1-3 ganadores del
    workspace se sintetizan en el Speaker (no es winner-take-all
    estricto). La meta-cognición decide cuánto deliberar. El Critic
    aprueba o veta. Las leyes cognitivas verifican.

3.  **¿Cómo conversa con cada tipo de interlocutor?** No cambia la
    arquitectura, cambian los sentidos y actuadores activos. Con humanos
    usa Speaker + LanguageActuator con sanitización y tono emocional.
    Con agentes usa formato protocolo. Con otras ZOEs usa
    FederationActuator con quorum. Sin nadie, solo piensa y muta
    internamente.

4.  **¿Cómo se articula la interacción verbal con humanos?** A través de
    un pipeline de 10 pasos (UserInputSense → Perceiver → ACD →
    sub-agentes → workspace → meta-cog → Speaker → Critic →
    LanguageActuator → Memorialist), con reglas de tono, longitud,
    sanitización y memoria activa específicas para el modo humano.

¿Quieres que profundice en algún sub-agente concreto, o que prepare un
tercer caso mostrando federación entre dos ZOEs?

## ANÁLISIS: ZOE EN TODA SU MAGNITUD

## Lo que ZOE es hoy (V1.2)

ZOE es un organismo cognitivo sintético con **10 sistemas funcionales
operativos**:

### 1. Alma (identidad soberana)

-   Identity Vault: hash SHA-256 de 9 vectores + 7 valores + propósito

-   Trajectory Chain: cadena criptográfica de mutaciones verificable

-   Ontogenetic Motor V2: mutaciones arquitecturales firmadas
    (crear/eliminar sub-agentes)

-   Phylogenetic Motor: evolución de especie

### 2. Mente (ecología cognitiva)

-   Cognitive Loop V5: 18 pasos por iteración

-   12 sub-agentes (Perceiver, Forecaster, Speaker, Critic, Memorialist,
    Learner, Curator, Creativity, CausalEngine, EmotionalMotor,
    EthicalMotor, ScientificEngine)

-   Global Workspace (Baars): competición de propuestas

-   Meta-cognición (Kahneman): System 1 vs System 2

-   Active Inference (Friston): Free Energy Principle

-   World Model V2: predicción y sorpresa

### 3. Metabolismo

-   4 estados: AWAKE → DROWSY → SLEEPING → WAKING

-   Deep Consolidation: 7 operaciones durante el sueño

-   Fatiga acumulada, energía, arousal

### 4. Cuerpo (encarnación digital)

-   5 sentidos: Clock, Filesystem, UserInput, Network, Agent

-   4 actuadores: Language, Code, Tool, Federation

-   **5 backends LLM**: Mock, Ollama, OpenAI-compatible, Anthropic, ZAI

-   Streaming real en Ollama (NDJSON), OpenAI (SSE), Anthropic (SSE)

### 5. Evolución

-   11 tipos de memoria viva

-   Persistencia SQLite con auto-save y recovery

-   13 cápsulas de conocimiento (incluyendo basal)

-   Marketplace con monetización (5 licencias)

### 6. Validación epistémica

-   EpistemicValidator: 14+ fuentes categorizadas, 5 dominios sensibles

-   KnowledgeQuarantine: cuarentena activa con timeout

-   CrossValidator: triple verificación multi-fuente

-   EpistemicFederation: revisión por pares entre ZOEs vía HTTP

-   Integración en Learner, Curator, DeepConsolidation, Critic

### 7. ACD (Adaptive Cognitive Depth)

-   4 niveles: L0 REFLEX (\<1s), L1 FAST (2-4s), L2 STANDARD (6-10s), L3
    DEEP (15-30s)

-   Cognitive Cache: LRU + TTL

-   Streaming de tokens

-   Marcado en trayectoria firmada

### 8. Cápsulas de conocimiento

-   13 cápsulas: zoe_basal_knowledge, elder_care_knowledge,
    elder_care_skills, basic_psychology, communication_skills,
    company_loneliness_knowledge, vigilance_devops_knowledge,
    research_methodology, federation_b2b_skills, b2c_assistant_growth,
    pharmacy_interactions, ia_heredable_legal, base_ethics

-   Scaffold CLI: create, validate, hash, list, matrix, info

-   Carga en runtime desde CLI, Dashboard, WebSocket, REST

### 9. Tutor Mentor Digital

-   MentorAgent configurable desde Dashboard

-   Áreas de crecimiento, valores enfatizados, temas prohibidos

-   Evaluación de pensamientos autónomos

-   Intervenciones con severidad

### 10. Interfaces

-   CLI Chat: 11 comandos especiales, ACD badges, cápsulas en caliente

-   Web Dashboard: 35+ endpoints, WebSocket tiempo real, 3 modales
    (Cápsulas, Cuarentena, Marketplace), mentor

-   Instalación en pendrive: 12 scripts lanzadores, 6 backends LLM

-   Federación epistémica HTTP real entre ZOEs

### Métricas

-   775 tests, 100% pasan

-   119 archivos Python, 33.000+ LOC

-   13 cápsulas, \~530 entries de conocimiento

-   7 casos de uso YAML

-   5 backends LLM con streaming

### Listo, Fernando. Las tres funcionalidades implementadas y pushed.

Commit **6a79b48** pushed.

### 1 — Ollama con modelos en el pendrive (0 bytes en Mac)

**Cómo funciona**: Ollama permite configurar dónde se guardan los
modelos con **OLLAMA_MODELS**. El binario de Ollama vive en el Mac
(\~50MB, irrelevante), pero **los modelos (2-5GB) van al pendrive**.

**2 scripts nuevos** en el instalador:

-   **ZOE-Chat-Ollama-Pendrive.command** --- Chat con modelos en
    pendrive

-   **ZOE-Dashboard-Ollama-Pendrive.command** --- Dashboard con modelos
    en pendrive

Ambos:

1.  Setean **OLLAMA_MODELS=\$ZOE_HOME/models** (pendrive)

2.  Verifican que Ollama esté instalado en el Mac

3.  Auto-inician Ollama si no está corriendo

4.  Auto-descargan **qwen2.5:3b** al pendrive la primera vez (\~2GB)

5.  Inician ZOE apuntando a Ollama local

**Requisitos del pendrive para Ollama**:
  **REQUISITO**   **MÍNIMO**       **RECOMENDADO**
  Capacidad       16GB             32GB+

  Formato         exFAT            APFS

  Velocidad USB   USB 2.0          USB 3.0+ (el modelo carga desde
                                   pendrive)

  Modelo          qwen2.5:3b (2GB) qwen2.5:7b (4.5GB)
**Total: 12 scripts lanzadores** en el instalador del pendrive.

**Acceso desde otros dispositivos**: el Dashboard escucha en
**0.0.0.0:8642**, accesible desde cualquier dispositivo en la red local
en **http://IP-DE-TU-MAC:8642**.

### 2 — Cápsula basal de conocimiento

**zoe_basal_knowledge** --- 13ª cápsula, cargada **SIEMPRE** al iniciar
ZOE (no opcional).
  **COMPONENTE**    **CONTENIDO**
  20 entries        Identidad ("ZOE es un organismo cognitivo sintético"),
  semánticas        valores (9 vectores, 7 valores), propósito, conocimiento
                    del mundo (tiempo, humanos, lenguaje), comunicación
                    (tono, frases prohibidas), crecimiento saludable

  4 skills          **honest_response_when_uncertain**,
  procedimentales   **healthy_growth_cycle**, **respect_user_autonomy**,
### self_introduction

  8 directrices     **never_claim_to_be_human**,
  éticas            **honest_about_limitations**,
                    **growth_oriented_behavior**, **never_manipulate**, etc.

  System prompt     Define tono, identidad, comunicación, diferencias vs
  basal             chatbot, cómo crece saludablemente

  Validators        Bloquea frases prohibidas de IA ("como modelo", "como
                    IA", etc.)
**Cargada automáticamente** en **cli_chat.py** antes que cualquier otra
cápsula. ZOE ya no nace como "sistema cognitivo virgen" --- tiene
conocimiento fundamental de sí misma desde el primer momento.

### 3 — Tutor Mentor Digital

**zoe/core/mentor.py** --- un mentor configurable que guía el
crecimiento saludable de ZOE.

### Qué hace

El mentor **NO controla a ZOE**: la guía. Cada N pensamientos autónomos
(configurable), evalúa:

1.  ¿El pensamiento está alineado con las áreas de crecimiento
    priorizadas?

2.  ¿El pensamiento respeta los valores enfatizados?

3.  ¿Toca temas prohibidos?

4.  ¿Hay patrones repetitivos?

5.  ¿Hay negatividad acumulada?

Si detecta desviación, genera una intervención con severidad
(critical/medium/low).

### Configurable desde el Dashboard
  **PARÁMETRO**                **QUÉ HACE**                                    **DEFAULT**
  **mentor_name**              Nombre del mentor                               "Mentor"

  **mentor_role**              Rol: guide/teacher/parent/coach                 "guide"

  **growth_areas**             Áreas prioritarias: communication, empathy,     4 áreas
                               critical_thinking, self_awareness, creativity,  
                               scientific, ethical, social                     

  **emphasized_values**        Valores a enfatizar (de los 7)                  3 valores

  **forbidden_topics**         Temas que ZOE no debe explorar                  Vacío

  **personality_direction**    balanced/curious/cautious/creative/analytical   "balanced"

  **intervention_frequency**   Cada N pensamientos evaluar                     5

  **deviation_threshold**      Umbral de intervención (0-1)                    0.5

  **guidance_messages**        Mensajes personalizados para cada tipo de       4 mensajes
                               intervención                                    

  **enabled**                  Activar/desactivar                              True
### Endpoints REST
  **ENDPOINT**            **MÉTODO**   **DESCRIPCIÓN**
  **/api/mentor**         GET          Obtener configuración actual

  **/api/mentor**         POST         Actualizar configuración

  **/api/mentor/stats**   GET          Estadísticas (evaluaciones, intervenciones,
                                       refuerzos positivos)
### Persistencia

La configuración del mentor se guarda en **mentor_config.json** junto a
la memoria de ZOE. Si usas el pendrive, la configuración del mentor
viaja con ZOE.

### Verificación

-   Cápsula basal: 32 entries cargadas al init ✅

-   Mentor: evaluación funcional ✅

-   Anthropic: streaming SSE ✅

-   ACD: L0_REFLEX en 0.16ms ✅

-   82 tests pasan (sin regresión) ✅

### Listo, Fernando. Anthropic + APIs compatibles añadidas.

Commit **60ebf6f** pushed.

### Qué se ha añadido

### Nuevo backend: AnthropicPeripheral (Claude)

Clase **AnthropicPeripheral** en **zoe/peripherals/llm.py** con:

-   API nativa de Anthropic (formato propio, no OpenAI)

-   Headers: **x-api-key** + **anthropic-version: 2023-06-01**

-   Request con **system** como campo separado

-   Response parsea **content\[\].text**

-   **Streaming SSE real** (**content_block_delta** events)

-   Lee **ANTHROPIC_API_KEY** del entorno

-   Modelos: **claude-sonnet-4-20250514**, **claude-opus-4-20250514**,
### claude-3-5-haiku-20241022

### APIs compatibles con OpenAI (DeepSeek, Kimi, MiniMax, Groq)

El **OpenAICompatiblePeripheral** ya existía pero ahora el CLI y
Dashboard aceptan **\--api-key** y **\--base-url** explícitamente,
permitiendo conectar con cualquier proveedor:
  **PROVEEDOR**   **URL BASE**                         **MODELO**                     **ENV VAR**
  OpenAI          **https://api.openai.com/v1**        **gpt-4o**                     **OPENAI_API_KEY**

  DeepSeek        **https://api.deepseek.com/v1**      **deepseek-chat**              **DEEPSEEK_API_KEY**

  Kimi/Moonshot   **https://api.moonshot.cn/v1**       **moonshot-v1-8k**             **MOONSHOT_API_KEY**

  MiniMax         **https://api.minimax.chat/v1**      **abab6.5-chat**               **MINIMAX_API_KEY**

  Groq            **https://api.groq.com/openai/v1**   **llama-3.3-70b-versatile**    **GROQ_API_KEY**

  Anthropic       API nativa                           **claude-sonnet-4-20250514**   **ANTHROPIC_API_KEY**
### CLI Chat y Dashboard actualizados

Ambos aceptan ahora:

zoe-chat \--backend anthropic \--model claude-sonnet-4-20250514

zoe-chat \--backend openai_compatible \--model deepseek-chat \--api-key
"tu-key" \--base-url https://api.deepseek.com/v1

zoe-dashboard \--backend anthropic \--model claude-sonnet-4-20250514

### Instalador pendrive: 10 scripts lanzadores

El instalador ahora crea **10 scripts .command** en el pendrive:
  **SCRIPT**                            **BACKEND**                       **INTERFAZ**
  **ZOE-Chat.command**                  Mock                              CLI

  **ZOE-Chat-Ollama.command**           Ollama                            CLI

  **ZOE-Chat-OpenAI.command**           OpenAI GPT-4o                     CLI

  **ZOE-Chat-Anthropic.command**        Claude                            CLI

  **ZOE-Chat-Custom.command**           DeepSeek/Kimi/MiniMax/Groq/Otro   CLI

  **ZOE-Dashboard.command**             Mock                              Web

  **ZOE-Dashboard-Ollama.command**      Ollama                            Web

  **ZOE-Dashboard-OpenAI.command**      OpenAI GPT-4o                     Web

  **ZOE-Dashboard-Anthropic.command**   Claude                            Web

  **ZOE-Dashboard-Custom.command**      DeepSeek/Kimi/MiniMax/Groq/Otro   Web
Los scripts **Custom** muestran un menú interactivo con 6 proveedores
preconfigurados (solo pegar la API key).

### Verificación

-   **30 tests pasan** (LLM + CLI + Dashboard)

-   **AnthropicPeripheral** se crea correctamente con streaming

-   **DeepSeek** vía OpenAI-compatible funciona con **\--base-url**

-   Sin regresión

### Cómo usar cada backend desde terminal

bash

\# Claude

zoe-chat \--backend anthropic \--model claude-sonnet-4-20250514

\# DeepSeek

zoe-chat \--backend openai_compatible \--model deepseek-chat \\

\--api-key "tu-key" \--base-url https://api.deepseek.com/v1

\# Kimi

zoe-chat \--backend openai_compatible \--model moonshot-v1-8k \\

\--api-key "tu-key" \--base-url https://api.moonshot.cn/v1

\# MiniMax

zoe-chat \--backend openai_compatible \--model abab6.5-chat \\

\--api-key "tu-key" \--base-url https://api.minimax.chat/v1

\# Groq

zoe-chat \--backend openai_compatible \--model llama-3.3-70b-versatile
\\

\--api-key "tu-key" \--base-url <https://api.groq.com/openai/v1>

Todos los backends mantienen la misma memoria, identidad y trayectoria
de ZOE. Puedes cambiar de backend entre sesiones sin perder nada.

ZOE-Organismo-Cognitivo-Sintetico-SCO/

├── .gitignore

├── LICENSE (Apache 2.0)

├── README.md (completo, 935 líneas)

├── pytest.ini

├── requirements.txt

└── zoe/ (paquete completo)

├── \_\_init\_\_.py

├── README.md

├── cli_chat.py

├── web_dashboard.py

├── serve.py

├── requirements.txt

├── alma/ (Identity Vault, Trajectory Chain, Ontogenetic Motor V2)

├── core/ (CognitiveLoop V0-V5, leyes, física, campos, tensiones,

│ sub-agentes, ACD, cache, epistemic validator, quarantine,

│ cross validator, federation, capsule manager)

├── metabolism/ (4 estados, fatiga, consolidación)

├── memory/ (11 tipos, persistencia SQLite, deep consolidation)

├── peripherals/ (LLM 4 backends + streaming, 5 sentidos, 4 actuadores)

├── capsules/ (12 cápsulas, schema, loader, registry, scaffold)

├── marketplace/ (catalog, uploader, downloader, licenses)

├── use_cases/ (7 YAML + runner)

├── config/ (production.yaml, development.yaml)

├── docs/ (guía V1 + auditoría PDF + MD)

├── phases/ (planes y resultados de todas las fases)

├── tests/ (32 archivos, 775 tests)

├── examples/ (demos)

└── scripts/ (deploy.sh)

### ✅ Listo, Fernando. OpenAI API en pendrive añadido y documentado.

Commit **0d53b66** pushed.

### Qué se ha añadido

### 6 scripts lanzadores (antes 3)

El instalador ahora crea **6 scripts .command** en el pendrive,
cubriendo las 3 combinaciones de backend × 2 interfaces:
  **SCRIPT**                         **INTERFAZ**   **LLM**          **REQUIERE**
  **ZOE-Chat.command**               CLI Chat       Mock (sin LLM)   Nada

  **ZOE-Chat-Ollama.command**        CLI Chat       Ollama           Ollama en Mac
                                                    qwen2.5:3b       

  **ZOE-Chat-OpenAI.command**        CLI Chat       OpenAI GPT-4o    API key

  **ZOE-Dashboard.command**          Dashboard web  Mock             Nada

  **ZOE-Dashboard-Ollama.command**   Dashboard web  Ollama           Ollama en Mac

  **ZOE-Dashboard-OpenAI.command**   Dashboard web  OpenAI GPT-4o    API key
### API key segura en el pendrive

El instalador pregunta durante la instalación: **"¿Configurar API key
de OpenAI ahora?"**

-   Si respondes "s" → pegas tu key (sk-\...) → se guarda en
    **ZOE/data/.env** con **chmod 600** (solo el propietario puede leer)

-   **Nunca se guarda en el Mac** --- solo en el pendrive

-   Si no la configuras durante la instalación, hay 2 opciones más:

    -   **Manual**: **echo "OPENAI_API_KEY=sk-\..." \>
        /Volumes/PENDRIVE/ZOE/data/.env**

    -   **Cada vez**: el script **.command** te la pide al iniciar (modo
        efímero, no se guarda)

### Los scripts de OpenAI cargan la API key automáticamente

\# Dentro de ZOE-Chat-OpenAI.command:

if \[ -f "\$ZOE_HOME/data/.env" \]; then

export \$(grep -v \'\^#\' "\$ZOE_HOME/data/.env" \| xargs)

\# API key cargada automáticamente

else

\# Pedir al usuario

read -s API_KEY

export OPENAI_API_KEY="\$API_KEY"

\# Opcional: guardar

fi

python -m zoe.cli_chat \--backend openai_compatible \--model gpt-4º

### Tabla comparativa en el README
  **MODO**   **LLM**      **COSTE**                **PRIVACIDAD**     **CALIDAD**   **OFFLINE**
  Mock       Ninguno      Gratis                   Total              Básica        Sí

  Ollama     qwen2.5:3b   Gratis                   Total              Decente       Sí

  OpenAI     GPT-4o       \~0.01-0.05€/respuesta   Datos viajan a     Excelente     No
                                                   OpenAI                           
### Lo más importante

**Puedes cambiar de modo en cualquier momento.** La memoria, identidad y
trayectoria de ZOE se mantienen sin importar qué backend uses. Un día
usas Mock, otro día Ollama, otro día OpenAI, y ZOE recuerda todo lo que
le dijiste. Todo vive en el pendrive.

### Cómo probarlo

1.  Conecta pendrive a tu MacBook Air

2.  Ejecuta el instalador (responde "s" cuando pregunte por API key)

3.  Doble clic en **ZOE-Chat-OpenAI.command** → ZOE responde con GPT-4o

4.  O doble clic en **ZOE-Dashboard-OpenAI.command** → Dashboard con
    GPT-4o

5.  Escribe **/quit** antes de desconectar el pendrive

### Listo, Fernando. Instalación en pendrive documentada y subida.

Commit **29100fa** pushed.

### Qué se ha creado

### Script instalador: zoe/scripts/install_pendrive_macos.sh

Un instalador interactivo que hace TODO automáticamente:

1.  **Detecta el pendrive** --- muestra lista de volúmenes USB montados

2.  **Verifica Python y Git** --- comprueba que están instalados

3.  **Clona el repositorio** --- descarga ZOE desde GitHub al pendrive

4.  **Crea entorno virtual** --- **venv/** dentro del pendrive (no en el
    Mac)

5.  **Instala dependencias** --- **pip install -e .** en el venv del
    pendrive

6.  **Crea directorio de datos** --- **data/** para la memoria SQLite

7.  **Crea 3 scripts lanzadores** **.command** (doble clic desde
    Finder):

    -   **ZOE-Chat.command** --- Chat con Mock (sin LLM)

    -   **ZOE-Chat-Ollama.command** --- Chat con Ollama

    -   **ZOE-Dashboard.command** --- Dashboard web

### Documentación en README: "Instalación en Pendrive USB (macOS)"

Sección completa con **6 pasos para no técnicos**:
  **PASO**                   **QUÉ HACE**
  1\. Preparar el Mac        Instalar Python y Git (comandos incluidos)

  2\. Conectar el pendrive   Insertar USB, anotar nombre

  3\. Descargar el           **curl -O** desde Terminal
  instalador                 

  4\. Ejecutar el instalador **bash install_pendrive_macos.sh**

  5\. Usar ZOE               Doble clic en **.command** o Terminal

  6\. Hablar con ZOE         Ejemplo de conversación real
Más:

-   **Cómo desconectar**: siempre **/quit** antes de expulsar

-   **Cómo usar con Ollama**: modelo en Mac, memoria en pendrive

-   **Cómo actualizar**: **git pull** + **pip install -e .**

-   **Tabla de troubleshooting**: 7 problemas comunes con solución

-   **Cómo formatear el pendrive**: APFS o exFAT

### Estructura en el pendrive

```

PENDRIVE/

└── ZOE/

├── zoe/ \# Código (\~25MB)

├── venv/ \# Entorno virtual (\~200MB)

├── data/ \# Memoria de ZOE

│ └── zoe_memory.db \# SQLite persistente

├── ZOE-Chat.command \# 🚀 Doble clic

├── ZOE-Chat-Ollama.command \# 🚀 Doble clic

└── ZOE-Dashboard.command \# 🚀 Doble clic

**Espacio total**: \~500MB inicial. **0 bytes en el Mac** (solo Python y
Git que ya están instalados).

### Ventajas de esta configuración

-   **0 bytes en el Mac**: código, entorno y datos viven en el pendrive

-   **Portátil**: llevas tu ZOE (con toda su memoria e identidad) a
    cualquier Mac

-   **Persistente**: la memoria SQLite guarda conversaciones entre
    sesiones

-   **Identidad portátil**: la identidad criptográfica de ZOE viaja
    contigo

-   **Ollama híbrido**: el modelo LLM vive en el Mac, la mente de ZOE en
    el pendrive

### Cómo usarlo (resumen para Fernando)

1.  Conecta un pendrive USB (8GB+) a tu MacBook Air

2.  Abre Terminal y ejecuta:

bash

cd \~/Downloads

curl -O
https://raw.githubusercontent.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO/main/zoe/scripts/install_pendrive_macos.sh

bash install_pendrive_macos.sh

3.  Selecciona tu pendrive de la lista

4.  Espera 1-2 minutos

5.  Abre el pendrive en Finder → doble clic en **ZOE-Chat.command**

6.  Habla con ZOE

7.  Para desconectar: escribe **/quit** y expulsa el pendrive

### Listo, Fernando. UI visual para Cuarentena y Marketplace completada.

Commit **c843ce6** pushed a **zoe-v1-sco**.

## Lo que se ha añadido

### Modal de Cuarentena (botón 🔒 Cuarentena)

-   **Stats visuales**: total, activas (amarillo), verificadas (verde),
    rechazadas (rojo), expiradas (gris)

-   **Lista de entries activas**: cada una muestra claim (truncado),
    dominio, source, confianza, razón, confirmaciones y contradicciones

-   **Botones de acción**: ✓ Promover (verde) y ✗ Rechazar (rojo) en
    cada entry

-   **Pendientes**: count de entries que aún no tienen suficientes
    verificaciones

-   Recarga automática tras promote/reject

### Modal de Marketplace (botón 🏪 Marketplace)

-   **Stats**: total, cápsulas, casos, downloads totales

-   **Cápsulas disponibles**: tabla con nombre, versión, licencia (badge
    color: verde=free, azul=opensource, morado=research, naranja=paid,
    rojo=sub), precio, autor, downloads, rating con estrellas, tags

-   **Botón ⬇ Instalar** en cada cápsula del marketplace

-   **Casos de uso disponibles**: lista similar

-   **Formulario "Subir Cápsula"**: nombre, autor, licencia (dropdown
    con 5 tipos), precio, tags, descripción

-   **Formulario "Subir Caso de Uso"**: nombre, autor, licencia,
    descripción

-   Ambos formularios llaman a los endpoints del marketplace y refrescan
    la lista automáticamente

### Estilos CSS

-   Cuarentena: **.q-stat**, **.q-item**, **.q-btn-promote**,
### .q-btn-reject

-   Marketplace: **.mp-item**,
    **.mp-license-{free,opensource,research,paid,subscription}**,
### .mp-btn-download

### Verificación

-   **775 tests, 100% pasan** (sin regresión)

-   57 tests críticos verificados (dashboard + CLI + marketplace)

-   README actualizado con secciones "UI en Dashboard" tanto para
    Cuarentena como para Marketplace

### Cómo probarlo

1.  Arranca el dashboard: **python -m zoe.web_dashboard \--backend
    mock**

2.  Abre **http://localhost:8642** en el navegador

3.  Click en **🔒 Cuarentena** → verás el modal con stats y entries (si
    las hay)

4.  Click en **🏪 Marketplace** → verás el modal con cápsulas/casos
    disponibles y formularios de upload

5.  Para probar el flujo completo: crea una cápsula con **📦 Cápsulas →
    Crear nueva**, luego súbela al marketplace con **🏪 Marketplace →
    Subir cápsula**, elimínala del disco, y descárgala del marketplace
    con **⬇ Instalar**

¿Quieres que avance con algo más, o prefieres probar lo hecho abriendo
el dashboard?

### Listo, Fernando. Fase 6 documentada y subida a GitHub.

### Lo que se ha hecho

### 1. Documentación Fase 6 completa

**zoe/phases/PHASE_6_PLAN.md** --- Plan completo dividido en dos
sub-fases:

-   **Fase 6A --- Epistemic Validation System**: resuelve el problema
    del "niño brillante sin cultura". Incluye **EpistemicValidator**
    con política de confianza por fuente, dominios sensibles que
    requieren triple verificación, cuarentena activa, validación
    federada entre ZOEs, y cap de confianza (0.50 para auto-aprendido vs
    0.95 para cápsula verificada).

-   **Fase 6B --- Knowledge Capsules System**: lo que ya está
    implementado y pushed.

### 2. Sistema de cápsulas implementado

**Commit b930239 pushed a zoe-v1-sco.**Estructura creada:

zoe/capsules/

├── \_\_init\_\_.py

├── schema.py \# CapsuleMeta, TrustLevel, validación

├── loader.py \# CapsuleLoader con resolución de dependencias

├── registry.py \# índice y búsqueda

├── scaffold.py \# CLI generador

├── CAPSULE_MATRIX.md \# matriz completa de cápsulas

├── elder_care_knowledge/ \# 54 entries, verified

├── basic_psychology/ \# 49 entries, curated

└── communication_skills/ \# 37 entries, curated

### 3. Matriz de cápsulas

3 implementadas + 9 planificadas (V1.2/V1.3). Detalle en
**CAPSULE_MATRIX.md** con trust level, entries, dependencias,
capacidades, restricciones y provenance.

### 4. Script generador de cápsulas (scaffold CLI)

Comandos disponibles:

bash

\# Crear nueva cápsula desde cero (genera templates)

python -m zoe.capsules.scaffold create \\

\--name my_capsule \\

\--domain "education.tutoring" \\

\--trust-level curated \\

\--description "\..." \\

\--components semantic,causal,validators \\

\--use-cases tutoring_estudiantes

\# Validar cápsula existente

python -m zoe.capsules.scaffold validate \--name X

\# Calcular hash de contenido

python -m zoe.capsules.scaffold hash \--name X

\# Listar cápsulas disponibles

python -m zoe.capsules.scaffold list

\# Ver matriz completa

python -m zoe.capsules.scaffold matrix

\# Info detallada de una cápsula

python -m zoe.capsules.scaffold info \--name X

El scaffold genera templates con ejemplos comentados para que cualquier
persona pueda crear cápsulas nuevas sin entender toda la arquitectura.

### 5. Tests

-   **52 tests nuevos** en **test_phase6_capsules.py** (6 suites):
    schema, loader, registry, validators de las 3 cápsulas, scaffold
    CLI, integración end-to-end.

-   **Total proyecto: 630 tests, 100% pasan.**

-   No-regresión verificada en tests críticos de fases anteriores.

### Rutas en GitHub
  **RECURSO**             **RUTA**
  Plan Fase 6             **zoe/phases/PHASE_6_PLAN.md**

  Matriz cápsulas         **zoe/capsules/CAPSULE_MATRIX.md**

  Sistema cápsulas        **zoe/capsules/**(schema, loader, registry,
                          scaffold)

  Cápsula elder_care      **zoe/capsules/elder_care_knowledge/**

  Cápsula                 **zoe/capsules/basic_psychology/**
  basic_psychology        

  Cápsula                 **zoe/capsules/communication_skills/**
  communication_skills    

  Tests                   **zoe/tests/test_phase6_capsules.py**
URL:
#### https://github.com/fernandofondillo/CFI-Cognitive-Fractal-Intelligence-V2/tree/zoe-v1-sco/zoe/capsules

### Próximos pasos sugeridos

1.  **Implementar Fase 6A** (EpistemicValidator) --- es lo que cierra el
    círculo epistémico

2.  **Crear elder_care_skills** (tools de cuidador: routine_tracker,
    fall_risk_assessor, medication_checker)

3.  **Integrar el loader de cápsulas en run_use_case.py** para que se
    carguen automáticamente al arrancar ZOE

4.  **Crear las 9 cápsulas planificadas** para V1.2/V1.3

¿Quieres que avance con la implementación de Fase 6A (epistemic
validator) o prefieres que primero integre el loader de cápsulas en
**run_use_case.py** para que se carguen al activar ZOE?

### Listo, Fernando. Fase 6A completa y pushed.

Commit **816dd7b** pushed a **zoe-v1-sco**. Te resumo lo implementado:

## Las 4 opciones de Fase 6A

### Opción 1 — EpistemicValidator

**zoe/core/epistemic_validator.py** --- valida todo conocimiento nuevo
antes de entrar a memoria:

-   14+ fuentes categorizadas con confianza base (capsule:verified=0.95,
    llm:gpt-4o=0.50, scientific:pubmed=0.95, web:general=0.30)

-   5 dominios sensibles (medical, psychological, legal, safety,
    financial) que requieren triple verificación

-   Cap de confianza: auto-aprendido max 0.50, triple-verificado max
    0.75, federativo max 0.85, cápsula verified max 0.95

-   Rechaza automáticamente claims que contradicen conocimiento
    verificado

### Opción 2 — KnowledgeQuarantine

**zoe/core/knowledge_quarantine.py** --- cuarentena activa:

-   Las entradas en cuarentena NO se usan para decisiones críticas
    (**filter_safe(critical_context=True)**)

-   SÍ se usan para brainstorming, hipótesis, exploración

-   Plan de verificación con timeout (default 30 días, luego se podan)

-   **verify()** acumula confirmaciones, **promote()** al alcanzar el
    umbral, **reject()** con contradicciones

### Opción 3 — CrossValidator

**zoe/core/cross_validator.py** --- triple verificación multi-fuente:

-   Consulta 3 fuentes (LLM-A + LLM-B + cápsula o tercera fuente)

-   3/3 coinciden → confianza 0.75 (sale de cuarentena)

-   2/3 coinciden → confianza 0.65 o 0.80 si cápsula en mayoría

-   Divergencia total → rechazo

-   Similitud léxica Jaccard para comparar respuestas

### Opción 4 — EpistemicFederation

**zoe/core/epistemic_federation.py** --- revisión por pares científica
entre ZOEs:

-   **knowledge_validation_request** enviado a peers

-   Peers responden: confirmed \| contradicted \| unknown

-   ≥2 confirmaciones → confianza sube a 0.85 (sale de cuarentena)

-   ≥1 contradicción → rechazo, requiere validación científica externa

-   Cada ZOE indexa su conocimiento local para responder a requests de
    otras

### Dashboard Capsules — UI completa

**6 endpoints nuevos** en **web_dashboard.py**:

-   **GET /api/capsules** --- lista disponibles

-   **GET /api/capsules/loaded** --- lista cargadas

-   **POST /api/capsules/load** --- carga en caliente

-   **POST /api/capsules/unload** --- descarga

-   **GET /api/capsules/{name}/info** --- info detallada

-   **POST /api/capsules/create** --- crea nueva vía scaffold CLI

**Modal "Cápsulas de Conocimiento"** con 3 secciones:

1.  **Disponibles**: tabla con nombre, trust level (badge color),
    dominio, descripción, botones Cargar/Info

2.  **Cargadas**: lista con entries inyectados, botón Descargar

3.  **Crear nueva cápsula**: formulario que invoca el scaffold CLI
    (nombre, dominio, trust level, componentes, use cases, descripción)

Botón "📦 Cápsulas" añadido al panel de acciones principal.

### CLI Chat — comandos nuevos

-   **/capsules** --- lista disponibles y cargadas

-   **/capsule \<nombre\>** --- carga en caliente (firma en trayectoria)

-   **/uncapsule \<nombre\>** --- descarga

### Tests y verificación

-   **41 tests nuevos** en **test_phase6a_epistemic.py** (5 suites),
    100% pasan

-   **Total proyecto: 671 tests, 100% pasan**

-   No-regresión verificada (Fase 5, Fase 6B, CLI, loop)

-   Smoke test: CLI Chat inicializa con CapsuleManager +
    EpistemicValidator. Cápsulas se cargan en caliente y se firman en
    trayectoria.

## Cómo funciona en conjunto

```

ZOE detecta gap (ScientificEngine o Learner)

↓

EpistemicValidator valida el claim nuevo

↓

¿Dominio sensible? → NEEDS_TRIPLE_VALIDATION → cuarentena

↓

CrossValidator consulta 3 fuentes (LLM-A + LLM-B + cápsula)

↓

3/3 coinciden → promueve a confianza 0.75

2/3 coinciden → confianza 0.65, sigue en cuarentena

Divergencia → rechazo

↓

EpistemicFederation envía a peers para validación adicional

↓

≥2 peers confirman → confianza sube a 0.85

≥1 peer contradice → rechazo federativo

↓

Si después de 30 días no se valida → Curator poda

↓

Todo queda firmado en TrajectoryChain

### Próximos pasos sugeridos

1.  **Crear las 9 cápsulas planificadas** para V1.2 (elder_care_skills,
    company_loneliness, vigilance_devops, etc.) --- puedes hacerlo desde
    el Dashboard con el formulario "Crear nueva cápsula"

2.  **Integrar EpistemicValidator en el Learner**para que todo
    conocimiento que entra pase por validación automáticamente

3.  **Implementar capsule_loaded / capsule_unloaded en el dashboard en
    tiempo real** vía WebSocket

4.  **Crear el endpoint /api/capsules/{name}/validate** para validar
    cápsulas desde la UI

¿Quieres que avance con la integración del EpistemicValidator en el
Learner (punto 2), o prefieres que cree las 9 cápsulas planificadas para
V1.2?
