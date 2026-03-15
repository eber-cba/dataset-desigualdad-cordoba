# Análisis Exploratorio Urbano (EDA) V14

## 1. Matriz de Correlación Sociodemográfica
|                       |   pct_nbi |   infraestructura_score |   poblacion |   densidad_poblacional |   escuelas_por_1000_hab |
|:----------------------|----------:|------------------------:|------------:|-----------------------:|------------------------:|
| pct_nbi               |      1    |                   -0.04 |        0.12 |                   0.06 |                   -0    |
| infraestructura_score |     -0.04 |                    1    |       -0.21 |                  -0.07 |                    0.69 |
| poblacion             |      0.12 |                   -0.21 |        1    |                   0.2  |                   -0.05 |
| densidad_poblacional  |      0.06 |                   -0.07 |        0.2  |                   1    |                   -0.16 |
| escuelas_por_1000_hab |     -0    |                    0.69 |       -0.05 |                  -0.16 |                    1    |

## 2. Análisis de Outliers Estadísticos (Rango Intercuartílico IQR)
Los outliers en estudios territoriales no siempre significan 'errores de lectura', sino realidades espaciales extremas (Grandes Asentamientos o Micro-Centros HIPER-densos).

| Variable Métrica | Limit Superior (Q3+1.5*IQR) | % Outliers Naturales |
|---|---|---|
| `pct_nbi` | 18.04 | 3.6% |
| `infraestructura_score` | 0.61 | 5.9% |
| `poblacion` | 6948.75 | 6.5% |
| `densidad_poblacional` | 15090.40 | 3.8% |
| `escuelas_por_1000_hab` | 3.82 | 7.3% |