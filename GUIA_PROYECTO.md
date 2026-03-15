# Gúia de Ejecución MLOps V19 🚀

Esta guía condensa las instrucciones pragmáticas para reproducir el Pipeline Definitivo (V19) de Urban Analytics, así como la consulta de sus Outputs Académicos.

## Estructura del Proyecto
El pipeline V19 es autosuficiente y de punta a punta. Se alimenta a sí mismo del `base_dataset_cordoba.csv` y reconstruye toda la analítica Geoespacial en una sola iteración de Terminal Matemática.

## 🛠️ Reproducir Resultados

### 1. Preparar el Entorno Vectorial
Instalar las dependencias Científicas y Geoespaciales necesarias (PySal/Folium):
```bash
pip install pandas numpy geopandas shapely scikit-learn matplotlib seaborn libpysal esda folium
```

### 2. Ejecutar Arquitectura Maestra (Pipeline V19)
Posicionado en la raíz del repositorio, forzar al engine a regenerar los datos espaciales y la matriz de K-Means.
```bash
python scripts/regenerar_dataset_v19.py
```
*Output Esperado:* Terminal listando el check progresivo [1/11] a [11/11] con la aprobación del _Integrity Gate_.

### 3. Extraer Gráficos Canónicos
El script base no machaca imágenes por defecto para no consumir Ram innecesaria. Para extraer los recursos puros y gráfos del modelo entrenado, corre el autómata visual:
```bash
python generate_final_visuals.py
```

### 4. Healthcheck & Test Pipeline
Para asegurarte empíricamente que tu compilación no tiene NaNs flotantes o centroides hundidos en África:
```bash
python test_pipeline_integrity.py
```
Si ves `DATA PIPELINE VERIFIED`, el Dataset está en Nivel Tesis.

---

## 🗺️ Visualizador Espacial HTML
El pipeline V19 escupe un mapa renderizado vectorial puro (App de reactividad offline). 
Para manipularlo y explorarlo de inmediato, entra a:
**`mapa_interactivo_clusters_v19.html`** y ábrelo en cualquier explorador como Chrome o Edge.
El visor soporta Zoom nativo e inspección de tooltips (Score de Infraestructura, Clusters, etc) al posar el mouse en el entorno de Carto Dark Matter.
