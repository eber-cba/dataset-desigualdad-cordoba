# Reporte Técnico de Auditoría Final - Urban Data Science V11

## 1. Validación de Hipótesis y Decisiones Estructurales
- **Escuelas Municipales (0%):** Ratificado el fallo de origen por *Unnamed columns*. Columna suprimida desde V10.
- **Centros de Salud (~19%):** Ratificado el subregistro al excluir la red provincial. Renombrado a `dispensarios_municipales` por exactitud léxica.
- **Mortalidad de Variables:** Se suprimió `densidad_hogares` y se reformuló `hogares_por_poblacion` en su inversa analítica `tamano_promedio_hogar` para evitar varianzas espurias (maximizando la interpretabilidad social de hacinamiento relativo).
- **Distribución de Score:** Plausible tras aplicar Winsorizing P95. Se mantienen los pesos MCDA (40/30/20/10) ya que la regresión territorial demanda sobreponderar transporte y educación primaria en análisis intra-urbanos.
- **Límites de Capping:** Se mantienen. Son vitales en Geometría Voronoi (Espacial Continua) para evitar que sumideros de falsos positivos absorban 400 paradas en límites abstractos de barrios grandes.

## 2. Ingeniería de Características (Feature Engineering V11)
- `tamano_promedio_hogar`: Proxy superior del nivel socioeconómico en sustitución de `hogares_por_poblacion`.
- `educacion_ratio_publico_privado`: Índice de segregación escolar.
- Índices de Ordenación: `ranking_infraestructura` y `percentil_infraestructura` añadidos para visualizaciones interactivas de tableros (e.g. 'Barrio Top 5%').

## 3. Profiling de Asimetría (Machine Learning Prep)

| Variable | Skewness (Simetría) | Kurtosis (Colas) | Recomendación ML |
|---|---|---|---|
| `poblacion` | 5.74 | 44.31 | Aplicar Logaritmo (log1p) o BoxCox |
| `hogares` | 6.46 | 50.32 | Aplicar Logaritmo (log1p) o BoxCox |
| `nbi` | 9.11 | 123.38 | Aplicar Logaritmo (log1p) o BoxCox |
| `pct_nbi` | 1.69 | 3.62 | Asimetría Leve (Vigilar Árboles vs OLS) |
| `escuelas_total` | 4.19 | 22.87 | Aplicar Logaritmo (log1p) o BoxCox |
| `escuelas_estatales` | 2.79 | 11.65 | Aplicar Logaritmo (log1p) o BoxCox |
| `escuelas_privadas` | 5.40 | 34.95 | Aplicar Logaritmo (log1p) o BoxCox |
| `dispensarios_municipales` | 1.74 | 1.73 | Asimetría Leve (Vigilar Árboles vs OLS) |
| `paradas_colectivo` | 3.49 | 24.23 | Aplicar Logaritmo (log1p) o BoxCox |
| `lineas_colectivo` | 5.23 | 44.40 | Aplicar Logaritmo (log1p) o BoxCox |
| `luminarias_reportes` | 3.94 | 21.98 | Aplicar Logaritmo (log1p) o BoxCox |
| `comisarias` | 3.73 | 14.38 | Aplicar Logaritmo (log1p) o BoxCox |
| `centros_vecinales` | 1.11 | 2.93 | Asimetría Leve (Vigilar Árboles vs OLS) |
| `poblacion_log` | 0.68 | 0.22 | OK |
| `pct_escuelas_privadas` | 2.26 | 4.02 | Aplicar Logaritmo (log1p) o BoxCox |
| `escuelas_por_1000_hab` | 1.52 | 1.58 | Asimetría Leve (Vigilar Árboles vs OLS) |
| `dispensarios_por_10000_hab` | 2.41 | 4.50 | Aplicar Logaritmo (log1p) o BoxCox |
| `comisarias_por_10000_hab` | 3.56 | 11.06 | Aplicar Logaritmo (log1p) o BoxCox |
| `paradas_por_1000_hab` | 1.37 | 1.04 | Asimetría Leve (Vigilar Árboles vs OLS) |
| `centros_vecinales_por_10000_hab` | 3.52 | 21.06 | Aplicar Logaritmo (log1p) o BoxCox |
| `tiene_escuela` | -0.32 | -1.90 | OK |
| `tiene_dispensario` | 1.53 | 0.35 | Asimetría Leve (Vigilar Árboles vs OLS) |
| `tiene_comisaria` | 3.08 | 7.53 | Aplicar Logaritmo (log1p) o BoxCox |
| `tiene_transporte` | -3.08 | 7.53 | Aplicar Logaritmo (log1p) o BoxCox |
| `infraestructura_score` | 1.34 | 1.73 | Asimetría Leve (Vigilar Árboles vs OLS) |
| `centroide_lat` | 0.16 | -0.91 | OK |
| `centroide_lon` | 0.16 | -0.67 | OK |
| `tamano_promedio_hogar` | 0.12 | -0.74 | OK |
| `educacion_ratio_publico_privado` | 1.61 | 2.23 | Asimetría Leve (Vigilar Árboles vs OLS) |
| `ranking_infraestructura` | -0.02 | -1.22 | OK |
| `percentil_infraestructura` | 0.00 | -1.20 | OK |

## 4. Multiplexación Tecnológica (Outputs Generados)
Con la intención de proveer material agnóstico para todo el espectro de la ciencia de datos, V11 derivó 3 objetos terminales:
1. **`dataset_dashboard_v11.csv`** (Plano): Versión limpia, legible y optimizada para alimentar motores como PowerBI, Tableau o React.js.
2. **`dataset_ml_v11.csv`** (Matriz Tensorial Z-Scored): Features normalizados computacionalmente mediante `StandardScaler` (Media 0, Var 1), impidiendo que distancias algorítmicas (Euclidiana) se sesguen en clústeres tipo K-Means o KNN.
3. **`dataset_gis_v11.geojson`** (GeoDataFrame): Empaquetamiento georeferenciado usando *EPSG:4326 (WGS84)* estándar mundial, instanciado vía Geopandas para consumo directo en QGIS o Leaflet/Mapbox frontend.