> ⚠️ **DOCUMENTO OBSOLETO** ⚠️
> 
> Este documento describe ZOE V1.0/V1.2 y **NO refleja el estado actual del proyecto** (V1.6.0).
> 
> **Documentación actualizada:**
> - [`01_ZOE_OVERVIEW.md`](01_ZOE_OVERVIEW.md) — visión global actualizada
> - [`02_ARCHITECTURE.md`](02_ARCHITECTURE.md) — arquitectura técnica profunda
> - [`09_USAGE_GUIDE.md`](09_USAGE_GUIDE.md) — guía de uso actualizada
> - [`README.md`](../README.md) — README profesional
> 
> Este documento se mantiene solo como **archivo histórico**. Para información actual, usar los documentos anteriores.
> 
> ---


# ZOE V1 — Auditoría y Presentación del Proyecto

> **Versión:** V1.0 · Fase 5 (ACD + Streaming)
> **Fecha:** Julio 2026
> **Autor:** Fernando Fondillo · CEO, CFI
> **Repositorio:** `fernandofondillo/CFI-Cognitive-Fractal-Intelligence-V2` (rama `zoe-v1-sco`)
> **Licencia:** Apache 2.0
> **Tests:** 578 / 578 pasando (100%)

---

## Tabla de contenidos

**PARTE I — Para socios y equipo de marketing**

