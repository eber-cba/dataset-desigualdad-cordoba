# Reporte de Clustering Ortogonal V15
## 1. Selección del Nivel 'K' Libre de Leakage
**Decisión Arquitectónica:** K-Means matemático puro sin sesgo de colinealidad. K Óptimo: 5.

| K | Silhouette Score |
|---|---|
| 2 | 0.2590  |
| 3 | 0.2488  |
| 4 | 0.2630  |
| 5 | 0.2721 *(Final)* |
| 6 | 0.2392  |
| 7 | 0.2317  |
| 8 | 0.2296  |

## 2. Tipologías Barriales Descubiertas y Covalidad (Sin sesgo)
|   cluster_barrio | cluster_descripcion                             |   Tamano_Barrios |   NBI_Mean |   Infra_Mean |
|-----------------:|:------------------------------------------------|-----------------:|-----------:|-------------:|
|                0 | Periferia Excluida (Vulnerabilidad Crítica NBI) |               79 |      15.11 |         0.17 |
|                1 | Núcleo Consolidado (Alta Infraestructura)       |               80 |       4.4  |         0.57 |
|                2 | Anillos Densos Trabajadores                     |               11 |       2.96 |         0.12 |
|                3 | Transición Urbana Mixta                         |              170 |       4.09 |         0.16 |
|                4 | Transición Urbana Mixta                         |              154 |       1.84 |         0.16 |