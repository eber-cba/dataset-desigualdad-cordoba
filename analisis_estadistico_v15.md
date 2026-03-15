# Análisis Exploratorio Urbano V15

## 1. Matriz Ortogonal Sociodemográfica
|                       |   pct_nbi |   infraestructura_score |   poblacion |   densidad_poblacional |
|:----------------------|----------:|------------------------:|------------:|-----------------------:|
| pct_nbi               |      1    |                   -0.04 |        0.12 |                   0.11 |
| infraestructura_score |     -0.04 |                    1    |       -0.21 |                  -0.06 |
| poblacion             |      0.12 |                   -0.21 |        1    |                   0.22 |
| densidad_poblacional  |      0.11 |                   -0.06 |        0.22 |                   1    |

## 2. Análisis de Outliers Típicos (Regiones Dispares)
| Variable Métrica | Limit Superior (Q3+1.5*IQR) | % Outliers Naturales |
|---|---|---|
| `pct_nbi` | 18.04 | 3.6% |
| `infraestructura_score` | 0.61 | 5.9% |
| `poblacion` | 6948.75 | 6.5% |
| `densidad_poblacional` | 16003.13 | 3.6% |