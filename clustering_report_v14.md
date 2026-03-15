# Reporte de Clustering MLOps V14

## 1. Selección del Nivel 'K' (Silhouette Score)
**Decisión Arquitectónica:** Modelado ajustado en 2 clústers al maximizar matemáticamente la Métrica Global (Silhouette).

| K | Silhouette Score |
|---|---|
| 2 | 0.3444 *(Final)* |
| 3 | 0.2282  |
| 4 | 0.2279  |
| 5 | 0.2332  |
| 6 | 0.2405  |
| 7 | 0.2323  |
| 8 | 0.2331  |
| 9 | 0.2193  |
| 10 | 0.2159  |

## 2. Tipologías Barriales Descubiertas e Interpretación Social
|   cluster_barrio | cluster_descripcion                                         |   Tamano_Barrios |   NBI_Mean |   Infra_Mean |
|-----------------:|:------------------------------------------------------------|-----------------:|-----------:|-------------:|
|                0 | Transición Urbana (Vulnerabilidad Media, Servicios Básicos) |              379 |       5.5  |         0.15 |
|                1 | Núcleo Consolidado (Alto Estándar, Alta Infraestructura)    |              115 |       4.11 |         0.5  |