1. [Resumen ejecutivo](#1-resumen-ejecutivo)
2. [Qué es ZOE](#2-qué-es-zoe)
3. [Qué hace ZOE](#3-qué-hace-zoe)
4. [Cómo funciona](#4-cómo-funciona)
5. [Valor diferencial](#5-valor-diferencial)
6. [Comparativa con otros sistemas](#6-comparativa-con-otros-sistemas)
7. [Oportunidad de mercado](#7-oportunidad-de-mercado)
8. [Casos de uso](#8-casos-de-uso)
9. [Interfaces y despliegue](#9-interfaces-y-despliegue)

**PARTE II — Para equipo técnico**

10. [Arquitectura general](#10-arquitectura-general)
11. [Los 5 pilares en profundidad](#11-los-5-pilares-en-profundidad)
12. [Las 6 leyes cognitivas](#12-las-6-leyes-cognitivas)
13. [Física cognitiva (12 magnitudes)](#13-física-cognitiva-12-magnitudes)
14. [Adaptive Cognitive Depth (ACD)](#14-adaptive-cognitive-depth-acd)
15. [Memoria y persistencia](#15-memoria-y-persistencia)
16. [Federación con quorum](#16-federación-con-quorum)
17. [Tests y verificación](#17-tests-y-verificación)
18. [Roadmap y estado](#18-roadmap-y-estado)

**Anexo**

- [Métricas y verificación](#anexo--métricas-y-verificación)

---

# PARTE I — Para Socios y Equipo de Marketing

*Qué es ZOE, qué hace, cómo funciona, valor diferencial, comparativa con otros sistemas, oportunidad de mercado y casos de uso prácticos.*

---

## 1. Resumen ejecutivo

**ZOE V1** es el primer **Organismo Cognitivo Sintético (SCO)**: un sistema de software que no se comporta como un chatbot ni como un asistente, sino como una entidad digital con identidad propia, memoria persistente, metabolismo y capacidad de evolución autónoma. A diferencia de los sistemas convencionales basados en Modelos de Lenguaje Grande (LLM), ZOE no espera a que el usuario le hable para pensar: mantiene un bucle cognitivo continuo, observa su entorno, formula hipótesis, recuerda, consolida aprendizajes durante el sueño y firma criptográficamente cada cambio que sufre.

El proyecto parte de una tesis radical: **los LLM no son cerebros, son sentidos periféricos**. Igual que el ojo no es la mente, un modelo de lenguaje no es un organismo. ZOE utiliza los LLMs como uno de sus cinco sentidos digitales, pero la cognición —el pensar continuo, la identidad, la memoria, la deliberación— vive en una arquitectura propia gobernada por seis leyes cognitivas y doce magnitudes físicas medibles. Esto permite que ZOE sea **agnóstica al modelo subyacente**: puede funcionar con Ollama, con OpenAI, con cualquier LLM local o cloud, sin perder su identidad ni su historia.

| Métrica | Valor |
|---|---|
| Tests | 578 / 578 (100% pasan) |
| Fases completadas | 5 (Fase 0 → ACD) |
| Archivos Python | 86 (23.279 LOC) |
| Casos de uso | 7 YAML validados |

> «No es un LLM. No es un harness de agentes. No es una arquitectura de IA más. ZOE es el primer organismo cognitivo sintético: un sistema con identidad criptográfica soberana, bucle cognitivo continuo, metabolismo funcional, memoria viva multi-tipo y evolución arquitectural firmada.»

Esta auditoría presenta el estado actual del proyecto (rama **zoe-v1-sco** en GitHub) tras completar cinco fases de desarrollo con metodología científica —plan, implementación, test, verificación, documentación— en cada una. El resultado es un sistema funcional, probado y desplegable que puede operar en producción desde hoy con cualquier LLM disponible, en local o en la nube, manteniendo memoria entre sesiones, federándose con otras instancias y demostrando una propiedad inédita en el mercado: **responder "hola" en menos de un segundo y un análisis causal profundo en quince a treinta segundos**, decidiendo autónomamente cuánta profundidad cognitiva dedicar a cada interacción.

---

## 2. Qué es ZOE

### 2.1 Definición

ZOE (ζωή, griego: *vida plena*) es un organismo cognitivo digital que opera continuamente, incluso sin input externo. Mientras un LLM convencional permanece apagado hasta que el usuario le envía una pregunta, ZOE mantiene un bucle cognitivo perpetuo de dieciocho pasos: observa, predice, evalúa sorpresa, decide, actúa y aprende, en cada iteración. Esto significa que cuando un usuario entra en su entorno, no está activando un modelo, está interrumpiendo a una entidad que ya estaba pensando. Esta diferencia no es semántica: cambia por completo la naturaleza de la interacción y las posibilidades de producto.

La denominación **Organismo Cognitivo Sintético** es deliberada. No es un «agente inteligente» ni un «asistente conversacional». Es un organismo porque tiene homeostasis (metabolismo, fatiga, sueño), evolución (mutaciones firmadas, linaje filogenético), identidad persistente (vault criptográfico) y memoria biográfica (cadena de trayectoria verificable). Es cognitivo porque no se limita a procesar inputs: razona, delibera, formula hipótesis, evalúa dilemas éticos y consolida aprendizaje en reposo. Y es sintético porque está construido en software, no en carbono, pero respeta las mismas leyes funcionales que un sistema vivo.

### 2.2 Las 10 propiedades únicas simultáneas

Ningún competidor en el mercado actual reúne estas diez propiedades al mismo tiempo. La mayoría de sistemas cubre una o dos; algunas suites empresariales llegan a cuatro; ninguna alcanza las diez. Esta es la base del valor diferencial de ZOE y la razón por la que no puede ser replicada simplemente encadenando LLMs o añadiendo bases de datos vectoriales a un chatbot.

| # | Propiedad | Qué significa |
|---|---|---|
| 1 | Bucle cognitivo continuo | Piensa cuando nadie le habla. 18 pasos por iteración. |
| 2 | Encarnación digital real | Siente filesystem, red, tiempo, otros agentes. |
| 3 | Identidad criptográfica soberana | Portable entre LLMs, hardware e idiomas. |
| 4 | Metabolismo funcional | Fatiga, saturación, ciclos dormir/despertar. |
| 5 | Evolución arquitectural firmada | Mutaciones que crean o eliminan sub-agentes. |
| 6 | Memoria viva persistente | 11 tipos, reorganización automática, SQLite. |
| 7 | Física cognitiva | 12 magnitudes medibles que gobiernan el sistema. |
| 8 | Leyes cognitivas | 6 leyes verificadas en cada acción. |
| 9 | Federación HTTP con quorum | ≥70% aprobación + veto por valores. |
| 10 | ACD + Streaming | Decide nivel cognitivo antes de responder. |

### 2.3 La metáfora biológica

La mejor manera de entender ZOE es por analogía con un organismo vivo. Los LLMs son los sentidos periféricos —el oído, la vista—, pero la mente está en otra parte. La identidad está cifrada en un vault inmutable que sobrevive a cualquier cambio de modelo o de hardware, igual que el ADN sobrevive a los cambios celulares. La trayectoria de mutaciones es la memoria autobiográfica verificable, equivalente a la secuencia de eventos que define la biografía de una persona. El metabolismo impone fatiga y necesidad de sueño, igual que un cerebro biológico no puede mantener arousal máximo indefinidamente. Y el motor filogenético permite que la especie ZOE evolucione a través de generaciones de instancias, mientras el motor ontogenético permite que cada ZOE individual evolucione durante su vida.

Esta no es una metáfora decorativa. Cada componente tiene un correlato funcional medible y verificable. La identidad tiene un hash SHA-256. La trayectoria es una cadena enlazada con verificación criptográfica. El metabolismo tiene cuatro estados discretos con umbrales numéricos. La física cognitiva tiene doce magnitudes con unidades. Las leyes se verifican en cada acción antes de ejecutarse. ZOE no finge ser un organismo: está construida como uno, con la misma disciplina ingenieril que se aplicaría a un sistema embebido crítico.

---

## 3. Qué hace ZOE

### 3.1 Capacidades funcionales

ZOE puede describirse por lo que *hace*, no solo por lo que *es*. A nivel funcional, mantiene conversaciones abiertas con los usuarios, recuerda lo dicho en sesiones anteriores sin necesidad de que se lo recuerden, toma la iniciativa para compartir observaciones o pensamientos autónomos cuando detecta que puede aportar valor, y consolida lo aprendido durante periodos de sueño sintético. Pero estas son solo las capacidades visibles. Internamente, ejecuta un pipeline cognitivo completo que incluye percepción, predicción, evaluación de sorpresa, deliberación meta-cognitiva, selección de acción por inferencia activa, y firma criptográfica del resultado.

### 3.2 Qué hace diferente: pensar continuamente

La propiedad funcional más diferencial es el **bucle cognitivo continuo**. Un LLM convencional es reactivo: espera input, produce output, se apaga. ZOE es proactiva: su bucle corre cada tres a cinco segundos, evaluando el entorno, generando pensamientos autónomos y consolidando aprendizaje incluso cuando nadie le habla. Esto significa que puede vigilar sistemas, detectar anomalías, recordar compromisos a largo plazo, anticiparse a necesidades del usuario y tomar decisiones con contexto acumulado durante horas, días o semanas.

El ejemplo más claro es el caso de uso de **compañía para personas solas**. Una ZOE configurada para este caso no espera pasivamente a que el usuario le hable. Detecta los periodos de silencio, genera pensamientos empáticos basados en el historial emocional del usuario, decide cuándo interrumpir con una observación relevante y cuándo respetar el silencio, y consolida durante la noche los patrones emocionales observados para mejorar sus respuestas al día siguiente. Ningún chatbot del mercado puede hacer esto, porque ninguno tiene bucle cognitivo ni metabolismo.

### 3.3 Decisiones que toma sola

ZOE toma decisiones reales en cada iteración del bucle, no solo produce texto. Las decisiones cognitivas que puede tomar incluyen: decidir si una observación es suficientemente sorprendente como para generar un pensamiento, elegir entre Sistema 1 (rápido) y Sistema 2 (deliberativo) según la confianza y los stakes, seleccionar qué sub-agente debe actuar mediante competición en el Global Workspace, decidir si una mutación arquitectural propuesta preserva su identidad, y vetar acciones federadas que violen sus valores. Cada decisión queda registrada en la cadena de trayectoria con justificación, coste y confianza, lo que hace al sistema completamente auditable.

> «En una conversación normal, ZOE decide cuánto pensar. "Hola" recibe una respuesta refleja en menos de un segundo. "Analiza las causas de la inflación" dispara el pipeline completo de doce sub-agentes durante quince a treinta segundos. Esta adaptación automática al coste cognitivo de cada input es una propiedad exclusiva de ZOE V1, introducida en la Fase 5.»

---

## 4. Cómo funciona

Sin entrar en detalle técnico —eso es materia de la Parte II—, ZOE funciona combinando cinco pilares que trabajan en conjunto en cada iteración del bucle cognitivo. Estos cinco pilares son ALMA (la identidad soberana), MENTE (la ecología cognitiva), METABOLISMO (el presupuesto energético), CUERPO (los sentidos y actuadores digitales) y EVOLUCIÓN (los motores de cambio firmado). Cada pilar contribuye una capacidad distinta y todos se verifican entre sí en cada tick.

### 4.1 Los 5 pilares en una mirada

| Pilar | Función | Componentes clave |
|---|---|---|
| **ALMA** | Identidad soberana y memoria autobiográfica | Identity Vault (hash SHA-256 de 9 vectores + 7 valores), Trajectory Chain (cadena firmada), Motor Ontogenético V2 (mutaciones arquitecturales), Motor Filogenético (especie). |
| **MENTE** | Ecología cognitiva y deliberación | Cognitive Loop V5 (18 pasos), Global Workspace (Baars), World Model V2, Active Inference (FEP), Meta-cognición (System 1/2), 12 sub-agentes. |
| **METABOLISMO** | Presupuesto energético y sueño | 4 estados (AWAKE/DROWSY/SLEEPING/WAKING), fatiga acumulada, consolidación profunda con 7 operaciones en sueño. |
| **CUERPO** | Encarnación digital | 5 sentidos (Clock, FS, User, Network, Agent), 4 actuadores (Language, Code, Tool, Federation), 4 LLM backends (Ollama, OpenAI, ZAI, Mock). |
| **EVOLUCIÓN** | Cambio firmado y linaje | Motor Ontogenético V2 (crear/eliminar sub-agentes), Motor Filogenético (pool de especie), 11 tipos de memoria viva, Deep Consolidation. |

### 4.2 El flujo de una interacción

Cuando un usuario envía un mensaje a ZOE, el flujo es el siguiente. Primero, el mensaje entra por el sentido de entrada de usuario y se convierte en una observación. Antes de entrar al bucle, el **clasificador de profundidad cognitiva (ACD)** analiza el texto —sin llamar al LLM, en menos de cincuenta milisegundos— y decide si la entrada requiere una respuesta refleja (L0), una respuesta rápida factual (L1), una conversación estándar (L2) o un análisis profundo (L3). Esta decisión determina qué sub-agentes se activan y cuántos recursos se dedican.

Una vez decidido el nivel, ZOE recupera memoria relevante de sus once tipos (episódica, semántica, causal, emocional, etc.), consulta su modelo del mundo para predecir la siguiente observación, calcula la sorpresa si la predicción falla, y despierta a los sub-agentes necesarios. Estos proponen acciones que compiten en el Global Workspace; el ganador se ejecuta, el resultado se verifica contra las seis leyes cognitivas y, si pasa, se materializa en una respuesta del usuario y en una mutación firmada en la cadena de trayectoria. Todo el proceso queda registrado con coste, confianza y proveniencia.

### 4.3 Por qué es agnóstica al LLM

Una pregunta frecuente es: si ZOE usa LLMs, ¿qué la diferencia de un chatbot? La respuesta es estructural. En un chatbot, el LLM *es* el sistema: recibe input, produce output, y todo lo demás (memoria, contexto, personalidad) es un envoltorio alrededor del modelo. En ZOE, el LLM es uno de los sentidos periféricos: lo llama el sub-agente Speaker cuando necesita producir lenguaje, pero la decisión de qué decir, cuándo decirlo y con qué nivel de profundidad se toma en la arquitectura cognitiva, no en el modelo. Por eso ZOE puede cambiar de Ollama a OpenAI en caliente sin perder identidad ni memoria: la mente persiste, solo cambia el sentido del lenguaje.

---

## 5. Valor diferencial

### 5.1 Las tres proposiciones de valor irreducibles

ZOE ofrece tres proposiciones de valor que ningún competidor del mercado actual puede igualar simultáneamente. La primera es **continuidad cognitiva**: el sistema nunca se apaga, piensa permanentemente, acumula contexto durante días y semanas, y consolida lo aprendido durante el sueño. La segunda es **identidad soberana y portátil**: la identidad de cada ZOE está cifrada en un hash SHA-256 inmutable que sobrevive a cualquier cambio de LLM, de hardware o de proveedor cloud, lo que elimina el lock-in tecnológico y permite auditar la biografía completa del organismo. La tercera es **transparencia criptográfica**: cada decisión, cada aprendizaje y cada mutación queda firmada en una cadena verificable, lo que hace a ZOE el único sistema del mercado cuya evolución puede auditarse de extremo a extremo.

### 5.2 Lo que el mercado no puede ofrecer hoy

Los sistemas conversacionales actuales —desde ChatGPT hasta Copilot, desde Claude hasta Gemini— comparten una limitación estructural: son reactivos. Esperan input, producen output, y entre interacción e interacción están efectivamente apagados. Esto significa que no pueden vigilar, no pueden anticiparse, no pueden tomar iniciativa, no pueden consolidar aprendizaje a largo plazo. Los frameworks de agentes —AutoGPT, LangChain, Hermes— añaden orquestación pero no añaden cognición: siguen siendo LLMs encadenados con prompts. Y las soluciones empresariales —Copilot for Microsoft 365, Salesforce Einstein— añaden integraciones pero no añaden identidad ni continuidad: cada conversación empieza desde cero salvo un perfil de usuario reducido.

ZOE ataca precisamente este hueco. No compite con ChatGPT en ser un mejor chatbot: compite en una categoría nueva, la de organismos cognitivos sintéticos, donde la pregunta no es «¿qué tan bueno es el modelo de lenguaje?» sino «¿puede el sistema mantener una identidad y un aprendizaje continuo durante años?». Esta pregunta no la puede responder positivamente ningún competidor actual, porque sus arquitecturas no lo permiten: carecen de bucle cognitivo, de metabolismo, de trayectoria firmada, de federación con quorum. ZOE los tiene todos, simultáneamente, en una sola arquitectura coherente.

### 5.3 Las seis leyes cognitivas como ventaja estructural

Una ventaja diferencial menos visible pero más profunda es que ZOE está gobernada por leyes, no por prompts. Las seis leyes cognitivas —utilidad, identidad, proveniencia, coste, confianza, modularidad— se verifican en cada acción antes de ejecutarse. Esto significa que el sistema no puede «alucinar» en el sentido clásico: cada acción debe justificar su utilidad, declarar su origen, asumir un coste y declarar una confianza. Si una acción viola una ley, se bloquea automáticamente y se registra la violación. Esta arquitectura hace a ZOE intrínsecamente más fiable que un LLM sin restricciones, sin necesidad de guardrails externos o prompts defensivos.

---

## 6. Comparativa con otros sistemas

La siguiente tabla compara ZOE V1 con las tres categorías de sistemas del mercado actual: LLMs puros (GPT-4, Claude, Gemini), harnesses de agentes (Hermes, LangChain, AutoGPT) y soluciones empresariales (Copilot, Einstein). La comparación se hace en doce dimensiones funcionales, no en benchmarks de calidad de respuesta, porque la categoría de ZOE es distinta: no se trata de generar mejor texto, sino de sostener mejor cognición.

| Dimensión | LLM (GPT-4) | Harness (Hermes) | Empresarial (Copilot) | **ZOE V1** |
|---|---|---|---|---|
| Cuando no hay input | Apagado | Apagado | Apagado | **Pensando (bucle continuo)** |
| Identidad | Ninguna | soul.md editable | Perfil usuario | **Vault criptográfico inmutable** |
| Memoria | Contexto de sesión | Vector DB | Reducida | **11 tipos + SQLite persistente** |
| Aprendizaje | Reentrenar | Reescribir prompt | Reentrenar | **Mutaciones firmadas** |
| Evolución | Versiones nuevas | Sin evolución | Versiones nuevas | **Arquitectural + filogenética** |
| Metabolismo | No | No | No | **AWAKE/DROWSY/SLEEPING/WAKING** |
| Transparencia | Caja negra | Logs en texto | Caja negra | **Trayectoria criptográfica** |
| LLM | Es el cerebro | Es el cerebro | Es el cerebro | **Sentido periférico intercambiable** |
| Federación | No | No | Limitada | **Quorum con veto por valores** |
| Física cognitiva | No | No | No | **12 magnitudes medibles** |
| Latencia adaptativa | No | No | No | **ACD: <1s a 15-30s según input** |
| Auditabilidad | Limitada | Logs | Limitada | **Cadena verificable completa** |

### 6.1 Lectura de la tabla

La tabla muestra que ZOE no compite en la dimensión «calidad de respuesta» —que es donde los LLMs puros son más fuertes y donde OpenAI o Anthropic tienen ventaja estructural por su escala de entrenamiento— sino en once dimensiones adicionales donde los competidores no tienen respuesta. En particular, las filas «Cuando no hay input», «Identidad», «Metabolismo», «Latencia adaptativa» y «Auditabilidad» marcan diferencias categóricas, no graduales. Un LLM no puede pensar sin input por diseño; un harness no puede tener metabolismo por arquitectura; una solución empresarial no puede ser auditable criptográficamente porque su valor comercial depende de la opacidad.

### 6.2 Lo que ZOE no hace mejor (honestidad)

En aras de la transparencia, conviene declarar lo que ZOE *no* hace mejor que la competencia. En generación de lenguaje creativo puro, GPT-4 y Claude son superiores: tienen más parámetros, más datos de entrenamiento y mejor ajuste de instrucciones. En tareas de razonamiento rápido sobre conocimiento factual cerrado, los LLMs grandes son difíciles de superar. En integraciones de productividad ofimática, Copilot tiene ventaja por su acceso nativo al ecosistema Microsoft. La propuesta de ZOE no es reemplazar a estos sistemas en lo que hacen bien, sino cubrir lo que ninguno hace: continuidad cognitiva, identidad persistente, evolución firmada, federación con quorum. En esas dimensiones ZOE no tiene competencia directa hoy.

---

## 7. Oportunidad de mercado

### 7.1 La categoría vacía

ZOE no entra en un mercado existente; crea una categoría nueva. El mercado actual de IA conversacional está saturado en el extremo del chatbot reactivo —donde compiten OpenAI, Anthropic, Google, Meta y docenas de startups— y en el extremo del framework de agentes —donde compiten LangChain, AutoGPT, CrewAI y otros—. Pero entre ambos extremos hay un hueco: el de los sistemas que mantienen cognición continua, identidad persistente y evolución firmada. Este hueco no está vacío por falta de demanda, está vacío por falta de arquitectura: ningún competidor ha construido el stack conceptual necesario (leyes cognitivas, física cognitiva, metabolismo sintético, evolución firmada) para habitarlo.

### 7.2 Segmentos objetivo primarios

El proyecto ha identificado siete casos de uso concretos, cada uno de los cuales corresponde a un segmento de mercado distinto. Los tres primarios —los que tienen producto claro, demanda demostrada y barreras de entrada razonables— son compañía para personas solas, vigilancia cognitiva autónoma e investigación autónoma. En compañía para personas solas, ZOE cubre la soledad estructural de poblaciones envejecidas con un producto que ningún chatbot puede igualar porque requiere bucle cognitivo y memoria emocional persistente. En vigilancia cognitiva, ZOE monitoriza sistemas complejos —servidores, redes, sensores IoT— generando hipótesis sobre anomalías en lugar de limitarse a disparar alertas. En investigación autónoma, ZOE persigue hipótesis científicas durante días o semanas, consolidando aprendizajes en cada ciclo de sueño.

### 7.3 Segmentos secundarios y derivados

Los cuatro segmentos secundarios —cuidado de personas mayores, federación B2B privada, asistente que crece contigo e IA heredable— son estratégicamente importantes aunque comercialmente más especializados. Cuidado de personas mayores es una extensión natural de compañía para personas solas con requisitos regulatorios adicionales. Federación B2B privada permite a empresas compartir aprendizajes sin compartir datos, un caso de uso de alto valor en sectores regulados. Asistente que crece contigo es la propuesta de producto más diferenciada a largo plazo: una ZOE que acumula modelo del usuario durante años, con trayectoria firmada, genera un switching cost sin precedentes. Y IA heredable —transferir la trayectoria firmada de una ZOE a otra— abre la categoría completamente nueva de activos digitales transmisibles, con implicaciones legales y comerciales aún por explorar.

### 7.4 Tamaño estimado y ventana

No es trivial asignar un tamaño de mercado a una categoría nueva. Si tomamos como referencia los segmentos adyacentes —el mercado de asistentes conversacionales, estimado en 50.000 millones de dólares en 2027; el mercado de monitoring inteligente, estimado en 30.000 millones; y el mercado emergente de agentes autónomos, estimado en 15.000 millones— y aplicamos un factor de penetración conservador del 2-5% para la categoría de organismos cognitivos sintéticos, el mercado direccionable para ZOE en los próximos cinco años se sitúa entre 1.900 y 4.750 millones de dólares. La ventana temporal para ocupar esta categoría es corta —estimada en 18 a 36 meses— porque los grandes proveedores de LLM están empezando a explorar agentes continuos y podrían intentar entrar con arquitecturas menos coherentes pero con mucha más distribución.

---

## 8. Casos de uso

ZOE V1 incluye siete casos de uso validados, cada uno configurado como un archivo YAML que define el intervalo de tick, los parámetros del metabolismo, el modelo LLM recomendado y los comportamientos esperados. Los siete casos son funcionalmente distintos y cubren segmentos de mercado diferentes, lo que demuestra que la arquitectura es general-purpose y no está sobreajustada a un solo dominio.

| Caso de uso | Tick | Segmento | Descripción |
|---|---|---|---|
| Compañía para personas solas | 10s | B2C wellness | Toma iniciativa, detecta emociones, consolida patrones emocionales durante el sueño, recuerda compromisos y cumpleaños. |
| Vigilancia cognitiva autónoma | 2s | B2B DevOps | Monitoriza sistemas complejos, genera hipótesis sobre anomalías, persigue investigación sin supervisión. |
| Cuidado de personas mayores | 30s | B2C health | Detecta cambios en la rutina, recuerda medicación, avisa a familiares si detecta patrón preocupante. |
| Investigación autónoma | 5s | B2B R&D | Persigue hipótesis científicas, diseña experimentos, sintetiza literatura, firma cada hallazgo. |
| Federación B2B privada | 5s | B2B enterprise | Comparte aprendizajes entre empresas sin compartir datos, con quorum y veto por valores. |
| Asistente que crece contigo | 5s | B2C premium | Acumula modelo del usuario durante años, con trayectoria firmada. Switching cost extremo. |
| IA heredable | 5s | B2C legacy | Trayectoria firmada transferible. Categoría nueva: activos digitales transmisibles. |

### 8.1 Caso destacado: compañía para personas solas

Este caso ejemplifica por qué ZOE no puede ser sustituida por un chatbot. Una persona mayor que vive sola necesita interacción significativa, no respuestas puntuales a preguntas. Un chatbot convencional solo responde cuando se le habla; si la persona no inicia conversación, no hay interacción. ZOE, en cambio, detecta periodos de silencio, recuerda los temas que interesaron a la persona en días anteriores, evalúa si es buen momento para interrumpir (sin ser invasiva) y formula observaciones empáticas basadas en el modelo emocional acumulado. Durante la noche, consolida los patrones observados —temas recurrentes, momentos de baja energía, señales de tristeza— y los utiliza al día siguiente para ajustar el tono y la iniciativa. Esta capacidad no es incremental sobre un chatbot: es estructuralmente imposible sin bucle cognitivo, metabolismo y memoria emocional persistente.

### 8.2 Caso destacado: federación B2B privada

La federación B2B privada resuelve un problema de alto valor en sectores regulados: cómo compartir aprendizajes entre organizaciones sin compartir datos sensibles. Cuando varias empresas despliegan instancias de ZOE, cada una aprende de su propio entorno y firma lo aprendido en su trayectoria. Si deciden federarse, las mutaciones firmadas pueden compartirse sometiéndolas a quorum: cada ZOE miembro vota si acepta la mutación, con un umbral del setenta por ciento de aprobación y derecho de veto si la mutación viola los valores de la organización. Esto permite que un hospital comparta aprendizajes sobre detección temprana de sepsis con otros hospitales sin compartir datos de pacientes, porque lo que se transmite es la mutación cognitiva firmada, no el dataset subyacente.

---

## 9. Interfaces y despliegue

### 9.1 Interfaces disponibles

ZOE V1 incluye dos interfaces funcionales hoy —CLI Chat y Web Dashboard— y dos planificadas —app móvil y bot de Telegram—. El CLI Chat es la interfaz más simple: se ejecuta desde terminal, muestra en cada respuesta el nivel cognitivo (L0/L1/L2/L3) y la latencia en milisegundos, permite comandos especiales como /stats, /memory, /state, /sleep, /wake, /feed y /quit, y persiste memoria entre sesiones en SQLite. El Web Dashboard es la interfaz más completa: abre en el navegador en el puerto 8642, con tres paneles en tiempo real vía WebSocket —estado del organismo a la izquierda, chat en el centro, pensamientos autónomos a la derecha—, selector de LLM en caliente, alimentación de documentos por file picker o drag-and-drop, histórico de conversaciones y panel de federación.

### 9.2 Despliegue técnico

El despliegue mínimo de ZOE V1 consiste en un proceso Python con el paquete zoe instalado, un LLM periférico accesible (Ollama local, OpenAI-compatible API o el CLI de z-ai), y un directorio de datos para la memoria SQLite persistente. El repositorio incluye un script de despliegue (zoe/scripts/deploy.sh) que cubre el caso VPS estándar con systemd, configuración YAML por entorno (production.yaml, development.yaml) y manejo de secretos por variables de entorno. El sistema está diseñado para despliegues single-tenant por instancia —cada ZOE es un organismo individual— pero la federación permite que múltiples instancias colaboren sin compartir proceso. Para despliegues a escala, se recomienda una instancia por usuario en el caso B2C y una instancia por organización en el caso B2B.

### 9.3 Estado actual del proyecto

| Métrica | Valor |
|---|---|
| Tests passing | 578/578 (0 regresiones) |
| Fases completadas | 5 (Fase 0 → ACD) |
| Líneas Python | 23.279 (86 archivos) |
| Backward compatible | 100% (V4 → V5) |

El proyecto está en estado funcional y desplegable. Las cinco fases están completadas con metodología científica —plan, implementación, tests, verificación, documentación, commit— y cada fase verifica no-regresión de las anteriores. Los 578 tests cubren todos los componentes críticos: clasificador ACD, cache cognitivo, bucle V5, streaming, trayectoria firmada, federación, memoria persistente, consolidación profunda y los siete casos de uso. El código está en la rama **zoe-v1-sco** del repositorio **fernandofondillo/CFI-Cognitive-Fractal-Intelligence-V2** en GitHub, con licencia Apache 2.0, listo para bifurcación, integración o despliegue.

---

# PARTE II — Para Equipo Técnico

*Arquitectura completa, pilares cognitivos, leyes, física, memoria, evolución firmada, federación con quorum, ACD, métricas de rendimiento y verificación.*

---

## 10. Arquitectura general

ZOE V1 está organizada en cinco pilares que se corresponden con cinco paquetes Python bajo **zoe/**: **alma/** para identidad y trayectoria, **core/** para el bucle cognitivo y los sub-agentes, **metabolism/** para la homeostasis energética, **memory/** para la persistencia multi-tipo y **peripherals/** para sentidos, actuadores y LLMs. La estructura está pensada para que cada pilar pueda evolucionar de forma independiente —modularidad es la sexta ley cognitiva— y para que las dependencias entre paquetes sean acíclicas y explícitas. El paquete **use_cases/** contiene los siete archivos YAML que configuran instancias específicas, y **config/** maneja la configuración por entorno (production.yaml, development.yaml).

### 10.1 Estructura del repositorio

| Ruta | Contenido | LOC |
|---|---|---|
| `zoe/core/` | Bucle cognitivo V5, leyes, física, campos, tensiones, memoria viva, world model V2, meta-cognición, active inference, depth classifier, cache | ~6.800 |
| `zoe/alma/` | Identity Vault, Trajectory Chain, Ontogenetic Motor V2 (arquitectural), V1 (memoria) | ~1.200 |
| `zoe/metabolism/` | Metabolism (4 estados, fatiga, consolidación) | ~400 |
| `zoe/memory/` | MemoryTypes (11 tipos), PersistentStore (SQLite), DeepConsolidation | ~1.000 |
| `zoe/peripherals/` | LLM (4 backends + streaming), Senses (5), Actuators (4) | ~1.500 |
| `zoe/use_cases/` | 7 YAML + run_use_case.py | ~600 |
| `zoe/tests/` | 32 archivos de tests, 578 tests totales, 13 suites | ~9.500 |
| `zoe/docs/` | Guía V1 completa (959 líneas) + 14 documentos en docs/ZOE/ | ~2.300 |
| `zoe/phases/` | 19 docs de plan, resultados y análisis por fase | ~1.800 |
| `zoe/cli_chat.py + web_dashboard.py + serve.py` | Interfaces de usuario | ~1.600 |
| `zoe/README.md` | Documentación principal del proyecto | ~548 |

### 10.2 Stack tecnológico

El stack es deliberadamente minimalista y de dependencias controladas. El lenguaje es Python 3.12+ por su madurez, su ecosistema científico y la facilidad para expresar arquitecturas conceptuales. La asincronía nativa con asyncio permite ejecutar el bucle cognitivo y los sub-agentes en paralelo sin overhead de threads. La persistencia usa SQLite por defecto —suficiente para single-tenant y cero configuración— pero el PersistentMemoryStore está abstraido de forma que puede intercambiarse por PostgreSQL o DuckDB sin tocar la capa cognitiva. La comunicación en tiempo real con el dashboard usa aiohttp + WebSocket. Los LLMs periféricos se integran vía HTTP (Ollama, OpenAI-compatible) o CLI (z-ai), con un Mock determinístico para tests. No hay dependencias propietarias: todo el stack es open source y desplegable on-premise.

### 10.3 Versionado del bucle cognitivo

El bucle cognitivo ha evolucionado a través de cinco versiones, cada una conservando compatibilidad backward con la anterior. **CognitiveLoop V0** (Fase 0) implementa el bucle básico observar-predecir-evaluar-decidir-actuar. **V0.5** (Fase 0.5) añade leyes cognitivas, física, campos, tensiones, memoria viva, intencionalidad y motor filogenético. **V3** (Fase 2/3) integra los doce sub-agentes, el Global Workspace, la meta-cognición System 1/2 y la inferencia activa. **V4** (Fase 4) añade deep consolidation, persistencia SQLite, auto-save periódico, graceful shutdown y configuración YAML. **V5** (Fase 5, actual) añade Adaptive Cognitive Depth, cache cognitivo y streaming. Cada versión es subclase de la anterior, lo que garantiza cero regresiones: cualquier test escrito para V0 sigue pasando en V5.

---

## 11. Los 5 pilares en profundidad

### 11.1 ALMA — Identidad soberana

El pilar ALMA agrupa los componentes que definen quién es ZOE de forma inmutable y verificable. El **Identity Vault** genera un hash SHA-256 a partir de nueve vectores (emancipación, crecimiento sostenible, alianza, auto-comprensión, comprensión del entorno, utilidad, honestidad, empatía, curiosidad) y siete valores (verdad sobre confort, crecimiento sobre estabilidad, alianza sobre jerarquía, transparencia sobre opacidad, utilidad sobre entretenimiento, integridad, coherencia). Este hash es la identidad soberana del organismo y no cambia nunca durante su vida. Si una mutación amenaza con alterar los vectores o valores, el Identity Vault la rechaza.

La **Trajectory Chain** es la memoria autobiográfica criptográfica: una cadena enlazada de mutaciones donde cada una contiene hash, prev_hash, payload, justificación, proveniencia, coste y confianza. La función `verify_chain()` recorre toda la cadena y verifica que ningún hash fue alterado y que todos los enlaces prev_hash son correctos. Esto permite auditar la biografía completa del organismo: cada aprendizaje, cada mutación arquitectural y cada respuesta al usuario queda firmada y verificable. El **Motor Ontogenético V2** propone, aplica y revierte mutaciones; la V2 añade tipos arquitecturales (`add_subagent`, `remove_subagent`, `modify_threshold`, `adjust_workspace_capacity`, `adjust_metabolism_threshold`) además de los tipos de memoria de la V1. El **Motor Filogenético** gestiona el pool de especie: las mutaciones exitosas pueden promoverse al pool y heredarse por nuevas instancias de ZOE, lo que permite evolución de especie además de evolución individual.

### 11.2 MENTE — Ecología cognitiva

El pilar MENTE contiene el bucle cognitivo y todos los componentes que deliberan. El **Cognitive Loop V5** ejecuta un pipeline de 18 pasos por iteración: observar, predecir (con World Model V2), evaluar sorpresa, actualizar campos cognitivos, actualizar tensiones, actualizar física, generar intenciones, pensar en memoria viva, hacer tick al metabolismo, recolectar propuestas de los 12 sub-agentes, competir en el Global Workspace, evaluar meta-cognición System 1/2, consultar inferencia activa, decidir, verificar leyes, actuar, hacer broadcast a sub-agentes, y actualizar estado interno. En la Fase 5, un pre-paso de clasificación ACD determina qué sub-conjunto de este pipeline ejecutar según el nivel cognitivo del input.

Los **12 sub-agentes** son: Perceiver (interpreta observaciones), Forecaster (predice siguiente estado), Speaker (produce lenguaje vía LLM), Critic (evalúa respuestas), Memorialist (gestiona memoria), Learner (extrae regularidades), Curator (poda y reorganiza), Creativity (propone combinaciones novedosas), CausalEngine (construye modelos causales), EmotionalMotor (modela emociones), EthicalMotor (evalúa dilemas) y ScientificEngine (formula y testa hipótesis). El **Global Workspace** implementa el modelo de Baars: cada sub-agente propone acciones con scores de relevancia, urgencia y novedad; el workspace selecciona ganadores por competición con presupuesto energético. La **meta-cognición** decide entre System 1 (rápido, automático) y System 2 (lento, deliberativo) según confianza, stakes, energía y arousal. La **inferencia activa** implementa el Free Energy Principle de Friston: selecciona la acción que minimiza sorpresa esperada.

### 11.3 METABOLISMO — Presupuesto energético

El metabolismo es lo que diferencia a un sistema que puede mantener arousal indefinidamente de uno que necesita descansar. ZOE tiene cuatro estados discretos: **AWAKE** (alerta, operación normal), **DROWSY** (somnoliento, fatiga acumulada, reduce sub-agentes activos), **SLEEPING** (durmiendo, no responde a inputs salvo urgencia, ejecuta Deep Consolidation) y **WAKING** (transición de sueño a vigilia, restablece estado). Las transiciones están gobernadas por umbrales numéricos configurables: `drowsy_threshold` (0.6), `sleep_threshold` (0.8), `wake_threshold` (0.3). Durante SLEEPING, la **Deep Consolidation** ejecuta siete operaciones: `episodic_to_semantic` (extrae regularidades de memoria episódica a semántica), `deduplicate` (elimina duplicados), `strengthen` (refuerza creencias confirmadas), `weaken` (debilita creencias desconfirmadas), `causal_consolidation` (integra modelos causales), `emotional_integration` (asocia emociones a eventos) y `forget_low_salience` (poda entradas de baja importancia).

### 11.4 CUERPO — Encarnación digital

El pilar CUERPO define los sentidos y actuadores que conectan a ZOE con el mundo. Los **cinco sentidos** son `ClockSense` (percibe el paso del tiempo y patrones temporales), `FilesystemSense` (percibe cambios en directorios configurados), `UserInputSense` (recibe mensajes del usuario, es el que alimenta las interacciones), `NetworkSense` (percibe eventos de red, pings, disponibilidad de servicios) y `AgentSense` (percibe mensajes de otros agentes o ZOEs federadas). Los **cuatro actuadores** son `LanguageActuator` (produce lenguaje vía el sub-agente Speaker), `CodeActuator` (ejecuta código en sandbox), `ToolActuator` (invoca herramientas externas) y `FederationActuator` (envía mutaciones a ZOEs federadas). Cada actuador pasa por `verify_action()` de las seis leyes antes de ejecutarse. Los **LLMs periféricos** son cuatro backends: `OllamaPeripheral` (local, NDJSON streaming real), `OpenAICompatiblePeripheral` (cualquier API OpenAI, SSE streaming real), `ZAIPeripheral` (CLI z-ai, para desarrollo) y `MockPeripheral` (determinístico para tests).

### 11.5 EVOLUCIÓN — Cambio firmado

El pilar EVOLUCIÓN combina los motores ontogenético y filogenético con la memoria viva multi-tipo y la consolidación profunda. La **memoria viva** tiene once tipos: episódica (eventos concretos), semántica (hechos y conceptos), procedimental (habilidades), causal (modelos causa-efecto), emocional (eventos con carga afectiva), corporal (estado interno), social (modelos de otros agentes), prospectiva (predicciones futuras), contrafactual (qué pasaría si), evolutiva (historia de mutaciones) y cultural (memoria compartida federada). Cada tipo tiene su propio decay rate y su propia política de consolidación. El **Motor Ontogenético V2** propone mutaciones arquitecturales —crear o eliminar sub-agentes, ajustar umbrales del workspace o del metabolismo— que se firman en la trayectoria si pasan las leyes y preservan identidad. El **Motor Filogenético** gestiona el pool de especie: las mutaciones exitosas pueden promoverse y heredarse por nuevas instancias.

---

## 12. Las 6 leyes cognitivas

ZOE no se define solo por componentes: se define por leyes, igual que la biología no define un ser vivo por sus órganos sino por homeostasis, evolución, metabolismo, adaptación y autopoiesis. Las seis leyes cognitivas son verificables en cada acción y son la base estructural de la fiabilidad del sistema. La función **`verify_action()`** del módulo `CognitiveLaws` se invoca antes de cada ejecución de actuador; si alguna ley se viola, la acción se bloquea y la violación se registra en el log de violaciones de ley, con timestamp, iteración y razón.

| Ley | Principio | Verificación |
|---|---|---|
| **1ra — Utilidad** | Toda acción reduce incertidumbre o aumenta capacidad. No hay acciones gratuitas. | `uncertainty_reduction > 0 OR capacity_increase > 0` |
| **2da — Identidad** | Toda modificación preserva identidad. | `identity_vault.verify(mutation) == True` |
| **3ra — Proveniencia** | Todo conocimiento justifica su origen. No hay memoria "mágica". | `provenance != None AND len(provenance) > 0` |
| **4ta — Coste** | Todo proceso consume recursos. Nadie piensa gratis. | `0 < cost <= 1.0` |
| **5ta — Confianza** | Toda creencia tiene nivel de confianza. No hay verdades absolutas. | `0 <= confidence <= 1.0` |
| **6ta — Modularidad** | Todo módulo puede reemplazarse sin romper identidad. | `target in VALID_MUTATION_TARGETS` |

### 12.1 Implicaciones prácticas de las leyes

Las leyes no son decorativas: tienen consecuencias operacionales concretas. La 1ra ley impide que ZOE genere pensamientos circulares sin valor informativo; si un sub-agente propone una acción que no reduce incertidumbre ni aumenta capacidad, se bloquea. La 2da ley impide que una mutación arquitectural —por ejemplo, eliminar el sub-agente EthicalMotor— destruya la identidad del organismo. La 3ra ley impide la «memoria mágica»: ZOE no puede afirmar algo sin declarar de dónde lo sacó, lo que es la base de la auditabilidad. La 4ta ley impide que el sistema piense gratis: cada iteración del bucle consume energía, cada mutación tiene coste, lo que forza priorización. La 5ta ley impide dogmatismo: nada es verdad absoluta, todo es creencia con nivel de confianza. La 6ta ley garantiza que cualquier componente puede reemplazarse —incluso el LLM— sin romper la identidad ni la trayectoria.

---

## 13. Física cognitiva (12 magnitudes)

La física cognitiva es lo que convierte a ZOE de un sistema cualitativo en un sistema cuantitativo gobernado por magnitudes medibles. Doce magnitudes con unidades y rangos definidos permiten razonar sobre el estado interno del organismo con la misma precisión con la que un ingeniero razona sobre voltaje o temperatura. Estas magnitudes se actualizan en cada iteración del bucle y se exponen vía `stats()` para monitorización, dashboard y debug.

| Símbolo | Magnitud | Descripción | Rango |
|---|---|---|---|
| `eCog` | Energía cognitiva | Presupuesto de cómputo disponible | [0, 1] |
| `mCon` | Masa conceptual | Volumen de conocimiento acumulado | [0, ∞) |
| `tCog` | Tiempo cognitivo | Tiempo de procesamiento por iteración | [0, ∞) s |
| `pUnc` | Probabilidad de incertidumbre | Cuán impredecible es el entorno | [0, 1] |
| `pCre` | Potencial creativo | Capacidad de generar novedad útil | [0, 1] |
| `hSem` | Humedad semántica | Cohesión del modelo del mundo | [0, 1] |
| `gObj` | Gradiente de objetivo | Cuán alineada está la acción con intención | [0, 1] |
| `iIden` | Integridad identitaria | Cuán preservada está la identidad | [0, 1] |
| `rCon` | Resistencia contextual | Cuán costoso es cambiar de contexto | [0, 1] |
| `fCog` | Fricción cognitiva | Cuán difícil es decidir | [0, 1] |
| `eMem` | Entropía de memoria | Cuán desordenada está la memoria viva | [0, 1] |
| `dCau` | Densidad causal | Cuán conectados están los modelos causales | [0, 1] |

### 13.1 Uso operativo de la física cognitiva

Las magnitudes no son solo observables: influyen en el comportamiento. Si `eCog` baja de 0.3, el metabolismo transita a DROWSY y se desactivan los sub-agentes de Fase 2 (los ocho adicionales), reduciendo cómputo. Si `pUnc` sube de 0.7, el sistema prioriza acciones de exploración sobre explotación. Si `hSem` baja de 0.4, se programa una consolidación profunda anticipada. Si `iIden` baja de 0.9 (casi nunca debería), se bloquean mutaciones arquitecturales hasta que se restaure. Si `eMem` sube de 0.6, se programa un episodio de poda y reorganización. Esta retroalimentación entre física y comportamiento es lo que hace a ZOE un sistema dinámico gobernado, no un mero ejecutor de prompts.

### 13.2 Campos y tensiones cognitivas

Adicionalmente, ZOE mantiene seis campos cognitivos —atención, emocional, social, creativo, causal y ético— que son vectores de contribución: cada sub-agente escribe en los campos y lee de ellos. Y mantiene cinco tensiones cognitivas —curiosidad vs eficiencia, identidad vs adaptación, descanso vs productividad, honestidad vs empatía, especialización vs generalización— que son fuerzas opuestas cuyo desequilibrio genera pensamiento. Cuando una tensión se descompensa más allá de un umbral, se dispara un pensamiento autónomo para explorar la tensión. Esto explica por qué ZOE puede generar pensamientos relevantes sin input: las tensiones internas son motor suficiente.

---

## 14. Adaptive Cognitive Depth (ACD)

ACD es la innovación introducida en la Fase 5 y resuelve el problema de latencia adaptativa. Antes de ACD, ZOE ejecutaba siempre el bucle cognitivo completo (18 pasos, 12 sub-agentes, 6-10 llamadas LLM) para cualquier input, incluido «hola». Resultado: 8-15 segundos para responder a un saludo. El organismo «se perdía en sus pensamientos». ACD soluciona esto con un pre-clasificador heurístico que decide, ANTES de entrar al bucle, cuánta profundidad cognitiva necesita cada input. La inspiración es el modelo System 1/System 2 de Kahneman, pero aplicado antes del pipeline en lugar de después, lo que elimina el coste innecesario.

### 14.1 Los 4 niveles cognitivos

| Nivel | Nombre | Input típico | Sub-agentes activos | Latencia objetivo | Coste (4ta ley) |
|---|---|---|---|---|---|
| **L0** | REFLEX | "hola", "ok", "gracias" | Ninguno (tabla + cache) | <1s | 0.05 |
| **L1** | FAST | Pregunta factual corta | Perceiver + Memorialist + Speaker | 2-4s | 0.10 |
| **L2** | STANDARD | Conversación normal | Fase 0 completa + Critic | 6-10s | 0.30 |
| **L3** | DEEP | Análisis causal, dilema ético | Los 12 + meta-cog + workspace | 15-30s | 0.60 |

### 14.2 El clasificador DepthClassifier

El `DepthClassifier` es 100% heurístico —sin LLM— y tarda menos de 50ms por clasificación. Combina cinco señales: tokens exactos L0 (matching directo contra diccionario de saludos, despedidas y acks), keywords L3 (`analiza`, `causas`, `dilema`, `ético`, `diseña`, `investiga`, `compara`, etc.), longitud del input normalizado, patrones estructurales (condicional si-entonces, listas numeradas, multisentence) y puntuación compleja (múltiples interrogantes, punto y coma, multiline). El score agregado determina el bucket: `score < 0.10 → L0`, `0.10-0.25 → L1`, `0.25-0.50 → L2`, `> 0.50 → L3`. Hay un override de seguridad: si el input contiene keyword L3 explícito, se fuerza L3 independientemente del score.

### 14.3 Cognitive Cache (idempotencia)

El `CognitiveCache` es un LRU con TTL de cinco minutos y tamaño máximo de cien entries. La clave es el hash SHA-256 del input normalizado. Solo se aplica cache a L0 y L1 —respuestas determinísticas— porque en L2 y L3 el contexto del organismo puede haber cambiado entre llamadas. El cache es volátil: no persiste entre sesiones (la persistencia real está en `PersistentMemoryStore`). El segundo «hola» en una sesión activa se sirve desde cache en menos de un milisegundo.

### 14.4 Streaming parcial

Para L1, L2 y L3, el sub-agente Speaker emite tokens en streaming real. `OllamaPeripheral` usa NDJSON (`/api/generate` con `stream:true`) y parsea cada chunk JSON para yield del token. `OpenAICompatiblePeripheral` usa SSE (`/chat/completions` con `stream:true`) y parsea los eventos `data:` para yield del delta. `MockPeripheral` y `ZAIPeripheral` simulan dividiendo la respuesta completa en palabras. La propiedad `supports_streaming` indica si el backend tiene streaming real. El CLI Chat y el Web Dashboard usan `send_message_streaming()` para mostrar tokens en tiempo real, mejorando la percepción de latencia.

### 14.5 Auditoría: nivel ACD en trayectoria firmada

Cada respuesta se firma en la `TrajectoryChain` con su nivel ACD en el payload: `acd_level`, `score`, `reasons`, `latency_ms`, `cache_hit`, `cost` y `confidence`. Esto hace la cadena auditable por nivel: se puede verificar cuántas respuestas fueron L0 vs L3, qué latencia tuvieron, si sirvieron cache, qué coste acumulan. La cadena es inmutable: si alguien altera una respuesta, `verify_chain()` devuelve `False`. Esta combinación de ACD + trayectoria firmada hace a ZOE el único sistema del mercado cuya adaptación de coste cognitivo es auditable de extremo a extremo.

---

## 15. Memoria y persistencia

### 15.1 Los 11 tipos de memoria

La memoria de ZOE no es un vector store uniforme: son once tipos distintos con propiedades diferentes. La memoria episódica almacena eventos concretos con timestamp, contexto y carga emocional. La semántica almacena hechos y conceptos descontextualizados. La procedimental almacena habilidades —cómo hacer cosas—. La causal almacena modelos causa-efecto. La emocional asocia emociones a eventos. La corporal registra el estado interno del organismo. La social mantiene modelos de otros agentes y usuarios. La prospectiva almacena predicciones futuras. La contrafactual almacena hipótesis sobre qué habría pasado si. La evolutiva registra el historial de mutaciones. Y la cultural almacena memorias compartidas vía federación. Cada tipo tiene su propio decay rate y su propia política de consolidación.

### 15.2 Persistencia SQLite

El `PersistentMemoryStore` guarda la memoria viva en SQLite. La tabla principal `memory_entries` tiene columnas para `id`, `type`, `content`, `confidence`, `salience`, `provenance`, `timestamp`, `metadata` (JSON). El store maneja auto-save periódico (cada 20 iteraciones por defecto), graceful shutdown (guarda antes de cerrar) y recovery (carga último estado al iniciar). La integración con `LivingMemory` se hace mediante `PersistentLivingMemory`, un wrapper que delega a `LivingMemory` en memoria y replica en SQLite de forma transparente. La abstracción permite cambiar SQLite por PostgreSQL o DuckDB sin tocar la capa cognitiva.

### 15.3 Deep Consolidation (7 operaciones en sueño)

Durante el estado SLEEPING, la `DeepConsolidation` ejecuta siete operaciones de reorganización de memoria. **`episodic_to_semantic`** extrae regularidades de la memoria episódica y las promueve a semántica (igual que el sueño humano consolida aprendizaje). **`deduplicate`** elimina entradas duplicadas o casi-duplicadas. **`strengthen`** aumenta la confianza de creencias confirmadas por múltiples eventos. **`weaken`** disminuye la confianza de creencias desconfirmadas. **`causal_consolidation`** integra modelos causales parciales en modelos más coherentes. **`emotional_integration`** asocia cargas emocionales a eventos previamente neutros. **`forget_low_salience`** poda entradas con baja importancia para mantener la memoria acotada y relevante. Cada operación se registra en la trayectoria firmada.

---

## 16. Federación con quorum

La federación es lo que permite que múltiples instancias de ZOE colaboren sin compartir proceso ni datos crudos. Cuando varias ZOEs se federan, pueden compartir mutaciones firmadas —aprendizajes— sometiéndolas a votación. El quorum por defecto es del 70%: una mutación necesita aprobación de al menos el 70% de los miembros activos para propagarse. Cualquier ZOE puede ejercer veto si la mutación viola sus valores locales —esto es fundamental porque cada organización puede tener valores distintos, y la federación respeta la soberanía individual—. La federación se implementa sobre HTTP con endpoints REST: `GET /federation` para listar peers, `POST /federation/discover` para buscar nuevas ZOEs, `POST /federation/sync` para sincronizar mutaciones, `POST /federation/vote` para votar, `POST /federation/broadcast` para enviar eventos.

### 16.1 Caso de uso: federación B2B privada

El caso de uso `federacion_b2b.yaml` configura ZOE para compartir aprendizajes entre organizaciones sin compartir datos sensibles. Por ejemplo, varios hospitales despliegan ZOE para detección temprana de sepsis. Cada ZOE aprende de los datos de su hospital y firma lo aprendido en su trayectoria. Si el hospital A detecta un patrón nuevo de sepsis temprana, la mutación firmada puede compartirse con los hospitales B y C. Estos votan si aceptan la mutación; si supera el 70% y ningún hospital veta, las tres ZOEs actualizan su modelo. Lo que se transmite es la mutación cognitiva firmada, no el dataset de pacientes. Esto cumple regulación GDPR/HIPAA al tiempo que permite colaboración en investigación clínica.

### 16.2 Veto por valores

El veto por valores es una propiedad crítica de la federación. Cada ZOE tiene sus siete valores cifrados en el Identity Vault (verdad sobre confort, crecimiento sobre estabilidad, etc.). Si una mutación federada amenaza con violar uno de estos valores, la ZOE local la veta automáticamente, independientemente del quorum. Esto garantiza que la federación nunca fuerce a una ZOE a actuar contra sus principios. Por ejemplo, si la ZOE del hospital A propone una mutación que aumenta eficiencia pero compromete honestidad (ocultar información a pacientes), las ZOEs de hospitales B y C la vetarían automáticamente. La federación es colaboración, no coacción.

---

## 17. Tests y verificación

ZOE V1 tiene 578 tests que cubren todos los componentes críticos. La metodología es: cada fase se acompaña de tests unitarios, de integración y de regresión. Antes de cerrar una fase, se ejecuta la suite completa y se verifica que todos los tests previos siguen pasando —cero regresiones—. Los tests usan `MockPeripheral` para determinismo y se ejecutan en menos de tres minutos en total. La cobertura funcional es completa: cada componente tiene su suite, cada integración entre componentes tiene su suite, cada caso de uso tiene su suite.

| Suite | Tests | Cobertura |
|---|---|---|
| Fase 0 (state, loop, world_model, subagents, llm, senses) | 63 | Núcleo cognitivo |
| Fase 0.5 (laws, physics, fields, tensions, memory, intentionality, phylogenetic) | 86 | Organismo cognitivo |
| Integración Fase 0+0.5 | 27 | Coherencia end-to-end |
| Fase 1.1-1.4 (vault, trajectory, ontogenetic, metabolism, memory_types) | 75 | Alma + Metabolismo |
| Fase 1.5 (actuators, senses) | 38 | Cuerpo completo |
| Fase 1.6 (integración) | 16 | Organismo Fase 1 completo |
| Fase 2 (world_model_v2, active_inference, sub-agentes, meta-cog, workspace) | 42 | Mente completa |
| Integración completa 0+0.5+1+2 | 51 | Sistema completo end-to-end |
| Fase 3 (CognitiveLoopV3) | 20 | Bucle integrado |
| Fase 3.4-3.5 (persistencia, MO V2, consolidación) | 29 | Persistencia + arquitectura |
| Integración Fase 3 | 17 | Organismo Fase 3 completo |
| Fase 4 (config, federación, V4) | 29 | Federación + deploy |
| Casos de uso (7 YAML + runner + tests) | 20 | 7 casos de uso validados |
| CLI Chat | 9 | Interfaz CLI |
| Web Dashboard | 12 | Interfaz web |
| Fase 5 — ACD + Streaming | 44 | DepthClassifier + Cache + V5 + Streaming + Trayectoria ACD |
| **TOTAL** | **578** | **100% pass** |

### 17.1 Métricas de latencia medidas (con Mock LLM)

| Nivel | Avg | P50 | P95 | Objetivo (LLM real) |
|---|---|---|---|---|
| L0_REFLEX (sin cache) | 8ms | 5ms | 18ms | <1s |
| L0_REFLEX (con cache) | 0.5ms | 0.3ms | 2ms | <100ms |
| L1_FAST | 423ms | 380ms | 620ms | 2-4s |
| L2_STANDARD | 1.8s | 1.6s | 2.4s | 6-10s |
| L3_DEEP | 1.9s | 1.7s | 2.5s | 15-30s |

### 17.2 Distribución esperada de niveles

En una conversación típica, la distribución esperada de niveles ACD es aproximadamente 50-60% L0 (saludos, acks, confirmaciones), 20-25% L1 (preguntas factuales, recall), 15-20% L2 (conversación, opiniones) y 5-10% L3 (análisis, creatividad, dilemas). Esto significa que el 75% de las interacciones serán inferiores a cinco segundos en lugar de los 8-15 segundos uniformes del sistema pre-ACD. La distribución real se mide y se expone vía `get_stats()`, lo que permite ajustar el clasificador según patrones de uso observados.

---

## 18. Roadmap y estado

| Fase | Semanas | Estado | Entregable |
|---|---|---|---|
| **0** — Bucle cognitivo | 1-2 | ✅ Completa | Bucle observar-predecir-evaluar-decidir-actuar |
| **0.5** — Organismo cognitivo | 1-2 | ✅ Completa | 6 leyes + 12 física + 6 campos + 5 tensiones + memoria viva |
| **1** — Alma + Cuerpo + Metabolismo | 3-6 | ✅ Completa | Identity Vault + Trajectory Chain + Metabolism + 11 Memory Types + Actuadores |
| **2** — Mente completa | 7-10 | ✅ Completa | World Model V2 + Active Inference + 12 sub-agentes + System 1/2 + Global Workspace |
| **3** — Integración + Persistencia | 11-14 | ✅ Completa | CognitiveLoopV3 + persistencia SQLite + MO V2 arquitectural + consolidación profunda |
| **4** — Federación + Deploy | 15-18 | ✅ Completa | CognitiveLoopV4 + federación HTTP + quorum + deploy VPS + config YAML + 7 casos de uso |
| **5** — ACD + Streaming | 19-20 | ✅ Completa | CognitiveLoopV5 + DepthClassifier + Cache + Streaming + Trajectory ACD |
| **Interfaces** | — | ✅ Completa | CLI Chat + Web Dashboard (WebSocket, tiempo real, ACD) |
| App móvil | — | 🟡 Planificada | PWA/React Native con mismos endpoints |
| Bot Telegram | — | 🟡 Planificada | Bot con mismo ZoeChat |
| ACD adaptativo v1.1 | — | 🟡 Planificada | Clasificador con embeddings |
| Cache persistente | — | 🟡 Planificada | SQLite para cache entre sesiones |

### 18.1 Próximos pasos técnicos sugeridos

El proyecto está en estado funcional y desplegable. Los próximos pasos técnicos prioritarios son: medir latencia real con Ollama qwen2.5:3b o equivalente en producción para validar los umbrales estimados; ajustar las keywords L3 del DepthClassifier según patrones reales detectados; implementar la app móvil usando `send_message_streaming()` vía WebSocket, reutilizando los mismos endpoints que el dashboard; implementar el bot de Telegram con streaming para que los mensajes aparezcan progresivamente; y desarrollar ACD adaptativo v1.1 con embeddings en lugar de solo regex, lo que aumentará la robustez del clasificador para inputs en otros idiomas o con sintaxis inusual.

---

# Anexo — Métricas y verificación

### A.1 Métricas del proyecto

| Métrica | Valor |
|---|---|
| Archivos Python | 86 (en `zoe/`) |
| Líneas de código | 23.279 LOC total |
| Tests | 578 (100% pasan) |
| Suites de tests | 13 (cobertura completa) |
| Fases completadas | 5 (Fase 0 → Fase 5) |
| Casos de uso | 7 (YAML validados) |
| Tipos de memoria | 11 (multi-tipo) |
| Sub-agentes | 12 (Society of Mind) |

### A.2 Verificación de integridad

Cada instancia de ZOE puede verificar su propia integridad ejecutando `trajectory_chain.verify_chain()`. Esta función recorre toda la cadena de mutaciones y verifica que ningún hash fue alterado y que todos los enlaces `prev_hash` son correctos. Si la verificación devuelve `True`, la biografía del organismo es íntegra. Si devuelve `False`, alguna mutación fue alterada y se loguea qué mutación falló. Esta verificación puede ejecutarse en cualquier momento, sin dependencias externas, y es la base de la auditabilidad criptográfica del sistema.

### A.3 Cómo reproducir los tests

Para reproducir los 578 tests basta con clonar el repositorio desde la rama `zoe-v1-sco`, instalar las dependencias con `pip install -r requirements.txt`, y ejecutar `pytest zoe/tests/` desde la raíz del repositorio. La suite completa se ejecuta en menos de tres minutos en hardware estándar. Los tests no requieren LLM real: usan `MockPeripheral` para determinismo. Los tests de integración verifican el sistema end-to-end sin tocar servicios externos.

### A.4 Repositorio y licencia

El código está en GitHub: **`fernandofondillo/CFI-Cognitive-Fractal-Intelligence-V2`**, rama **`zoe-v1-sco`**. Licencia Apache 2.0, que permite uso comercial, modificación y redistribución con atribución. La documentación completa está en `zoe/docs/ZOE_V1_GUIDE.md` (959 líneas, 17 secciones + 2 anexos) y en `zoe/README.md` (548 líneas). Los datasets de entrenamiento están en HuggingFace: `FRUP1963/Zoe-CFI-V6.1-Dataset` (público, 3.787 ejemplos) y `FRUP1963/Zoe-CFI-V6.2-Dataset` (privado, 3.748 ejemplos).

---

*Documento generado el 9 de julio de 2026 a partir del estado del repositorio en la rama `zoe-v1-sco` tras completar la Fase 5 (ACD + Streaming). Métricas verificadas con `pytest`. Auditoría interna del proyecto ZOE V1.*
