# 🏙️ Identificación de Tipologías Urbanas en Córdoba mediante Ciencia de Datos

---

## 📌 Resumen

Este proyecto aplica técnicas de **Machine Learning (clustering)** sobre datos abiertos para analizar la **desigualdad urbana en Córdoba Capital (Argentina)**.

A partir de variables como pobreza estructural (NBI) y acceso a servicios públicos, se construyen **tipologías urbanas** que permiten agrupar barrios según su nivel de consolidación socioeconómica.

👉 El resultado es una segmentación interpretable que evidencia la distribución espacial de la vulnerabilidad urbana y facilita la toma de decisiones basada en datos.

---

## 🗺️ Visualización Principal

<p align="center">
  <img src="figures/mapa_clusters_pro.png" alt="Mapa de Clusters Córdoba Profesional" width="700"/>
  <br>
  <i>Segmentación geoespacial de barrios según tipologías urbanas sobre el mapa real de la ciudad.</i>
</p>

---

## 🔍 Exploración Interactiva

> [!IMPORTANT]
>
> ### 🌐 Dashboard en tiempo real
>
> 🔗 https://dashboard-desigualdad-cordoba.vercel.app
>
> Navega sobre el mapa de la ciudad, explora los clústeres y visualiza la distribución del equipamiento urbano de forma interactiva.

---

## 🧠 Problema

El crecimiento urbano no es uniforme. En una misma ciudad conviven:

- 🟢 Zonas altamente desarrolladas
- 🟡 Áreas en transición
- 🔴 Sectores con alta vulnerabilidad

Este proyecto busca responder:

👉 ¿Cómo identificar estos patrones de forma objetiva usando datos?

---

## ❓ Preguntas de investigación

1. ¿Qué barrios presentan mayor vulnerabilidad socioeconómica?
2. ¿Existe relación entre pobreza estructural y acceso a servicios?
3. ¿Es posible identificar tipologías urbanas sin intervención subjetiva?

---

## 📊 Dataset

**Unidad de análisis:** Barrios de Córdoba Capital  
**Cantidad:** 495 unidades territoriales

### Variables clave:

- 📉 % Necesidades Básicas Insatisfechas (NBI)
- 🏫 Infraestructura educativa
- 🚌 Transporte público
- 🏥 Salud y seguridad
- 🏘️ Tejido social

---

## ⚙️ Metodología

El proyecto sigue un pipeline típico de ciencia de datos:

1. 🧹 Limpieza y estandarización de datos
2. 🗺️ Integración geoespacial (GeoPandas + KD-Tree)
3. 🧠 Feature engineering (indicadores normalizados)
4. 📏 Normalización de variables
5. 🤖 Clustering con K-Means
6. 📉 Optimización con método del codo

<p align="center">
  <img src="figures/elbow.png" width="500"/>
  <br>
  <i>K=3 representa el equilibrio óptimo entre simplicidad y capacidad explicativa.</i>
</p>

---

## 📈 Resultados

El modelo identifica **3 tipologías urbanas**:

- 🟢 **Núcleo Consolidado:** alto acceso a servicios, baja vulnerabilidad
- 🟡 **Zona en Transición:** desarrollo intermedio
- 🔴 **Periferia Vulnerable:** alta criticidad social

### 📊 Tabla de perfiles

| Cluster    | % NBI | Escuelas | Transporte | Score Infra |
| ---------- | ----- | -------- | ---------- | ----------- |
| Núcleo     | 2.83  | 0.58     | 5.06       | 0.15        |
| Transición | 3.90  | 2.68     | 15.96      | 0.54        |
| Vulnerable | 14.14 | 0.81     | 3.40       | 0.17        |

---

## 🧠 Conclusiones

- La desigualdad urbana presenta una **fuerte distribución espacial**
- Las zonas vulnerables se concentran en la **periferia**
- El núcleo consolidado se ubica en áreas centrales con mayor acceso a servicios

👉 El clustering permite construir **tipologías objetivas útiles para políticas públicas**

---

## 📊 Visualizaciones Analíticas

### 📉 PCA (Separación de Clusters)

<p align="center">
  <img src="figures/clusters_pca_visualization.png" width="700"/>
  <br>
  <i>Los clusters presentan separación en el espacio de variables, validando el modelo.</i>
</p>

---

### 🔥 Correlaciones

<p align="center">
  <img src="figures/heatmap_correlacion.png" width="700"/>
</p>

---

### 🚨 Zonas críticas

<p align="center">
  <img src="figures/ranking_vulnerables.png" width="700"/>
</p>

---

## ⚠️ Limitaciones

- ⏳ Datos de distintas temporalidades
- ⚠️ Correlación ≠ causalidad
- 📦 Modelo simplificado (K-Means)

---

## 🚀 Mejoras futuras

- 🗺️ Mapas choropleth por barrio
- 📊 Nuevas variables socioeconómicas
- ⚛️ Integración full-stack con React

---

## 📂 Estructura del proyecto

```bash
dataset-desigualdad-cordoba/
├── data/
├── notebooks/
├── scripts/
├── figures/
└── README.md
⚙️ Cómo ejecutar
git clone https://github.com/eber-cba/dataset-desigualdad-cordoba.git
pip install -r requirements.txt
💡 Stack tecnológico

🐍 Python

📊 Pandas / Scikit-learn

🗺️ GeoPandas

📈 Matplotlib / Plotly

📚 Fuentes de datos

IDECOR

Municipalidad de Córdoba

INDEC

❤️ Sobre el proyecto

Desarrollado como caso de estudio de Ciencia de Datos aplicada a problemáticas reales, combinando análisis técnico con impacto social.
```
