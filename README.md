# Identificación de tipologías urbanas en Córdoba mediante datos abiertos y clustering

<p align="center">
  <img src="figures/mapa_clusters.png" alt="Mapa de Clusters Córdoba" width="700"/>
</p>

## Descripción del problema

El crecimiento de las ciudades muchas veces ocurre de manera desigual, generando zonas con profundas carencias estructurales que conviven con otras de alta consolidación urbana. Este proyecto fue diseñado como un **caso de estudio pedagógico** para explorar la medición y clasificación de la desigualdad territorial en la ciudad de Córdoba Capital (Argentina) utilizando herramientas de Ciencia de Datos.

A través del cruce de datos estructurales de pobreza histórica (NBI del Censo Nacional) con el despliegue moderno de infraestructura a nivel de servicios públicos (gestión municipal 2023), este material permite a los estudiantes aplicar algoritmos para detectar patrones de segregación y construir perfiles que faciliten la comprensión de la dinámica urbana.

## Preguntas de investigación

1. ¿Qué barrios de Córdoba Capital presentan un mayor grado de vulnerabilidad socioeconómica y déficits de infraestructura?
2. ¿Existe una relación matemática comprobable entre los niveles de pobreza estructural (NBI) y la escasez de acceso a servicios básicos como salud, educación, transporte y seguridad?
3. ¿Se pueden identificar **tipologías urbanas** (clústeres naturales) que agrupen a los barrios bajo características comunes sin la intervención subjetiva humana?

## Dataset

La investigación se sustenta en un ecosistema de datos cruzados obtenidos a partir del cruce espacial de archivos GIS y bases tabulares:
* **Unidad de análisis:** Los barrios de la ciudad de Córdoba Capital.
* **Cantidad:** **495 unidades territoriales**. Esta cifra corresponde a la cartografía oficial utilizada para este estudio, garantizando consistencia espacial en el análisis (aunque pueden existir variaciones menores según la fuente cartográfica utilizada).
* **Variables incluidas:** 
  * Necesidades Básicas Insatisfechas (% NBI)
  * Infraestructura Educativa (Escuelas provinciales y municipales)
  * Transporte Público (Paradas y recorridos de colectivos)
  * Salud y Seguridad (Dispensarios, comisarías, luminaria pública)
  * Centros Vecinales (Tejido social e infraestructura ciudadana comunitaria)

## Metodología

El proyecto propone un *pipeline* (flujo de trabajo) reproducible, ideal para el aprendizaje de las distintas etapas de un proyecto de datos:

1. **Recolección y Limpieza de datos:** Tratamiento de fuentes heterogéneas (GeoJSON y CSV), manejo de valores nulos y estandarización de nomenclaturas.
2. **Integración Geoespacial:** Uso de *GeoPandas* para asignar equipamiento urbano (escuelas, paradas) a cada polígono de barrio mediante técnicas de proximidad y pertenencia espacial.
3. **Feature Engineering:** Creación de nuevas métricas (como índices por habitante) para permitir comparaciones equitativas entre barrios de distinto tamaño.
4. **Normalización:** Proceso de ajustar las escalas de los datos (media 0 y varianza 1) para que variables con rangos muy distintos (ej: población vs \% NBI) tengan el mismo peso en el modelo.
5. **Clustering no supervisado (K-Means):** Algoritmo que agrupa automáticamente los datos basándose en sus similitudes, sin necesidad de etiquetas previas de "bueno" o "malo".
6. **Selección de K (Elbow Method o Método del Codo):** Técnica visual para elegir el número óptimo de grupos buscando el punto donde agregar más clusters deja de aportar una mejora significativa en la cohesión interna (inercia).

<p align="center">
  <img src="figures/elbow.png" alt="Método del Codo" width="500"/>
</p>

## Resultados

El modelo K-Means **sugiere** la existencia de 3 perfiles urbanos con características diferenciadas:

1. **Núcleo Consolidado (Cluster 0):** Áreas con los más bajos niveles de necesidades estructurales y alta aglomeración de servicios.
2. **Zona en Transición (Cluster 1):** Sectores periurbanos con niveles medios de NBI y distribución de infraestructura variable.
3. **Periferia Vulnerable (Cluster 2):** Aglomeraciones de alta criticidad social con déficits acentuados de presencia estatal.

### Tabla de Perfiles (Promedios)
| Cluster | % NBI | Escuelas (x1000) | Paradas (x1000) | Score Infra. |
|:---|---:|---:|---:|---:|
| Núcleo Consolidado | 2.83 | 0.58 | 5.06 | 0.15 |
| Zona en Transición | 3.90 | 2.68 | 15.96 | 0.54 |
| Periferia Vulnerable | 14.14 | 0.81 | 3.40 | 0.17 |

