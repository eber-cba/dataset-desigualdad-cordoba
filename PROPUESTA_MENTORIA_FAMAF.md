# Propuesta de Mentoría | DiploDatos FAMAF 2026 🎓🇦🇷

**Documento elaborado para postulación a Mentor Titular de la Diplomatura en Ciencias de Datos, Aprendizaje Automático y sus Aplicaciones de la Universidad Nacional de Córdoba (FAMAF).**

---

## 1. Información General del Proyecto

* **Título de la Mentoría:** Urban Data Science: Segmentación territorial, desigualdad y análisis geoespacial de la ciudad de Córdoba.
* **Mentor Propuesto:** Eber (Especialista en Datos y Arquitectura de ML).
* **Naturaleza del Dataset:** Datos 100% públicos y abiertos de la Provincia y Municipio de Córdoba (Open Data Córdoba, IDECOR, Censo Provincial). 
* **Privacidad Sensible:** **No aplica.** El dataset está anonimizado y agregado estrictamente a nivel de **Barrio**. No presenta ni un solo registro individual a nivel de persona física o vivienda unifamiliar. Son polígonos urbanos y métricas de densidad. 

## 2. Descripción y Objetivos del Dataset

### Contexto
Las políticas públicas de infraestructura urbana usualmente se trazan bajo intuición política. En esta mentoría, los estudiantes trabajarán con un repositorio `dataset_ml_v19.csv` que aglomera variables poblacionales, cantidad de hogares, índices de pobreza (NBI), y lo cruza espacialmente con equipamiento consolidado mediante GIS (escuelas, centros de salud, seguridad, centros vecinales y paradas de transporte de MoviBus).

### Objetivo Educativo
Plantear un abordaje interdisciplinario de Data Science respondiendo a investigaciones socioeconómicas reales. Los alumnos construirán sistemas de decisión que evalúan matemáticamente qué polígonos de la ciudad concentran las vulnerabilidades más críticas (autocorrelación espacial) y por qué.

---

## 3. Planificación Estructurada de Prácticos (3 Materias Obligatorias)

Bajo la técnica de *Aprendizaje Basado en Proyectos (ABP)*, los alumnos seguirán la trinidad analítica progresando desde la simple estadística al algoritmo pesado:

### Práctico 1: Análisis y Visualización de Datos (AyVD)
**Objetivo:** Comprender la semántica territorial, encontrar inconsistencias en las fuentes estatales y graficar mapas coropléticos interactivos.
* **Tareas a desarrollar:** 
  1. *Data Cleaning:* Identificar missing values, cruzar identificadores de barrios (`fuzzy matching`) de fuentes gubernamentales heterogéneas. Imputar NaNs usando la mediana y crear variables logarítmicas de densidad poblacional por Km².
  2. *Exploratory Data Analysis (EDA):* Histogramas e índices de asimetría para ratios como `educacion_por_1000_hab`.
  3. *GIS Visualization:* Renderizar las densidades de Paradas de Transporte Masivo vs Centros de Salud en un mapa de la ciudad, descubriendo la varianza.

### Práctico 2: Aprendizaje Automático No Supervisado (AANS)
**Objetivo:** Descubrir tipologías urbanas invisibles y certificar su validez (Clusterización Geoespacial).
* **Tareas a desarrollar:** 
  1. *Estandarización:* Transformar y escalar las features demográficas y espaciales usando preprocesamiento estricto.
  2. *Clustering Dinámico:* Encontrar el $K$ óptimo de Córdoba usando los scores Elbow Curve, Silhouette y Davies-Bouldin. 
  3. *DBSCAN vs K-Means:* Evaluar un clustering de distancias geográficas (radianes) contra el clustering social (K-Means), explicando fenómenos demográficos.
  4. *Evaluación MLOps:* Aplicar el *Clusterability Test de Hopkins* para que el alumno aprenda a dudar de sus hallazgos estadísticos.  

### Práctico 3: Aprendizaje Automático Supervisado (AAS)
**Objetivo:** Arquitectar modelos predictivos y descifrarlos, evitando caer en algoritmos "caja negra".
* **Tareas a desarrollar:** 
  1. *Predicción de Clusters Categóricos:* Entrenar Random Forest, Regresión Logística y XGBoost Multiclase para intentar predecir el perfil socio-urbano de un barrio ciego.
  2. *Interpretación Aleatoria:* Utilizar la clasificación para minar y abstraer **Feature Importances**. Aquí el alumno descifrará científicamente que el "Ratio de Colegios vs Demografía" influye más en la clase socioeconómica que la cantidad de Dispensarios Médicos.
  3. *Detección de Subdesarrollo Crítico:* Entrenar algoritmos de Isolation Forest para flaggear Outliers Extremos de manera analítica en el mapa urbano de manera de asistir hipotéticamente a un plan de obra pública del Gobierno Provincial. 

---

## 4. Cronograma Estimado (Junio - Octubre)

* **Preparación Total a Cargo del Mentor (5 horas):** El pipeline iterativo del Dataset Base (V19) incluyendo todas las variables sintéticas ya está masterizado, con diccionarios de datos documentados y sanetizados, ahorrando enorme fricción inicial a los alumnos y garantizando cero demoras operativas.
* **Seguimiento Mentorizado (30 horas / 2 Grupos):** Encuentros virtuales periódicos, pull requests compartidos del avance y resolución heurística de los problemas matemáticos. Producción de videos del "pitch" analítico final emulando reportes gerenciales no técnicos.
