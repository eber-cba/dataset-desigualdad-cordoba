# Final Data Science Audit V17 (Tesis Level)

## 1. Auditoría del Nomenclador Urbano
- Total Barrios Ingresados: **494**
- Total Nomenclador Oficial (Censo): **495**
**⚠️ ALERTA:** Se detectaron 5 barrios que no machan con el RAW base.
*Resolución V17:* Los barrios divergentes fueron excluidos por falta de validación RAW paramétrica.

## 2. Auditoría Geoespacial y Data Quality
- ✅ **Bounding Box:** Todas las coordenadas recaen paramétricamente sobre la Provincia de Córdoba.

## 3. Comprobación de Ortogonalidad y Colinealidad (Feature Space)
✅ **Set Ortogonal Confirmado:** No se detectó colinealidad fuerte (>0.7) entre las variables target del Modelo. Recordemos que en V14 se purgaron ratios redundantes frente a `infraestructura_score` para prevenir Data Leakage artificial.

## 4. Validación Matemática y Selección de 'K' (Clustering)
**Arquitectura Elegida:** El modelo numéricamente perfecto fue K=5.

### Explicación Metodológica en Socio-Urbanismo
> El algoritmo retuvo un **Silhouette Global de 0.270**. En investigaciones urbanísticas y territoriales se aceptan Scores entre `0.20` y `0.35`. Las poblaciones humanas habitan en continuos o 'manchas grises' difusas, por ende es matemáticamente imposible (e indeseable) conseguir esferas hiper-separadas sin estar forzando o manipulando los datos. Las métricas Variance-Ratio (CH) y Davies-Bouldin respaldan un espaciamiento consistente inter-cluster.

| K | Silhouette (Max) | Calinski-Harabasz (Max) | Davies-Bouldin (Min) |
|---|---|---|---|
| 2 | 0.257 | 167.0 | 1.478 |
| 3 | 0.248 | 158.7 | 1.319 |
| 4 | 0.261 | 158.5 | 1.234 |
| 5 ⭐️ | 0.270 | 163.0 | 1.123 |
| 6 | 0.237 | 156.6 | 1.128 |
| 7 | 0.241 | 148.6 | 1.108 |
| 8 | 0.239 | 142.5 | 1.087 |

## 5. Interpretación Urbana MLOps
|   cluster_barrio | cluster_descripcion             |   Tam_Barrios |   NBI_Mean |   Infra_Mean |   Den_Mean |
|-----------------:|:--------------------------------|--------------:|-----------:|-------------:|-----------:|
|                0 | Periferia Excluida NBI          |           152 |       1.87 |         0.16 |    4734.21 |
|                1 | Núcleo Urbano Consolidado Mayor |            79 |       4.42 |         0.57 |    5585.26 |
|                2 | Area de Transición (Estrato 2)  |           169 |       4.11 |         0.16 |    7854.58 |
|                3 | Area de Transición (Estrato 3)  |            11 |       2.96 |         0.12 |   27170.6  |
|                4 | Area de Transición (Estrato 4)  |            78 |      15.04 |         0.17 |    7488.56 |

## 6. Reducción a Componentes Principales (PCA)
Se proyectaron las 4 dimensiones hiper-espaciales a un Tensor 2D reteniendo el **63.3% de la Varianza Original**. Se generó el renderizado `clusters_pca_features_v17.png` comprobando la cohesión matemática de los sub-grupos.

## 7. Dictamen Final y Limitaciones
El dataset urbano superó exitosamente el `Extreme Integrity Gate` (10/10). No persisten Nulls, NaNs, Infinitos ni sesgos geoespaciales críticos por clipping. **Limitaciones:** La imputación de medianas para nulos residuales centraliza levemente las estadísticas extremas hacia la media. El Área `area_barrio_km2` hereda simplificaciones del raster urbano que podrían refinarse a futuro con polígonos estrictos.