<p align="center">
  <img src="figures/perfil_clusters.png" alt="Perfil Proporcional de Variables" width="700"/>
</p>

## Visualizaciones

A continuación se exponen resultados visuales extra que refuerzan el entendimiento de la matriz general poblacional para las variables estudiadas.

### Reducción de Dimensionalidad (PCA)
El PCA (Análisis de Componentes Principales) es una técnica que permite simplificar muchas variables en solo dos ejes visuales, manteniendo la mayor cantidad de información posible para entender cómo se separan los grupos.

<p align="center">
  <img src="figures/clusters_pca_visualization.png" alt="PCA Tipologías" width="700"/>
</p>

### Mapa de Calor - Correlaciones Cruzadas

<p align="center">
  <img src="figures/heatmap_correlacion.png" alt="Correlación" width="700"/>
</p>

### Sectores Críticos (Vulnerabilidad Extrema)

<p align="center">
  <img src="figures/ranking_vulnerables.png" alt="Top 10 Vulnerable" width="700"/>
</p>

Este análisis exploratorio permite identificar patrones de interés para profundizar en investigaciones urbanas:
* Los resultados **indican posibles patrones** de conformación Centro-Periferia, donde la accesibilidad a servicios parece disminuir hacia los bordes de la mancha urbana.
* Se observa una **tendencia de correlación** (Heatmap) entre el \% de NBI y la densidad de infraestructura, lo que invita a reflexionar sobre cómo el entorno construido impacta en la calidad de vida.
* El caso de estudio **permite explorar** cómo la ciencia de datos puede complementar el diseño de políticas públicas mediante el diagnóstico territorial basado en evidencia.

## Limitaciones del análisis
Es importante reconocer las limitaciones de este ejercicio pedagógico:
* **Temporalidad:** Los datos provienen de distintas fuentes y años (Censo vs. Catastro municipal), lo que puede generar desfasajes en la realidad actual.
* **Correlación vs. Causalidad:** Los hallazgos sugieren asociaciones espaciales pero no prueban que la falta de un servicio sea la causa única de la pobreza.
* **Modelo Simplicado:** El algoritmo K-Means asume grupos de forma esférica y similar tamaño, lo que podría simplificar excesivamente la complejidad real de los barrios.
* **Construcción de variables:** Los índices son aproximaciones construidas por los autores y pueden ser cuestionados o mejorados.

## Trabajo para estudiantes
Este repositorio no es una solución definitiva, sino un punto de partida para el debate:
1. **Validación:** ¿Son coherentes estos clusters con tu conocimiento de la ciudad?
2. **Alternativas:** ¿Qué pasaría si se usaran otros algoritmos como DBSCAN o Clustering Jerárquico?
3. **Nuevos ejes:** ¿Qué otra variable (ej: espacios verdes, criminalidad) agregaría mayor valor al modelo?
4. **Crítica:** Los resultados son sensibles a la normalización elegida. ¿Cómo cambiarían con otro escalador?

## Estructura del repositorio

```text
dataset-desigualdad-cordoba/
├── data/
│   ├── raw/                  # Datasets crudos extraídos originalmente de diversas fuentes
│   └── processed/            # Datasets transformados y unificados listos para IA & EDA
├── notebooks/                
│   ├── 01_limpieza.ipynb     # Proceso de depuración, limpieza de nulos y estandarización
│   ├── 02_analisis.ipynb     # Análisis descriptivo exploratorio visual sobre la población
│   └── 03_modelado.ipynb     # Entrenamiento de algoritmos no supervisados y Machine Learning
├── scripts/                  # Código Python reproducible y encapsulado en módulos
├── figures/                  # Imágenes, plots y salidas geográficas definitivas de reportes
├── requirements.txt          # Dependencias y bibliotecas vitales del entorno Python
└── README.md                 # Informe y documentación del proyecto
```

## Cómo ejecutar

1. Realiza el clone del repositorio a tu disco duro local:
```bash
git clone https://github.com/eber-cba/dataset-desigualdad-cordoba.git
```
2. Instala las dependencias estipuladas dentro del entorno virtual usando `pip`:
```bash
pip install -r requirements.txt
```
3. Navega hacia el directorio de análisis y comienza ejecutar utilizando Jupyter o tu IDE predeterminado:
```bash
jupyter notebook notebooks/01_limpieza.ipynb
```
