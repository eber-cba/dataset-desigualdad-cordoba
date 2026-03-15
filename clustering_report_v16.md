# Reporte de Clustering MLOps V16 (Senior Review)

## 1. Selección del Nivel 'K' Libre de Leakage
**Decisión Arquitectónica:** K-Means matemático puro sin sesgo de colinealidad. K Óptimo: 5.

### 🎓 Explicación Metodológica (Nota de Autor)
> El modelo arrojó un Silhouette Score global de **0.272**. En datasets territoriales y socio-urbanos heterogéneos es académicamente común obtener Silhouette Scores entre `0.20` y `0.35`. Esto sucede porque los fenómenos humanos y demográficos (como la densificación urbana o la pobreza en la periferia) **no generan clusters espacialmente aislados y perfectamente separados** (esferas puras), sino que interactúan contiguamente creando continuos o zonas grises difusas inter-barriales. El puntaje es altamente aceptable para propósitos de Planeamiento Urbano.


| K | Silhouette Score |
|---|---|
| 2 | 0.259  |
| 3 | 0.249  |
| 4 | 0.263  |
| 5 | 0.272 *(Final)* |
| 6 | 0.239  |
| 7 | 0.232  |
| 8 | 0.230  |

## 2. Tipologías Barriales Descubiertas y Covalidad (Sin sesgo)
|   cluster_barrio | cluster_descripcion                       |   Tamano_Barrios |   NBI_Mean |   Infra_Mean |
|-----------------:|:------------------------------------------|-----------------:|-----------:|-------------:|
|                0 | Vulnerabilidad y Periferia NBI            |               79 |      15.11 |         0.17 |
|                1 | Núcleo Consolidado (Alta Infraestructura) |               80 |       4.4  |         0.57 |
|                2 | Anillos Densos Poblacionales              |               11 |       2.96 |         0.12 |
|                3 | Transición Urbana Mixta                   |              170 |       4.09 |         0.16 |
|                4 | Transición Urbana Mixta                   |              154 |       1.84 |         0.16 |