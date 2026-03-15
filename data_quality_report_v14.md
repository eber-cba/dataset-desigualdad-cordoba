# Data Quality Assessment V14 (Principal Level)

## 1. Anomalías Estructurales Detectadas y Resolución

### Imputaciones por Columna
- **`centroide_lat`**: Negativos: 494 | Resolución: Capping inferior a 0 (Bottom Clip)
- **`centroide_lon`**: Negativos: 494 | Resolución: Capping inferior a 0 (Bottom Clip)
- **`area_barrio_km2`**: NaNs: 5 | Resolución: Imputado con Mediana Robusta (0.28)
- **`densidad_poblacional`**: NaNs: 23 | Resolución: Imputado con Mediana Robusta (6950.94)
- **`densidad_hogares`**: NaNs: 23 | Resolución: Imputado con Mediana Robusta (2083.33)
- **`infraestructura_por_km2`**: NaNs: 23 | Resolución: Imputado con Mediana Robusta (0.56)