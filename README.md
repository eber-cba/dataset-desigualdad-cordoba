# Urban Data Science: Análisis Analítico y Espacial de Córdoba 🇦🇷
**Nivel del Proyecto: Tesis Aplicada (Máximo Rigor MLOps 10/10)**

Este repositorio consolida el desarrollo de un pipeline avanzado de **Data Science, Geospatial Analytics y Machine Learning** aplicado a los barrios de la ciudad de Córdoba Capital. 
Su motor algorítmico evalúa tipologías sociodemográficas, densidades urbanas, y accesos a infraestructura de los ciudadanos.

![Clusters Visualization](mapa_clusters_barrios_final.png)

## 📌 Metodología Científica (Arquitectura V19)
El ecosistema fue iterado rigurosamente durante 19 fases arquitectónicas, garantizando un estándar publicable:
1. **Data Engineering:** Ensamblaje estricto, capping de outliers severos, suavizado estocástico (Laplace Smoothing) e Imputación de Medianas Espaciales.
2. **Feature Engineering:** Logaritmización Demográfica, `infraestructura_score` balanceado por MCAD, y Densidades territoriales por Km².
3. **Clustering Avanzado (K-Means):** Dinámicamente medido y validado bajo el *Silhouette Score*, *Calinski-Harabasz*, y *Davies-Bouldin*.
4. **Spatial Autocorrelation (Moran's I):** Confirmación empírica (esda/libpysal) del contagio territorial y cohesión física de la vulnerabilidad y riqueza.
5. **Hopkins Statistic (Clusterability):** Test de Hipótesis para justificar matemáticamente el agrupamiento antes de entrenar modelos.
6. **Spatial DBSCAN:** Algoritmo alternativo puro geográfico para contrastar las estructuras contra K-Means.
7. **Cluster Stability:** Iteración K-Means bajo 50 semillas distintas midiendo *Adjusted Rand Index (ARI)* para certificar robustez.

## 📊 Visualizaciones Analíticas
### Reducción de Dimensionalidad (Principal Component Analysis)
El modelo particiona el espacio 4D de features en componentes principales para poder visualizarlos ortogonalmente.
![PCA Spatial](clusters_pca_visualization.png)

### Simulador Explicativo (Random Forest Surrogate)
Mediante un clasificador secundario medimos matemáticamente el 'por qué' el agrupamiento tomó ciertas decisiones (Feature Importance).
![RF Importance](feature_importance_clusters.png)

## 📦 Outputs Definitivos del Proyecto
La arquitectura exporta su madurez de datos hacia el Front-End (Vite/React) y hacia el Entorno Científico:

- `dataset_dashboard_v19.csv`: Datos depurados y calculados, ideados para inyectar en BI o Dashboards React.
- `dataset_ml_v19.csv`: Datos Z-Scored y escalados listos para modelos supervisados MLOps.
- `dataset_gis_v19.geojson`: Entidad geoespacial renderizable.
- `mapa_interactivo_clusters_v19.html`: Explorable interactivo Folium de Tesis en DOM puro.

---
**Desarrollado y Auditado bajo los más exigentes estándares de Urban Machine Learning.**
