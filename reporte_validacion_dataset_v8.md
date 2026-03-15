# Reporte Técnico de Validación - Dataset Urbano v8

## 1. Resumen de Transformaciones
El presente reporte detalla las transformaciones de Feature Engineering aplicadas para llevar el dataset a nivel analítico (Machine Learning y GIS).

## 2. Fase 1: Auditoría Estructural
- **Barrios duplicados removidos:** 0
- **Manejo de Nulos y Negativos:** Se forzó a cero estadístico.

## 3. Fase 2: Corrección de Outliers (Capping)
- **Población:** 1 barrios limitados al umbral máximo de 60,000 hab.
- **Escuelas:** 2 macro-zonas limitadas a 40 escuelas (filtrando ruido regional).
- **Comisarías:** 2 barrios limitados a 2 dependencias.
- **Paradas:** 1 barrios limitados a 120 (corredores interurbanos descartados).

## 4. Fase 3: Validación Educativa
- Se recalculó algebraicamente `escuelas_total = estatales + privadas` para asegurar consistencia perfecta.
- Total de escuelas en el municipio sumadas: 1422

## 5. Fase 5: Validación Geográfica
> [!WARNING] Limitación Espacial
> Ante la falta de un Shapefile / GeoJSON oficial con los polígonos exactos de los 495 barrios censales, fue matemáticamente inviable utilizar el algoritmo `Point-in-Polygon`. Como mitigación documentada (ver v7), se empleó un híbrido de `Fuzzy Matching` Textual de alta precisión (>=75%) y Nearest-Neighbor `KD-Tree`.

## 6. Fases 7 y 8: Variables Derivadas y Dummy Access
Para habilitar un análisis equitativo entre macro-barrios y barrios pequeños, se derivaron las siguientes tasas y banderas lógicas:
- `hogares_por_poblacion`, `_por_1000_hab`, `_por_10000_hab`.
- Indicadores binarios `tiene_X`.

## 7. Fase 9: Índice Sintético de Infraestructura
Se instrumentó un `infraestructura_score` [0-1] calculado como la media estandarizada (MinMaxScaler) de las tasas de escuelas, transporte, comisarías y salud. Útil para mapas de calor.

## 8. Fase 4 & 6: Tabla de Cobertura y Descriptiva V8

| Variable | Cobertura % | Media | Max |
|---|---|---|---|
| `poblacion` | 96.0% | 3008.18 | 60000.00 |
| `hogares` | 96.0% | 1126.33 | 115184.00 |
| `nbi` | 87.7% | 98.63 | 22586.00 |
| `pct_nbi` | 87.7% | 5.78 | 40.62 |
| `escuelas_municipales` | 0.0% | 0.00 | 0.00 |
| `escuelas_total` | 58.0% | 2.87 | 80.00 |
| `escuelas_estatales` | 52.9% | 1.95 | 40.00 |
| `escuelas_privadas` | 20.6% | 0.93 | 40.00 |
| `centros_salud` | 19.6% | 0.20 | 2.00 |
| `paradas_colectivo` | 91.9% | 11.20 | 120.00 |
| `lineas_colectivo` | 91.5% | 4.09 | 64.00 |
| `luminarias_reportes` | 73.3% | 89.75 | 1419.00 |
| `comisarias` | 8.1% | 0.09 | 2.00 |
| `centros_vecinales` | 61.4% | 0.76 | 5.00 |
| `hogares_por_poblacion` | 96.0% | 0.28 | 1.92 |
| `escuelas_por_1000_hab` | 57.4% | 1.18 | 20.83 |
| `centros_salud_por_10000_hab` | 19.4% | 1.54 | 151.52 |
| `comisarias_por_10000_hab` | 8.1% | 0.35 | 15.92 |
| `paradas_por_1000_hab` | 89.1% | 9.72 | 230.77 |
| `centros_vec_por_10000_hab` | 60.2% | 6.07 | 129.03 |
| `tiene_escuela` | 58.0% | 0.58 | 1.00 |
| `tiene_centro_salud` | 19.6% | 0.20 | 1.00 |
| `tiene_comisaria` | 8.1% | 0.08 | 1.00 |
| `tiene_transporte` | 91.9% | 0.92 | 1.00 |
| `infraestructura_score` | 91.7% | 0.08 | 1.00 |