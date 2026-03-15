# Diccionario de Datos V12 - Urban Data Platform

| Variable | Tipo | Rol Analítico |
|---|---|---|
| `barrio` | str | Característica Base Espacial |
| `poblacion` | float64 | Característica Base Espacial |
| `hogares` | float64 | Característica Base Espacial |
| `nbi` | float64 | Característica Base Espacial |
| `pct_nbi` | float64 | Característica Base Espacial |
| `escuelas_total` | int64 | Característica Base Espacial |
| `escuelas_estatales` | int64 | Característica Base Espacial |
| `escuelas_privadas` | int64 | Característica Base Espacial |
| `dispensarios_municipales` | int64 | Característica Base Espacial |
| `paradas_colectivo` | int64 | Característica Base Espacial |
| `lineas_colectivo` | int64 | Característica Base Espacial |
| `luminarias_reportes` | int64 | Característica Base Espacial |
| `comisarias` | int64 | Característica Base Espacial |
| `centros_vecinales` | int64 | Característica Base Espacial |
| `hogares_por_poblacion` | float64 | Característica Base Espacial |
| `poblacion_log` | float64 | Característica Base Espacial |
| `pct_escuelas_privadas` | float64 | Característica Base Espacial |
| `escuelas_por_1000_hab` | float64 | Característica Base Espacial |
| `dispensarios_por_10000_hab` | float64 | Característica Base Espacial |
| `comisarias_por_10000_hab` | float64 | Característica Base Espacial |
| `paradas_por_1000_hab` | float64 | Característica Base Espacial |
| `centros_vecinales_por_10000_hab` | float64 | Característica Base Espacial |
| `tiene_escuela` | int64 | Característica Base Espacial |
| `tiene_dispensario` | int64 | Característica Base Espacial |
| `tiene_comisaria` | int64 | Característica Base Espacial |
| `tiene_transporte` | int64 | Característica Base Espacial |
| `infraestructura_score` | float64 | Feature Engineering (Ingeniería Avanzada) |
| `area_barrio_km2` | float64 | Característica Base Espacial |
| `densidad_poblacional` | float64 | Característica Base Espacial |
| `densidad_hogares` | float64 | Característica Base Espacial |
| `infraestructura_por_km2` | float64 | Característica Base Espacial |
| `educacion_ratio_publico_privado` | float64 | Feature Engineering (Ingeniería Avanzada) |
| `centroide_lat` | float64 | Característica Base Espacial |
| `centroide_lon` | float64 | Característica Base Espacial |
| `cluster_barrio` | int32 | Métrica Machine Learning (K-Means) |
| `cluster_descripcion` | str | Métrica Machine Learning (K-Means) |
| `categoria_infraestructura` | str | Meta-Feature para Viz (Frontend) |
| `tooltip_barrio` | str | Meta-Feature para Viz (Frontend) |
| `servicios_basicos_score` | float64 | Feature Engineering (Ingeniería Avanzada) |
| `infraestructura_por_habitante` | float64 | Característica Base Espacial |
| `ranking_infraestructura` | int64 | Característica Base Espacial |
| `percentil_infraestructura` | float64 | Característica Base Espacial |